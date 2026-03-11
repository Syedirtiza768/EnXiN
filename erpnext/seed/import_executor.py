from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import frappe


def _read_csv(path: Path):
	with path.open("r", encoding="utf-8") as handle:
		return list(csv.DictReader(handle))


def _ensure_exists(doctype: str, value: str):
	if not value:
		return

	def _ensure_tree_record(dt: str, title_field: str, parent_field: str, root_name: str):
		if frappe.db.exists(dt, value) or frappe.db.exists(dt, {title_field: value}):
			return

		# Some fresh sites can miss expected tree roots if setup did not run fully.
		if not frappe.db.exists(dt, root_name) and not frappe.db.exists(dt, {title_field: root_name}):
			root_doc = frappe.get_doc({
				"doctype": dt,
				title_field: root_name,
				"is_group": 1,
			})
			root_doc.insert(ignore_permissions=True)

		doc = frappe.get_doc({
			"doctype": dt,
			title_field: value,
			parent_field: root_name,
			"is_group": 0,
		})
		doc.insert(ignore_permissions=True)

	# Handle key setup doctypes with explicit naming fields.
	if doctype == "Customer Group":
		_ensure_tree_record("Customer Group", "customer_group_name", "parent_customer_group", "All Customer Groups")
		return

	if doctype == "Supplier Group":
		_ensure_tree_record("Supplier Group", "supplier_group_name", "parent_supplier_group", "All Supplier Groups")
		return

	if doctype == "Territory":
		_ensure_tree_record("Territory", "territory_name", "parent_territory", "All Territories")
		return

	if not frappe.db.exists(doctype, value):
		doc = frappe.new_doc(doctype)
		if "name" in doc.meta.get_valid_columns():
			doc.name = value
		doc.insert(ignore_permissions=True)


def _safe_insert(doc):
	try:
		doc.insert(ignore_permissions=True)
		return True, None
	except Exception:
		return False, frappe.get_traceback()


