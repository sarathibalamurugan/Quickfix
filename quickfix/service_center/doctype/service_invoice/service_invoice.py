# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amended_from: DF.Link | None
		customer_name: DF.Data | None
		invoice_date: DF.Date | None
		job_card: DF.Link
		labour_charge: DF.Currency
		parts_total: DF.Currency
		payment_status: DF.Literal["Unpaid", "Paid"]
		total_amount: DF.Currency
	# end: auto-generated types


def get_permission_query_conditions(user=None):
	if not user:
		user = frappe.session.user
	if (user == "Administrator") or ("QF Manager" in frappe.get_roles(user)):
		return None
	else:
		return "`tabService Invoice`.`job_card` IN (SELECT name FROM `tabJob Card` WHERE payment_status = 'Paid')"
