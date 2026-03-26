# Copyright (c) 2026, Parthsarathi and Contributors
# See license.txt

import time
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from quickfix.service_center.doctype.spare_part.test_spare_part import IntegrationTestSparePart

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestJobCard(IntegrationTestSparePart):
	"""
	Integration tests for JobCard.
	Use this class for testing interactions between multiple components.
	"""

	def create_job_card(self, spare_part=None, status=None, no_tech=None, tech=None):
		if not no_tech:
			tech = self.create_technician("9999999999").insert()
		doc = frappe.get_doc(
			{
				"doctype": "Job Card",
				"customer_name": "Test Customer",
				"customer_phone": "9999999999",
				"device_type": "Laptop",
				"problem_description": "test ",
			}
		)
		if tech:
			doc.assigned_technician = tech.name
		doc.insert()
		# doc.reload()

		if spare_part:
			doc.append("parts_used", {"part": spare_part, "quantity": 1})
			doc.save()
		return doc.name

	def test_job_card(self):
		doc_name = self.create_job_card()
		doc = frappe.db.get_value("Job Card", doc_name, "docstatus")

		self.assertEqual(doc, 0)

	def create_technician(self, phone=None):
		return frappe.get_doc({"doctype": "Technician", "technician_name": "Test Tech", "phone": phone})

	def test_phone_valid(self):
		doc = self.create_technician("9876543210")
		if not (doc.phone).isdigit():
			with self.assertRaises(frappe.ValidationError):
				doc.insert()
		if len(doc.phone) < 10:
			with self.assertRaises(frappe.ValidationError):
				doc.insert()
		if len(doc.phone) > 10:
			with self.assertRaises(frappe.ValidationError):
				doc.insert()

		doc.insert()

		self.assertTrue(doc.name)

	def test_spare_part_selling_price(self):
		spare = self.create_spare_part()
		doc = self.create_job_card(spare_part=spare)
		job = frappe.get_doc("Job Card", doc)
		for row in job.parts_used:
			spare_part = frappe.get_doc("Spare Part", row.part)

			self.assertTrue(spare_part.unit_cost < row.unit_price)

	def test_final_amount(self):
		spare = self.create_spare_part()
		doc = self.create_job_card(spare_part=spare)
		parts_total = frappe.db.get_value("Job Card", doc, "parts_total")
		job = frappe.get_doc("Job Card", doc)
		parts_total_manual = 0
		for row in job.parts_used:
			parts_total_manual += row.total_price

		self.assertEqual(parts_total, parts_total_manual)

	def test_status_transition_guard(self):
		job_name = self.create_job_card(no_tech=True)
		doc = frappe.get_doc("Job Card", job_name)

		doc.status = "In Repair"

		with self.assertRaises(frappe.ValidationError):
			doc.save()

		tech = self.create_technician().insert()

		doc = frappe.get_doc("Job Card", job_name)
		doc.assigned_technician = tech.name
		doc.status = "In Repair"

		doc.save()
		self.assertEqual(doc.status, "In Repair")

	def test_estimated_cost(self):
		doc = self.create_job_card()
		job = frappe.get_doc("Job Card", doc)
		job.status = "In Repair"
		job.diagnosis_notes = "testing"
		job.estimated_cost = 200
		job.save()

		self.assertNotEqual(job.estimated_cost, 0)

	def test_child_row_computation(self):
		spare = self.create_spare_part()
		doc = self.create_job_card(spare_part=spare)
		job = frappe.get_doc("Job Card", doc)
		for part in job.parts_used:
			manual_total = part.quantity * part.unit_price
			self.assertEqual(manual_total, part.total_price)

	def test_status_before_submit(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "In Repair"
		doc.save()
		with self.assertRaises(frappe.ValidationError):
			doc.submit()
		self.assertEqual(doc.docstatus, 1)

	def test_stock_check_on_submit(self):
		spare = self.create_spare_part()
		job = self.create_job_card(spare_part=spare)
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		with self.assertRaises(frappe.ValidationError) as context:
			doc.save()
			doc.submit()
		for part in doc.parts_used:
			spare = frappe.get_doc("Spare Part", part.part)
			spare.stock_qty = part.quantity
			spare.save()
		self.assertIn(spare.part_name.lower(), str(context.exception).lower())
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		doc.submit()
		self.assertEqual(doc.docstatus, 1)

	def test_deduct_stock_on_submit(self):
		spare = self.create_spare_part()
		job = self.create_job_card(spare_part=spare)
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		old_spare_qty = {}
		for part in doc.parts_used:
			spare = frappe.get_doc("Spare Part", part.part)
			spare.stock_qty = part.quantity
			spare.save()
			old_spare_qty[part.part] = (
				frappe.db.get_value("Spare Part", part.part, "stock_qty") - part.quantity
			)
		doc.submit()
		for part in doc.parts_used:
			self.assertEqual(
				old_spare_qty[part.part], frappe.db.get_value("Spare Part", part.part, "stock_qty")
			)

	def test_service_invoice_creation(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		doc.submit()
		invoice = frappe.db.exists("Service Invoice", {"job_card": doc.name})
		self.assertTrue(invoice)
		invoice_job_name = frappe.db.get_value("Service Invoice", invoice, "job_card")
		self.assertEqual(invoice_job_name, doc.name)

	def test_stock_on_cancel(self):
		spare = self.create_spare_part()
		job = self.create_job_card(spare_part=spare)
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()

		spare_qty = {}
		for part in doc.parts_used:
			spare = frappe.get_doc("Spare Part", part.part)
			spare.stock_qty = part.quantity
			spare.save()
			spare_qty[part.part] = frappe.db.get_value("Spare Part", part.part, "stock_qty")
		doc.submit()
		doc.cancel()
		for part in doc.parts_used:
			spare_cur = frappe.db.get_value("Spare Part", part.part, "stock_qty")
			self.assertEqual(spare_qty[part.part], spare_cur)

	def test_cancel_linked_invoice(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		doc.submit()
		invoice = frappe.db.exists("Service Invoice", {"job_card": doc.name})
		doc.cancel()
		invoice_docstatus = frappe.db.get_value("Service Invoice", invoice, "docstatus")
		self.assertEqual(invoice_docstatus, 2)

	def test_on_trash_guard(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		doc.submit()
		with self.assertRaises(frappe.ValidationError):
			doc.delete()
		doc.cancel()
		invoice = frappe.db.exists("Service Invoice", {"job_card": doc.name})
		frappe.delete_doc("Service Invoice", invoice)
		doc.delete()
		exist = frappe.db.exists("Job Card", doc.name)
		self.assertFalse(exist)

	def test_sendmail_on_submit(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.customer_email = "test@gmail.com"
		doc.save()
		with patch("frappe.sendmail") as mock_mail:
			doc.submit()
			self.assertEqual(mock_mail.call_count, 1)

		_args, kwargs = mock_mail.call_args
		self.assertIn("recipients", kwargs)
		self.assertIn(doc.customer_email, kwargs["recipients"])

	def test_enqueue_on_submit(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.customer_email = "testenqueue@gmail.com"
		doc.save()
		with patch("frappe.enqueue") as mock_queue:
			doc.submit()
		_args, kwargs = mock_queue.call_args
		self.assertTrue(mock_queue.call_count)
		self.assertEqual(kwargs["job_card_name"], doc.name)

	def test_publish_realtime(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.customer_email = "testpublishrealtime@gmail.com"
		doc.save()
		with patch("frappe.publish_realtime") as mock_realtime:
			doc.submit()
		job_call = next(
			(
				(args, kwargs)
				for args, kwargs in mock_realtime.call_args_list
				if args and args[0] == "job_ready"
			),
			None,
		)

		self.assertIsNotNone(job_call, "job_ready event not triggered")

		args, _kwargs = job_call
		event = args[0]
		message = args[1]
		self.assertEqual(event, "job_ready")
		self.assertEqual(message["job_card"], doc.name)

	def test_duplicate_invoice(self):
		job = self.create_job_card()
		doc = frappe.get_doc("Job Card", job)
		doc.status = "Ready for Delivery"
		doc.save()
		doc.submit()
		invoice1 = frappe.db.exists("Service Invoice", {"job_card": doc.name})
		doc.on_submit()
		invoice2 = frappe.db.exists("Service Invoice", {"job_card": doc.name})
		self.assertEqual(invoice1, invoice2)
