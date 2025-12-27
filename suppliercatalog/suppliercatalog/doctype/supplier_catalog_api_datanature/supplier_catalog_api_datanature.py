# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from suppliercatalog.utils.datanature_api import fetch_security_token


class SupplierCatalogAPIDatanature(Document):
   pass


@frappe.whitelist()
def test_login():
        """Fetch token from API and store it in this document"""
        token = fetch_security_token()
        doc = frappe.get_single("Supplier Catalog API Datanature")
        doc.security_token = token
        doc.save()
        frappe.db.commit()
