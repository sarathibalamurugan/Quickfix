// Copyright (c) 2026, Parthsarathi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	refresh(frm) {
		frappe.db.get_single_value("Quickfix Settings", "default_labour_charge").then((value) => {
			if (value) {
				frm.set_value("labour_charge", value);
			}
		});
	},
});
