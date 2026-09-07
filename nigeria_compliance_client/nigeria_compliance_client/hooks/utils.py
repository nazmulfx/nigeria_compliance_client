import xml.etree.ElementTree as ET

import frappe
import requests


@frappe.whitelist()
def fetch_firs_invoice_type(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/invoice-types"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching Nigeria Revenue Service Invoice Types: {e!s}\nURL: {url}", title="Nigeria Revenue Service Invoice Fetch Error"
		)
		frappe.throw(f"Failed to fetch Nigeria Revenue Service Invoice Types: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="Nigeria Revenue Service XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from Nigeria Revenue Service server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		code = data.find("Code").text
		value = data.find("Value").text
		entries.append({"code": code, "value": value})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists("FIRS Invoice Type", {"code": entry["code"], "value": entry["value"]}):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{"doctype": "FIRS Invoice Type", "code": entry["code"], "value": entry["value"]}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_payment_means(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/payment-means"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Payment Means: {e!s}\nURL: {url}",
			title="NRS Payment Means Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Payment Means: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		code = data.find("Code").text
		value = data.find("Value").text
		entries.append({"code": code, "value": value})

	# Save All data to Doctype
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
			doc.save()
		else:
			frappe.get_doc(
				{
					"doctype": "Mode of Payment",
					"custom_code": entry["code"],
					"mode_of_payment": entry["value"],
					"type": payment_type,
				}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_tax_categories(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/tax-categories"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Tax Categories: {e!s}\nURL: {url}",
			title="NRS Tax Categories Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Tax Categories: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		code = data.find("Code").text
		value = data.find("Value").text
		try:
			percent = float(data.find("Percent").text)
		except (ValueError, TypeError):
			percent = 0.0
		entries.append({"code": code, "value": value, "percent": percent})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists("Tax Category", {"title": entry["code"], "custom_value": entry["value"]}):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{
					"doctype": "Tax Category",
					"title": entry["code"],
					"custom_value": entry["value"],
					"custom_percent": entry["percent"],
				}
			).insert()

		# Create Tax Account Head for each tax category
		if frappe.db.exists("Account", f"{entry['code']} - {company.abbr}"):
			account = frappe.get_doc("Account", f"{entry['code']} - {company.abbr}")
			account.tax_rate = entry["percent"]
			account.save()
		else:
			account = frappe.new_doc("Account")
			account.account_name = entry["code"]
			account.parent_account = f"Duties and Taxes - {company.abbr}"
			account.account_type = "Tax"
			account.tax_rate = entry["percent"]
			account.company = company.name
			account.is_group = 0
			account.save()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_currency(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/currencies"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Currency: {e!s}\nURL: {url}", title="NRS Currency Fetch Error"
		)
		frappe.throw(f"Failed to fetch NRS Currency: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
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

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists("Currency", {"name": entry["code"]}):
			# Data Already exists, update as FIRS Currency Format
			doc = frappe.get_doc("Currency", entry["code"])
			doc.custom_firs_currency_name = entry["currency_name"]
			doc.custom_symbol_native = entry["symbol_native"]
			doc.custom_rounding = entry["currency_rounding"]
			doc.custom_name_plural = entry["currency_name_plural"]
			if doc.symbol:
				pass
			else:
				doc.symbol = entry["symbol"]
			doc.save()
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
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_product_code(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/hs-codes"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Products Codes: {e!s}\nURL: {url}",
			title="NRS Products Codes Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Products Codes: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		hscode = data.find("Hscode").text
		description = data.find("Description").text
		entries.append({"hscode": hscode, "description": description})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists(
			"FIRS Products Codes", {"hscode": entry["hscode"], "description": entry["description"]}
		):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{
					"doctype": "FIRS Products Codes",
					"hscode": entry["hscode"],
					"description": entry["description"],
				}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_service_code(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/services-codes"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Service Codes: {e!s}\nURL: {url}",
			title="NRS Service Codes Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Service Codes: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		code = data.find("Code").text
		description = data.find("Description").text
		entries.append({"code": code, "description": description})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists(
			"FIRS Service Codes", {"code": entry["code"], "description": entry["description"]}
		):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{"doctype": "FIRS Service Codes", "code": entry["code"], "description": entry["description"]}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_country(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/countries"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Country: {e!s}\nURL: {url}", title="NRS Country Fetch Error"
		)
		frappe.throw(f"Failed to fetch NRS Country: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		name = data.find("Name").text
		alpha2 = data.find("Alpha2").text
		alpha3 = data.find("Alpha3").text
		country_code = data.find("CountryCode").text
		iso_code = data.find("ISO31662").text
		region = data.find("Region").text
		sub_region = data.find("SubRegion").text
		intermediate_region = data.find("IntermediateRegion").text
		region_code = data.find("RegionCode").text
		sub_region_code = data.find("SubRegionCode").text
		intermediate_region_code = data.find("IntermediateRegionCode").text

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

	# Save/Update All data to Doctype
	for entry in entries:
		if frappe.db.exists("Country", {"name": entry["name"]}):
			# Data Already exists, update as FIRS Currency Format
			doc = frappe.get_doc("Country", entry["name"])
			doc.custom_alpha2 = (entry["alpha2"],)
			doc.custom_alpha3 = (entry["alpha3"],)
			doc.custom_countrycode = (entry["country_code"],)
			doc.custom_iso31662 = (entry["iso_code"],)
			doc.custom_region = (entry["region"],)
			doc.custom_subregion = (entry["sub_region"],)
			doc.custom_intermediateregion = (entry["intermediate_region"],)
			doc.custom_regioncode = (entry["region_code"],)
			doc.custom_subregioncode = (entry["sub_region_code"],)
			doc.custom_intermediateregioncode = entry["intermediate_region_code"]
			doc.save()
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
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_states(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/states"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS State Codes: {e!s}\nURL: {url}",
			title="NRS State Codes Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS State Codes: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		name = data.find("Name").text
		code = data.find("Code").text
		entries.append({"name": name, "code": code})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists("FIRS State Code", {"name1": entry["name"], "code": entry["code"]}):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{"doctype": "FIRS State Code", "name1": entry["name"], "code": entry["code"]}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_local_government(company):
	company = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company.custom_base_url}/api/v1/invoice/resources/lgas"
	headers = {
		"Accept": "application/xml",
		"api-key": company.custom_api_key,
		"api-secret": company.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Local Governments: {e!s}\nURL: {url}",
			title="NRS Local Governments Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Local Governments: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		name = data.find("Name").text
		code = data.find("Code").text
		statecode = data.find("StateCode").text
		entries.append({"name": name, "code": code, "statecode": statecode})

	# Save All data to Doctype
	for entry in entries:
		if frappe.db.exists(
			"FIRS Local Government",
			{"code": entry["code"], "name1": entry["name"], "statecode": entry["statecode"]},
		):
			# Data Already Created
			pass
		else:
			frappe.get_doc(
				{
					"doctype": "FIRS Local Government",
					"name1": entry["name"],
					"code": entry["code"],
					"statecode": entry["statecode"],
				}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}


@frappe.whitelist()
def fetch_firs_tax_exemption(company):
	company_obj = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company_obj.custom_base_url}/api/v1/invoice/resources/vat-exemptions"
	headers = {
		"Accept": "application/xml",
		"api-key": company_obj.custom_api_key,
		"api-secret": company_obj.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS VAT Exemption: {e!s}\nURL: {url}",
			title="NRS VAT Exemption Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS VAT Exemption: {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convent XML Data to Dict data
	entries = []
	for data in root.findall("Data"):
		heading_no = data.find("HeadingNo").text
		harmonized_system_code = data.find("HarmonizedSystemCode").text
		tariff_category = data.find("TariffCategory").text
		tariff = data.find("Tariff").text
		description = data.find("Description").text
		entries.append(
			{
				"heading_no": heading_no,
				"harmonized_system_code": harmonized_system_code,
				"tariff_category": tariff_category,
				"tariff": tariff,
				"description": description,
			}
		)

	# Save All data to Doctype
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
			# Data Already Created
			pass
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
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}

@frappe.whitelist()
def fetch_unit_of_measurement_uom(company):
	company_obj = frappe.get_doc("Company", company)

	# Fetch Firs Invoice Data
	url = f"{company_obj.custom_base_url}/api/v1/invoice/resources/invoice-quantity-codes"
	headers = {
		"Accept": "application/xml",
		"api-key": company_obj.custom_api_key,
		"api-secret": company_obj.custom_client_secret,
	}

	try:
		resp = requests.get(url, headers=headers, timeout=30)
		resp.raise_for_status()
	except requests.exceptions.RequestException as e:
		frappe.log_error(
			message=f"Error fetching NRS Unit of Measure (UoM): {e!s}\nURL: {url}",
			title="NRS Unit of Measure (UoM) Fetch Error",
		)
		frappe.throw(f"Failed to fetch NRS Unit of Measure (UoM): {e!s}")

	try:
		xml_data = resp.text
		root = ET.fromstring(xml_data)
	except ET.ParseError as e:
		frappe.log_error(
			message=f"XML parsing error: {e!s}\nResponse Text:\n{resp.text}", title="NRS XML Parse Error"
		)
		frappe.throw("Failed to parse XML response from NRS server.")

	# Convert XML Data to Dict data
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

	# Save/Update All data to FIRS UOM Doctype
	for entry in entries:
		if frappe.db.exists("FIRS UOM", entry["code"]):
			doc = frappe.get_doc("FIRS UOM", entry["code"])
			doc.uom_name = entry["uom_name"]
			doc.description = entry["description"] or ""
			doc.save()
		else:
			frappe.get_doc(
				{
					"doctype": "FIRS UOM",
					"code": entry["code"],
					"uom_name": entry["uom_name"],
					"description": entry["description"] or "",
				}
			).insert()

	frappe.db.commit()

	return {"status": "success", "message": f"{len(entries)} records processed successfully."}

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