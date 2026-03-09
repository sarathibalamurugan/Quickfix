import frappe


def after_install():
	# Default Device Types already created by fixtures
	frappe.get_doc(
		{
			"doctype": "QuickFix Settings",
			"shop_name": "Quickfix Service Center",
			"manager_email": "manager@quickfix.com",
		}
	).insert(ignore_permissions=True)
	frappe.msgprint("Quickfix installed successfully and default settings created.")


def before_uninstall():
	jobcards = frappe.get_all("Job Card", fields=["name"], filters={"docstatus": 1})
	if jobcards:
		frappe.throw("Cannot uninstall Quickfix. Submitted Job Cards exist.")
