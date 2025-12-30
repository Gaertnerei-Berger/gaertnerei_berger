# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from suppliercatalog.utils.datanature_api import fetch_security_token, import_brand_abbreviations_from_api, import_approved_brands


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


@frappe.whitelist()
def load_brands():
    """Import brand abbreviations from DataNatuRe API."""
    import_brand_abbreviations_from_api()
    return "Brand import completed"


@frappe.whitelist()
def load_authorised_brands():
    """Import authorised brands from DataNatuRe API und the Logo Images."""
    import_approved_brands()
    return "Authorised Brand import completed"
