#!/usr/bin/env python3
"""Validate generated demo seed files for referential integrity and volume targets."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Set


REQUIRED_FILES = [
    "Company.csv",
    "Warehouse.csv",
    "Department.csv",
    "Supplier.csv",
    "Customer.csv",
    "Item.csv",
    "Item_Price.csv",
    "Sales_Order.csv",
    "Sales_Order_Item.csv",
    "Issue.csv",
    "Address.csv",
    "waste_collection_events.json",
    "financial_events.json",
    "validation_report.json",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ensure_files(base: Path) -> None:
    missing = [name for name in REQUIRED_FILES if not (base / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing files: {missing}")


def validate(base: Path) -> Dict[str, object]:
    ensure_files(base)

    customers = read_csv(base / "Customer.csv")
    items = read_csv(base / "Item.csv")
    sales_orders = read_csv(base / "Sales_Order.csv")
    sales_order_items = read_csv(base / "Sales_Order_Item.csv")
    issues = read_csv(base / "Issue.csv")

    customer_names: Set[str] = {r["customer_name"] for r in customers}
    item_codes: Set[str] = {r["item_code"] for r in items}
    so_names: Set[str] = {r["name"] for r in sales_orders}

    missing_so_customer = [r["name"] for r in sales_orders if r["customer"] not in customer_names]
    missing_soi_parent = [r["parent"] for r in sales_order_items if r["parent"] not in so_names]
    missing_soi_item = [r["item_code"] for r in sales_order_items if r["item_code"] not in item_codes]
    missing_issue_customer = [r["subject"] for r in issues if r["customer"] not in customer_names]

    waste_payload = json.loads((base / "waste_collection_events.json").read_text(encoding="utf-8"))
    waste_missing_customer = [
        e["event_id"] for e in waste_payload.get("events", []) if e["customer"] not in customer_names
    ]

    ok = not any(
        [
            missing_so_customer,
            missing_soi_parent,
            missing_soi_item,
            missing_issue_customer,
            waste_missing_customer,
        ]
    )

    report = {
        "valid": ok,
        "counts": {
            "customers": len(customers),
            "items": len(items),
            "sales_orders": len(sales_orders),
            "sales_order_items": len(sales_order_items),
            "issues": len(issues),
            "waste_events": len(waste_payload.get("events", [])),
        },
        "errors": {
            "sales_orders_missing_customer": missing_so_customer[:20],
            "sales_order_items_missing_parent": missing_soi_parent[:20],
            "sales_order_items_missing_item": missing_soi_item[:20],
            "issues_missing_customer": missing_issue_customer[:20],
            "waste_events_missing_customer": waste_missing_customer[:20],
        },
    }

    (base / "validation_runtime_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated EnXi demo seed data")
    parser.add_argument("--input", default="seed_output", help="Input directory with generated seed files")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = validate(Path(args.input))
    print(json.dumps(report, indent=2))
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
