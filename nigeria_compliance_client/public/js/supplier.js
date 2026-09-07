frappe.ui.form.on('Supplier', {
    refresh(frm) {
        // your code here
    },
    custom_b2b_supplier(frm) {
        if (frm.doc.custom_b2b_supplier == 1) {
            if (frm.doc.custom_b2b_supplier == 1 && frm.doc.custom_b2c_supplier == 1) {
                frm.set_value("custom_b2c_supplier", 0)
            }
        }

    },
    custom_b2c_supplier(frm) {
        if (frm.doc.custom_b2c_supplier == 1) {
            if (frm.doc.custom_b2c_supplier == 1 && frm.doc.custom_b2b_supplier == 1) {
                frm.set_value("custom_b2b_supplier", 0)
            }
        }
    }
})