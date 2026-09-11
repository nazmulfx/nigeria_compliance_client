import xml.etree.ElementTree as ET

import frappe
from frappe import _
import requests


@frappe.whitelist()
def fetch_firs_invoice_type(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_invoice_type",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Invoice Types started in background. You will be notified upon completion.")}


def _process_fetch_firs_invoice_type(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/invoice-types"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=60)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			code = data.find("Code").text
			value = data.find("Value").text
			entries.append({"code": code, "value": value})

		for entry in entries:
			if frappe.db.exists("FIRS Invoice Type", {"code": entry["code"], "value": entry["value"]}):
				doc = frappe.get_doc("FIRS Invoice Type", {"code": entry["code"], "value": entry["value"]})
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{"doctype": "FIRS Invoice Type", "code": entry["code"], "value": entry["value"]}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Invoice Type records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Invoice Type Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Invoice Types: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_payment_means(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_payment_means",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Payment Method List started in background. You will be notified upon completion.")}


def _process_fetch_firs_payment_means(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/payment-means"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=60)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			code = data.find("Code").text
			value = data.find("Value").text
			entries.append({"code": code, "value": value})

		for entry in entries:
			payment_type = ""
			if entry["value"] in [
				"Cheque",
				"Credit Transfer",
				"Debit Transfer",
				"ACH Credit",
				"ACH Debit",
				"Bank Card",
				"Direct Debit",
				"Credit Card",
				"Banker's Draft",
			]:
				payment_type = "Bank"
			elif entry["value"] in ["Cash"]:
				payment_type = "Cash"
			else:
				payment_type = "General"

			if frappe.db.exists("Mode of Payment", {"name": entry["value"]}):
				doc = frappe.get_doc("Mode of Payment", entry["value"])
				doc.custom_code = entry["code"]
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "Mode of Payment",
						"custom_code": entry["code"],
						"mode_of_payment": entry["value"],
						"type": payment_type,
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Payment Means records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Payment Means Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Payment Means: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_tax_categories(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_tax_categories",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Tax Category List started in background. You will be notified upon completion.")}


def _process_fetch_firs_tax_categories(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/tax-categories"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=60)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			code = data.find("Code").text
			value = data.find("Value").text
			try:
				percent = float(data.find("Percent").text)
			except (ValueError, TypeError):
				percent = 0.0
			entries.append({"code": code, "value": value, "percent": percent})

		for entry in entries:
			if frappe.db.exists("Tax Category", {"title": entry["code"], "custom_value": entry["value"]}):
				doc = frappe.get_doc("Tax Category", {"title": entry["code"], "custom_value": entry["value"]})
				doc.custom_percent = entry["percent"]
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "Tax Category",
						"title": entry["code"],
						"custom_value": entry["value"],
						"custom_percent": entry["percent"],
					}
				).insert(ignore_permissions=True)

			if frappe.db.exists("Account", f"{entry['code']} - {company_doc.abbr}"):
				account = frappe.get_doc("Account", f"{entry['code']} - {company_doc.abbr}")
				account.tax_rate = entry["percent"]
				account.save(ignore_permissions=True)
			else:
				account = frappe.new_doc("Account")
				account.account_name = entry["code"]
				account.parent_account = f"Duties and Taxes - {company_doc.abbr}"
				account.account_type = "Tax"
				account.tax_rate = entry["percent"]
				account.company = company_doc.name
				account.is_group = 0
				account.save(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Tax Category records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Tax Categories Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Tax Categories: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_currency(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_currency",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Currency List started in background. You will be notified upon completion.")}


def _process_fetch_firs_currency(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/currencies"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=60)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			symbol = data.find("Symbol").text
			currency_name = data.find("Name").text
			symbol_native = data.find("SymbolNative").text
			decimal_digits = data.find("DecimalDigits").text
			currency_rounding = float(data.find("Rounding").text)
			code = data.find("Code").text
			currency_name_plural = data.find("NamePlural").text
			entries.append(
				{
					"symbol": symbol,
					"currency_name": currency_name,
					"symbol_native": symbol_native,
					"decimal_digits": decimal_digits,
					"currency_rounding": currency_rounding,
					"code": code,
					"currency_name_plural": currency_name_plural,
				}
			)

		for entry in entries:
			if frappe.db.exists("Currency", {"name": entry["code"]}):
				doc = frappe.get_doc("Currency", entry["code"])
				doc.custom_firs_currency_name = entry["currency_name"]
				doc.custom_symbol_native = entry["symbol_native"]
				doc.custom_rounding = entry["currency_rounding"]
				doc.custom_name_plural = entry["currency_name_plural"]
				if not doc.symbol:
					doc.symbol = entry["symbol"]
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "Currency",
						"currency_name": entry["code"],
						"enabled": 1,
						"fraction": "",
						"fraction_units": 100,
						"smallest_currency_fraction_value": 0.00,
						"symbol": entry["symbol"],
						"number_format": "#,###.##",
						"custom_firs_currency_name": entry["currency_name"],
						"custom_symbol_native": entry["symbol_native"],
						"custom_rounding": entry["currency_rounding"],
						"custom_name_plural": entry["currency_name_plural"],
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Currency records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Currency Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Currency: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_product_code(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_product_code",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Product Code List started in background. You will be notified upon completion.")}


