import frappe
import time

def before_submit(doc, method):
    # only runs on save/update
    update_stock(doc)

def update_stock(doc):

    settings = frappe.get_single("German Accounting Settings")
    if int(settings.later_warehousesetup or 0) != 1:
        return

    items_to_receive = []

    for row in doc.items:
        if not row.item_code or row.qty is None:
            continue

        is_stock_item = frappe.db.get_value(
            "Item",
            row.item_code,
            "is_stock_item"
        )

        if not is_stock_item:
            continue

        warehouse = row.warehouse
        if not warehouse:
            continue

        available_qty = frappe.db.get_value(
            "Bin",
            {
                "item_code": row.item_code,
                "warehouse": warehouse
            },
            "actual_qty"
        ) or 0

        
        missing_qty = row.qty - available_qty

        if missing_qty > 0:
            items_to_receive.append({
                "item_code": row.item_code,
                "t_warehouse": warehouse,
                "qty": missing_qty,
                "incoming_rate": 0,
                "allow_zero_valuation_rate": 1
           })

        
    if not items_to_receive:
        return

    se = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt",
        "company": doc.company,
        "posting_date": doc.posting_date,
        "posting_time": doc.posting_time,
        "remarks": f"Auto receipt (missing qty) for DN {doc.name}",
        "items": items_to_receive
    })

    se.insert(ignore_permissions=True)
    se.submit()

