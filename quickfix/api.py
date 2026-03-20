import hashlib
import hmac
import json
import time

import frappe
import requests
from frappe.utils import now_datetime, today


def only_if_manager():
	frappe.only_for("QF Manager")


@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
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


@frappe.whitelist()
def prepare_technician_performance(filters=None):
	filters = frappe.parse_json(filters) if filters else {}
	frappe.enqueue(
		"frappe.core.doctype.prepared_report.prepared_report.make_prepared_report",
		queue="long",
		report_name="Technician Performance Report",
		filters=filters,
	)
	return


@frappe.whitelist()
def get_job_summary():
	jc = frappe.form_dict.get("job_card_name")
	if not frappe.db.exists("Job Card", jc):
		frappe.response["http_status_code"] = 404
		return {"error": "Not found"}
	job = frappe.db.get_value(
		"Job Card", jc, ["name", "status", "assigned_technician", "creation", "delivery_date"], as_dict=True
	)
	job["today_python date"] = today()

	return job


RATE_LIMIT = 20  # max requests
WINDOW_SECONDS = 60  # per minute


@frappe.whitelist(allow_guest=True)
def get_job_by_phone():
	# Identify caller IP
	ip = frappe.local.request_ip or "unknown"

	# Cache key per IP per minute
	current_minute = now_datetime().strftime("%Y%m%d%H%M")
	cache_key = f"rate_limit:{ip}:{current_minute}"

	cache = frappe.cache()

	# Increment count
	current_count = cache.get(cache_key)

	if current_count:
		current_count = int(current_count)
	else:
		current_count = 0

	if current_count >= RATE_LIMIT:
		frappe.response["http_status_code"] = 429
		return {"error": "Too many requests"}

	cache.set(cache_key, current_count + 1, expires_in_sec=WINDOW_SECONDS)

	phone = frappe.form_dict.get("phone")

	if not phone:
		frappe.response["http_status_code"] = 400
		return {"error": "Phone required"}

	job = frappe.db.get_value(
		"Job Card", {"customer_phone": phone}, ["name", "status", "delivery_date"], as_dict=True
	)

	if not job:
		frappe.response["http_status_code"] = 404
		return {"error": "Not found"}

	return job


def send_webhook(job_card_name, sleep=None, retry_count=0):
	if sleep:
		time.sleep(60)
		frappe.msgprint("slept 60")
	else:
		frappe.msgprint("Not slept 60")
	settings = frappe.get_single("QuickFix Settings")

	if not settings.webhook_url:
		return

	doc = frappe.get_doc("Job Card", job_card_name)

	payload = {
		"event": "job_submitted",
		"job_card": doc.name,
		"customer": doc.customer_name,
		"amount": doc.final_amount,
	}

	raw = f"{doc.name}|job_submitted|{doc.modified}"
	webhook_id = hashlib.sha256(raw.encode()).hexdigest()

	if frappe.db.exists("Audit Log", {"name": webhook_id}):
		return

	try:
		response = requests.post(settings.webhook_url, json=payload, timeout=5)
		response.raise_for_status()

		frappe.get_doc(
			{
				"doctype": "Audit Log",
				"name": webhook_id,
				"doctype_name": "Job Card",
				"document_name": doc.name,
				"action": "Webhook Sent",
				"user": frappe.session.user,
				"timestamp": now_datetime(),
			}
		).insert(ignore_permissions=True)

	except Exception as e:
		frappe.log_error(f"Webhook failed: {e}", "Webhook Error")

		if retry_count < 3:
			frappe.enqueue(
				"quickfix.api.send_webhook",
				job_card_name=job_card_name,
				retry_count=retry_count + 1,
				sleep=60,
				queue="short",
			)
			frappe.get_doc(
				{
					"doctype": "Audit Log",
					"doctype_name": "Job Card",
					"document_name": doc.name,
					"action": f"Webhook Retry {retry_count + 1}",
					"user": frappe.session.user,
					"timestamp": now_datetime(),
				}
			).insert(ignore_permissions=True)


def enqueue_job_submitted_webhook(doc, method=None):
	frappe.enqueue("quickfix.api.send_webhook", job_card_name=doc.name, retry_count=0, queue="short")


@frappe.whitelist(allow_guest=True)
def payment_webhook():
	# 1. Read raw request body
	payload = frappe.request.data
	# 2. Validate HMAC signature
	secret = frappe.conf.get("payment_webhook_secret", "")
	signature = frappe.get_request_header("X-Signature")
	expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
	if not hmac.compare_digest(expected, signature or ""):
		frappe.throw("Invalid signature", frappe.AuthenticationError)
	# 3. Parse payload
	data = json.loads(payload)
	# 4. Deduplication check
	if frappe.db.exists("Audit Log", {"action": "payment_received", "document_name": data["ref"]}):
		return {"status": "duplicate", "message": "Already processed"}
	# 5. Update Job Card / Service Invoice payment status
	# 6. Log to Audit Log
	frappe.db.commit()
	return {"status": "ok"}