def _process_fetch_firs_product_code(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/hs-codes"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			hscode = data.find("Hscode").text if data.find("Hscode") is not None else ""
			description = data.find("Description").text if data.find("Description") is not None else ""
			entries.append({"hscode": hscode, "description": description})

		for entry in entries:
			if frappe.db.exists("FIRS Products Codes", {"hscode": entry["hscode"], "description": entry["description"]}):
				doc = frappe.get_doc("FIRS Products Codes", {"hscode": entry["hscode"], "description": entry["description"]})
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "FIRS Products Codes",
						"hscode": entry["hscode"],
						"description": entry["description"],
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Product Code records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Product Code Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Product Codes: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_service_code(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_service_code",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Services Code List started in background. You will be notified upon completion.")}


def _process_fetch_firs_service_code(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/services-codes"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			code = data.find("Code").text if data.find("Code") is not None else ""
			description = data.find("Description").text if data.find("Description") is not None else ""
			entries.append({"code": code, "description": description})

		for entry in entries:
			if frappe.db.exists("FIRS Service Codes", {"code": entry["code"], "description": entry["description"]}):
				doc = frappe.get_doc("FIRS Service Codes", {"code": entry["code"], "description": entry["description"]})
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{"doctype": "FIRS Service Codes", "code": entry["code"], "description": entry["description"]}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Service Code records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Service Code Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Service Codes: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_country(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_country",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Country List started in background. You will be notified upon completion.")}


def _process_fetch_firs_country(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/countries"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			name = data.find("Name").text if data.find("Name") is not None else ""
			alpha2 = data.find("Alpha2").text if data.find("Alpha2") is not None else ""
			alpha3 = data.find("Alpha3").text if data.find("Alpha3") is not None else ""
			country_code = data.find("CountryCode").text if data.find("CountryCode") is not None else ""
			iso_code = data.find("ISO31662").text if data.find("ISO31662") is not None else ""
			region = data.find("Region").text if data.find("Region") is not None else ""
			sub_region = data.find("SubRegion").text if data.find("SubRegion") is not None else ""
			intermediate_region = data.find("IntermediateRegion").text if data.find("IntermediateRegion") is not None else ""
			region_code = data.find("RegionCode").text if data.find("RegionCode") is not None else ""
			sub_region_code = data.find("SubRegionCode").text if data.find("SubRegionCode") is not None else ""
			intermediate_region_code = data.find("IntermediateRegionCode").text if data.find("IntermediateRegionCode") is not None else ""

			entries.append(
				{
					"name": name,
					"alpha2": alpha2,
					"alpha3": alpha3,
					"country_code": country_code,
					"iso_code": iso_code,
					"region": region,
					"sub_region": sub_region,
					"intermediate_region": intermediate_region,
					"region_code": region_code,
					"sub_region_code": sub_region_code,
					"intermediate_region_code": intermediate_region_code,
				}
			)

		for entry in entries:
			if frappe.db.exists("Country", {"name": entry["name"]}):
				doc = frappe.get_doc("Country", entry["name"])
				doc.custom_alpha2 = entry["alpha2"]
				doc.custom_alpha3 = entry["alpha3"]
				doc.custom_countrycode = entry["country_code"]
				doc.custom_iso31662 = entry["iso_code"]
				doc.custom_region = entry["region"]
				doc.custom_subregion = entry["sub_region"]
				doc.custom_intermediateregion = entry["intermediate_region"]
				doc.custom_regioncode = entry["region_code"]
				doc.custom_subregioncode = entry["sub_region_code"]
				doc.custom_intermediateregioncode = entry["intermediate_region_code"]
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "Country",
						"country_name": entry["name"],
						"date_format": "dd-mm-yyyy",
						"time_format": "HH:mm:ss",
						"code": entry["alpha2"],
						"custom_alpha2": entry["alpha2"],
						"custom_alpha3": entry["alpha3"],
						"custom_countrycode": entry["country_code"],
						"custom_iso31662": entry["iso_code"],
						"custom_region": entry["region"],
						"custom_subregion": entry["sub_region"],
						"custom_intermediateregion": entry["intermediate_region"],
						"custom_regioncode": entry["region_code"],
						"custom_subregioncode": entry["sub_region_code"],
						"custom_intermediateregioncode": entry["intermediate_region_code"],
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Country records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Country Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Countries: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_states(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_states",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS State List started in background. You will be notified upon completion.")}


