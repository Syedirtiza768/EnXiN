from __future__ import annotations

import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import frappe


def _log(msg: str):
	"""Print progress and flush immediately so Docker logs show it in real time."""
	print(msg, flush=True)


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


def _safe_insert(doc, skip_validation=False):
	try:
		if skip_validation:
			doc.flags.ignore_validate = True
			doc.flags.ignore_links = True
			doc.flags.ignore_mandatory = True
		doc.insert(ignore_permissions=True)
		return True, None
	except Exception:
		return False, frappe.get_traceback()


def _import_cost_centers(rows, target_company=None, target_abbr=None):
	"""Tree-aware Cost Center importer — creates parents before children."""
	inserted = 0
	skipped = 0
	errors = []

	# Find existing company root cost center (created by Company.on_update)
	company_root = None
	if target_company:
		# First try to find an existing group root
		company_root = frappe.db.get_value(
			"Cost Center",
			{"company": target_company, "is_group": 1, "parent_cost_center": ("in", ["", None])},
			"name",
		) or frappe.db.get_value(
			"Cost Center",
			{"company": target_company, "is_group": 1},
			"name",
		)
		# If no group root, find any root and force it to be a group
		if not company_root:
			any_root = frappe.db.get_value(
				"Cost Center",
				{"company": target_company, "parent_cost_center": ("in", ["", None])},
				"name",
			) or frappe.db.get_value(
				"Cost Center",
				{"company": target_company},
				"name",
			)
			if any_root:
				frappe.db.set_value("Cost Center", any_root, "is_group", 1)
				company_root = any_root

	for row in rows:
		name = row.get("cost_center_name")
		company = row.get("company") or target_company
		if not name:
			skipped += 1
			continue
		# Cost Center name in ERPNext includes company abbreviation
		if frappe.db.exists("Cost Center", {"cost_center_name": name, "company": company}):
			skipped += 1
			continue
		try:
			doc = frappe.new_doc("Cost Center")
			doc.cost_center_name = name
			doc.company = company
			parent = row.get("parent_cost_center", "")
			if parent:
				# Check if the referenced parent exists; if not, use company root
				if frappe.db.exists("Cost Center", parent):
					doc.parent_cost_center = parent
				elif company_root:
					doc.parent_cost_center = company_root
			elif company_root:
				# No parent specified — nest under existing company root
				doc.parent_cost_center = company_root
			doc.is_group = row.get("is_group", 0)
			doc.insert(ignore_permissions=True)
			inserted += 1
		except Exception:
			errors.append({"doctype": "Cost Center", "key": name, "error": frappe.get_traceback()})
	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _upsert_simple(doctype: str, rows, key_field: str, field_map: dict[str, str] | None = None,
				   skip_validation: bool = False):
	inserted = 0
	skipped = 0
	errors = []
	field_map = field_map or {}

	for row in rows:
		key = row.get(key_field)
		if not key:
			skipped += 1
			continue

		# Check by field filter first, then fallback to name-based lookup.
		# This handles doctypes where existing records have name set but the
		# title field is empty (e.g. Designation created by setup wizard).
		if frappe.db.exists(doctype, {key_field: key}) or frappe.db.exists(doctype, key):
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

		ok, err = _safe_insert(doc, skip_validation=skip_validation)
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
		# Force the explicit name from CSV so that other doctypes (Delivery Stop)
		# can reference the address by this deterministic name.
		if name:
			doc.name = name
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


