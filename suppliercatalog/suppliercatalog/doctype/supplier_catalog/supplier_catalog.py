# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


# Sets the Doctype Name
class SupplierCatalog(Document):
    def autoname(self):
            if not self.supplier:
                frappe.throw("Please select a Supplier before saving.")

            # Fetch linked Supplier document
            supplier = frappe.get_doc("Supplier", self.supplier)

            # Get the Supplier's ID (e.g., SUP-00023)
            supplier_id = supplier.name

            # Get the Supplier's readable name
            supplier_name = supplier.supplier_name.strip().replace(" ", "_")

            # Construct the document name
            self.name = f"{supplier_id}-{supplier_name}"


@frappe.whitelist()
def import_supplier_catalog_items_from_file(docname):
    doc = frappe.get_doc("Supplier Catalog", docname)

    doc.db_set("import_status", "Running")

    from suppliercatalog.utils.file_importer import import_supplier_catalog_items_from_csv
    return import_supplier_catalog_items_from_csv(doc)


@frappe.whitelist()
# Its the DataNature API Import logic
def run_import_products(brand_id: str, supplier_catalog: str):
     from suppliercatalog.utils.datanature_api import import_products
     import_products(brand_id,supplier_catalog)



@frappe.whitelist()
def enqueue_delete_all_catalog_items(docname):
    if not docname:
        frappe.throw("Supplier Catalog name is required")

    doc = frappe.get_doc("Supplier Catalog", docname)

    doc.db_set("import_status", "Deleting")

    frappe.enqueue(
        method="suppliercatalog.suppliercatalog.utils.delete_sup_item.delete_all_catalog_items_job",
        queue="long",
        timeout=60 * 30,
        docname=docname
    )

    return "Deletion of all supplier catalog items has been started."