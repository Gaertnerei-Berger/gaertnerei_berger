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

    frappe.enqueue(
        method="suppliercatalog.utils.file_importer.import_supplier_catalog_items_from_csv",
        queue="long",
        timeout=60 * 60,
        doc=doc
    )

    return "Import started in background. This may take a while."


@frappe.whitelist()
# Its the DataNature API Import logic
def run_import_products(brand_id: str, supplier_catalog: str):

    if not brand_id or not supplier_catalog:
        frappe.throw("Brand ID and Supplier Catalog are required.")

    job_id = frappe.generate_hash(length=10)

    frappe.enqueue(
        method="suppliercatalog.utils.datanature_api.import_products",
        queue="long",
        timeout=60 * 30,
        job_id=job_id,
        brand_id=brand_id,
        supplier_catalog=supplier_catalog
    )

    return job_id


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