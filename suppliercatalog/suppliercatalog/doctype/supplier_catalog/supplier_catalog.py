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

# Its the File Import logic
def import_supplier_catalog_items_from_file(docname):
    from suppliercatalog.utils.file_importer import import_supplier_catalog_items_from_csv
    doc = frappe.get_doc("Supplier Catalog", docname)
    return import_supplier_catalog_items_from_csv(doc)
