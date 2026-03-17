import base64
from io import BytesIO

import frappe
import qrcode


def get_shop_name():
	shop_name = frappe.db.get_value("QuickFix Settings", "QuickFix Settings", "shop_name")
	if not shop_name:
		return
	return shop_name


def format_job_id(job_card):
	if not job_card:
		return ""
	return f"JOB#{job_card}"


def get_jobcard_qr(docname):
	url = frappe.utils.get_url(f"/desk/job-card/{docname}")

	qr = qrcode.make(url)

	buffer = BytesIO()
	qr.save(buffer, format="PNG")

	img_str = base64.b64encode(buffer.getvalue()).decode()

	return f"data:image/png;base64,{img_str}"
