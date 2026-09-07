app_name = "nigeria_compliance_client"
app_title = "Nigeria Compliance Client"
app_publisher = "Nazmul Hossain"
app_description = "Compliance for Nigeria (Nigeria Revenue Service)"
app_email = "nazmulfx.dev@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "nigeria_compliance_client",
# 		"logo": "/assets/nigeria_compliance_client/logo.png",
# 		"title": "Nigeria Compliance Client",
# 		"route": "/nigeria_compliance_client",
# 		"has_permission": "nigeria_compliance_client.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nigeria_compliance_client/css/nigeria_compliance_client.css"
# app_include_js = "/assets/nigeria_compliance_client/js/nigeria_compliance_client.js"

# include js, css files in header of web template
# web_include_css = "/assets/nigeria_compliance_client/css/nigeria_compliance_client.css"
# web_include_js = "/assets/nigeria_compliance_client/js/nigeria_compliance_client.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nigeria_compliance_client/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
	"Sales Invoice": "public/js/sales_invoice.js",
	"Company": "public/js/company.js",
    "Purchase Order": "public/js/purchase_order.js",
	"Customer": "public/js/customer.js",
	"Supplier": "public/js/supplier.js",
	"Payment Entry": "public/js/payment_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "nigeria_compliance_client/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "nigeria_compliance_client.utils.jinja_methods",
# 	"filters": "nigeria_compliance_client.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "nigeria_compliance_client.install.before_install"
after_install = "nigeria_compliance_client.install.after_install"


# Uninstallation
# ------------

# before_uninstall = "nigeria_compliance_client.uninstall.before_uninstall"
# after_uninstall = "nigeria_compliance_client.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "nigeria_compliance_client.utils.before_app_install"
# after_app_install = "nigeria_compliance_client.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "nigeria_compliance_client.utils.before_app_uninstall"
# after_app_uninstall = "nigeria_compliance_client.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nigeria_compliance_client.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
		"on_update": "nigeria_compliance_client.nrs_bridge_connection.api.sync_doc_on_update",
		"on_submit": "nigeria_compliance_client.nrs_bridge_connection.api.sync_doc_on_submit",
		"on_cancel": "nigeria_compliance_client.nrs_bridge_connection.api.sync_doc_on_cancel",
		"on_trash": "nigeria_compliance_client.nrs_bridge_connection.api.sync_doc_on_trash"
	},
	"Sales Invoice": {
		"before_validate": "nigeria_compliance_client.nigeria_compliance_client.hooks.sales_invoice.before_validate",
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.sales_invoice.before_save",
		"on_submit": "nigeria_compliance_client.nigeria_compliance_client.hooks.sales_invoice.on_submit",
		"on_change": "nigeria_compliance_client.nigeria_compliance_client.hooks.sales_invoice.on_change",
		"on_cancel": "nigeria_compliance_client.nigeria_compliance_client.hooks.sales_invoice.on_cancel"
	},
	"Payment Entry": {
		"before_submit": "nigeria_compliance_client.nigeria_compliance_client.hooks.payment_entry.before_submit",
		"on_cancel": "nigeria_compliance_client.nigeria_compliance_client.hooks.payment_entry.on_cancel"
	},
	"Tax Category": {
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.tax_category.before_save"
	},
	"Item": {
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.item.before_save"
	},
	"Item Tax Template": {
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.item_tax_template.before_save"
	},
	"Purchase Order": {
		"before_validate": "nigeria_compliance_client.nigeria_compliance_client.hooks.purchase_order.before_validate",
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.purchase_order.before_save",
		"on_submit": "nigeria_compliance_client.nigeria_compliance_client.hooks.purchase_order.on_submit",
	},
	"Company": {
		"before_save": "nigeria_compliance_client.nigeria_compliance_client.hooks.company.before_save"
	},
	"Customer": {
		"validate": "nigeria_compliance_client.nigeria_compliance_client.hooks.customer.validate"
	},
	"Supplier": {
		"validate": "nigeria_compliance_client.nigeria_compliance_client.hooks.supplier.validate"
	}
	# "POS Invoice": {
	# 	"before_validate": "nigeria_compliance_client.nigeria_compliance_client.hooks.pos_invoice.before_validate",
	# }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"cron": {
# 		## Night 2:00AN
# 		"0 2 * * *": [
# 			"nigeria_compliance_client.nigeria_compliance_client.hooks.e_invoice.auto_transmit_b2c_invoices"
# 		]
# 	}
# }

# Testing
# -------

# before_tests = "nigeria_compliance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nigeria_compliance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "nigeria_compliance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["nigeria_compliance.utils.before_request"]
# after_request = ["nigeria_compliance.utils.after_request"]

# Job Events
# ----------
# before_job = ["nigeria_compliance.utils.before_job"]
# after_job = ["nigeria_compliance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"nigeria_compliance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


fixtures = [
	{"doctype": "Role", "filters": [["name", "in", ["e-invoicing Admin", "e-invoicing Manager"]]]},
	{"doctype": "Property Setter", "filters": [["name", "in", []]]},
	# {
	#     "doctype": "Property Setter",
	#     "filters": [
	#         ["doc_type", "=", "Sales Invoice"]
	#     ]
	# },
	# {
	#     "doctype": "Custom Field",
	#     "filters": [
	#         ["dt", "=", "Sales Invoice"],
	#         ["fieldname", "like", "custom_%"]
	#     ]
	# }
]
