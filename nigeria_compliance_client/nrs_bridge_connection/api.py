import base64
import json
import frappe
from frappe import _
from nigeria_compliance_client.nrs_bridge_connection.constants import DEFAULT_EXCLUDED_DOCTYPES
from nigeria_compliance_client.nrs_bridge_connection.doctype.nrs_bridge_settings.nrs_bridge_settings import (
	get_bridge_client,
)


def get_excluded_doctypes() -> set:
	"""
	Returns the set of DocTypes excluded from bridge sync, fetched dynamically from NRS Bridge Settings.
	"""
	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if settings.excluded_doctypes:
			return {row.document_type for row in settings.excluded_doctypes if row.document_type}
	except Exception:
		pass

	return set(DEFAULT_EXCLUDED_DOCTYPES)


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
	doc_to_save = prepare_doc_for_remote_update(client, doc)

	return client.post_api("frappe.client.save", {"doc": doc_to_save})


@frappe.whitelist()
def submit_doc(doctype: str, name: str):
	"""
	Submits a document of any DocType on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()
	remote_doc = client.get_doc(doctype, name)
	doc_to_save = prepare_doc_for_remote_update(client, remote_doc)
	return client.submit(doc_to_save)


@frappe.whitelist()
def cancel_doc(doctype: str, name: str):
	"""
	Cancels a document of any DocType on the remote NRS Bridge Server.
	"""
	client = get_bridge_client()
	client.cancel(doctype, name)
	return {"status": "success", "message": _("Document {0} {1} cancelled on remote server.").format(doctype, name)}


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
			payload_to_save = prepare_doc_for_remote_update(client, payload)
			client.post_api("frappe.client.save", {"doc": payload_to_save})
		else:
			client.insert(payload)
	except Exception:
		try:
			client.insert(payload)
		except Exception:
			if doc.name:
				payload["name"] = doc.name
				payload_to_save = prepare_doc_for_remote_update(client, payload)
				client.post_api("frappe.client.save", {"doc": payload_to_save})


def prepare_doc_for_remote_update(client, doc_dict):
	"""
	Prepares document dict for updating remote document by fetching remote modified/creation metadata.
	"""
	doc_copy = json.loads(frappe.as_json(doc_dict))
	doctype = doc_copy.get("doctype")
	name = doc_copy.get("name")

	if doctype and name:
		try:
			remote_info = client.get_value(doctype, ["modified", "creation", "owner", "docstatus"], {"name": name})
			if remote_info and isinstance(remote_info, dict):
				for k in ["modified", "creation", "owner", "docstatus"]:
					if k in remote_info:
						doc_copy[k] = remote_info[k]
		except Exception:
			pass

	# Strip transient local UI flags
	for f in ["__islocal", "__unsaved", "_user_tags", "_comments", "_assign", "_liked_by"]:
		doc_copy.pop(f, None)

	return doc_copy


def create_or_update_remote_doc(client, doc_dict):
	"""
	Inserts document on remote server if new, or saves update if already existing.
	"""
	doctype = doc_dict.get("doctype")
	name = doc_dict.get("name")

	remote_info = None
	if name:
		try:
			remote_info = client.get_value(doctype, ["name", "docstatus"], {"name": name})
		except Exception:
			remote_info = None

	if remote_info and isinstance(remote_info, dict):
		# If document is already submitted on remote server (docstatus == 1), do not attempt to re-save draft edits
		if remote_info.get("docstatus") == 1:
			return remote_info
		doc_to_save = prepare_doc_for_remote_update(client, doc_dict)
		return client.post_api("frappe.client.save", {"doc": doc_to_save})
	else:
		return client.insert(doc_dict)


def extract_clean_error_message(e: Exception) -> str:
	msg = str(e)
	if hasattr(e, "args") and e.args:
		first_arg = e.args[0]
		if isinstance(first_arg, str):
			msg = first_arg
		elif isinstance(first_arg, dict):
			msg = first_arg.get("message") or first_arg.get("exc") or str(first_arg)

	if "ValidationError:" in msg:
		msg = msg.split("ValidationError:")[-1].strip()
	elif "FrappeException:" in msg:
		msg = msg.split("FrappeException:")[-1].strip()

	return msg.strip() or str(e)


def sync_doc_on_update(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_update) to sync created/updated documents to remote NRS Bridge server.
	"""
	if doc.doctype in get_excluded_doctypes():
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
			doc_to_save = prepare_doc_for_remote_update(client, doc_dict)
			client.post_api("frappe.client.save", {"doc": doc_to_save})
			return

		create_or_update_remote_doc(client, doc_dict)
	except Exception as e:
		frappe.log_error(
			title=f"Bridge Sync Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)
		clean_err = extract_clean_error_message(e)
		frappe.throw(
			_("Failed to save {0} {1} on NRS Bridge Server:<br><br>{2}").format(
				doc.doctype, frappe.bold(doc.name), clean_err
			),
			title=_("Bridge Sync Error")
		)


def sync_doc_on_submit(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_submit) to submit the document on remote NRS Bridge server.
	"""
	if doc.doctype in get_excluded_doctypes():
		return

	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if not settings.enabled:
			return

		client = get_bridge_client()
		doc_dict = doc.as_dict()

		doctype = doc_dict.get("doctype")
		name = doc_dict.get("name")

		remote_info = None
		if name:
			try:
				remote_info = client.get_value(doctype, ["name", "docstatus"], {"name": name})
			except Exception:
				remote_info = None

		if remote_info and isinstance(remote_info, dict):
			# If already submitted remotely (docstatus == 1), skip submitting again
			if remote_info.get("docstatus") == 1:
				return
			doc_to_save = prepare_doc_for_remote_update(client, doc_dict)
			client.submit(doc_to_save)
		else:
			# If document does not exist remotely, insert and submit
			created_doc = client.insert(doc_dict)
			if created_doc and isinstance(created_doc, dict) and created_doc.get("docstatus") == 0:
				client.submit(created_doc)
	except Exception as e:
		frappe.log_error(
			title=f"Bridge Submit Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)
		clean_err = extract_clean_error_message(e)
		frappe.throw(
			_("Failed to submit {0} {1} on NRS Bridge Server:<br><br>{2}").format(
				doc.doctype, frappe.bold(doc.name), clean_err
			),
			title=_("Bridge Submit Error")
		)


def sync_doc_on_cancel(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_cancel) to cancel the document on remote NRS Bridge server.
	"""
	if doc.doctype in get_excluded_doctypes():
		return

	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if not settings.enabled:
			return

		client = get_bridge_client()
		remote_info = None
		if doc.name:
			try:
				remote_info = client.get_value(doc.doctype, ["name", "docstatus"], {"name": doc.name})
			except Exception:
				remote_info = None

		if remote_info and isinstance(remote_info, dict):
			if remote_info.get("docstatus") == 2:
				# Already cancelled on remote server
				return
			if remote_info.get("docstatus") == 1:
				client.cancel(doc.doctype, doc.name)
	except Exception as e:
		frappe.log_error(
			title=f"Bridge Cancel Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)
		clean_err = extract_clean_error_message(e)
		frappe.throw(
			_("Failed to cancel {0} {1} on NRS Bridge Server:<br><br>{2}").format(
				doc.doctype, frappe.bold(doc.name), clean_err
			),
			title=_("Bridge Cancel Error")
		)


def sync_doc_on_trash(doc, method=None):
	"""
	Automatically called by Frappe document hooks (on_trash) to delete document on remote NRS Bridge server.
	"""
	if doc.doctype in get_excluded_doctypes():
		return

	try:
		settings = frappe.get_single("NRS Bridge Settings")
		if not settings.enabled:
			return

		client = get_bridge_client()
		client.delete(doc.doctype, doc.name)
	except Exception as e:
		frappe.log_error(
			title=f"Bridge Delete Error: {doc.doctype} {doc.name}",
			message=frappe.get_traceback()
		)
		clean_err = extract_clean_error_message(e)
		frappe.throw(
			_("Failed to delete {0} {1} on NRS Bridge Server:<br><br>{2}").format(
				doc.doctype, frappe.bold(doc.name), clean_err
			),
			title=_("Bridge Delete Error")
		)
