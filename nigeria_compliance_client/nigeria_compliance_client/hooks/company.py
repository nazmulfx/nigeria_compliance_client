
import frappe
import base64

    

def before_save(doc, method=None):
    # Only process if cryptographic_key has changed
    if doc.has_value_changed("custom_cryptographic_key") and doc.custom_cryptographic_key:
        process_cryptographic_key(doc)
    live_and_sandbox_check(doc)


def process_cryptographic_key(doc):
    """Process cryptographic key without causing save recursion"""
    # Get the file content
    file_doc = frappe.get_doc("File", {"file_url": doc.custom_cryptographic_key})
    file_path = file_doc.get_full_path()

    # Read the file content
    with open(file_path) as f:
        content = f.read()

    # Parse the JSON content
    crypto_data = frappe.parse_json(content)
    public_key_encoded = crypto_data.get("public_key")
    certificate_encoded = crypto_data.get("certificate")

    if not public_key_encoded or not certificate_encoded:
        frappe.throw("Invalid cryptographic key format. Missing public_key or certificate")

    # Decode public key
    decoded_bytes = base64.b64decode(public_key_encoded)
    decoded_text = decoded_bytes.decode("utf-8")

    # Update instance variables
    doc.custom_public_key = public_key_encoded
    doc.custom_public_key_decoded = decoded_text
    doc.custom_certificate = certificate_encoded

def live_and_sandbox_check(doc):
    if doc.custom_nrs_enviroment == "Production":
        doc.custom_base_url = doc.custom_live_base_url
        doc.custom_report_base_url = doc.custom_live_report_base_url
        doc.custom_api_key = doc.custom_live_api_key
        doc.custom_client_secret = doc.custom_live_api_secret
        doc.custom_service_id = doc.custom_live_service_id
        doc.custom_irn_template = doc.custom_live_irn_temeplate
        doc.custom_entity_id = doc.custom_live_entity_id
        doc.custom_business_id = doc.custom_live_business_id
    elif doc.custom_nrs_enviroment == "Sandbox":
        doc.custom_base_url = doc.custom_sandbox_base_url
        doc.custom_report_base_url = doc.custom_sandbox_report_base_url
        doc.custom_api_key = doc.custom_sandbox_api_key
        doc.custom_client_secret = doc.custom_sandbox_api_secret
        doc.custom_service_id = doc.custom_sandbox_service_id
        doc.custom_irn_template = doc.custom_sandbox_irn_temeplate
        doc.custom_entity_id = doc.custom_sandbox_entity_id
        doc.custom_business_id = doc.custom_sandbox_business_id