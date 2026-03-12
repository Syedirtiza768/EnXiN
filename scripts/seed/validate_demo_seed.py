#!/usr/bin/env python3
"""Validate generated demo seed files for referential integrity and volume targets.

Checks:
  1. All required CSV and JSON files exist.
  2. Every parent-child CSV has valid parent references.
  3. Foreign-key references (customer, supplier, item_code, vehicle, driver, address)
     resolve to their respective master-data sets.
  4. JSON sidecar customer/vehicle references are consistent.
  5. Row counts meet minimum volume thresholds.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ── Required files ───────────────────────────────────────────────────────────

REQUIRED_CSV_FILES = [
    "Company.csv", "Branch.csv", "Department.csv", "Designation.csv",
    "Warehouse.csv", "Cost_Center.csv",
    "Customer_Group.csv", "Supplier_Group.csv", "Item_Group.csv", "Brand.csv",
    "Customer.csv", "Supplier.csv", "Item.csv", "Item_Price.csv",
    "Employee.csv", "Vehicle.csv", "Driver.csv",
    "Holiday_List.csv", "Holiday.csv",
    "Address.csv", "Contact.csv",
    "Lead.csv", "Opportunity.csv", "Opportunity_Item.csv",
    "Contract.csv", "Project.csv", "Task.csv",
    "Quotation.csv", "Quotation_Item.csv",
    "Sales_Order.csv", "Sales_Order_Item.csv",
    "Purchase_Order.csv", "Purchase_Order_Item.csv",
    "Material_Request.csv", "Material_Request_Item.csv",
    "Purchase_Receipt.csv", "Purchase_Receipt_Item.csv",
    "Stock_Entry.csv", "Stock_Entry_Detail.csv",
    "Delivery_Note.csv", "Delivery_Note_Item.csv",
    "Sales_Invoice.csv", "Sales_Invoice_Item.csv",
    "Purchase_Invoice.csv", "Purchase_Invoice_Item.csv",
    "Delivery_Trip.csv", "Delivery_Stop.csv",
    "Maintenance_Visit.csv", "Maintenance_Visit_Purpose.csv",
    "Maintenance_Schedule.csv", "Maintenance_Schedule_Item.csv",
    "Issue.csv", "Quality_Inspection.csv",
]

REQUIRED_JSON_FILES = [
    "waste_collection_events.json",
    "incinerator_operations.json",
    "transport_logs.json",
    "training_sessions.json",
    "compliance_reports.json",
    "disposal_certificates.json",
    "vehicle_fuel_logs.json",
    "environmental_monitoring.json",
    "route_schedules.json",
    "financial_events.json",
    "validation_report.json",
]

# Minimum expected row counts (roughly 60 % of VolumeConfig targets as a floor).
MIN_COUNTS: Dict[str, int] = {
    "Customer.csv": 80,
    "Supplier.csv": 20,
    "Item.csv": 300,
    "Employee.csv": 200,
    "Vehicle.csv": 30,
    "Driver.csv": 20,
    "Sales_Order.csv": 1500,
    "Purchase_Order.csv": 250,
    "Sales_Invoice.csv": 1200,
    "Purchase_Invoice.csv": 250,
    "Delivery_Note.csv": 700,
    "Delivery_Trip.csv": 1500,
    "Issue.csv": 450,
    "Project.csv": 30,
    "Maintenance_Visit.csv": 150,
    "Maintenance_Schedule.csv": 100,
    "Stock_Entry.csv": 200,
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def read_csv_safe(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json_safe(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _check_fk(rows: List[Dict], field: str, valid: Set[str],
              id_field: str = "name") -> List[str]:
    """Return list of row identifiers where *field* is not in *valid*."""
    bad = []
    for r in rows:
        val = r.get(field, "")
        if val and val not in valid:
            bad.append(r.get(id_field) or r.get("parent") or str(r)[:80])
    return bad


def _check_parent(child_rows: List[Dict], parent_names: Set[str]) -> List[str]:
    return [r.get("parent", "") for r in child_rows
            if r.get("parent") and r["parent"] not in parent_names]


# ── Main validation ─────────────────────────────────────────────────────────

def validate(base: Path) -> Dict[str, object]:
    all_errors: Dict[str, List[str]] = {}
    counts: Dict[str, int] = {}

    # 1. File existence
    missing_csv = [f for f in REQUIRED_CSV_FILES if not (base / f).exists()]
    missing_json = [f for f in REQUIRED_JSON_FILES if not (base / f).exists()]
    if missing_csv:
        all_errors["missing_csv_files"] = missing_csv
    if missing_json:
        all_errors["missing_json_files"] = missing_json

    # 2. Load master data sets
    customers = read_csv_safe(base / "Customer.csv")
    suppliers = read_csv_safe(base / "Supplier.csv")
    items = read_csv_safe(base / "Item.csv")
    employees = read_csv_safe(base / "Employee.csv")
    vehicles = read_csv_safe(base / "Vehicle.csv")
    drivers = read_csv_safe(base / "Driver.csv")
    addresses = read_csv_safe(base / "Address.csv")

    customer_names: Set[str] = {r["customer_name"] for r in customers}
    supplier_names: Set[str] = {r["supplier_name"] for r in suppliers}
    item_codes: Set[str] = {r["item_code"] for r in items}
    vehicle_plates: Set[str] = {r["license_plate"] for r in vehicles}
    driver_names: Set[str] = {r["full_name"] for r in drivers}
    address_names: Set[str] = {r["name"] for r in addresses if r.get("name")}

    # 3. Load transactional data
    so = read_csv_safe(base / "Sales_Order.csv")
    soi = read_csv_safe(base / "Sales_Order_Item.csv")
    po = read_csv_safe(base / "Purchase_Order.csv")
    poi = read_csv_safe(base / "Purchase_Order_Item.csv")
    si = read_csv_safe(base / "Sales_Invoice.csv")
    sii = read_csv_safe(base / "Sales_Invoice_Item.csv")
    pi = read_csv_safe(base / "Purchase_Invoice.csv")
    pii = read_csv_safe(base / "Purchase_Invoice_Item.csv")
    dn = read_csv_safe(base / "Delivery_Note.csv")
    dni = read_csv_safe(base / "Delivery_Note_Item.csv")
    pr = read_csv_safe(base / "Purchase_Receipt.csv")
    pri = read_csv_safe(base / "Purchase_Receipt_Item.csv")
    mr = read_csv_safe(base / "Material_Request.csv")
    mri = read_csv_safe(base / "Material_Request_Item.csv")
    se = read_csv_safe(base / "Stock_Entry.csv")
    sed = read_csv_safe(base / "Stock_Entry_Detail.csv")
    qt = read_csv_safe(base / "Quotation.csv")
    qti = read_csv_safe(base / "Quotation_Item.csv")
    opp = read_csv_safe(base / "Opportunity.csv")
    oppi = read_csv_safe(base / "Opportunity_Item.csv")
    dt = read_csv_safe(base / "Delivery_Trip.csv")
    ds = read_csv_safe(base / "Delivery_Stop.csv")
    mv = read_csv_safe(base / "Maintenance_Visit.csv")
    mvp = read_csv_safe(base / "Maintenance_Visit_Purpose.csv")
    ms = read_csv_safe(base / "Maintenance_Schedule.csv")
    msi = read_csv_safe(base / "Maintenance_Schedule_Item.csv")
    issues = read_csv_safe(base / "Issue.csv")

    # Name sets for parent-child checks
    so_names: Set[str] = {r["name"] for r in so if r.get("name")}
    po_names: Set[str] = {r["name"] for r in po if r.get("name")}
    si_names: Set[str] = {r["name"] for r in si if r.get("name")}
    pi_names: Set[str] = {r["name"] for r in pi if r.get("name")}
    dn_names: Set[str] = {r["name"] for r in dn if r.get("name")}
    pr_names: Set[str] = {r["name"] for r in pr if r.get("name")}
    mr_names: Set[str] = {r["name"] for r in mr if r.get("name")}
    se_names: Set[str] = {r["name"] for r in se if r.get("name")}
    qt_names: Set[str] = {r["name"] for r in qt if r.get("name")}
    opp_names: Set[str] = {r["name"] for r in opp if r.get("name")}
    dt_names: Set[str] = {r["name"] for r in dt if r.get("name")}
    mv_names: Set[str] = {r["name"] for r in mv if r.get("name")}
    ms_names: Set[str] = {r["name"] for r in ms if r.get("name")}

    # 4. Parent-child integrity
    parent_child_checks: List[Tuple[str, List[Dict], Set[str]]] = [
        ("Sales_Order_Item→SO", soi, so_names),
        ("Purchase_Order_Item→PO", poi, po_names),
        ("Sales_Invoice_Item→SI", sii, si_names),
        ("Purchase_Invoice_Item→PI", pii, pi_names),
        ("Delivery_Note_Item→DN", dni, dn_names),
        ("Purchase_Receipt_Item→PR", pri, pr_names),
        ("Material_Request_Item→MR", mri, mr_names),
        ("Stock_Entry_Detail→SE", sed, se_names),
        ("Quotation_Item→QT", qti, qt_names),
        ("Opportunity_Item→Opp", oppi, opp_names),
        ("Delivery_Stop→DT", ds, dt_names),
        ("Maintenance_Visit_Purpose→MV", mvp, mv_names),
        ("Maintenance_Schedule_Item→MS", msi, ms_names),
    ]
    for label, child_rows, parent_set in parent_child_checks:
        bad = _check_parent(child_rows, parent_set)
        if bad:
            all_errors[f"orphan_{label}"] = bad[:20]

    # 5. Foreign-key checks on transactional docs
    fk_checks: List[Tuple[str, List[Dict], str, Set[str], str]] = [
        ("SO→customer", so, "customer", customer_names, "name"),
        ("PO→supplier", po, "supplier", supplier_names, "name"),
        ("SI→customer", si, "customer", customer_names, "name"),
        ("PI→supplier", pi, "supplier", supplier_names, "name"),
        ("DN→customer", dn, "customer", customer_names, "name"),
        ("Issue→customer", issues, "customer", customer_names, "subject"),
        ("MV→customer", mv, "customer", customer_names, "name"),
        ("MS→customer", ms, "customer", customer_names, "name"),
        ("DT→vehicle", dt, "vehicle", vehicle_plates, "name"),
        ("DS→address", ds, "address", address_names, "parent"),
    ]
    for label, rows, field, valid_set, id_fld in fk_checks:
        bad = _check_fk(rows, field, valid_set, id_fld)
        if bad:
            all_errors[f"fk_{label}"] = bad[:20]

    # Item code checks on child tables
    item_child_checks: List[Tuple[str, List[Dict]]] = [
        ("SOI→item", soi), ("POI→item", poi), ("SII→item", sii),
        ("PII→item", pii), ("DNI→item", dni), ("PRI→item", pri),
        ("MRI→item", mri), ("QTI→item", qti),
        ("MSI→item", msi),
    ]
    for label, rows in item_child_checks:
        bad = _check_fk(rows, "item_code", item_codes, "parent")
        if bad:
            all_errors[f"fk_{label}"] = bad[:20]

    # Driver FK (optional field — only check non-empty)
    dt_bad_driver = [r["name"] for r in dt
                     if r.get("driver") and r["driver"] not in driver_names]
    if dt_bad_driver:
        all_errors["fk_DT→driver"] = dt_bad_driver[:20]

    # 6. JSON sidecar checks
    waste = read_json_safe(base / "waste_collection_events.json")
    waste_events = waste.get("events", [])
    waste_bad_cust = [e["event_id"] for e in waste_events
                      if e.get("customer") and e["customer"] not in customer_names]
    if waste_bad_cust:
        all_errors["json_waste→customer"] = waste_bad_cust[:20]

    transport = read_json_safe(base / "transport_logs.json")
    transport_logs = transport.get("logs", [])
    transport_bad_veh = [t.get("log_id", "") for t in transport_logs
                         if t.get("vehicle") and t["vehicle"] not in vehicle_plates]
    if transport_bad_veh:
        all_errors["json_transport→vehicle"] = transport_bad_veh[:20]

    fuel = read_json_safe(base / "vehicle_fuel_logs.json")
    fuel_logs = fuel.get("logs", [])
    fuel_bad_veh = [f_.get("log_id", "") for f_ in fuel_logs
                    if f_.get("vehicle") and f_["vehicle"] not in vehicle_plates]
    if fuel_bad_veh:
        all_errors["json_fuel→vehicle"] = fuel_bad_veh[:20]

    # 7. Row counts
    count_files = {
        "Customer.csv": customers, "Supplier.csv": suppliers, "Item.csv": items,
        "Employee.csv": employees, "Vehicle.csv": vehicles, "Driver.csv": drivers,
        "Sales_Order.csv": so, "Purchase_Order.csv": po,
        "Sales_Invoice.csv": si, "Purchase_Invoice.csv": pi,
        "Delivery_Note.csv": dn, "Delivery_Trip.csv": dt,
        "Issue.csv": issues, "Project.csv": read_csv_safe(base / "Project.csv"),
        "Maintenance_Visit.csv": mv, "Maintenance_Schedule.csv": ms,
        "Stock_Entry.csv": se,
    }
    below_minimum: Dict[str, str] = {}
    for fname, rows in count_files.items():
        counts[fname] = len(rows)
        minimum = MIN_COUNTS.get(fname, 0)
        if len(rows) < minimum:
            below_minimum[fname] = f"{len(rows)} < {minimum}"
    if below_minimum:
        all_errors["below_minimum_counts"] = [f"{k}: {v}" for k, v in below_minimum.items()]

    # Also count child tables and JSON
    counts["Sales_Order_Item.csv"] = len(soi)
    counts["Delivery_Stop.csv"] = len(ds)
    counts["waste_events"] = len(waste_events)
    counts["transport_logs"] = len(transport_logs)
    counts["fuel_logs"] = len(fuel_logs)

    ok = len(all_errors) == 0
    report = {
        "valid": ok,
        "counts": counts,
        "error_count": sum(len(v) for v in all_errors.values()),
        "errors": all_errors,
    }

    (base / "validation_runtime_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated EnXi demo seed data")
    parser.add_argument("--input", default="seed_output",
                        help="Input directory with generated seed files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate(Path(args.input))
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
