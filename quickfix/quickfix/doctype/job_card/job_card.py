# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class JobCard(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from quickfix.quickfix.doctype.part_usage_entry.part_usage_entry import PartUsageEntry

		amended_from: DF.Link | None
		assigned_technician: DF.Link | None
		customer_email: DF.Data | None
		customer_name: DF.Data
		customer_phone: DF.Data
		delivery_date: DF.Date | None
		device_brand: DF.Data | None
		device_model: DF.Data | None
		device_type: DF.Link
		diagnosis_date: DF.Date | None
		diagnosis_notes: DF.TextEditor | None
		estimated_cost: DF.Currency
		final_amount: DF.Currency
		imei_or_serial: DF.Data | None
		labour_charge: DF.Currency
		parts_total: DF.Currency
		parts_used: DF.Table[PartUsageEntry]
		payment_status: DF.Literal["Unpaid", "Paid"]
		priority: DF.Literal["Normal", "High", "Urgent"]
		problem_description: DF.TextEditor
		remarks: DF.SmallText | None
		status: DF.Literal[
			"Draft",
			"Pending Diagnosis",
			"Awaiting Customer Approval",
			"In Repair",
			"Ready for Delivery",
			"Delivered",
			"Cancelled",
		]
	# end: auto-generated types


@frappe.whitelist()
def share_job_card(job_card_name, user_email):
	frappe.share.add("Job Card", job_card_name, user_email, read=1)


def get_permission_query_conditions(user=None):
	if not user:
		user = frappe.session.user
	if user == "Administrator":
		return None

	if "QF Technician" in frappe.get_roles(user):
		technician = frappe.get_value("Technician", {"user": user}, "name")
		if technician:
			return f"`tabJob Card`.`assigned_technician` = {frappe.db.escape(technician)}"
	return None
