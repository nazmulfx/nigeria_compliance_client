# Copyright (c) 2026, Nazmul Hossain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt


def execute(filters: dict | None = None) -> tuple[list[dict], list[dict]]:
	if not filters:
		filters = {}

	show_collection_payment = cint(filters.get("show_collection_payment"))

	# 1. Build filters and query Sales Invoice using ORM
	inv_filters = {"docstatus": 1}

	if filters.get("company"):
		inv_filters["company"] = filters["company"]

	# if filters.get("pos_profile"):
	# 	inv_filters["pos_profile"] = filters["pos_profile"]

	if filters.get("from_date") and filters.get("to_date"):
		inv_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]
	else:
		frappe.msgprint(_("Please select both From Date and To Date"))
		return [], []

	invoices = frappe.get_all(
		"Sales Invoice",
		filters=inv_filters,
		fields=["name", "customer", "grand_total", "status", "outstanding_amount", "outstanding_on_invoice_creation", "pos_profile"],
		order_by="posting_date desc, creation desc",
	)

	# 2. Query Sales Invoice Payment child table for fetched invoices
	payments_map = {}
	payment_modes = set()

	if invoices:
		invoice_names = [inv["name"] for inv in invoices]
		payments = frappe.get_all(
			"Sales Invoice Payment",
			filters={"parent": ["in", invoice_names]},
			fields=["parent", "mode_of_payment", "amount"],
		)

		for p in payments:
			mop = p.get("mode_of_payment")
			if not mop:
				continue
			payment_modes.add(mop)
			parent = p.get("parent")
			if parent not in payments_map:
				payments_map[parent] = {}
			payments_map[parent][mop] = payments_map[parent].get(mop, 0.0) + flt(p.get("amount"))

	# 3. Query Payment Entry if show_collection_payment is enabled
	payment_entries = []
	if show_collection_payment:
		pe_filters = {"docstatus": 1, "payment_type": "Receive"}
		if filters.get("company"):
			pe_filters["company"] = filters["company"]
		if filters.get("from_date") and filters.get("to_date"):
			pe_filters["posting_date"] = ["between", [filters["from_date"], filters["to_date"]]]

		payment_entries = frappe.get_all(
			"Payment Entry",
			filters=pe_filters,
			fields=["name", "party_type", "party", "mode_of_payment", "paid_amount", "received_amount"],
			order_by="posting_date desc, creation desc",
		)

		for pe in payment_entries:
			mop = pe.get("mode_of_payment")
			if mop:
				payment_modes.add(mop)

	# Fallback to all Mode of Payment if no payment modes found in dataset
	if not payment_modes:
		payment_modes = set(frappe.get_all("Mode of Payment", pluck="name"))

	sorted_payment_modes = sorted(list(payment_modes))

	# 4. Define columns
	columns = [
		{"label": _("Invoice ID"), "fieldname": "name", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
	]

	if show_collection_payment:
		columns.append(
			{
				"label": _("Payment Entry ID"),
				"fieldname": "payment_entry",
				"fieldtype": "Link",
				"options": "Payment Entry",
				"width": 140,
			}
		)

	columns.extend([
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Curr. Outstanding"), "fieldname": "outstanding_amount", "fieldtype": "Currency", "width": 180},
		{"label": _("Outstanding on Invoice Creation"), "fieldname": "outstanding_on_invoice_creation", "fieldtype": "Currency", "width": 220},
	])

	if show_collection_payment:
		columns.append(
			{"label": _("Collected Amount"), "fieldname": "collected_amount", "fieldtype": "Currency", "width": 120}
		)

	mode_field_map = {}
	for mode in sorted_payment_modes:
		fn = frappe.scrub(mode)
		mode_field_map[mode] = fn
		columns.append(
			{
				"label": _(mode),
				"fieldname": fn,
				"fieldtype": "Currency",
				"width": 120,
			}
		)

	# columns.append(
	# 	{
	# 		"label": _("POS Profile"),
	# 		"fieldname": "pos_profile",
	# 		"fieldtype": "Link",
	# 		"options": "POS Profile",
	# 		"width": 140,
	# 	}
	# )

	# 5. Build data rows
	data = []

	# Add Sales Invoice rows
	for inv in invoices:
		inv_payments = payments_map.get(inv["name"], {})
		total_collected = sum(inv_payments.values())
		row = {
			"name": inv["name"],
			"customer": inv["customer"],
			"grand_total": inv["grand_total"],
			"status": inv["status"],
			"outstanding_amount": inv["outstanding_amount"],
			"outstanding_on_invoice_creation": inv.get("outstanding_on_invoice_creation") or 0.0,
			"pos_profile": inv.get("pos_profile") or "",
		}
		if show_collection_payment:
			row["payment_entry"] = ""
			row["collected_amount"] = total_collected

		for mode in sorted_payment_modes:
			fn = mode_field_map[mode]
			row[fn] = inv_payments.get(mode, 0.0)
		data.append(row)

	# Add Payment Entry rows after all Sales Invoices
	if show_collection_payment:
		for pe in payment_entries:
			amt = flt(pe.get("paid_amount")) or flt(pe.get("received_amount")) or 0.0
			pe_mop = pe.get("mode_of_payment")
			row = {
				"name": "",
				"payment_entry": pe["name"],
				"customer": pe.get("party") if pe.get("party_type") == "Customer" else (pe.get("party") or ""),
				"grand_total": 0.0,
				"status": "Submitted",
				"outstanding_amount": 0.0,
				"outstanding_on_invoice_creation": 0.0,
				"pos_profile": "",
				"collected_amount": amt,
				"is_payment_entry": 1,
			}
			for mode in sorted_payment_modes:
				fn = mode_field_map[mode]
				row[fn] = amt if mode == pe_mop else 0.0
			data.append(row)

	return columns, data
