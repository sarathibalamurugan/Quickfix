import frappe


def only_if_manager():
	frappe.only_for("QF Manager")
