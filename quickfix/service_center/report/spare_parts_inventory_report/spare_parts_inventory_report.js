// Copyright (c) 2026, Parthsarathi and contributors
// For license information, please see license.txt

frappe.query_reports["Spare Parts Inventory Report"] = {
	filters: [
		// {
		// 	"fieldname": "my_filter",
		// 	"label": __("My Filter"),
		// 	"fieldtype": "Data",
		// 	"reqd": 1,
		// },
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data && data.stock_qty <= data.reorder_level) {
			value = `<span style="background-color:#ffcccc">${value}</span>`;
		}

		return value;
	},
};