def _process_fetch_firs_states(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/states"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			name = data.find("Name").text if data.find("Name") is not None else ""
			code = data.find("Code").text if data.find("Code") is not None else ""
			entries.append({"name": name, "code": code})

		for entry in entries:
			if frappe.db.exists("FIRS State Code", {"name1": entry["name"], "code": entry["code"]}):
				doc = frappe.get_doc("FIRS State Code", {"name1": entry["name"], "code": entry["code"]})
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{"doctype": "FIRS State Code", "name1": entry["name"], "code": entry["code"]}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS State Code records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS State Codes Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS State Codes: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_local_government(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_local_government",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Local Government List started in background. You will be notified upon completion.")}


def _process_fetch_firs_local_government(company, user=None):
	try:
		company_doc = frappe.get_doc("Company", company)

		url = f"{company_doc.custom_base_url}/api/v1/invoice/resources/lgas"
		headers = {
			"Accept": "application/xml",
			"api-key": company_doc.custom_api_key,
			"api-secret": company_doc.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			name = data.find("Name").text if data.find("Name") is not None else ""
			code = data.find("Code").text if data.find("Code") is not None else ""
			statecode = data.find("StateCode").text if data.find("StateCode") is not None else ""
			entries.append({"name": name, "code": code, "statecode": statecode})

		for entry in entries:
			if frappe.db.exists(
				"FIRS Local Government",
				{"code": entry["code"], "name1": entry["name"], "statecode": entry["statecode"]},
			):
				doc = frappe.get_doc(
					"FIRS Local Government",
					{"code": entry["code"], "name1": entry["name"], "statecode": entry["statecode"]},
				)
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "FIRS Local Government",
						"name1": entry["name"],
						"code": entry["code"],
						"statecode": entry["statecode"],
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Local Government records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Local Governments Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Local Governments: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_firs_tax_exemption(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_firs_tax_exemption",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS VAT Exemption List started in background. You will be notified upon completion.")}


