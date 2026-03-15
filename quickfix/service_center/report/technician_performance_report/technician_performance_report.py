# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt


import frappe
from frappe import _


def execute(filters):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_summary(data)

	return columns, data, None, chart, report_summary


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	cols = [
		{
			"label": _("Technician"),
			"fieldname": "technician",
			"fieldtype": "Data",
		},
		{
			"label": _("Completed"),
			"fieldname": "completed",
			"fieldtype": "Int",
		},
		{
			"label": _("Avg Turnaround Days"),
			"fieldname": "avg_turnaround_days",
			"fieldtype": "Int",
		},
		{
			"label": _("Revenue"),
			"fieldname": "revenue",
			"fieldtype": "Currency",
		},
		{
			"label": _("Completion Rate"),
			"fieldname": "completion_rate",
			"fieldtype": "Float",
		},
		{
			"label": _("Total Jobs"),
			"fieldname": "total_jobs",
			"fieldtype": "Int",
		},
	]

	for dt in frappe.get_all("Device Type", fields=["name"]):
		cols.append(
			{
				"label": dt.name,
				"fieldname": dt.name.lower().replace(" ", "_"),
				"fieldtype": "Int",
				"width": 100,
			}
		)

	return cols


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	filters = filters or {}
	job_filters = {"status": "Delivered"}
	if filters.get("from_date") and filters.get("to_date"):
		job_filters["creation"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	if filters.get("technician"):
		job_filters["assigned_technician"] = filters.get("technician")

	jobs = frappe.get_list(
		"Job Card",
		fields=[
			"name",
			"assigned_technician",
			"status",
			"device_type",
			"creation",
			"modified",
			"final_amount",
		],
		filters=job_filters,
	)
	data = {}
	device_types = [dt.name for dt in frappe.get_all("Device Type", fields=["name"])]

	for job in jobs:
		tech = job.assigned_technician
		if not tech:
			continue
		if tech not in data:
			data[tech] = {
				"technician": tech,
				"completed": 0,
				"avg_turnaround_days": 0,
				"revenue": 0,
				"completion_rate": 0,
				**{dt.lower().replace(" ", "_"): 0 for dt in device_types},
				"total_jobs": 0,
			}
		row = data[tech]
		row["completed"] += 1
		row["revenue"] += job.final_amount
		row["avg_turnaround_days"] += (job.modified - job.creation).days
		row[job.device_type.lower().replace(" ", "_")] += 1
	for row in data.values():
		row["avg_turnaround_days"] = row["avg_turnaround_days"] / row["completed"] if row["completed"] else 0
		row["completion_rate"] = (row["completed"] / len(jobs)) * 100 if jobs else 0

	return list(data.values())


def get_chart(data):
	if not data:
		return None

	return {
		"data": {
			"labels": [d.get("technician") for d in data],
			"datasets": [
				{"name": "Total Jobs", "values": [d.get("total_jobs", 0) for d in data]},
				{"name": "Completed", "values": [d.get("completed", 0) for d in data]},
			],
		},
		"type": "bar",
	}


def get_summary(data):
	total_jobs = sum(d.get("total_jobs", 0) for d in data)
	total_revenue = sum(d.get("revenue", 0) for d in data)

	best = max(data, key=lambda x: x.get("completion_rate", 0), default=None)

	return [
		{"value": total_jobs, "label": "Total Jobs", "indicator": "blue"},
		{"value": total_revenue, "label": "Total Revenue", "indicator": "green"},
		{"value": best.get("technician") if best else "-", "label": "Best Technician", "indicator": "orange"},
	]
