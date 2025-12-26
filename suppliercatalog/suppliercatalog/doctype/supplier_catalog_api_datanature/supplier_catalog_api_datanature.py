# Copyright (c) 2025, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from suppliercatalog.utils.datanature_api import fetch_and_store_security_token


class SupplierCatalogAPIDatanature(Document):
	pass


@frappe.whitelist()

def test_login():
    fetch_and_store_security_token()
