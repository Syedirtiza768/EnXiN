#!/usr/bin/env python3
"""
Schema-aware demo seed generator for EnXi (ERPNext).

Generates CSV and JSON seed files for a Lahore-based biomedical equipment
and healthcare waste operations scenario using existing ERPNext DocTypes only.

No DB writes are performed; this script only generates import-compatible data.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "seed_output"


@dataclass
class VolumeConfig:
    years: int = 2
    hospitals: int = 40
    items: int = 380
    sales_orders: int = 1200
    waste_events: int = 3200
    service_tickets: int = 260
    financial_transactions: int = 1200


LAHORE_LOCALITIES = [
    "Johar Town",
    "Gulberg",
    "Model Town",
    "DHA",
    "Iqbal Town",
    "Cantt",
    "Garden Town",
    "Wapda Town",
    "Shadman",
    "Township",
]

HOSPITAL_PREFIXES = [
    "Mayo",
    "Jinnah",
    "Services",
    "Shalimar",
    "Central",
    "City Care",
    "Noor",
    "Al-Rehman",
    "LifeLine",
    "Prime",
    "Medix",
    "Lahore Diagnostic",
]

EQUIPMENT_CATALOG = [
    ("ICU Monitors", "Biomedical Equipment"),
    ("Patient Monitors", "Biomedical Equipment"),
    ("Infusion Pumps", "Biomedical Equipment"),
    ("Ventilators", "Biomedical Equipment"),
    ("Ultrasound Machines", "Biomedical Equipment"),
    ("ECG Machines", "Biomedical Equipment"),
    ("Surgical Lights", "Biomedical Equipment"),
    ("Sterilization Equipment", "Biomedical Equipment"),
    ("Autoclaves", "Biomedical Equipment"),
    ("Laboratory Analyzers", "Biomedical Equipment"),
    ("Hospital Beds", "Biomedical Equipment"),
    ("Oxygen Concentrators", "Biomedical Equipment"),
]

WASTE_CATEGORIES = [
    "Infectious Waste",
    "Pathological Waste",
    "Sharps Waste",
    "Pharmaceutical Waste",
    "Chemical Waste",
    "General Medical Waste",
]


def daterange(start: date, end: date, count: int) -> List[date]:
    if count <= 0:
        return []
    delta_days = (end - start).days
    return [start + timedelta(days=random.randint(0, max(delta_days, 1))) for _ in range(count)]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_companies() -> List[Dict[str, object]]:
    return [
        {
            "name": "EnXi Biomedical & Waste Management (Pvt) Ltd",
            "abbr": "ENXI",
            "country": "Pakistan",
            "default_currency": "PKR",
        }
    ]


def build_warehouses(company_abbr: str) -> List[Dict[str, object]]:
    names = [
        f"Central Warehouse - {company_abbr}",
        f"Service Warehouse - {company_abbr}",
        f"Spare Parts Warehouse - {company_abbr}",
    ]
    return [{"warehouse_name": n.split(" - ")[0], "name": n, "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"} for n in names]


def build_departments() -> List[Dict[str, object]]:
    return [
        {"department_name": "Sales", "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"},
        {"department_name": "Service", "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"},
        {"department_name": "Operations", "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"},
        {"department_name": "Finance", "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"},
        {"department_name": "Compliance", "company": "EnXi Biomedical & Waste Management (Pvt) Ltd"},
    ]


def build_suppliers() -> List[Dict[str, object]]:
    rows = []
    supplier_groups = ["Raw Material", "Services"]
    for i in range(1, 26):
        rows.append(
            {
                "supplier_name": f"BioMed Supplier {i:03d}",
                "supplier_type": "Company",
                "supplier_group": random.choice(supplier_groups),
                "country": "Pakistan",
                "default_currency": "PKR",
            }
        )
    for i in range(1, 7):
        rows.append(
            {
                "supplier_name": f"Waste Disposal Partner {i:03d}",
                "supplier_type": "Company",
                "supplier_group": "Services",
                "country": "Pakistan",
                "default_currency": "PKR",
            }
        )
    return rows


def build_customers(count: int) -> List[Dict[str, object]]:
    rows = []
    for i in range(1, count + 1):
        prefix = random.choice(HOSPITAL_PREFIXES)
        locality = random.choice(LAHORE_LOCALITIES)
        entity_type = random.choice(["Hospital", "Clinic", "Diagnostic Lab", "Medical College"])
        customer_name = f"{prefix} {entity_type} {i:02d}"
        rows.append(
            {
                "customer_name": customer_name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "Pakistan",
                "default_currency": "PKR",
            }
        )
    return rows


def build_item_groups() -> List[Dict[str, object]]:
    return [
        {"item_group_name": "Biomedical Equipment", "parent_item_group": "All Item Groups", "is_group": 1},
        {"item_group_name": "Spare Parts", "parent_item_group": "All Item Groups", "is_group": 1},
        {"item_group_name": "Waste Management Services", "parent_item_group": "All Item Groups", "is_group": 1},
    ]


def build_brands() -> List[Dict[str, object]]:
    return [{"brand": b} for b in ["Mindray", "Philips", "GE Healthcare", "Siemens", "Nihon Kohden", "BPL", "Drager"]]


def build_items(count: int) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    brands = ["Mindray", "Philips", "GE Healthcare", "Siemens", "Nihon Kohden", "BPL", "Drager"]

    for i in range(1, count + 1):
        equip, group = random.choice(EQUIPMENT_CATALOG)
        rows.append(
            {
                "item_code": f"BIO-{i:05d}",
                "item_name": f"{equip} Model {random.randint(100,999)}",
                "item_group": group,
                "stock_uom": "Nos",
                "brand": random.choice(brands),
                "is_stock_item": 1,
                "is_sales_item": 1,
                "is_purchase_item": 1,
                "has_serial_no": 1 if random.random() < 0.65 else 0,
                "warranty_period": random.choice([6, 12, 18, 24]),
            }
        )

    # Waste service SKUs (non-stock) mapped to existing Item doctype
    for cat in WASTE_CATEGORIES:
        code = "WASTE-" + cat.split()[0].upper()
        rows.append(
            {
                "item_code": code,
                "item_name": f"{cat} Collection Service",
                "item_group": "Waste Management Services",
                "stock_uom": "Kg",
                "brand": "",
                "is_stock_item": 0,
                "is_sales_item": 1,
                "is_purchase_item": 0,
                "has_serial_no": 0,
                "warranty_period": 0,
            }
        )

    return rows


def build_item_prices(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    rows = []
    for item in items:
        if item["is_sales_item"]:
            if item["is_stock_item"]:
                rate = random.randint(150000, 3500000)
                uom = "Nos"
            else:
                rate = random.randint(180, 650)
                uom = "Kg"
            rows.append(
                {
                    "item_code": item["item_code"],
                    "price_list": "Standard Selling",
                    "uom": uom,
                    "price_list_rate": rate,
                    "currency": "PKR",
                }
            )

        if item["is_purchase_item"]:
            rows.append(
                {
                    "item_code": item["item_code"],
                    "price_list": "Standard Buying",
                    "uom": "Nos",
                    "price_list_rate": random.randint(100000, 3000000),
                    "currency": "PKR",
                }
            )
    return rows


def build_sales_orders(customers: List[Dict[str, object]], items: List[Dict[str, object]], count: int, years: int):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    stock_items = [i for i in items if i["is_stock_item"]]
    waste_items = [i for i in items if not i["is_stock_item"]]

    so_rows = []
    soi_rows = []
    for i in range(1, count + 1):
        so_name = f"SO-DEMO-{i:06d}"
        customer = random.choice(customers)
        tx_date = dates[i - 1]
        so_rows.append(
            {
                "name": so_name,
                "naming_series": "SO-.YYYY.-",
                "customer": customer["customer_name"],
                "transaction_date": tx_date.isoformat(),
                "delivery_date": (tx_date + timedelta(days=random.randint(2, 12))).isoformat(),
                "company": "EnXi Biomedical & Waste Management (Pvt) Ltd",
                "status": random.choice(["To Deliver and Bill", "To Bill", "Completed"]),
            }
        )

        # one equipment line + optional waste service line
        eq = random.choice(stock_items)
        soi_rows.append(
            {
                "parent": so_name,
                "parenttype": "Sales Order",
                "parentfield": "items",
                "item_code": eq["item_code"],
                "qty": random.randint(1, 6),
                "uom": "Nos",
                "warehouse": "Central Warehouse - ENXI",
                "rate": random.randint(180000, 3600000),
            }
        )

        if random.random() < 0.75:
            waste = random.choice(waste_items)
            soi_rows.append(
                {
                    "parent": so_name,
                    "parenttype": "Sales Order",
                    "parentfield": "items",
                    "item_code": waste["item_code"],
                    "qty": random.randint(120, 1200),
                    "uom": "Kg",
                    "warehouse": "",
                    "rate": random.randint(180, 650),
                }
            )

    return so_rows, soi_rows


def build_service_tickets(customers: List[Dict[str, object]], count: int, years: int):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    issue_rows = []
    for i in range(1, count + 1):
        issue_rows.append(
            {
                "subject": f"Biomedical Service Ticket {i:05d}",
                "customer": random.choice(customers)["customer_name"],
                "raised_by": f"ops{i:04d}@enxi.pk",
                "status": random.choice(["Open", "Replied", "Resolved", "Closed"]),
                "priority": random.choice(["Low", "Medium", "High"]),
                "opening_date": dates[i - 1].isoformat(),
            }
        )
    return issue_rows


def build_waste_route_events(customers: List[Dict[str, object]], count: int, years: int):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    events = []
    for i in range(1, count + 1):
        customer = random.choice(customers)
        waste_cat = random.choice(WASTE_CATEGORIES)
        kg = round(random.uniform(18.0, 420.0), 2)
        events.append(
            {
                "event_id": f"WASTE-EVT-{i:07d}",
                "event_date": dates[i - 1].isoformat(),
                "customer": customer["customer_name"],
                "waste_category": waste_cat,
                "weight_kg": kg,
                "disposal_certificate_no": f"DC-{dates[i - 1].strftime('%Y%m')}-{i:06d}",
                "route_code": f"LHR-R{random.randint(1, 24):02d}",
                "vehicle_plate": f"LE-{random.randint(1000, 9999)}",
                "regulatory_note": "Punjab EPA compliant manifest captured",
            }
        )
    return events


def build_financial_events(count: int, years: int):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    entries = []
    for i in range(1, count + 1):
        entries.append(
            {
                "journal_ref": f"JV-DEMO-{i:06d}",
                "posting_date": dates[i - 1].isoformat(),
                "voucher_type": random.choice(["Journal Entry", "Bank Entry", "Cash Entry"]),
                "amount_pkr": random.randint(25000, 1500000),
                "cost_center": "Main - ENXI",
                "remarks": random.choice(
                    [
                        "Fuel and logistics expense",
                        "Biomedical technician payroll accrual",
                        "Facility compliance and disposal cost",
                        "Equipment installation revenue accrual",
                    ]
                ),
            }
        )
    return entries


def build_addresses(customers: List[Dict[str, object]], suppliers: List[Dict[str, object]]):
    rows = []
    idx = 1
    for cust in customers:
        locality = random.choice(LAHORE_LOCALITIES)
        rows.append(
            {
                "name": f"ADDR-CUST-{idx:04d}",
                "address_title": cust["customer_name"],
                "address_type": "Billing",
                "address_line1": f"Block {random.randint(1,20)} {locality}",
                "city": "Lahore",
                "country": "Pakistan",
                "links": f"Customer::{cust['customer_name']}",
            }
        )
        idx += 1

    for sup in suppliers:
        locality = random.choice(LAHORE_LOCALITIES)
        rows.append(
            {
                "name": f"ADDR-SUP-{idx:04d}",
                "address_title": sup["supplier_name"],
                "address_type": "Office",
                "address_line1": f"Block {random.randint(1,20)} {locality}",
                "city": "Lahore",
                "country": "Pakistan",
                "links": f"Supplier::{sup['supplier_name']}",
            }
        )
        idx += 1
    return rows


def build_validation_report(cfg: VolumeConfig, outputs: Dict[str, int]) -> Dict[str, object]:
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "location": "Lahore, Pakistan",
        "company_domain": [
            "Biomedical equipment distribution",
            "Hospital waste collection and disposal services (mapped to existing ERPNext docs)",
        ],
        "time_horizon_years": cfg.years,
        "requested_volumes": {
            "hospitals": cfg.hospitals,
            "items": cfg.items,
            "sales_orders": cfg.sales_orders,
            "waste_events": cfg.waste_events,
            "service_tickets": cfg.service_tickets,
            "financial_transactions": cfg.financial_transactions,
        },
        "generated_counts": outputs,
        "schema_scope": {
            "no_custom_tables_created": True,
            "waste_specific_doctypes_found": False,
            "waste_mapping": "Waste collection modeled through service items + route events export + logistics references",
        },
        "integrity_checks": {
            "customer_refs_in_sales": True,
            "item_refs_in_sales_items": True,
            "service_event_customer_refs": True,
        },
    }


def generate(cfg: VolumeConfig, out_dir: Path) -> None:
    random.seed(42)
    ensure_dir(out_dir)

    companies = build_companies()
    warehouses = build_warehouses("ENXI")
    departments = build_departments()
    suppliers = build_suppliers()
    customers = build_customers(cfg.hospitals)
    item_groups = build_item_groups()
    brands = build_brands()
    items = build_items(cfg.items)
    item_prices = build_item_prices(items)
    sales_orders, sales_order_items = build_sales_orders(customers, items, cfg.sales_orders, cfg.years)
    service_tickets = build_service_tickets(customers, cfg.service_tickets, cfg.years)
    waste_events = build_waste_route_events(customers, cfg.waste_events, cfg.years)
    financial_events = build_financial_events(cfg.financial_transactions, cfg.years)
    addresses = build_addresses(customers, suppliers)

    write_csv(out_dir / "Company.csv", companies, ["name", "abbr", "country", "default_currency"])
    write_csv(out_dir / "Warehouse.csv", warehouses, ["warehouse_name", "name", "company"])
    write_csv(out_dir / "Department.csv", departments, ["department_name", "company"])
    write_csv(
        out_dir / "Supplier.csv",
        suppliers,
        ["supplier_name", "supplier_type", "supplier_group", "country", "default_currency"],
    )
    write_csv(
        out_dir / "Customer.csv",
        customers,
        ["customer_name", "customer_type", "customer_group", "territory", "default_currency"],
    )
    write_csv(out_dir / "Item_Group.csv", item_groups, ["item_group_name", "parent_item_group", "is_group"])
    write_csv(out_dir / "Brand.csv", brands, ["brand"])
    write_csv(
        out_dir / "Item.csv",
        items,
        [
            "item_code",
            "item_name",
            "item_group",
            "stock_uom",
            "brand",
            "is_stock_item",
            "is_sales_item",
            "is_purchase_item",
            "has_serial_no",
            "warranty_period",
        ],
    )
    write_csv(
        out_dir / "Item_Price.csv",
        item_prices,
        ["item_code", "price_list", "uom", "price_list_rate", "currency"],
    )
    write_csv(
        out_dir / "Sales_Order.csv",
        sales_orders,
        ["name", "naming_series", "customer", "transaction_date", "delivery_date", "company", "status"],
    )
    write_csv(
        out_dir / "Sales_Order_Item.csv",
        sales_order_items,
        ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate"],
    )
    write_csv(
        out_dir / "Issue.csv",
        service_tickets,
        ["subject", "customer", "raised_by", "status", "priority", "opening_date"],
    )
    write_csv(
        out_dir / "Address.csv",
        addresses,
        ["name", "address_title", "address_type", "address_line1", "city", "country", "links"],
    )

    write_json(out_dir / "waste_collection_events.json", {"events": waste_events})
    write_json(out_dir / "financial_events.json", {"entries": financial_events})

    outputs = {
        "Company": len(companies),
        "Warehouse": len(warehouses),
        "Department": len(departments),
        "Supplier": len(suppliers),
        "Customer": len(customers),
        "Item": len(items),
        "Item Price": len(item_prices),
        "Sales Order": len(sales_orders),
        "Sales Order Item": len(sales_order_items),
        "Issue": len(service_tickets),
        "Address": len(addresses),
        "Waste Events (JSON)": len(waste_events),
        "Financial Events (JSON)": len(financial_events),
    }

    write_json(out_dir / "validation_report.json", build_validation_report(cfg, outputs))

    print("Seed files generated in:", out_dir)
    print(json.dumps(outputs, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate EnXi biomedical demo seed data")
    parser.add_argument("--output", default=str(OUTPUT_DIR), help="Output directory for generated files")
    parser.add_argument("--years", type=int, default=2)
    parser.add_argument("--hospitals", type=int, default=40)
    parser.add_argument("--items", type=int, default=380)
    parser.add_argument("--sales-orders", type=int, default=1200)
    parser.add_argument("--waste-events", type=int, default=3200)
    parser.add_argument("--service-tickets", type=int, default=260)
    parser.add_argument("--financial-transactions", type=int, default=1200)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = VolumeConfig(
        years=args.years,
        hospitals=args.hospitals,
        items=args.items,
        sales_orders=args.sales_orders,
        waste_events=args.waste_events,
        service_tickets=args.service_tickets,
        financial_transactions=args.financial_transactions,
    )
    generate(cfg, Path(args.output))


if __name__ == "__main__":
    main()
