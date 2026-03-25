# Copyright (c) 2026, Parthsarathi and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestSparePart(IntegrationTestCase):
	"""
	Integration tests for SparePart.
	Use this class for testing interactions between multiple components.
	"""

	def create_spare_part(self):
		doc = frappe.get_doc(
			{
				"doctype": "Spare Part",
				"part_name": "Test Part",
				"part_code": "test0001",
				"unit_cost": 100,
				"selling_price": 150,
			}
		).insert(ignore_permissions=True)
		return doc.name
