// Copyright (c) 2026, Parthsarathi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Job Card", {
	onload(frm) {
		frappe.realtime.on("job_ready", (data) => {
			if (data.name === frm.doc.name) {
				frappe.show_alert({
					message: __("This Job is ready now!"),
					indicator: "green",
				});
			}
		});
	},
	refresh(frm) {
		frm.add_custom_button("Transfer Technician", () => {
			frappe.prompt(
				[
					{
						label: "New Technician",
						fieldname: "new_technician",
						fieldtype: "Link",
						options: "Technician",
						reqd: 1,
					},
				],
				(values) => {
					frappe.confirm(
						__("Transfer this job to {0}?", [values.new_technician]),
						() => {
							frappe.call({
								method: "quickfix.service_center.doctype.job_card.job_card.transfer_technician",
								args: {
									job_card_name: frm.doc.name,
									technician_name: values.new_technician,
								},
								callback: (r) => {
									if (r.message) {
										frm.trigger("assigned_technician");
										frm.reload_doc();
									} else {
										frappe.msgprint("noo");
									}
								},
							});
						}
					);
				}
			);
		});
		frm.add_custom_button("Reject Job", () => {
			let d = new frappe.ui.Dialog({
				title: "Reject Job",
				fields: [
					{
						label: "Rejection Reason",
						fieldname: "rejection_reason",
						fieldtype: "Small Text",
						reqd: 1,
					},
				],
				primary_action_label: "Submit",
				primary_action(values) {
					console.log(values.rejection_reason);
					d.hide();
				},
			});

			d.show();
		});
		const status_color_map = {
			Pending: "orange",
			"In Progress": "blue",
			"Ready for Delivery": "green",
			Delivered: "gray",
		};

		if (frm.doc.status) {
			frm.dashboard.clear_headline();
			frm.dashboard.add_indicator(
				frm.doc.status,
				status_color_map[frm.doc.status] || "gray"
			);
		}

		frappe.db.get_single_value("Quickfix Settings", "default_labour_charge").then((value) => {
			if (value) {
				frm.set_value("labour_charge", value);
			}
		});

		if (frm.doc.status == "Ready for Delivery" && frm.doc.docstatus == 1) {
			frm.add_custom_button("Mark as Delivered", () => {
				frappe.call({
					method: "quickfix.service_center.doctype.job_card.job_card.mark_as_delivered",
					args: {
						job_card_name: frm.doc.name,
					},
					callback: (r) => {
						frm.reload_doc();
						frappe.show_alert({
							message: __("Job marked as Delivered!"),
							indicator: "green",
						});
					},
				});
			});
		}

		if (frappe.boot.quickfix_shop_name) {
			frm.page.set_title(`${frappe.boot.quickfix_shop_name}`);
		}
	},

	assigned_technician(frm) {
		if (!frm.doc.assigned_technician) return;

		frappe.db
			.get_value("Technician", frm.doc.assigned_technician, "specialization")
			.then((r) => {
				if (r.message.specialization !== frm.doc.device_type) {
					frappe.msgprint({
						title: __("Warning"),
						message: __("Technician specialization does not match Device Type"),
						indicator: "orange",
					});
				}
			});
	},

	setup(frm) {
		frm.set_query("assigned_technician", () => {
			return {
				filters: {
					status: "Active",
					specialization: frm.doc.device_type,
				},
			};
		});
	},
});

frappe.ui.form.on("Part Usage Entry", {
	quantity(frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		const total = (row.quantity || 0) * (row.unit_price || 0);

		frappe.model.set_value(cdt, cdn, "total_price", total);
	},
});
