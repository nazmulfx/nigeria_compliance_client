frappe.ui.form.on('Customer', {
    refresh(frm) {
        // your code here
    },
    custom_b2b_customer(frm) {
        if (frm.doc.custom_b2b_customer == 1) {
            if (frm.doc.custom_b2b_customer == 1 && frm.doc.custom_b2c_customer == 1) {
                frm.set_value("custom_b2c_customer", 0)
            }
        }
    },
    custom_b2c_customer(frm) {
        if (frm.doc.custom_b2c_customer == 1) {
            if (frm.doc.custom_b2c_customer && frm.doc.custom_b2b_customer == 1) {
                frm.set_value("custom_b2b_customer", 0)
            }
        }
    }
})