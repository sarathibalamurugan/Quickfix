import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

from quickfix.monkey_patches import apply_all


def after_install():
	apply_all()
	# Default Device Types already created by fixtures
	frappe.get_doc(
		{
			"doctype": "QuickFix Settings",
			"shop_name": "Quickfix Service Center",
			"manager_email": "manager@quickfix.com",
		}
	).insert(ignore_permissions=True)

	make_property_setter("Job Card", "remarks", "bold", 1, "Check")

	frappe.msgprint("Quickfix installed successfully and default settings created.")


def before_uninstall():
	jobcards = frappe.get_all("Job Card", fields=["name"], filters={"docstatus": 1})
	if jobcards:
		frappe.throw("Cannot uninstall Quickfix. Submitted Job Cards exist.")
