import frappe

def validate(doc, method=None):
    if doc.custom_b2b_customer and doc.custom_b2c_customer:
        frappe.throw("B2B Customer and B2C Customer cannot be same")

    if doc.custom_b2b_customer:
        check_address_for_b2b_customer(doc)

def check_address_for_b2b_customer(doc):
    if not frappe.db.exists("Dynamic Link", {"link_doctype": "Customer", "link_name": doc.name, "parenttype": "Address"}):
        frappe.throw("Address is required for B2B Customer")

