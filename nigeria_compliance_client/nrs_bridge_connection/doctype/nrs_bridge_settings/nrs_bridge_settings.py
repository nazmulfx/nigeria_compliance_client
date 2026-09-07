import frappe
from frappe import _
from frappe.frappeclient import FrappeClient
from frappe.model.document import Document


class NRSBridgeSettings(Document):
	pass


@frappe.whitelist()
def test_connection():
	"""Tests connection to the configured NRS Bridge Server."""
	settings = frappe.get_single("NRS Bridge Settings")

	if not settings.enabled:
		frappe.throw(_("Bridge Connection is currently disabled. Please enable it first."))

	if not settings.server_url or not settings.api_key or not settings.get_password("api_secret"):
		frappe.throw(_("Server Base URL, API Key, and API Secret are required to test connection."))

	try:
		client = FrappeClient(
			url=settings.server_url.rstrip("/"),
			api_key=settings.api_key,
			api_secret=settings.get_password("api_secret"),
			verify=bool(settings.verify_ssl)
		)

		user = client.post_api("frappe.auth.get_logged_user")
		status_msg = _("Successfully connected to {0} as user: {1}").format(settings.server_url, user)
		settings.db_set("last_connection_status", status_msg)

		return {
			"status": "success",
			"message": status_msg
		}
	except Exception as e:
		error_msg = _("Failed to connect to {0}: {1}").format(settings.server_url, str(e))
		settings.db_set("last_connection_status", error_msg)
		frappe.throw(error_msg)


def get_bridge_client():
	"""
	Helper function to get an authenticated FrappeClient instance for NRS Bridge Server.
	Can be used anywhere in client hooks/scripts for CRUD operations.
	"""
	settings = frappe.get_single("NRS Bridge Settings")

	if not settings.enabled:
		frappe.throw(_("NRS Bridge Connection is disabled in NRS Bridge Settings."))

	if not settings.server_url or not settings.api_key or not settings.get_password("api_secret"):
		frappe.throw(_("NRS Bridge Settings are incomplete. Please configure Server URL and API credentials."))

	return FrappeClient(
		url=settings.server_url.rstrip("/"),
		api_key=settings.api_key,
		api_secret=settings.get_password("api_secret"),
		verify=bool(settings.verify_ssl)
	)


# Export generic CRUD API methods for NRS Bridge Connection
from nigeria_compliance_client.nrs_bridge_connection.api import (
	create_doc,
	delete_doc,
	get_list,
	post_api,
	read_doc,
	update_doc,
)

