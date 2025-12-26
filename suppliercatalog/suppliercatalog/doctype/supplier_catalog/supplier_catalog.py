# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SupplierCatalog(Document):
	pass

@frappe.whitelist()
def import_supplier_catalog_items_from_file(docname):
    from suppliercatalog.utils.file_importer import import_supplier_catalog_items_from_csv
    doc = frappe.get_doc("Supplier Catalog", docname)
    return import_supplier_catalog_items_from_csv(doc)
