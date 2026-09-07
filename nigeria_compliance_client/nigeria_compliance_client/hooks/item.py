import frappe

def before_save(doc, method):
	if doc.custom_vat_exempted_productservice == 1:
		doc.taxes = []

	for row in doc.uoms:
		if not row.nrs_uom_code:
			uom_doc = frappe.get_doc("UOM", row.uom)
			row.nrs_uom_code = uom_doc.nrs_uom_code
			row.nrs_uom_name = uom_doc.nrs_uom_name
			row.nrs_uom_description = uom_doc.nrs_uom_description

		