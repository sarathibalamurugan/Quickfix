# Copyright (c) 2026, Parthsarathi and Contributors
# See license.txt

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

	def create_job_card(self, spare_part=None):
		tech = self.create_technician("9999999999").insert(ignore_permissions=True)
		doc = frappe.get_doc(
			{
				"doctype": "Job Card",
				"assigned_technician": tech.name,
				"customer_name": "Test Customer",
				"customer_phone": "9999999999",
				"device_type": "Laptop",
				"problem_description": "test ",
			}
		).insert(ignore_permissions=True)

		if spare_part:
			doc.append("parts_used", {"part": spare_part, "quantity": 1})
			doc.save(ignore_permissions=True)

		return doc.name

	def test_job_card(self):
		doc_name = self.create_job_card()
		doc = frappe.db.get_value("Job Card", doc_name, "docstatus")

		self.assertEqual(doc, 0)

	def create_technician(self, phone):
		return frappe.get_doc({"doctype": "Technician", "technician_name": "Test Tech", "phone": phone})

	def test_phone_too_short(self):
		doc = self.create_technician("12345")

		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_phone_too_long(self):
		doc = self.create_technician("1234567890123")

		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_phone_non_numeric(self):
		doc = self.create_technician("12345abcd9")

		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_phone_valid(self):
		doc = self.create_technician("9876543210")

		doc.insert(ignore_permissions=True)

		self.assertTrue(doc.name)

	def test_spare_part_selling_price(self):
		spare = self.create_spare_part()
		doc = self.create_job_card(spare_part=spare)
		job = frappe.get_doc("Job Card", doc)
		for row in job.parts_used:
			spare_part = frappe.get_doc("Spare Part", row.part)

			self.assertTrue(row.unit_price < spare_part.selling_price)
