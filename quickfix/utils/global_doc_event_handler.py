import frappe


def global_doc_event_handler(doc, method):
	if doc.doctype in ["Audit Log", "Version", "Comment"]:
		return
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": doc.doctype,
			"document_name": doc.name,
			"action": method,
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}
	).insert(ignore_permissions=True)


def log_login():
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"action": "Login",
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}
	).insert(ignore_permissions=True)


def log_logout():
	frappe.get_doc(
		{
			"doctype": "Audit Log",
			"doctype_name": "User",
			"action": "Logout",
			"user": frappe.session.user,
			"timestamp": frappe.utils.now(),
		}
	).insert(ignore_permissions=True)
