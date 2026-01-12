# Copyright (c) 2026, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from suppliercatalog.german_accounting.utils.price_list_calculation import calculate_all_from_settings
from frappe.model.document import Document


class PriceListCalculationSettings(Document):
	pass


@frappe.whitelist()
def run_price_list_calculation():
    return calculate_all_from_settings()