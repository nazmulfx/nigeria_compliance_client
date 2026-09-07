import frappe
from frappe import _
from .e_invoice import send_invoice_to_firs

def before_submit(doc, method=None):
    """
    Before submitting a Payment Entry, check if any referenced Sales Invoice 
    is pending transmission to NRS. If so, automatically transmit the invoice 
    to NRS first so NRS receives the initial registration in PENDING status.
    """
    if not doc.references:
        return

    for row in doc.references:
        if row.reference_doctype == "Sales Invoice" and row.reference_name:
            inv = frappe.get_doc("Sales Invoice", row.reference_name)
            
            if (
                inv.custom_transmission_mode != "Do Not Transmit" 
                and inv.custom_invoice_kind in ["B2B", "B2C"]
            ):
                if inv.custom_transmission_status == "Pending":
                    frappe.msgprint(
                        _("Sales Invoice {0} is being transmitted to NRS prior to Payment Entry submission.").format(inv.name),
                        alert=True
                    )
                    send_invoice_to_firs(inv, type="selling")


def on_cancel(doc, method=None):
    """
    Prevent cancelling Payment Entry if referenced Sales Invoice has been transmitted to NRS.
    """
    if not doc.references:
        return

    for row in doc.references:
        if row.reference_doctype == "Sales Invoice" and row.reference_name:
            inv = frappe.get_doc("Sales Invoice", row.reference_name)
            if (
                inv.custom_transmission_mode != "Do Not Transmit"
                and inv.custom_transmission_status == "Complete"
            ):
                frappe.throw(
                    _("Cannot cancel Payment Entry {0}. Referenced Sales Invoice {1} has already been transmitted to NRS with recorded payment status.").format(
                        frappe.bold(doc.name), frappe.bold(inv.name)
                    ),
                    title=_("NRS Payment Cancellation Restriction")
                )
