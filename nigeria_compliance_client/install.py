import frappe


def after_install():
	set_amended_naming_to_default()


def set_amended_naming_to_default():
	dns = frappe.get_doc("Document Naming Settings")
	dns.default_amend_naming = "Default Naming"
	dns.update_amendment_rule()

