import json
import frappe
from frappe import _
from nigeria_compliance_client.nrs_bridge_connection.doctype.nrs_bridge_settings.nrs_bridge_settings import (
	get_bridge_client,
)


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
