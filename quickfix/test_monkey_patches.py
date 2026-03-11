import frappe
from frappe.tests.utils import FrappeTestCase

from quickfix.monkey_patches import apply_all


class TestGetUrlPatch(FrappeTestCase):
	def setUp(self):
		apply_all()

	def test_prefix_applied(self):
		frappe.conf.custom_url_prefix = "https://cdn.example.com"

		from frappe.utils import get_url

		url = get_url("/test-path")
		self.assertTrue(url.startswith("https://cdn.example.com"))

	def test_original_behavior_without_prefix(self):
		frappe.conf.custom_url_prefix = ""

		from frappe.utils import get_url

		url = get_url("/test-path")
		self.assertFalse(url.startswith("https://cdn.example.com"))
