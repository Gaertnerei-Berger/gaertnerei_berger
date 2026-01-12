import frappe
import json
from frappe.utils import cint
from suppliercatalog.utils.sup_item_import_mapping import (FIELD_MAPPING, is_empty)  

@frappe.whitelist()
def import_sci_bulk(lookup_type, lookup_values, item_group):
    """
    Bulk import Supplier Catalog Items based on lookup values.
    Returns found / not found values.
    """

    if isinstance(lookup_values, str):
        lookup_values = json.loads(lookup_values)

    if not lookup_values:
        frappe.throw("Keine Suchwerte übergeben.")

    # Mapping Lookup-Typ → Feld
    lookup_field_map = {
        "EAN Shop": "ean_shop",
        "Name": "name1",
        "BIO-ID": "item_bio_id",
        "Supplier Itemnumber":"supplier_itemnumber",
    }

    lookup_field = lookup_field_map.get(lookup_type)

    if not lookup_field:
        frappe.throw(f"Unbekannter Lookup-Typ: {lookup_type}")

    found_items = []
    not_found = []

    # Suche Supplier Catalog Items
    for value in lookup_values:
        value = value.strip()
        if not value:
            continue

        sci_name = frappe.db.get_value(
            "Supplier Catalog Item",
            {lookup_field: value},
            "name"
        )

        if sci_name:
            found_items.append(sci_name)
        else:
            not_found.append(value)

    # Nichts gefunden → sauber abbrechen
    if not found_items:
        return {
            "found": [],
            "not_found": not_found,
            "created": [],
            "skipped": []
        }

    # Import aufrufen (reuse existing logic)
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
    Import Supplier Catalog Items into ERPNext Item.
    """

    # Check is Supplier Catalog Settings are set
    required_fields = [
    "sell_pricelist",
    "purchase_pricelist",
    "tax_category_ek",
    "tax_category_vk",
    "tax_template_7_ek",
    "tax_template_7_vk",
    "expense_account_7",
    "income_account_7",
    "tax_template_19_ek",
    "tax_template_19_vk",
    "expense_account_19",
    "income_account_19"
    ]
    settings = frappe.get_single("Supplier Catalog Settings")
    for field in required_fields:
        if not settings.get(field):
            frappe.throw(
                "Supplier Catalog Settings are not fully configured. "
                "Please check the settings before running the import."
            )

    if not item_group:
        item_group = settings.itemgroup_select

    if not item_group:
        frappe.throw("Keine Artikelgruppe definiert in Supplier Catalog Settings.")

    # Get the Items from the List view
    if isinstance(supplier_catalog_item_names, str):
        try:
            supplier_catalog_item_names = json.loads(supplier_catalog_item_names)
        except Exception:
            supplier_catalog_item_names = [supplier_catalog_item_names]

    created_items = []
    skipped_items = []

    

    for sci_name in supplier_catalog_item_names:

        if not frappe.db.exists("Supplier Catalog Item", sci_name):
            skipped_items.append(sci_name)
            continue

        supplier_item = frappe.get_doc("Supplier Catalog Item", sci_name)


        if supplier_item.get("imported") == 1:
            skipped_items.append(sci_name)
            continue

        bio_id = supplier_item.get("item_bio_id")

        if not is_empty(bio_id):
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
            item.item_name = supplier_item.get("name1")


        # Add Shop barcode child row if ean_shop exists
        ean_shop = supplier_item.get("ean_shop")
        uom_shop = supplier_item.get("shop_unit_uom")

        if not is_empty(ean_shop):
            item.append("barcodes", {
                "barcode": ean_shop,
                "barcode_type": "EAN",
                "uom": uom_shop
            })

        # Add Vpe1 barcode child row if ean_shop exists
        ean_vpe1 = supplier_item.get("ean_order")
        uom_vpe1 = supplier_item.get("orderunit")

        if not is_empty(ean_vpe1):
            item.append("barcodes", {
                "barcode": ean_vpe1,
                "barcode_type": "EAN",
                "uom": uom_vpe1
            })

        # Add Supplier Nr to Supplier Items Childtabel
        sup_name = supplier_item.get("supplier")
        sup_item_nr = supplier_item.get("supplier_itemnumber")

        if not is_empty(sup_item_nr):
            item.append("supplier_items", {
                "supplier_part_no": sup_item_nr,
                "supplier": sup_name
            })

     
        # We need to insert the Item before we can set the Price
        item.insert(ignore_permissions=True)

       
        # Create Item Selling Price
        sell_price = supplier_item.get("recommended_sales_price")
        if sell_price > 0:
            if not is_empty(sell_price):
                supplier_catalog = frappe.get_doc(
                    "Supplier Catalog Settings",
                    supplier_item.supplier_catalog
                )

                item_price = frappe.new_doc("Item Price")
                item_price.item_code = item.name
                item_price.price_list = supplier_catalog.sell_pricelist
                item_price.price_list_rate = sell_price
                item_price.uom = supplier_item.get("shop_unit_uom")
                item_price.insert(ignore_permissions=True)



        # Create Item Purchasing Price
        buy_price = supplier_item.get("ek_price")
        if buy_price > 0:
            if not is_empty(buy_price):
                supplier_catalog = frappe.get_doc(
                    "Supplier Catalog Settings",
                    supplier_item.supplier_catalog
                )

                item_price = frappe.new_doc("Item Price")
                item_price.item_code = item.name
                item_price.price_list = supplier_catalog.purchase_pricelist
                item_price.price_list_rate = buy_price
                item_price.uom = supplier_item.get("shop_unit_uom")
                item_price.insert(ignore_permissions=True)


        # ------------------------------------------------------------
        # Set Taxes & Item Defaults based on tax_amount (7% / 19%)
        # ------------------------------------------------------------
               
        tax_amount = cint(supplier_item.get("tax_amount"))

        if tax_amount in (7, 9, 19):
            # Werte aus Supplier Catalog Settings (Singleton)
            tax_template_vk = settings.get(f"tax_template_{tax_amount}_vk")
            tax_template_ek = settings.get(f"tax_template_{tax_amount}_ek")
            income_account = settings.get(f"income_account_{tax_amount}")
            expense_account = settings.get(f"expense_account_{tax_amount}")
            tax_category_vk = settings.get("tax_category_vk")
            tax_category_ek = settings.get("tax_category_ek")



            # Item Defaults ersetzen
            item.set("item_defaults", [])
            default_company = frappe.defaults.get_global_default("company")

            item.append("item_defaults", {
                "company": default_company,
                "income_account": income_account,
                "expense_account": expense_account
            })

            # Item Taxes ersetzen
            item.set("taxes", [])

            # Verkauf
            if tax_template_vk:
                item.append("taxes", {
                    "item_tax_template": tax_template_vk,
                    "tax_category": tax_category_vk
                })

            # Einkauf
            if tax_template_ek:
                item.append("taxes", {
                    "item_tax_template": tax_template_ek,
                    "tax_category": tax_category_ek
                })

            item.save(ignore_permissions=True)


        supplier_item.linked_item = item.name
        supplier_item.imported = 1
        supplier_item.save(ignore_permissions=True)

        created_items.append(item.name)

    frappe.db.commit()

    return {
        "created": created_items,
        "skipped": skipped_items
    }