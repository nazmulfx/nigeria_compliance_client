import frappe


def before_save(doc, method):
    return
    # if doc.custom_percent >= 0:
    #     company = frappe.defaults.get_user_default("Company")
    #     abbr = frappe.db.get_value("Company", company, ["abbr"])
    #     parent_account = f"Duties and Taxes - {abbr}"

    #     # Create Tax Account Head for each tax category
    #     if frappe.db.exists("Account", f"{doc.name} - {abbr}"):
    #         account = frappe.get_doc("Account", f"{doc.name} - {abbr}")
    #         account.tax_rate = doc.custom_percent
    #         account.save()
    #     else:
    #         account = frappe.new_doc("Account")
    #         account.account_name = doc.name
    #         account.parent_account = parent_account
    #         account.account_type = "Tax"
    #         account.tax_rate = doc.custom_percent
    #         account.company = company
    #         account.is_group = 0

    #         account.save()