def _upsert_simple(doctype: str, rows, key_field: str, field_map: dict[str, str] | None = None):
	inserted = 0
	skipped = 0
	errors = []
	field_map = field_map or {}

	for row in rows:
		key = row.get(key_field)
		if not key:
			skipped += 1
			continue

		if frappe.db.exists(doctype, {key_field: key}):
			skipped += 1
			continue

		doc = frappe.new_doc(doctype)
		for src, val in row.items():
			if src in ("name",):
				continue
			if src not in doc.meta.get_valid_columns():
				mapped = field_map.get(src)
				if not mapped:
					continue
				src = mapped
			if src in doc.meta.get_valid_columns() and val != "":
				doc.set(src, val)

		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": doctype, "key": key, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_addresses(rows):
	inserted = 0
	skipped = 0
	errors = []

	for row in rows:
		name = row.get("name")
		if name and frappe.db.exists("Address", name):
			skipped += 1
			continue

		doc = frappe.new_doc("Address")
		doc.address_title = row.get("address_title")
		doc.address_type = row.get("address_type")
		doc.address_line1 = row.get("address_line1")
		doc.city = row.get("city")
		doc.country = row.get("country")

		link_spec = row.get("links", "")
		if link_spec and "::" in link_spec:
			link_doctype, link_name = link_spec.split("::", 1)
			doc.append(
				"links",
				{
					"link_doctype": link_doctype,
					"link_name": link_name,
				},
			)

		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Address", "key": row.get("name"), "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_sales_orders(so_rows, soi_rows):
	items_by_parent = defaultdict(list)
	for row in soi_rows:
		items_by_parent[row.get("parent")].append(row)

	inserted = 0
	skipped = 0
	errors = []

	for row in so_rows:
		name = row.get("name")
		if name and frappe.db.exists("Sales Order", name):
			skipped += 1
			continue

		doc = frappe.new_doc("Sales Order")
		doc.naming_series = row.get("naming_series") or "SO-.YYYY.-"
		doc.customer = row.get("customer")
		doc.transaction_date = row.get("transaction_date")
		doc.delivery_date = row.get("delivery_date")
		doc.company = row.get("company")

		for item in items_by_parent.get(name, []):
			doc.append(
				"items",
				{
					"item_code": item.get("item_code"),
					"qty": item.get("qty"),
					"uom": item.get("uom"),
					"warehouse": item.get("warehouse") or None,
					"rate": item.get("rate"),
				},
			)

		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Sales Order", "key": name, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_item_prices(rows):
	inserted = 0
	skipped = 0
	errors = []

	for row in rows:
		filters = {
			"item_code": row.get("item_code"),
			"price_list": row.get("price_list"),
			"uom": row.get("uom"),
			"customer": row.get("customer") or "",
			"supplier": row.get("supplier") or "",
		}
		if frappe.db.exists("Item Price", filters):
			skipped += 1
			continue

		doc = frappe.new_doc("Item Price")
		doc.item_code = row.get("item_code")
		doc.price_list = row.get("price_list")
		doc.uom = row.get("uom")
		doc.price_list_rate = row.get("price_list_rate")
		doc.currency = row.get("currency") or "PKR"
		if row.get("customer"):
			doc.customer = row.get("customer")
		if row.get("supplier"):
			doc.supplier = row.get("supplier")

		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Item Price", "key": filters, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _auto_create_company(name: str, country: str = "Pakistan", currency: str = "PKR"):
	"""Create a minimal Company record so the seed import can proceed."""
	if frappe.db.exists("Company", name):
		return

	# Pre-create setup records that Company.on_update expects to exist.
	for wh_type in ("Transit",):
		if not frappe.db.exists("Warehouse Type", wh_type):
			frappe.get_doc({"doctype": "Warehouse Type", "name": wh_type}).insert(ignore_permissions=True)

	abbr = "".join(w[0] for w in name.split() if w).upper()[:4]
	doc = frappe.get_doc({
		"doctype": "Company",
		"company_name": name,
		"abbr": abbr,
		"country": country,
		"default_currency": currency,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()


def _resolve_company(seed_company: str, company_override: str | None,
                     country: str = "Pakistan", currency: str = "PKR"):
	if company_override:
		if not frappe.db.exists("Company", company_override):
			_auto_create_company(company_override, country, currency)
		return company_override

	if frappe.db.exists("Company", seed_company):
		return seed_company

	existing = frappe.get_all("Company", pluck="name")
	if len(existing) == 1:
		return existing[0]

	frappe.throw(
		f"Seed company '{seed_company}' not found and no unambiguous mapping exists. "
		"Pass company_override in bench execute kwargs."
	)


def import_seed(seed_dir: str = "seed_output", company_override: str | None = None):
	"""Import generated seed CSVs into current site using Frappe ORM.

	Run with:
	bench --site <site> execute erpnext.seed.import_executor.import_seed --kwargs "{'seed_dir':'/workspace/seed_output'}"
	"""

	base = Path(seed_dir)
	if not base.exists():
		frappe.throw(f"Seed directory not found: {seed_dir}")

	# Ensure baseline refs expected by generated CSVs.
	_ensure_exists("Customer Group", "Commercial")
	_ensure_exists("Supplier Group", "Services")
	_ensure_exists("Supplier Group", "Raw Material")
	_ensure_exists("Territory", "Pakistan")

	report = {}

	company_rows = _read_csv(base / "Company.csv")
	warehouse_rows = _read_csv(base / "Warehouse.csv")
	department_rows = _read_csv(base / "Department.csv")
	supplier_rows = _read_csv(base / "Supplier.csv")
	customer_rows = _read_csv(base / "Customer.csv")
	item_group_rows = _read_csv(base / "Item_Group.csv")
	brand_rows = _read_csv(base / "Brand.csv")
	item_rows = _read_csv(base / "Item.csv")
	item_price_rows = _read_csv(base / "Item_Price.csv")
	so_rows = _read_csv(base / "Sales_Order.csv")
	soi_rows = _read_csv(base / "Sales_Order_Item.csv")
	issue_rows = _read_csv(base / "Issue.csv")
	address_rows = _read_csv(base / "Address.csv")

	seed_company = company_rows[0].get("name") if company_rows else ""
	seed_country = company_rows[0].get("country", "Pakistan") if company_rows else "Pakistan"
	seed_currency = company_rows[0].get("default_currency", "PKR") if company_rows else "PKR"
	target_company = _resolve_company(seed_company, company_override, seed_country, seed_currency)

	for row in warehouse_rows:
		if row.get("company") == seed_company:
			row["company"] = target_company
	for row in department_rows:
		if row.get("company") == seed_company:
			row["company"] = target_company
	for row in so_rows:
		if row.get("company") == seed_company:
			row["company"] = target_company

	report["Company Mapping"] = {"seed_company": seed_company, "target_company": target_company}

	# Company creation is intentionally skipped by default because ERPNext sites
	# usually already have chart-of-accounts bootstrapped for an existing company.
	report["Company"] = {"inserted": 0, "skipped": len(company_rows), "errors": []}
	report["Department"] = _upsert_simple("Department", department_rows, "department_name")
	report["Warehouse"] = _upsert_simple("Warehouse", warehouse_rows, "name")
	report["Supplier"] = _upsert_simple("Supplier", supplier_rows, "supplier_name")
	report["Customer"] = _upsert_simple("Customer", customer_rows, "customer_name")
	report["Item Group"] = _upsert_simple("Item Group", item_group_rows, "item_group_name")
	report["Brand"] = _upsert_simple("Brand", brand_rows, "brand")
	report["Item"] = _upsert_simple("Item", item_rows, "item_code")
	report["Item Price"] = _import_item_prices(item_price_rows)
	report["Issue"] = _upsert_simple("Issue", issue_rows, "subject")
	report["Address"] = _import_addresses(address_rows)
	report["Sales Order"] = _import_sales_orders(so_rows, soi_rows)

	# Optional sidecar data for audit/analytics only.
	report["Waste Events JSON"] = {
		"loaded": (base / "waste_collection_events.json").exists(),
		"rows": len(json.loads((base / "waste_collection_events.json").read_text(encoding="utf-8")).get("events", []))
		if (base / "waste_collection_events.json").exists()
		else 0,
	}
	report["Financial Events JSON"] = {
		"loaded": (base / "financial_events.json").exists(),
		"rows": len(json.loads((base / "financial_events.json").read_text(encoding="utf-8")).get("entries", []))
		if (base / "financial_events.json").exists()
		else 0,
	}

	out_path = base / "frappe_import_report.json"
	out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
	frappe.db.commit()
	return report
