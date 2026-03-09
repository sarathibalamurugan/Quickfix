import frappe
from frappe.tests.utils import FrappeTestCase


class TestCustomJobCard(FrappeTestCase):
	def test_technician_unassigned(self):
		job_card = frappe.get_doc(
			{
				"doctype": "Job Card",
				"customer_name": "Test Customer",
				"status": "Ready for Delivery",
			}
		)
		with self.assertRaises(frappe.ValidationError):
			job_card.insert()
