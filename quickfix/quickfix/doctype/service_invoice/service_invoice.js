// Copyright (c) 2026, Parthsarathi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Service Invoice", {
	refresh(frm) {
		frm.set_value("invoice_date", frappe.datetime.get_today());
	},
});