def _import_sales_orders(so_rows, soi_rows, company_currency: str = "PKR"):
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
		# Force currency to company default to avoid missing Currency Exchange records.
		doc.currency = company_currency
		doc.conversion_rate = 1.0

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

		ok, err = _safe_insert(doc, skip_validation=True)
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
		# Use only core fields for dedup â€” customer/supplier can be NULL in DB
		# which doesn't match an empty-string filter, causing false misses.
		dedup_filters = {
			"item_code": row.get("item_code"),
			"price_list": row.get("price_list"),
			"uom": row.get("uom") or None,
		}
		if frappe.db.exists("Item Price", dedup_filters):
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
			errors.append({"doctype": "Item Price", "key": dedup_filters, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_quotations(q_rows, qi_rows, company_currency: str = "PKR"):
	items_by_parent = defaultdict(list)
	for row in qi_rows:
		items_by_parent[row.get("parent")].append(row)

	inserted = 0
	skipped = 0
	errors = []

	for row in q_rows:
		name = row.get("name")
		if name and frappe.db.exists("Quotation", name):
			skipped += 1
			continue

		doc = frappe.new_doc("Quotation")
		doc.naming_series = row.get("naming_series") or "QTN-.YYYY.-"
		doc.quotation_to = row.get("quotation_to") or "Customer"
		doc.party_name = row.get("party_name")
		doc.transaction_date = row.get("transaction_date")
		doc.valid_till = row.get("valid_till")
		doc.company = row.get("company")
		doc.currency = company_currency
		doc.conversion_rate = 1.0

		for item in items_by_parent.get(name, []):
			doc.append(
				"items",
				{
					"item_code": item.get("item_code"),
					"qty": item.get("qty"),
					"uom": item.get("uom"),
					"rate": item.get("rate"),
				},
			)

		ok, err = _safe_insert(doc, skip_validation=True)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Quotation", "key": name, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_purchase_orders(po_rows, poi_rows, company_currency: str = "PKR"):
	items_by_parent = defaultdict(list)
	for row in poi_rows:
		items_by_parent[row.get("parent")].append(row)

	inserted = 0
	skipped = 0
	errors = []

	for row in po_rows:
		name = row.get("name")
		if name and frappe.db.exists("Purchase Order", name):
			skipped += 1
			continue

		doc = frappe.new_doc("Purchase Order")
		doc.naming_series = row.get("naming_series") or "PO-.YYYY.-"
		doc.supplier = row.get("supplier")
		doc.transaction_date = row.get("transaction_date")
		doc.schedule_date = row.get("schedule_date")
		doc.company = row.get("company")
		doc.currency = company_currency
		doc.conversion_rate = 1.0

		for item in items_by_parent.get(name, []):
			doc.append(
				"items",
				{
					"item_code": item.get("item_code"),
					"qty": item.get("qty"),
					"uom": item.get("uom"),
					"warehouse": item.get("warehouse") or None,
					"rate": item.get("rate"),
					"schedule_date": item.get("schedule_date"),
				},
			)

		ok, err = _safe_insert(doc, skip_validation=True)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Purchase Order", "key": name, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_stock_entries(se_rows, sed_rows):
	items_by_parent = defaultdict(list)
	for row in sed_rows:
		items_by_parent[row.get("parent")].append(row)

	inserted = 0
	skipped = 0
	errors = []

	for row in se_rows:
		name = row.get("name")
		if name and frappe.db.exists("Stock Entry", name):
			skipped += 1
			continue

		doc = frappe.new_doc("Stock Entry")
		doc.naming_series = row.get("naming_series") or "STE-.YYYY.-"
		doc.stock_entry_type = row.get("stock_entry_type") or row.get("purpose") or "Material Receipt"
		doc.posting_date = row.get("posting_date")
		doc.company = row.get("company")

		for item in items_by_parent.get(name, []):
			child = {
				"item_code": item.get("item_code"),
				"qty": item.get("qty"),
				"uom": item.get("uom"),
				"basic_rate": item.get("basic_rate"),
				"allow_zero_valuation_rate": 0,
			}
			if item.get("t_warehouse"):
				child["t_warehouse"] = item["t_warehouse"]
			if item.get("s_warehouse"):
				child["s_warehouse"] = item["s_warehouse"]
			doc.append("items", child)

		ok, err = _safe_insert(doc, skip_validation=True)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Stock Entry", "key": name, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_with_children(doctype, parent_rows, child_rows, child_fieldname,
						  extra_parent_cb=None, skip_validation=False):
	"""Generic importer for parent-child doctypes."""
	items_by_parent = defaultdict(list)
	for row in child_rows:
		items_by_parent[row.get("parent")].append(row)

	inserted = 0
	skipped = 0
	errors = []

	for row in parent_rows:
		name = row.get("name")
		if name and frappe.db.exists(doctype, name):
			skipped += 1
			continue

		doc = frappe.new_doc(doctype)
		valid_cols = set(doc.meta.get_valid_columns())
		for k, v in row.items():
			if k == "name" or not v:
				continue
			if k in valid_cols:
				doc.set(k, v)

		if extra_parent_cb:
			extra_parent_cb(doc, row)

		for child_row in items_by_parent.get(name, []):
			child_dict = {k: v for k, v in child_row.items()
						  if k not in ("parent", "parenttype", "parentfield", "") and v}
			doc.append(child_fieldname, child_dict)

		ok, err = _safe_insert(doc, skip_validation=skip_validation)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": doctype, "key": name, "error": err})

	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_contacts(rows):
	inserted = 0
	skipped = 0
	errors = []
	for row in rows:
		dup = {"first_name": row.get("first_name"), "email_id": row.get("email_id")}
		if frappe.db.exists("Contact", dup):
			skipped += 1
			continue
		doc = frappe.new_doc("Contact")
		for f in ("first_name", "last_name", "email_id", "phone", "mobile_no", "company_name"):
			if row.get(f):
				doc.set(f, row[f])
		if row.get("link_doctype") and row.get("link_name"):
			doc.append("links", {"link_doctype": row["link_doctype"], "link_name": row["link_name"]})
		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Contact", "key": str(dup), "error": err})
	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_holiday_lists(hl_rows, h_rows):
	holidays_by_list = defaultdict(list)
	for row in h_rows:
		holidays_by_list[row.get("holiday_list")].append(row)

	inserted = 0
	skipped = 0
	errors = []
	for row in hl_rows:
		name = row.get("holiday_list_name")
		if name and frappe.db.exists("Holiday List", name):
			skipped += 1
			continue
		doc = frappe.new_doc("Holiday List")
		doc.holiday_list_name = name
		doc.from_date = row.get("from_date")
		doc.to_date = row.get("to_date")
		doc.company = row.get("company")
		for h in holidays_by_list.get(name, []):
			doc.append("holidays", {
				"holiday_date": h.get("holiday_date"),
				"description": h.get("description"),
			})
		ok, err = _safe_insert(doc)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": "Holiday List", "key": name, "error": err})
	return {"inserted": inserted, "skipped": skipped, "errors": errors}


def _import_bulk(doctype, rows, skip_validation=False):
	"""Import rows without dedup - for doctypes without natural unique keys."""
	inserted = 0
	errors = []
	for row in rows:
		doc = frappe.new_doc(doctype)
		valid_cols = set(doc.meta.get_valid_columns())
		for k, v in row.items():
			if k == "name" or not v:
				continue
			if k in valid_cols:
				doc.set(k, v)
		ok, err = _safe_insert(doc, skip_validation=skip_validation)
		if ok:
			inserted += 1
		else:
			errors.append({"doctype": doctype, "key": str(row)[:100], "error": err})
	return {"inserted": inserted, "skipped": 0, "errors": errors}


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
	"""Import comprehensive seed CSVs into current site using Frappe ORM."""

	base = Path(seed_dir)
	if not base.exists():
		frappe.throw(f"Seed directory not found: {seed_dir}")

	# Helper to read CSV if it exists
	def _csv(name):
		p = base / name
		return _read_csv(p) if p.exists() else []

	# ── Read all CSV files ──
	company_rows = _csv("Company.csv")
	branch_rows = _csv("Branch.csv")
	department_rows = _csv("Department.csv")
	designation_rows = _csv("Designation.csv")
	warehouse_rows = _csv("Warehouse.csv")
	cost_center_rows = _csv("Cost_Center.csv")
	customer_group_rows = _csv("Customer_Group.csv")
	supplier_group_rows = _csv("Supplier_Group.csv")
	territory_rows = _csv("Territory.csv")
	item_group_rows = _csv("Item_Group.csv")
	brand_rows = _csv("Brand.csv")
	customer_rows = _csv("Customer.csv")
	supplier_rows = _csv("Supplier.csv")
	item_rows = _csv("Item.csv")
	item_price_rows = _csv("Item_Price.csv")
	employee_rows = _csv("Employee.csv")
	vehicle_rows = _csv("Vehicle.csv")
	driver_rows = _csv("Driver.csv")
	holiday_list_rows = _csv("Holiday_List.csv")
	holiday_rows = _csv("Holiday.csv")
	address_rows = _csv("Address.csv")
	contact_rows = _csv("Contact.csv")
	lead_rows = _csv("Lead.csv")
	opportunity_rows = _csv("Opportunity.csv")
	opportunity_item_rows = _csv("Opportunity_Item.csv")
	contract_rows = _csv("Contract.csv")
	quotation_rows = _csv("Quotation.csv")
	quotation_item_rows = _csv("Quotation_Item.csv")
	so_rows = _csv("Sales_Order.csv")
	soi_rows = _csv("Sales_Order_Item.csv")
	po_rows = _csv("Purchase_Order.csv")
	poi_rows = _csv("Purchase_Order_Item.csv")
	mr_rows = _csv("Material_Request.csv")
	mri_rows = _csv("Material_Request_Item.csv")
	pr_rows = _csv("Purchase_Receipt.csv")
	pri_rows = _csv("Purchase_Receipt_Item.csv")
	stock_entry_rows = _csv("Stock_Entry.csv")
	stock_entry_detail_rows = _csv("Stock_Entry_Detail.csv")
	dn_rows = _csv("Delivery_Note.csv")
	dni_rows = _csv("Delivery_Note_Item.csv")
	si_rows = _csv("Sales_Invoice.csv")
	sii_rows = _csv("Sales_Invoice_Item.csv")
	pi_rows = _csv("Purchase_Invoice.csv")
	pii_rows = _csv("Purchase_Invoice_Item.csv")
	issue_rows = _csv("Issue.csv")
	project_rows = _csv("Project.csv")
	task_rows = _csv("Task.csv")
	mv_rows = _csv("Maintenance_Visit.csv")
	mvp_rows = _csv("Maintenance_Visit_Purpose.csv")
	qi_rows = _csv("Quality_Inspection.csv")
	dt_rows = _csv("Delivery_Trip.csv")
	ds_rows = _csv("Delivery_Stop.csv")
	ms_rows = _csv("Maintenance_Schedule.csv")
	msi_rows = _csv("Maintenance_Schedule_Item.csv")

	# ── Resolve company ──
	seed_company = company_rows[0].get("name") if company_rows else ""
	seed_abbr = company_rows[0].get("abbr", "") if company_rows else ""
	seed_country = company_rows[0].get("country", "Pakistan") if company_rows else "Pakistan"
	seed_currency = company_rows[0].get("default_currency", "PKR") if company_rows else "PKR"
	target_company = _resolve_company(seed_company, company_override, seed_country, seed_currency)
	target_abbr = frappe.db.get_value("Company", target_company, "abbr") or ""

	def _remap_wh(val):
		if not val or not seed_abbr or not target_abbr or seed_abbr == target_abbr:
			return val
		return val.replace(f" - {seed_abbr}", f" - {target_abbr}")

	# ── Remap company & warehouse across all rows ──
	all_company_rows = [
		warehouse_rows, department_rows, cost_center_rows, employee_rows,
		so_rows, quotation_rows, po_rows, stock_entry_rows,
		mr_rows, pr_rows, dn_rows, si_rows, pi_rows,
		project_rows, task_rows, mv_rows, qi_rows,
		lead_rows, opportunity_rows, holiday_list_rows,
		dt_rows, ms_rows,
	]
	for rows_list in all_company_rows:
		for row in rows_list:
			if row.get("company") == seed_company:
				row["company"] = target_company

	for row in warehouse_rows:
		row["name"] = _remap_wh(row.get("name", ""))

	wh_fields = [
		(soi_rows, ["warehouse"]),
		(poi_rows, ["warehouse"]),
		(stock_entry_detail_rows, ["t_warehouse", "s_warehouse"]),
		(mri_rows, ["warehouse"]),
		(pri_rows, ["warehouse"]),
		(dni_rows, ["warehouse"]),
		(pii_rows, ["warehouse"]),
	]
	for rows_list, fields in wh_fields:
		for row in rows_list:
			for fld in fields:
				row[fld] = _remap_wh(row.get(fld, ""))

	for row in cost_center_rows:
		row["parent_cost_center"] = _remap_wh(row.get("parent_cost_center", ""))

	# Department names in ERPNext include company abbreviation (e.g. "Waste Operations - GBCD").
	# We resolve these dynamically from the DB after department import (see below).

	report = {}
	report["Company Mapping"] = {
		"seed_company": seed_company, "target_company": target_company,
		"seed_abbr": seed_abbr, "target_abbr": target_abbr,
	}

	# ── Pre-create baseline references ──
	_log("  Pre-creating baseline references ...")
	target_currency = frappe.db.get_value("Company", target_company, "default_currency") or "PKR"
	for cg in ("Commercial", "Institutional", "Government"):
		_ensure_exists("Customer Group", cg)
	for sg in ("Services", "Raw Material", "Equipment Vendor", "Fuel Supplier", "Vehicle Parts", "IT Services", "Insurance"):
		_ensure_exists("Supplier Group", sg)
	_ensure_exists("Territory", "Pakistan")
	for uom_name in ("Nos", "Kg", "Unit", "Pair", "Box", "Set", "Ltr"):
		if not frappe.db.exists("UOM", uom_name):
			frappe.get_doc({"doctype": "UOM", "uom_name": uom_name}).insert(ignore_permissions=True)	# Ensure Stock Entry Types exist
	for set_name in ("Material Receipt", "Material Issue", "Material Transfer"):
		if not frappe.db.exists("Stock Entry Type", set_name):
			frappe.get_doc({"doctype": "Stock Entry Type", "name": set_name, "purpose": set_name}).insert(ignore_permissions=True)
	# Ensure Price Lists exist
	for pl_name in ("Standard Selling", "Standard Buying"):
		if not frappe.db.exists("Price List", pl_name):
			frappe.get_doc({"doctype": "Price List", "price_list_name": pl_name,
				"selling": 1 if "Selling" in pl_name else 0,
				"buying": 1 if "Buying" in pl_name else 0,
				"currency": target_currency}).insert(ignore_permissions=True)
	# Pre-create Sales Person records needed by Maintenance Visit Purposes
	sp_root = "Sales Team"
	if not frappe.db.exists("Sales Person", sp_root):
		try:
			frappe.get_doc({"doctype": "Sales Person", "sales_person_name": sp_root, "is_group": 1}).insert(ignore_permissions=True)
		except Exception:
			pass
	sp_names = set()
	for row in mvp_rows:
		sp = row.get("service_person")
		if sp:
			sp_names.add(sp)
	for sp in sp_names:
		if not frappe.db.exists("Sales Person", sp) and not frappe.db.exists("Sales Person", {"sales_person_name": sp}):
			try:
				doc = frappe.new_doc("Sales Person")
				doc.sales_person_name = sp
				doc.parent_sales_person = sp_root
				doc.is_group = 0
				doc.insert(ignore_permissions=True)
			except Exception:
				pass
	frappe.db.commit()
	_log("  ✓ Baseline references ready")

	def _set_currency(doc, row):
		doc.currency = target_currency
		doc.conversion_rate = 1.0

	def _set_si_defaults(doc, row):
		"""Set Sales Invoice currency + price list defaults."""
		doc.currency = target_currency
		doc.conversion_rate = 1.0
		doc.selling_price_list = "Standard Selling"
		doc.price_list_currency = target_currency
		doc.plc_conversion_rate = 1.0
		debit_to = frappe.db.get_value("Company", target_company, "default_receivable_account")
		if debit_to:
			doc.debit_to = debit_to

	def _set_pi_defaults(doc, row):
		"""Set Purchase Invoice currency + price list defaults."""
		doc.currency = target_currency
		doc.conversion_rate = 1.0
		doc.buying_price_list = "Standard Buying"
		doc.price_list_currency = target_currency
		doc.plc_conversion_rate = 1.0
		credit_to = frappe.db.get_value("Company", target_company, "default_payable_account")
		if credit_to:
			doc.credit_to = credit_to

	# ── Import in dependency order (commit after each step to release DB locks) ──
	def _step(label, fn, *args, **kwargs):
		_log(f"  Importing {label} ...")
		t0 = time.time()
		result = fn(*args, **kwargs)
		frappe.db.commit()
		dt = time.time() - t0
		ins = result.get('inserted', 0)
		skp = result.get('skipped', 0)
		errs = result.get('errors', [])
		err_count = len(errs)
		_log(f"  ✓ {label}: {ins} inserted, {skp} skipped, {err_count} errors  ({dt:.1f}s)")
		if errs:
			first = errs[0]
			tb = first.get("error", "")
			last_line = tb.strip().split('\n')[-1] if tb else "unknown"
			_log(f"    ⚠ First error [{first.get('key', '?')}]: {last_line[:200]}")
		report[label] = result

	_log("\n═══ Starting seed import ═══")
	_log(f"  Target company: {target_company} ({target_abbr})")

	report["Company"] = {"inserted": 0, "skipped": len(company_rows), "errors": []}
	_step("Branch", _upsert_simple, "Branch", branch_rows, "branch")
	_step("Designation", _upsert_simple, "Designation", designation_rows, "designation_name")
	_step("Department", _upsert_simple, "Department", department_rows, "department_name")

	# ── Resolve department references from DB (name includes company abbr) ──
	_log("  Resolving department references ...")
	dept_lookup = {}
	for d in frappe.get_all("Department", filters={"company": target_company}, fields=["name", "department_name"]):
		dept_lookup[d.department_name] = d.name
		dept_lookup[d.name] = d.name
	for d in frappe.get_all("Department", filters={"company": ["in", ["", None]]}, fields=["name", "department_name"]):
		if d.department_name not in dept_lookup:
			dept_lookup[d.department_name] = d.name
			dept_lookup[d.name] = d.name
	for rows_list in [employee_rows, project_rows, task_rows]:
		for row in rows_list:
			dept = row.get("department", "")
			if not dept:
				continue
			if dept in dept_lookup:
				row["department"] = dept_lookup[dept]
			elif f"{dept} - {target_abbr}" in dept_lookup:
				row["department"] = dept_lookup[f"{dept} - {target_abbr}"]
	_log(f"  ✓ Resolved {len(dept_lookup)} department mappings")

	_step("Warehouse", _upsert_simple, "Warehouse", warehouse_rows, "name")
	_step("Cost Center", _import_cost_centers, cost_center_rows, target_company, target_abbr)
	_step("Customer Group", _upsert_simple, "Customer Group", customer_group_rows, "customer_group_name")
	_step("Supplier Group", _upsert_simple, "Supplier Group", supplier_group_rows, "supplier_group_name")
	_step("Territory", _upsert_simple, "Territory", territory_rows, "territory_name")
	_step("Item Group", _upsert_simple, "Item Group", item_group_rows, "item_group_name")
	_step("Brand", _upsert_simple, "Brand", brand_rows, "brand")
	_step("Customer", _upsert_simple, "Customer", customer_rows, "customer_name")
	_step("Supplier", _upsert_simple, "Supplier", supplier_rows, "supplier_name")
	_step("Item", _upsert_simple, "Item", item_rows, "item_code")
	_step("Item Price", _import_item_prices, item_price_rows)
	_step("Employee", _upsert_simple, "Employee", employee_rows, "employee_name", skip_validation=True)
	_step("Vehicle", _upsert_simple, "Vehicle", vehicle_rows, "license_plate")
	_step("Driver", _upsert_simple, "Driver", driver_rows, "full_name")
	_step("Holiday List", _import_holiday_lists, holiday_list_rows, holiday_rows)
	_step("Address", _import_addresses, address_rows)
	_step("Contact", _import_contacts, contact_rows)
	_step("Lead", _upsert_simple, "Lead", lead_rows, "company_name")
	_step("Opportunity", _import_with_children, "Opportunity", opportunity_rows, opportunity_item_rows, "items", _set_currency, skip_validation=True)
	_step("Contract", _upsert_simple, "Contract", contract_rows, "party_name")
	_step("Project", _upsert_simple, "Project", project_rows, "project_name")

	# ── Resolve project references (Project name includes naming series) ──
	_log("  Resolving project references ...")
	proj_lookup = {}
	for p in frappe.get_all("Project", filters={"company": target_company}, fields=["name", "project_name"]):
		proj_lookup[p.project_name] = p.name
		proj_lookup[p.name] = p.name
	for row in task_rows:
		proj = row.get("project", "")
		if not proj:
			continue
		if proj in proj_lookup:
			row["project"] = proj_lookup[proj]
		else:
			row["project"] = ""  # clear invalid ref to avoid DoesNotExistError
	_log(f"  ✓ Resolved {len(proj_lookup)} project mappings")

	_step("Task", _upsert_simple, "Task", task_rows, "subject", skip_validation=True)
	_step("Quotation", _import_quotations, quotation_rows, quotation_item_rows, company_currency=target_currency)
	_step("Sales Order", _import_sales_orders, so_rows, soi_rows, company_currency=target_currency)
	_step("Purchase Order", _import_purchase_orders, po_rows, poi_rows, company_currency=target_currency)
	_step("Material Request", _import_with_children, "Material Request", mr_rows, mri_rows, "items", skip_validation=True)
	_step("Purchase Receipt", _import_with_children, "Purchase Receipt", pr_rows, pri_rows, "items", _set_currency, skip_validation=True)
	_step("Stock Entry", _import_stock_entries, stock_entry_rows, stock_entry_detail_rows)
	_step("Delivery Note", _import_with_children, "Delivery Note", dn_rows, dni_rows, "items", _set_currency, skip_validation=True)
	_step("Sales Invoice", _import_with_children, "Sales Invoice", si_rows, sii_rows, "items", _set_si_defaults, skip_validation=True)
	_step("Purchase Invoice", _import_with_children, "Purchase Invoice", pi_rows, pii_rows, "items", _set_pi_defaults, skip_validation=True)
	_step("Issue", _upsert_simple, "Issue", issue_rows, "subject", skip_validation=True)
	_step("Maintenance Visit", _import_with_children, "Maintenance Visit", mv_rows, mvp_rows, "purposes", skip_validation=True)
	_step("Delivery Trip", _import_with_children, "Delivery Trip", dt_rows, ds_rows, "delivery_stops", skip_validation=True)
	_step("Maintenance Schedule", _import_with_children, "Maintenance Schedule", ms_rows, msi_rows, "items", skip_validation=True)
	_step("Quality Inspection", _import_bulk, "Quality Inspection", qi_rows, skip_validation=True)

	# ── JSON sidecars (for audit/analytics) ──
	json_sidecars = [
		("Waste Events", "waste_collection_events.json", "events"),
		("Incinerator Ops", "incinerator_operations.json", "operations"),
		("Transport Logs", "transport_logs.json", "logs"),
		("Training Sessions", "training_sessions.json", "sessions"),
		("Compliance Reports", "compliance_reports.json", "reports"),
		("Disposal Certificates", "disposal_certificates.json", "certificates"),
		("Fuel Logs", "vehicle_fuel_logs.json", "logs"),
		("Environmental Monitoring", "environmental_monitoring.json", "records"),
		("Route Schedules", "route_schedules.json", "routes"),
		("Financial Events", "financial_events.json", "entries"),
	]
	for label, filename, key in json_sidecars:
		p = base / filename
		report[f"{label} JSON"] = {
			"loaded": p.exists(),
			"rows": len(json.loads(p.read_text(encoding="utf-8")).get(key, [])) if p.exists() else 0,
		}

	out_path = base / "frappe_import_report.json"
	out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
	frappe.db.commit()
	return report
