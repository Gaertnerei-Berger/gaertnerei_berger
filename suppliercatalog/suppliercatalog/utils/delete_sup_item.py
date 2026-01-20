import frappe

def delete_all_catalog_items_job(docname):

    items = frappe.get_all(
        "Supplier Catalog Item",
        filters={"supplier_catalog": docname},
        pluck="name"
    )

    total = len(items)
    deleted = 0
    failed = 0

    if not total:
        frappe.publish_progress(
            100,
            title="Delete Supplier Catalog Items",
            description="No items found to delete."
        )
        return

    for index, name in enumerate(items, start=1):
        try:
            frappe.delete_doc(
                "Supplier Catalog Item",
                name,
                ignore_permissions=True,
                force=True,
                ignore_on_trash=True
            )
            deleted += 1
        except Exception:
            failed += 1
            frappe.log_error(
                title="Supplier Catalog Item Delete Failed",
                message=f"Item: {name}\n\n{frappe.get_traceback()}"
            )

        # Progress update
        progress = int((index / total) * 100)

        frappe.publish_progress(
            progress,
            title="Delete Supplier Catalog Items",
            description=f"Deleted {index} of {total}"
        )

        # Commit in batches
        if index % 100 == 0:
            frappe.db.commit()

    frappe.db.commit()

    frappe.db.set_value(
        "Supplier Catalog",
        docname,
        {
            "import_status": "Empty",
            "import_amount": 0
        }
    )

    frappe.publish_progress(
        100,
        title="Delete Supplier Catalog Items",
        description=f"Finished. Deleted: {deleted}, Failed: {failed}"
    )