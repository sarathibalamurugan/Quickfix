# Copyright (c) 2026, Parthsarathi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns()
	data = get_data()
	report_summary = get_report_summary(data)

	return columns, data, None, None, report_summary


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""

	return [
		{
			"label": _("Part Name"),
			"fieldname": "part_name",
			"fieldtype": "Data",
		},
		{
			"label": _("Part Code"),
			"fieldname": "part_code",
			"fieldtype": "Int",
		},
		{
			"label": _("Device Type"),
			"fieldname": "compatible_device_type",
			"fieldtype": "Data",
		},
		{
			"label": _("Stock Qty"),
			"fieldname": "stock_qty",
			"fieldtype": "Int",
		},
		{
			"label": _("Reorder Level"),
			"fieldname": "reorder_level",
			"fieldtype": "Int",
		},
		{
			"label": _("Unit Cost"),
			"fieldname": "unit_cost",
			"fieldtype": "Currency",
		},
		{
			"label": _("Selling Price"),
			"fieldname": "selling_price",
			"fieldtype": "Currency",
		},
		{
			"label": _("Margin %"),
			"fieldname": "margin_percent",
			"fieldtype": "Float",
		},
	]


def get_data():
	parts = frappe.get_all(
		"Spare Part",
		fields=[
			"part_name",
			"part_code",
			"compatible_device_type",
			"stock_qty",
			"reorder_level",
			"selling_price",
			"unit_cost",
		],
	)

	data = []
	total_stock = 0
	total_inventory_value = 0

	for p in parts:
		stock = flt(p.stock_qty)
		cost = flt(p.unit_cost)
		price = flt(p.selling_price)

		margin = 0
		if cost:
			margin = ((price - cost) / cost) * 100

		total_value = stock * cost

		total_stock += stock
		total_inventory_value += total_value

		data.append({**p, "margin_percent": margin, "total_value": total_value})

	# 🔹 Add Total Row
	data.append({"part_name": "TOTAL", "stock_qty": total_stock, "unit_cost": total_inventory_value})

	return data


def get_report_summary(data):
	total_parts = len(data) - 1
	below_reorder = sum(1 for d in data if d.get("stock_qty", 0) <= d.get("reorder_level", 0))

	total_inventory_value = sum(d.get("total_value", 0) for d in data)

	return [
		{
			"label": "Total Parts",
			"value": total_parts,
			"indicator": "Blue",
		},
		{
			"label": "Below Reorder",
			"value": below_reorder,
			"indicator": "Red" if below_reorder else "Green",
		},
		{
			"label": "Total Inventory Value",
			"value": total_inventory_value,
			"indicator": "Green",
		},
	]
