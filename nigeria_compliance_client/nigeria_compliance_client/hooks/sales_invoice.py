import base64
import json
import time
from io import BytesIO
from frappe.utils import flt

import frappe
from frappe import _
import qrcode
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from . utils import get_previous_outstannding_amount



def before_validate(doc, method):
    set_outstanding_on_creation(doc)
    doc.previous_outstanding = get_previous_outstannding_amount(doc.customer)


    # for duplicate/Amend invoice set status to pending.
    if doc.docstatus==0:
        doc.custom_transmission_status = "Pending"
    


def before_save(doc, method):
    calculate_vat(doc)


def on_submit(doc, method=None):
    # on submit, send invoice to FIRS
    pass


def on_change(doc, method=None):
    # on status change, update invoice status in FIRS
    pass

def on_cancel(doc, method=None):
    # Prevent cancellation if invoice was transmitted to NRS and had payment recorded (PE or POS)
    if doc.custom_transmission_status == "Complete":
        has_had_payment = (
            frappe.db.exists("Payment Entry Reference", {
                "reference_doctype": "Sales Invoice",
                "reference_name": doc.name
            })
            or (doc.is_pos and (doc.paid_amount or 0) > 0)
            or (doc.outstanding_amount < doc.grand_total)
        )
        if has_had_payment:
            frappe.throw(
                _("Cannot cancel Sales Invoice {0}. This invoice was transmitted to NRS and has recorded payments. NRS compliance guidelines do not permit cancelling invoices with recorded payments.").format(
                    frappe.bold(doc.name)
                ),
                title=_("NRS Cancellation Restriction")
            )

    # status update (REJECTED) is only sent to NRS if the invoice was previously registered
    pass

def set_outstanding_on_creation(doc):
    total = flt(doc.rounded_total) if doc.rounded_total else flt(doc.grand_total)
    paid = flt(doc.paid_amount)
    doc.outstanding_on_invoice_creation = total - paid

def calculate_vat(doc):
    for item in doc.items:
        item.custom_vat = item.rate * item.custom_total_tax_percent / 100
        item.custom_vat_inclusive_rate = item.rate + item.custom_vat
        item.custom_vat_inclusive_amount = item.custom_vat_inclusive_rate * item.qty