def _process_fetch_firs_tax_exemption(company, user=None):
	try:
		company_obj = frappe.get_doc("Company", company)

		url = f"{company_obj.custom_base_url}/api/v1/invoice/resources/vat-exemptions"
		headers = {
			"Accept": "application/xml",
			"api-key": company_obj.custom_api_key,
			"api-secret": company_obj.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			heading_no = data.find("HeadingNo").text if data.find("HeadingNo") is not None else ""
			harmonized_system_code = data.find("HarmonizedSystemCode").text if data.find("HarmonizedSystemCode") is not None else ""
			tariff_category = data.find("TariffCategory").text if data.find("TariffCategory") is not None else ""
			tariff = data.find("Tariff").text if data.find("Tariff") is not None else ""
			description = data.find("Description").text if data.find("Description") is not None else ""
			entries.append(
				{
					"heading_no": heading_no,
					"harmonized_system_code": harmonized_system_code,
					"tariff_category": tariff_category,
					"tariff": tariff,
					"description": description,
				}
			)

		for entry in entries:
			if frappe.db.exists(
				"FIRS VAT Exemptions",
				{
					"heading_no": entry["heading_no"],
					"harmonized_system_code": entry["harmonized_system_code"],
					"tariff_category": entry["tariff_category"],
					"tariff": entry["tariff"],
					"description": entry["description"],
				},
			):
				doc = frappe.get_doc(
					"FIRS VAT Exemptions",
					{
						"heading_no": entry["heading_no"],
						"harmonized_system_code": entry["harmonized_system_code"],
						"tariff_category": entry["tariff_category"],
						"tariff": entry["tariff"],
						"description": entry["description"],
					},
				)
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "FIRS VAT Exemptions",
						"heading_no": entry["heading_no"],
						"harmonized_system_code": entry["harmonized_system_code"],
						"tariff_category": entry["tariff_category"],
						"tariff": entry["tariff"],
						"description": entry["description"],
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS VAT Exemption records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS VAT Exemption Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS VAT Exemptions: {0}").format(str(e)), user=user)


@frappe.whitelist()
def fetch_unit_of_measurement_uom(company):
	frappe.enqueue(
		"nigeria_compliance_client.nigeria_compliance_client.hooks.utils._process_fetch_unit_of_measurement_uom",
		company=company,
		user=frappe.session.user,
		queue="long",
		timeout=3000,
		now=frappe.flags.in_test,
	)
	return {"status": "queued", "message": _("Fetching NRS Approved Unit of Measurement (UoM) started in background. You will be notified upon completion.")}


def _process_fetch_unit_of_measurement_uom(company, user=None):
	try:
		company_obj = frappe.get_doc("Company", company)

		url = f"{company_obj.custom_base_url}/api/v1/invoice/resources/invoice-quantity-codes"
		headers = {
			"Accept": "application/xml",
			"api-key": company_obj.custom_api_key,
			"api-secret": company_obj.custom_client_secret,
		}

		resp = requests.get(url, headers=headers, timeout=120)
		resp.raise_for_status()

		xml_data = resp.text
		root = ET.fromstring(xml_data)

		entries = []
		for data in root.findall("Data"):
			code_node = data.find("Code")
			name_node = data.find("Name")
			desc_node = data.find("Description")

			code = code_node.text.strip() if code_node is not None and code_node.text else ""
			uom_name = name_node.text.strip() if name_node is not None and name_node.text else ""
			description = desc_node.text.strip() if desc_node is not None and desc_node.text else ""

			entries.append(
				{
					"code": code,
					"uom_name": uom_name,
					"description": description,
				}
			)

		for entry in entries:
			if frappe.db.exists("FIRS UOM", entry["code"]):
				doc = frappe.get_doc("FIRS UOM", entry["code"])
				doc.uom_name = entry["uom_name"]
				doc.description = entry["description"] or ""
				doc.save(ignore_permissions=True)
			else:
				frappe.get_doc(
					{
						"doctype": "FIRS UOM",
						"code": entry["code"],
						"uom_name": entry["uom_name"],
						"description": entry["description"] or "",
					}
				).insert(ignore_permissions=True)

		frappe.db.commit()
		msg = _("{0} NRS Unit of Measurement (UoM) records processed and synced to Bridge site successfully.").format(len(entries))
		if user:
			frappe.publish_realtime("msgprint", msg, user=user)
	except Exception as e:
		frappe.log_error(message=frappe.get_traceback(), title="NRS Unit of Measure Fetch Error")
		if user:
			frappe.publish_realtime("msgprint", _("Error fetching NRS Unit of Measurement: {0}").format(str(e)), user=user)

@frappe.whitelist()
def validate_irn(invoicereference, company, irn):
	company = frappe.get_doc("Company", company)

	# POST to validate IRN
	url = f"{company.custom_base_url}/api/v1/invoice/irn/validate"
	headers = {
		"accept": "*/*",
		"Content-Type": "application/json",
		"x-api-key": company.custom_api_key,
		"x-api-secret": company.custom_client_secret,
	}

	json_payload = {
		"invoice_reference": invoicereference,
		"irn": irn,
		"business_id": company.custom_business_id,
	}

	response = requests.post(url, headers=headers, json=json_payload, timeout=30)
	message = {
		"status_code": response.status_code,
		"ok": response.ok,
	}

	return message

@frappe.whitelist()
def confirm_invoice(irn, company):
	company = frappe.get_doc("Company", company)

	# POST to confirm Invoice
	url = f"{company.custom_base_url}/api/v1/invoice/confirm/{irn}"
	headers = {
		"accept": "*/*",
		"Content-Type": "application/json",
		"x-api-key": company.custom_api_key,
		"x-api-secret": company.custom_client_secret,
	}
	response = requests.post(url, headers=headers, timeout=30)
	data = response.json()
	message = {
		"status_code": response.status_code,
		"issue_date": data.get("issue_date"),
		"due_date": data.get("due_date"),
		"sync_date": data.get("sync_date"),
		"payment_status": data.get("payment_status"),
		"transmitted": data.get("transmitted"),
		"delivered": data.get("delivered"),
	}

	return message

from erpnext.accounts.report.customer_ledger_summary.customer_ledger_summary import PartyLedgerSummaryReport
@frappe.whitelist()
def get_previous_outstannding_amount(customer):
    filters = {'company': frappe.defaults.get_user_default("Company"),
               'from_date': frappe.utils.now(),
               'to_date': frappe.utils.now(),
               'party': customer
            }
    args = {
        "party_type": "Customer",
        "naming_by": ["Selling Settings", "cust_master_name"],
    }
    data = PartyLedgerSummaryReport(filters).run(args)
    if len(data[1]) > 0:
        return data[1][0].get("closing_balance")