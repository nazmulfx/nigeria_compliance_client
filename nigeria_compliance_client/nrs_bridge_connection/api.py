import base64
import json
import frappe
from frappe import _
from nigeria_compliance_client.nrs_bridge_connection.doctype.nrs_bridge_settings.nrs_bridge_settings import (
	get_bridge_client,
)

# System DocTypes that should be excluded from automatic bridge sync
EXCLUDED_DOCTYPES = {
	"NRS Bridge Settings",
	"Error Log",
	"Activity Log",
	"Version",
	"Sessions",
	"Scheduled Job Log",
	"Prepared Report",
	"DocType",
	"Custom Field",
	"Property Setter",
	"Print Format",
	"Report",
	"Workspace",
	"Role",
	"User",
	"Installed Application",
	"Module Def",
	"Patch Log",
	"Singles",
	"Comment",
}


@frappe.whitelist()
def create_doc(doctype: str, doc: str | dict):
	"""
	Sends/Creates a new document of any DocType on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()

	if isinstance(doc, str):
		doc = json.loads(doc)

	doc["doctype"] = doctype
	return client.insert(doc)


@frappe.whitelist()
def read_doc(doctype: str, name: str):
	"""
	Reads/Fetches a single document of any DocType from the remote NRS Bridge Server.
	"""
	client = get_bridge_client()
	return client.get_doc(doctype, name)


@frappe.whitelist()
def get_list(
	doctype: str,
	filters: str | dict | None = None,
	fields: str | list | None = None,
	order_by: str | None = None,
	limit_start: int = 0,
	limit_page_length: int = 20,
):
	"""
	Queries a list of documents for any DocType from the remote NRS Bridge Server.
	"""
	client = get_bridge_client()

	if isinstance(filters, str):
		filters = json.loads(filters)

	if isinstance(fields, str):
		fields = json.loads(fields)

	return client.get_list(
		doctype=doctype,
		filters=filters,
		fields=fields,
		order_by=order_by,
		limit_start=limit_start,
		limit_page_length=limit_page_length,
	)


@frappe.whitelist()
def update_doc(doctype: str, name: str, doc: str | dict):
	"""
	Updates an existing document of any DocType on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()

	if isinstance(doc, str):
		doc = json.loads(doc)

	doc["doctype"] = doctype
	doc["name"] = name
	return client.update(doc)


@frappe.whitelist()
def delete_doc(doctype: str, name: str):
	"""
	Deletes a document of any DocType on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()
	client.delete(doctype, name)
	return {"status": "success", "message": _("Document {0} {1} deleted from remote server.").format(doctype, name)}


@frappe.whitelist()
def post_api(method: str, params: str | dict | None = None):
	"""
	Calls any whitelisted RPC method on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()

	if isinstance(params, str):
		params = json.loads(params)

	return client.post_api(method, params=params or {})


def sync_file_doc(doc, client):
	"""
	Syncs a File document and its binary contents to the remote server.
	"""
	content = None
	try:
		content = doc.get_content()
	except Exception:
		content = None

	if isinstance(content, str):
		content = content.encode("utf-8")

	payload = {
		"doctype": "File",
		"file_name": doc.file_name,
		"is_private": doc.is_private,
		"attached_to_doctype": doc.attached_to_doctype,
		"attached_to_name": doc.attached_to_name,
		"attached_to_field": doc.attached_to_field,
		"folder": doc.folder,
	}

	if content:
		payload["content"] = base64.b64encode(content).decode("utf-8")
		payload["decode"] = 1
	elif doc.file_url:
		payload["file_url"] = doc.file_url

	# Insert or update File on remote site
	try:
		if doc.name and client.get_value("File", "name", {"name": doc.name}):
			payload["name"] = doc.name
			client.update(payload)
		else:
			client.insert(payload)
	except Exception:
		try:
			client.insert(payload)
		except Exception:
			if doc.name:
				payload["name"] = doc.name
				client.update(payload)


def sync_doc_on_update(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_update) to sync created/updated documents to remote NRS Bridge server.
	"""
	if doc.doctype in EXCLUDED_DOCTYPES:
		return

	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if not settings.enabled:
			return

		client = get_bridge_client()

		# Dedicated handler for File attachments and binaries
		if doc.doctype == "File":
			sync_file_doc(doc, client)
			return

		doc_dict = doc.as_dict()

		# Single DocType handling (e.g. System Settings)
		if doc.meta.issingle:
			client.update(doc_dict)
			return

		# Standard DocType handling
		remote_exists = False
		try:
			remote_exists = bool(client.get_value(doc.doctype, "name", {"name": doc.name}))
		except Exception:
			remote_exists = False

		if remote_exists:
			client.update(doc_dict)
		else:
			client.insert(doc_dict)
	except Exception:
		frappe.log_error(
			title=f"Bridge Sync Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)


def sync_doc_on_trash(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_trash) to delete document on remote NRS Bridge server.
	"""
	if doc.doctype in EXCLUDED_DOCTYPES:
		return

	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if not settings.enabled:
			return

		client = get_bridge_client()
		client.delete(doc.doctype, doc.name)
	except Exception:
		frappe.log_error(
			title=f"Bridge Delete Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)
