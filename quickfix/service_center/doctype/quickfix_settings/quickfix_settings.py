# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class QuickFixSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		default_labour_charge: DF.Currency
		low_stock_alert_enabled: DF.Check
		low_stock_threshold: DF.Float
		manager_email: DF.Data
		shop_name: DF.Data | None
		webhook_url: DF.Data | None
	# end: auto-generated types

	pass
