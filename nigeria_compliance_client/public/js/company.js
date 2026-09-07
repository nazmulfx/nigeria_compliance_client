frappe.ui.form.on("Company", {
    refresh(frm) {

    },
    custom_get_invoice_type_list(frm) {
        frappe.call({
            method: "nigeria_compliance_client.nigeria_compliance_client.hooks.utils.fetch_firs_invoice_type",
            args: {
                company: frm.doc.name,
            },
            freeze: true,
            freeze_message: "Fetching NRS Invoice Type List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Payment Method List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Tax Category List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Currency List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Product Code List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Services Code List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Country List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS State List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Local Government List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS VAT Exemption List...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
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
            freeze: true,
            freeze_message: "Fetching NRS Approved Unit of Measurement (UoM)...",
            callback: function (r) {
                if (!r.exc) {
                    frappe.msgprint(r.message);
                }
            },
        });
    }
});
