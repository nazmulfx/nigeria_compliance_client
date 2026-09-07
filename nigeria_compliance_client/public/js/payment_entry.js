frappe.ui.form.on("Payment Entry", {
	refresh(frm) {
		frm._nrs_confirmed = false;
	},
	before_submit(frm) {
		if (frm._nrs_confirmed) {
			return;
		}

		let references = frm.doc.references || [];
		let pending_invoices = [];

		for (let row of references) {
			if (row.reference_doctype === "Sales Invoice" && row.reference_name) {
				frappe.call({
					method: "frappe.client.get_value",
					args: {
						doctype: "Sales Invoice",
						fieldname: ["custom_transmission_status", "custom_transmission_mode"],
						filters: { name: row.reference_name }
					},
					async: false,
					callback: (r) => {
						if (
							r.message &&
							r.message.custom_transmission_status === "Pending" &&
							r.message.custom_transmission_mode !== "Do Not Transmit"
						) {
							pending_invoices.push(row.reference_name);
						}
					}
				});
			}
		}

		if (pending_invoices.length > 0) {
			frappe.validated = false;
			frappe.confirm(
				__(
					"The following Sales Invoice(s) must be transmitted to NRS before submitting this Payment Entry: <b>{0}</b>.<br><br>Do you want to proceed with transmitting to NRS and submitting?",
					[pending_invoices.join(", ")]
				),
				() => {
					frm._nrs_confirmed = true;
					frm.savesubmit();
				},
				() => {
					frm._nrs_confirmed = false;
				}
			);
		}
	}
});
