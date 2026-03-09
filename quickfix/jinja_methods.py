import frappe


def get_shop_name():
	shop_name = frappe.db.get_value("QuickFix Settings", "QuickFix Settings", "shop_name")
	if not shop_name:
		return
	return shop_name


def format_job_id(job_card):
	if not job_card:
		return ""
	return f"JOB#{job_card}"
