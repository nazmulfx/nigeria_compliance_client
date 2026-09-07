import frappe
from frappe import _
from frappe.frappeclient import FrappeClient
from frappe.model.document import Document


def sanitize_url(url: str) -> str:
	if not url:
		return ""
	url = url.strip().rstrip("/")
	if not (url.startswith("http://") or url.startswith("https://")):
		url = f"http://{url}"
	return url


class NRSBridgeSettings(Document):
	def validate(self):
		if self.server_url:
			self.server_url = sanitize_url(self.server_url)


@frappe.whitelist()
def test_connection():
	"""Tests connection to the configured NRS Bridge Server."""
	settings = frappe.get_single("NRS Bridge Settings")

	if not settings.enabled:
		frappe.throw(_("Bridge Connection is currently disabled. Please enable it first."))

	if not settings.server_url or not settings.api_key or not settings.get_password("api_secret"):
		frappe.throw(_("Server Base URL, API Key, and API Secret are required to test connection."))

	server_url = sanitize_url(settings.server_url)

	try:
		client = FrappeClient(
			url=server_url,
			api_key=settings.api_key,
			api_secret=settings.get_password("api_secret"),
			verify=bool(settings.verify_ssl)
		)

		user = client.post_api("frappe.auth.get_logged_user")
		status_msg = _("Successfully connected to {0} as user: {1}").format(server_url, user)
		settings.db_set("last_connection_status", status_msg)

		return {
			"status": "success",
			"message": status_msg
		}
	except Exception as e:
		error_msg = _("Failed to connect to {0}: {1}").format(server_url, str(e))
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

	server_url = sanitize_url(settings.server_url)

	return FrappeClient(
		url=server_url,
		api_key=settings.api_key,
		api_secret=settings.get_password("api_secret"),
		verify=bool(settings.verify_ssl)
	)




