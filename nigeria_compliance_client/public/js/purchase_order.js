frappe.ui.form.on('Purchase Order', {
	refresh(frm) {
		// secondary button add
		frm.add_custom_button("Validate IRN", () => {
			frappe.call({
				method: 'nigeria_compliance_client.nigeria_compliance_client.hooks.utils.validate_irn',
				args: {
					invoicereference: frm.doc.name,
					irn : frm.doc.custom_irn,
					company: frm.doc.company
				},
				freeze: true,
				callback: (r) => {
					if (r.message && r.message.status_code === 200 && r.message.ok === true) {
						frappe.msgprint({
							title: __("Success"),
							indicator: "green",
							message: __("IRN validated successfully.")
						});
					} else {
						frappe.msgprint({
							title: __("Failed"),
							indicator: "red",
							message: __("IRN validation failed.")
						});
					}
				}
			})
		}, "NRS e-Invoice")
	}
})