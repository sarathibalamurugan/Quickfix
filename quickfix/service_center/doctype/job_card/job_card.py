# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt
import time
import uuid

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils.data import today


class JobCard(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		from quickfix.service_center.doctype.part_usage_entry.part_usage_entry import PartUsageEntry

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
		print_summary: DF.SmallText | None
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

	# end: auto-generated types
	def validate(self):
		self.validate_customer_phone()
		self.validate_technician()
		self.validate_price()

	def before_submit(self):
		msg = ""
		if self.status != "Ready for Delivery":
			frappe.throw(_("Job Card can only be submitted when status is 'Ready for Delivery'."))
		for part in self.parts_used:
			part_qty = frappe.get_value("Spare Part", part.part, "stock_qty")
			if part.quantity > part_qty:
				msg += f"Not enough stock for Spare Part {part.part}. Available: {part_qty}. \n "

		if msg:
			frappe.throw(_(msg))

	def on_submit(self):
		for part in self.parts_used:
			frappe.db.set_value(
				"Spare Part",
				part.part,
				"stock_qty",
				frappe.get_value("Spare Part", part.part, "stock_qty") - part.quantity,
			)
			# frappe.db.set_value("Spare Part", part.part, "stock_qty", part_qty - part.quantity) is not triggered by the user. Its a System triggered action thats why. But I still didn't understand why we need to use Ignore permissions here. Because the frappe.db automatically update in DB by bypassing permissions. And I cant use Ignore Permissions on set_value in this version of frappe.

		frappe.get_doc(
			{
				"doctype": "Service Invoice",
				"job_card": self.name,
				"labour_charge": self.labour_charge,
				"parts_total": self.parts_total,
				"total_amount": self.final_amount,
			}
		).insert(ignore_permissions=True)

		frappe.publish_realtime(
			"job_ready",
			{"job_card": self.name, "status": self.status, "msg": "Job Card is ready for delivery"},
			user=self.owner,
		)

		frappe.enqueue(
			"quickfix.service_center.doctype.job_card.job_card.send_job_ready_email",
			queue="short",
			job_card=self.name,
		)

	def on_cancel(self):
		for part in self.parts_used:
			frappe.db.set_value(
				"Spare Part",
				part.part,
				"stock_qty",
				frappe.get_value("Spare Part", part.part, "stock_qty") + part.quantity,
			)
		doc = frappe.get_doc("Service Invoice", ({"job_card": self.name}))
		if doc.docstatus == 1:
			doc.cancel()
		elif doc.docstatus == 0:
			doc.delete()
		frappe.db.set_value("Job Card", self.name, "status", "Cancelled")

	def on_trash(self):
		if self.status != "Draft" and self.status != "Cancelled":
			frappe.throw(_("Only Job Cards in Draft or Cancelled status can be deleted."))

	def on_update(self):
		pass

	def validate_customer_phone(self):
		if self.customer_phone and self.customer_phone.isdigit() and len(self.customer_phone) == 10:
			return
		else:
			frappe.throw(_("Invalid Customer Phone. It should be a 10-digit number."))

	def validate_technician(self):
		if (
			self.status in ["In Repair", "Ready for Delivery", "Delivered", "Cancelled"]
			and not self.assigned_technician
		):
			frappe.throw(_("Technician assignment is required for this status."))

	def validate_price(self):
		self.parts_total = 0
		self.final_amount = 0
		for part in self.parts_used:
			part.total_price = part.quantity * part.unit_price
			self.parts_total += part.total_price
		self.final_amount = self.parts_total + self.labour_charge

	def before_print(self, settings=None):
		self.print_summary = f"{self.customer_name} - {self.device_type} {self.device_brand}"


@frappe.whitelist()
def share_job_card(job_card_name, user_email):
	frappe.share.add("Job Card", job_card_name, user_email, read=1)


@frappe.whitelist()
def safe_and_unsafe():
	unsafe = frappe.get_all("Job Card", filters={"docstatus": 1}, fields=["name", "customer_name"])
	print("Unsafe Job Cards:", unsafe)
	safe = frappe.get_list("Job Card", filters={"docstatus": 1}, fields=["name", "customer_name"])
	print("Safe Job Cards:", safe)


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


def send_job_ready_email(job_card):
	job_card = frappe.get_doc("Job Card", job_card)
	frappe.sendmail(
		recipients=job_card.customer_email,
		subject=f"Your device is ready for delivery - Job Card {job_card.name}",
		message=f"Dear {job_card.customer_name},<br><br>Your device with Job Card {job_card.name} is ready for delivery.<br><br>Thank you<br><br>Best regards,<br>QuickFix Team",
		now=True,
	)


@frappe.whitelist()
def transfer_technician(job_card_name, technician_name):
	frappe.db.set_value("Job Card", job_card_name, "assigned_technician", technician_name)
	technician = frappe.db.get_value("Job Card", job_card_name, "assigned_technician")
	return technician


@frappe.whitelist()
def mark_as_delivered(job_card_name):
	frappe.db.set_value("Job Card", job_card_name, "status", "Delivered")
	return


@frappe.whitelist()
def mark_as_ready_for_delivery(job_card_name):
	frappe.db.set_value("Job Card", job_card_name, "status", "Ready for Delivery")
	frappe.db.set_value("Job Card", job_card_name, "docstatus", 1)
	return


def check_low_stock():
	# Idempotency guard: check if already run today
	last_run = frappe.db.get_value("Audit Log", {"action": "low_stock_check", "date": today()}, "name")
	if last_run:
		return  # already ran today, skip
	else:
		frappe.get_doc({"doctype": "Audit Log", "action": "low_stock_check", "user": "System"}).insert(
			ignore_permissions=True
		)


def monthly_revenue_report():
	frappe.enqueue(
		"quickfix.service_center.doctype.job_card.job_card.generate_monthly_revenue_report",
		queue="long",
		timeout=600,
		year=frappe.utils.data.nowdate().split("-")[0],
	)


def generate_monthly_revenue_report(year):
	months = range(1, 13)
	for i, month in enumerate(months, 1):
		# process month
		frappe.publish_progress(
			percent=round(i / 12 * 100),
			title="Generating Revenue Report",
			description=f"Processing month {month}...",
		)


def cancel_old_job_cards():
	start = time.time()
	frappe.db.sql("""
        UPDATE `tabJob Card`
        SET docstatus = '2'
        WHERE status = 'Draft'
               order by creation asc
               limit 1000
    """)
	frappe.db.commit()
	end = time.time()
	print(f"Cancelled 1000 old Job Cards in {end - start:.2f} seconds")


def create_bulk_audit_log():
	start = time.time()
	fields = [
		"name",
		"creation",
		"modified",
		"modified_by",
		"owner",
		"docstatus",
		"idx",
		"doctype_name",
		"document_name",
		"action",
		"user",
		"timestamp",
	]

	values = []
	current_user = frappe.session.user
	current_time = now()

	for i in range(500):
		values.append(
			(
				str(uuid.uuid4()),
				current_time,
				current_time,
				current_user,
				current_user,
				0,
				0,
				"Job Card",
				f"JC-TEST-{i}",
				f"Bulk Action {i}",
				current_user,
				current_time,
			)
		)

	frappe.db.bulk_insert("Audit Log", fields, values)
	frappe.db.commit()
	end = time.time()
	print(f"Created 500 audit logs in {end - start:.2f} seconds")
	return


def create_bulk_job_cards():
	start = time.time()
	fields = [
		"name",
		"creation",
		"modified",
		"modified_by",
		"owner",
		"docstatus",
		"idx",
		"customer_name",
		"customer_phone",
		"device_type",
		"problem_description",
		"assigned_technician",
		"parts_total",
		"labour_charge",
		"final_amount",
		"status",
	]

	values = []
	current_user = frappe.session.user
	current_time = now()

	for i in range(1000):
		values.append(
			(
				str(uuid.uuid4()),
				current_time,
				current_time,
				current_user,
				current_user,
				0,
				0,
				"test customer",
				"1234567890",
				"Laptop",
				f"Test problem description {i}",
				"TECH-0099",
				0,
				500,
				500,
				"Draft",
			)
		)

	frappe.db.bulk_insert("Job Card", fields, values)
	frappe.db.commit()
	end = time.time()
	print(f"Created 500 job cards in {end - start:.2f} seconds")
	return
