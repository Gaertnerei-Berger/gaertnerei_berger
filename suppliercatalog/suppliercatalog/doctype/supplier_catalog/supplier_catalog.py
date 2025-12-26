# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe

from frappe.model.document import Document

class SupplierCatalog(Document):
	pass

@frappe.whitelist()
def import_bnn_items_from_file(docname):
    from suppliercatalog.utils.bnn_importer import import_bnn_items_from_csv
    doc = frappe.get_doc("Supplier Catalog", docname)
    return import_bnn_items_from_csv(doc)
