from __future__ import annotations

import frappe


def ensure_company(
	company_name: str,
	abbr: str | None = None,
	country: str = "Pakistan",
	currency: str = "PKR",
	set_global_defaults: bool = True,
):
	"""Create demo company if missing using existing chart template.

	This function is intended to be called via:
	bench --site <site> execute erpnext.seed.demo_setup.ensure_company --kwargs "{...}"
	"""

	if frappe.db.exists("Company", company_name):
		return {"created": False, "company": company_name, "reason": "already_exists"}

	if not abbr:
		abbr = "".join([c for c in company_name.upper() if c.isalpha()][:4]) or "DEMO"

	if not frappe.db.exists("Currency", currency):
		frappe.throw(f"Currency not found: {currency}")

	if not frappe.db.exists("Country", country):
		frappe.throw(f"Country not found: {country}")

	# Reuse chart template from first company if available, fallback to Standard.
	existing_company_name = frappe.get_all("Company", pluck="name", limit=1)
	chart_template = None
	if existing_company_name:
		existing_company = frappe.get_doc("Company", existing_company_name[0])
		chart_template = existing_company.get("chart_of_accounts")

	doc = frappe.new_doc("Company")
	doc.company_name = company_name
	doc.abbr = abbr
	doc.enable_perpetual_inventory = 1
	doc.default_currency = currency
	doc.country = country
	doc.create_chart_of_accounts_based_on = "Standard Template"
	if chart_template:
		doc.chart_of_accounts = chart_template

	doc.insert(ignore_permissions=True)

	if set_global_defaults:
		frappe.db.set_single_value("Global Defaults", "default_company", doc.name)
		frappe.db.set_single_value("Global Defaults", "default_currency", currency)
		frappe.db.set_single_value("Global Defaults", "country", country)
		frappe.db.set_default("company", doc.name)

	frappe.db.commit()
	return {"created": True, "company": doc.name, "abbr": abbr}
