frappe.ui.form.on("Company", {
    refresh(frm) {

    },
    custom_get_invoice_type_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_invoice_type",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_payment_method_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_payment_means",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_tax_category_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_tax_categories",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_currency_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_currency",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_product_code_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_product_code",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_service_code_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_service_code",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_country_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_country",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_state_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_states",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_local_government_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_local_government",
            args: {
                company: frm.doc.name
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_vat_exemption_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_tax_exemption",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    },
    custom_get_unit_of_measurement_uom(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_unit_of_measurement_uom",
            args: {
                company: frm.doc.name,
            },
            callback: function (r) {
                if (!r.exc && r.message) {
                    frappe.show_alert({
                        message: r.message.message || r.message,
                        indicator: "blue"
                    });
                }
            },
        });
    }
});
