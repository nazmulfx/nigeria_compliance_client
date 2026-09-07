frappe.ui.form.on("NRS Bridge Settings", {
	refresh(frm) {
		frm.add_custom_button(__("Test Connection"), () => {
			frm.call({
				method: "nigeria_compliance_client.nrs_bridge_connection.doctype.nrs_bridge_settings.nrs_bridge_settings.test_connection",
				freeze: true,
				freeze_message: __("Connecting to NRS Bridge Server..."),
				callback: function(r) {
					if (!r.exc && r.message) {
						frappe.msgprint({
							title: __("Connection Successful"),
							indicator: "green",
							message: r.message.message
						});
						frm.reload_doc();
					}
				}
			});
		}).addClass("btn-primary");
	}
});
