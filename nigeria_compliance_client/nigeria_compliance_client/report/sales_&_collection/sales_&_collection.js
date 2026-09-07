// Copyright (c) 2026, Nazmul Hossain and contributors
// For license information, please see license.txt

frappe.query_reports["Sales & Collection"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		// {
		// 	fieldname: "pos_profile",
		// 	label: __("POS Profile"),
		// 	fieldtype: "Link",
		// 	options: "POS Profile",
		// },
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "show_collection_payment",
			label: __("Show Collection by Payment Entry"),
			fieldtype: "Check",
			default: 1,
		},
	],
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.is_payment_entry && value) {
			value = `<span style="color: #2563eb; font-weight: bold;">${value}</span>`;
			value = value.replace(/<a /g, '<a style="color: #2563eb !important; font-weight: bold;" ');
		} else if (data && data.bold) {
			value = value.bold();
		}
		return value;
	},
};
