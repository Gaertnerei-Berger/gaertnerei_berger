# Copyright (c) 2026, Gärtnerei Berger and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime
from decimal import Decimal, ROUND_HALF_UP
from frappe.model.document import Document


class PriceListCalculationSettings(Document):
	pass
