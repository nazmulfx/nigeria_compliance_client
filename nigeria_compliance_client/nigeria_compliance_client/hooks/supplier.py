import frappe

def validate(doc, method=None):
    if doc.custom_b2b_supplier and doc.custom_b2c_supplier:
        frappe.throw("B2B Supplier and B2C Supplier cannot be same")

    if doc.custom_b2b_supplier:
        check_address_for_b2b_supplier(doc)

def check_address_for_b2b_supplier(doc):
    if not frappe.db.exists("Dynamic Link", {"link_doctype": "Supplier", "link_name": doc.name, "parenttype": "Address" }):
        frappe.throw("Address is required for B2B Supplier")