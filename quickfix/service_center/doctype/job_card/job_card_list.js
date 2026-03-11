frappe.listview_settings["Job Card"] = {
	add_fields: ["status", "final_amount", "priority"],
	has_indicator_for_draft: true,
	get_indicator: function (doc) {
		const status_map = {
			Pending: ["Pending", "orange"],
			"Pending Diagnosis": ["Pending Diagnosis", "orange"],
			"Awaiting Customer Approval": ["Awaiting Approval", "orange"],
			"In Repair": ["In Repair", "yellow"],
			"Ready for Delivery": ["Ready", "green"],
			Delivered: ["Delivered", "green"],
			Rejected: ["Rejected", "red"],
		};

		return status_map[doc.status] || [doc.status, "gray"];
	},
	formatters: {
		final_amount(value) {
			if (!value) return "";

			return `${frappe.format(value, { fieldtype: "Currency" })}`;
		},

		priority(value) {
			if (!value) return "";

			const color_map = {
				Normal: "green",
				High: "orange",
				Urgent: "red",
			};

			return `<span style="color:${color_map[value] || "black"};">
                        ${value}
                    </span>`;
		},
	},

	button: {
		show(doc) {
			return doc.status === "In Repair";
		},

		get_label() {
			return "Mark Ready";
		},

		get_description(doc) {
			return `Mark ${doc.name} as Ready for Delivery`;
		},

		action(doc) {
			frappe
				.call({
					method: "quickfix.service_center.doctype.job_card.job_card.mark_as_ready_for_delivery",
					args: {
						job_card_name: doc.name,
					},
				})
				.then(() => {
					frappe.show_alert({
						message: "Marked as Ready",
						indicator: "green",
					});
					frappe.listview.refresh();
				});
		},
	},
};
