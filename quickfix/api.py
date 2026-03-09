import frappe


def only_if_manager():
	frappe.only_for("QF Manager")


@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
	# First log the request to Audit Log, then call original behaviour
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doctype,
			"action": "count_queried",
			"user": frappe.session.user,
		}
	).insert(ignore_permissions=True)
	from frappe.client import get_count

	return get_count(doctype, filters, debug, cache)
