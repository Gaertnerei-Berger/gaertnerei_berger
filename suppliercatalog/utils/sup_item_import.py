import frappe
import json
from frappe.utils import cint
from suppliercatalog.utils.sup_item_import_mapping import (FIELD_MAPPING, is_empty)  

@frappe.whitelist()
def import_sci_bulk(lookup_type, lookup_values, item_group, supplier_catalog):
    """
    Bulk import Supplier Catalog Items based on lookup values
    and a selected Supplier Catalog.
    Returns found / not found values.
    """

    if isinstance(lookup_values, str):
        lookup_values = json.loads(lookup_values)

    if not lookup_values:
        frappe.throw("Keine Suchwerte übergeben.")

    if not supplier_catalog:
        frappe.throw("Supplier Catalog ist erforderlich.")

    lookup_field_map = {
        "EAN Shop": "ean_shop",
        "Name": "name1",
        "BIO-ID": "item_bio_id",
        "Supplier Itemnumber": "supplier_itemnumber",
    }

    lookup_field = lookup_field_map.get(lookup_type)
    if not lookup_field:
        frappe.throw(f"Unbekannter Lookup-Typ: {lookup_type}")

    found_items = []
    not_found = []

    for value in lookup_values:
        value = value.strip()
        if not value:
            continue

        sci_name = frappe.db.get_value(
            "Supplier Catalog Item",
            {
                lookup_field: value,
                "supplier_catalog": supplier_catalog
            },
            "name"
        )

        if sci_name:
            found_items.append(sci_name)
        else:
            not_found.append(value)

    if not found_items:
        return {
            "found": [],
            "not_found": not_found,
            "created": [],
            "skipped": []
        }

    result = import_sci(
        supplier_catalog_item_names=json.dumps(found_items),
        item_group=item_group
    )

    return {
        "found": found_items,
        "not_found": not_found,
        "created": result.get("created", []),
        "skipped": result.get("skipped", [])
    }




@frappe.whitelist()
def import_sci(supplier_catalog_item_names, item_group=None):
    """
    Import Supplier Catalog Items into ERPNext Items.
    Item-specific import, no Supplier Catalog check required.
    """

    # ------------------------------------------------------------------
    # Validate Supplier Catalog Settings (singleton)
    # ------------------------------------------------------------------
    required_fields = [
        "sell_pricelist",
        "purchase_pricelist",
        "tax_category",
        "tax_template_7",
        "expense_account_7",
        "income_account_7",
        "tax_template_19",
        "expense_account_19",
        "income_account_19",
    ]

    settings = frappe.get_single("Supplier Catalog Settings")

    for field in required_fields:
        if not settings.get(field):
            frappe.throw(
                "Supplier Catalog Settings are not fully configured. "
                "Please check the settings before running the import."
            )

    # ------------------------------------------------------------------
    # Resolve item group
    # ------------------------------------------------------------------
    if not item_group:
        item_group = settings.itemgroup_select

    if not item_group:
        frappe.throw("Keine Artikelgruppe definiert in Supplier Catalog Settings.")

    # ------------------------------------------------------------------
    # Normalize input
    # ------------------------------------------------------------------
    if isinstance(supplier_catalog_item_names, str):
        try:
            supplier_catalog_item_names = json.loads(supplier_catalog_item_names)
        except Exception:
            supplier_catalog_item_names = [supplier_catalog_item_names]

    created_items = []
    skipped_items = []

    # ------------------------------------------------------------------
    # Process items
    # ------------------------------------------------------------------
    for sci_name in supplier_catalog_item_names:

        if not frappe.db.exists("Supplier Catalog Item", sci_name):
            skipped_items.append(sci_name)
            continue

        supplier_item = frappe.get_doc("Supplier Catalog Item", sci_name)

        if supplier_item.imported == 1:
            skipped_items.append(sci_name)
            continue

        # ------------------------------------------------------------------
        # Prevent duplicate Items by BIO-ID
        # ------------------------------------------------------------------
        bio_id = supplier_item.get("item_bio_id")
        if bio_id:
            existing_item = frappe.db.get_value(
                "Item",
                {"custom_item_bio_id": bio_id},
                "name"
            )
            if existing_item:
                supplier_item.linked_item = existing_item
                supplier_item.imported = 1
                supplier_item.save(ignore_permissions=True)
                skipped_items.append(sci_name)
                continue

        # ------------------------------------------------------------------
        # Create Item
        # ------------------------------------------------------------------
        item = frappe.new_doc("Item")
        item.item_group = item_group
        item.is_stock_item = 1
        item.is_purchase_item = 1
        item.is_sales_item = 1
        item.custom_imported_supc = 1

        for source_field, target_field in FIELD_MAPPING.items():
            value = supplier_item.get(source_field)
            if not is_empty(value):
                item.set(target_field, value)

        if is_empty(item.item_name):
            item.item_name = supplier_item.name1

        # ------------------------------------------------------------------
        # Barcodes
        # ------------------------------------------------------------------
        if supplier_item.ean_shop:
            item.append("barcodes", {
                "barcode": supplier_item.ean_shop,
                "barcode_type": "EAN",
                "uom": supplier_item.shop_unit_uom
            })

        if supplier_item.ean_order:
            item.append("barcodes", {
                "barcode": supplier_item.ean_order,
                "barcode_type": "EAN",
                "uom": supplier_item.orderunit
            })

        # ------------------------------------------------------------------
        # Supplier Item
        # ------------------------------------------------------------------
        if supplier_item.supplier_itemnumber:
            item.append("supplier_items", {
                "supplier": supplier_item.supplier,
                "supplier_part_no": supplier_item.supplier_itemnumber
            })

        item.insert(ignore_permissions=True)

        # ------------------------------------------------------------------
        # Prices
        # ------------------------------------------------------------------
        if supplier_item.recommended_sales_price:
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item.name,
                "price_list": settings.sell_pricelist,
                "price_list_rate": supplier_item.recommended_sales_price,
                "uom": supplier_item.shop_unit_uom
            }).insert(ignore_permissions=True)

        if supplier_item.ek_price:
            frappe.get_doc({
                "doctype": "Item Price",
                "item_code": item.name,
                "price_list": settings.purchase_pricelist,
                "price_list_rate": supplier_item.ek_price,
                "uom": supplier_item.shop_unit_uom
            }).insert(ignore_permissions=True)

        # ------------------------------------------------------------------
        # Taxes
        # ------------------------------------------------------------------
        tax_amount = cint(supplier_item.tax_amount)

        if tax_amount in (7, 9, 19):
            item.set("item_defaults", [])
            item.set("taxes", [])

            item.append("item_defaults", {
                "company": frappe.defaults.get_global_default("company"),
                "income_account": settings.get(f"income_account_{tax_amount}"),
                "expense_account": settings.get(f"expense_account_{tax_amount}")
            })

            if settings.get(f"tax_template_{tax_amount}"):
                item.append("taxes", {
                    "item_tax_template": settings.get(f"tax_template_{tax_amount}"),
                    "tax_category": settings.tax_category
                })

            item.save(ignore_permissions=True)

        # ------------------------------------------------------------------
        # Mark Supplier Catalog Item as imported
        # ------------------------------------------------------------------
        supplier_item.linked_item = item.name
        supplier_item.imported = 1
        supplier_item.save(ignore_permissions=True)

        created_items.append(item.name)

    frappe.db.commit()

    return {
        "created": created_items,
        "skipped": skipped_items
    }