frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (frm.doc.is_return == 1) {
			frm.set_value("custom_invoice_type", "380");
		} else {
			frm.set_value("custom_invoice_type", "381");
		}

		// secondary button add
		if (frm.doc.custom_irn) {
			frm.add_custom_button("Validate IRN", () => {
				frappe.call({
					method: 'nigeria_compliance_client.nigeria_compliance_client.hooks.utils.validate_irn',
					args: {
						invoicereference: frm.doc.name,
						irn: frm.doc.custom_irn,
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
		};
		// if (frm.doc.docstatus == 1 && frm.doc.custom_transmission_status == 'Pending') {
		// 	frm.add_custom_button("Transmit to NRS", ()=> {
		// 		frappe.call({
		// 			method: 'nigeria_compliance_client.nigeria_compliance_client.hooks.e_invoice.transmit_invoice',
		// 			args: {
		// 				doctype: frm.doc.doctype,
		// 				document_id: frm.doc.name,
		// 				type: "selling"
		// 			},
		// 			// free window to prevent multiple click by user
		// 			freeze: true,
		// 			callback: (r) => {
		// 				if (!r.exc) {
		// 					// Reload document ONLY after the server response is received
		// 					frm.reload_doc();
		// 				}
		// 			}
		// 		});
		// 	}, "NRS e-Invoice")
		// };
		// if (frm.doc.docstatus == 1 && frm.doc.custom_transmission_status == 'Pending') {
		// 	frm.add_custom_button("Regenerate Payload", ()=> {
		// 		frappe.call({
		// 			method: 'nigeria_compliance_client.nigeria_compliance_client.hooks.e_invoice.regenerate_payload',
		// 			args: {
		// 				doctype: frm.doc.doctype,
		// 				document_id: frm.doc.name,
		// 				type: "selling"
		// 			},
		// 			// free window to prevent multiple click by user
		// 			freeze: true,
		// 			callback: (r) => {
		// 				if (!r.exc) {
		// 					// Reload document ONLY after the server response is received
		// 					frm.reload_doc();
		// 				}
		// 			}
		// 		});
		// 	}, "NRS e-Invoice")
		// };

		// Invoice Confirmation
		// frm.add_custom_button("Confirm Invoice", () => {
		// 	frappe.call({
		// 		method: 'nigeria_compliance_client.nigeria_compliance_client.hooks.utils.confirm_invoice',
		// 		args: {
		// 			irn: frm.doc.custom_irn,
		// 			company: frm.doc.company
		// 		},
		// 		freeze: true,
		// 		callback: (r) => {

		// 			frm.set_value("custom_confirm_invoice_response", JSON.stringify(r.message));
		// 			if (r.message && r.message.status_code === 200 && r.message.ok === true) {
		// 				frappe.msgprint({
		// 					title: __("Success"),
		// 					indicator: "green",
		// 					message: __("Invoice Confirmed successfully.")
		// 				});
		// 			} else {
		// 				frappe.msgprint({
		// 					title: __("Failed"),
		// 					indicator: "red",
		// 					message: __("Invoice confirmation failed.")
		// 				});
		// 			}
		// 		}
		// 	})
		// })
	},
	custom_b2b_customer_tag(frm) {
		set_transmission_mode(frm);
		set_invoice_kind(frm);
	},
	custom_b2c_customer_tag(frm) {
		set_transmission_mode(frm);
		set_invoice_kind(frm);
	}

});


function set_transmission_mode(frm) {
	if (frm.doc.custom_b2b_customer_tag == 1) {
		frm.set_value("custom_transmission_mode", "Instant Transmission (B2B)");
	} else if (frm.doc.custom_b2c_customer_tag == 1) {
		frm.set_value("custom_transmission_mode", "Transmit Later (B2C - within 24 hours)");
	} else {
		frm.set_value("custom_transmission_mode", "Do Not Transmit");
	}
}


function set_invoice_kind(frm) {
	if (frm.doc.custom_b2b_customer_tag == 1) {
		frm.set_value("custom_invoice_kind", "B2B");
	} else if (frm.doc.custom_b2c_customer_tag == 1) {
		frm.set_value("custom_invoice_kind", "B2C");
	} else {
		frm.set_value("custom_invoice_kind", "");
	}
}


frappe.ui.form.on('Sales Invoice Item', {
	qty(frm, cdt, cdn) {
		calculate_vat(frm, cdt, cdn);
	},
	rate(frm, cdt, cdn) {
		calculate_vat(frm, cdt, cdn);
	},
	custom_total_tax_percent(frm, cdt, cdn) {
		calculate_vat(frm, cdt, cdn);
	}
})

function calculate_vat(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	let custom_vat = row.rate * row.custom_total_tax_percent / 100;
	let custom_vat_inclusive_rate = row.rate + custom_vat;
	let custom_vat_inclusive_amount = custom_vat_inclusive_rate * row.qty;

	frappe.model.set_value(cdt, cdn, "custom_vat", custom_vat);
	frappe.model.set_value(cdt, cdn, "custom_vat_inclusive_rate", custom_vat_inclusive_rate);
	frappe.model.set_value(cdt, cdn, "custom_vat_inclusive_amount", custom_vat_inclusive_amount);
}