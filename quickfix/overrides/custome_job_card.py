import frappe
from frappe.tests.utils import FrappeTestCase

from quickfix.service_center.doctype.job_card.job_card import JobCard


class CustomJobCard(JobCard):
	def validate(self):
		super().validate()  # ALWAYS call super first
		self._check_urgent_unassigned()
		# MRO is an order in which Python looks for a method in a hierarchy of classes. and calling super() is non-negotiable , because it ensures all validations from the parent class. if the validiations are skipped , leads to data integrity issues.
		# override_doctype_class is used when we need to change the core logics without touching it. and doc_events is used when we need to trigger some custom logics on some events.

	def _check_urgent_unassigned(self):
		if self.priority == "Urgent" and not self.assigned_technician:
			settings = frappe.get_single("QuickFix Settings")
			frappe.enqueue(
				"quickfix.utils.send_urgent_alert", job_card=self.name, manager=settings.manager_email
			)
