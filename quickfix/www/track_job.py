import frappe


def get_context(context):
	context.title = "Track Jobs"

	job_id = frappe.form_dict.get("job_id")

	if job_id:
		try:
			doc = frappe.get_doc("Job Card", job_id)
			context.data = doc
		except frappe.DoesNotExistError:
			context.error = "Invalid Job Card ID"
	else:
		context.data = None
