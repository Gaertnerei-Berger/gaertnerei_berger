import frappe
from frappe.utils import flt, now_datetime


SETTINGS_DOCTYPE = "Price List Calculation Settings"

def on_update(doc, method=None):
    # only runs on save/update
    calculate_single_item_price(doc)

def _get_settings():
    settings = frappe.get_single("Price List Calculation Settings")

    required = [
        "source_price_list",
        "calculated_price_list",
        "price_list_type",
        "vat_7_tax_template",
        "vat_19_tax_template",
    ]

    missing = [f for f in required if not settings.get(f)]
    if missing:
        frappe.throw(
            "Price List Calculation Settings not fully configured. "
            f"Missing: {', '.join(missing)}"
        )

    return settings


def _get_price_list_currency(price_list_name: str) -> str:
    return frappe.db.get_value("Price List", price_list_name, "currency")


def _get_item_vat_rate_from_first_tax_template(item_code: str, settings, *, strict: bool):
    """
    VAT rate is determined by:
    Item -> taxes (first row) -> item_tax_template

    The template itself is compared against:
    - settings.vat_7_tax_template
    - settings.vat_19_tax_template

    Returns:
        (vat_rate: float | None, error_message: str | None)
    """

    # Load Item (cached for performance)
    item = frappe.get_cached_doc("Item", item_code)

    # Item must have Item Taxes
    if not item.get("taxes"):
        if strict:
            return None, "Item has no Item Taxes rows"
        return None, None

    # Always use the first tax row
    first_tax_row = item.taxes[0]
    template_name = first_tax_row.get("item_tax_template")

    if not template_name:
        if strict:
            return None, "First Item Taxes row has no Item Tax Template"
        return None, None

    # Match directly against configured templates
    if template_name == settings.vat_7_tax_template:
        return 0.07, None

    if template_name == settings.vat_19_tax_template:
        return 0.19, None

    # Template exists but is not mapped
    if strict:
        return (
            None,
            f"Item Tax Template '{template_name}' is not mapped to 7% or 19% in settings"
        )

    return None, None

def _calculate_target_rate(source_rate: float, vat_rate: float, price_list_type: str) -> float:
    """
    price_list_type describes the SOURCE.
    Gross -> target is Net
    Net   -> target is Gross
    """
    if price_list_type == "Gross":
        return source_rate / (1.0 + vat_rate)
    if price_list_type == "Net":
        return source_rate * (1.0 + vat_rate)
    frappe.throw(f"Unknown price_list_type: {price_list_type}")


def _upsert_item_price(*, item_code: str, uom: str, price_list: str, rate: float, currency: str):
    """
    Upsert Item Price for (item_code, uom, price_list). Always overwrite.
    """
    existing = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "uom": uom, "price_list": price_list},
        "name",
    )

    if existing:
        doc = frappe.get_doc("Item Price", existing)
        # If same, do nothing (optional micro-optimization)
        if flt(doc.price_list_rate) == flt(rate) and doc.currency == currency:
            return existing, False

        doc.price_list_rate = rate
        doc.currency = currency
        doc.save(ignore_permissions=True)
        return existing, True

    doc = frappe.new_doc("Item Price")
    doc.item_code = item_code
    doc.price_list = price_list
    doc.uom = uom
    doc.currency = currency
    doc.price_list_rate = rate
    doc.insert(ignore_permissions=True)
    return doc.name, True


def calculate_all_from_settings():
    """
    Start Now: process all Item Prices in source_price_list
    - strict VAT mapping: errors collected, no hard stop
    - updates last_run at end
    """
    settings = _get_settings()

    source_pl = settings.source_price_list
    target_pl = settings.calculated_price_list
    price_list_type = settings.price_list_type
    rounding_precision = int(settings.rounding_precision or 2)

    currency = _get_price_list_currency(source_pl)
    if not currency:
        frappe.throw(f"Source Price List '{source_pl}' has no currency set.")

    # Fetch all source Item Prices (all UOMs)
    rows = frappe.get_all(
        "Item Price",
        filters={"price_list": source_pl},
        fields=["name", "item_code", "uom", "price_list_rate"],
        order_by="modified desc",
    )

    processed = 0
    updated = 0
    created = 0
    skipped = 0
    errors = []  # list of dicts

    for r in rows:
        item_code = r.get("item_code")
        uom = r.get("uom")
        source_rate = flt(r.get("price_list_rate"))

        processed += 1

        vat_rate, err = _get_item_vat_rate_from_first_tax_template(item_code, settings, strict=True)
        if not vat_rate:
            skipped += 1
            errors.append({
                "item_code": item_code,
                "uom": uom,
                "reason": err or "VAT not determinable"
            })
            continue

        target_rate = _calculate_target_rate(source_rate, vat_rate, price_list_type)
        target_rate = round(flt(target_rate), rounding_precision)

        name, did_change = _upsert_item_price(
            item_code=item_code,
            uom=uom,
            price_list=target_pl,
            rate=target_rate,
            currency=currency,
        )
        if did_change:
            # created vs updated
            if name and frappe.db.get_value("Item Price", name, "creation") == frappe.db.get_value("Item Price", name, "modified"):
                created += 1
            else:
                updated += 1

    # update last_run
    settings.last_run = now_datetime()
    settings.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "processed": processed,
        "updated": updated,
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "source_price_list": source_pl,
        "calculated_price_list": target_pl,
    }


def calculate_single_item_price(item_price_doc):
    """
    Auto Generate: process only this one Item Price row (item_code + uom)
    - strict=False: if VAT not determinable -> skip silently
    - only used when price_list == source_price_list and auto_generate_prices enabled
    """
    settings = _get_settings()

    if not settings.auto_generate_prices:
        return

    if item_price_doc.price_list != settings.source_price_list:
        return

    source_rate = flt(item_price_doc.price_list_rate)
    item_code = item_price_doc.item_code
    uom = item_price_doc.uom

    vat_rate, _ = _get_item_vat_rate_from_first_tax_template(
        item_code, settings, strict=False
    )
    if not vat_rate:
        return  # silent skip

    rounding_precision = int(settings.rounding_precision or 2)
    currency = _get_price_list_currency(settings.source_price_list)

    target_rate = _calculate_target_rate(
        source_rate, vat_rate, settings.price_list_type
    )
    target_rate = round(flt(target_rate), rounding_precision)

    name, changed = _upsert_item_price(
        item_code=item_code,
        uom=uom,
        price_list=settings.calculated_price_list,
        rate=target_rate,
        currency=currency,
    )
