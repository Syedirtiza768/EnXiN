#!/usr/bin/env python3
"""
Enterprise-grade comprehensive seed generator for EnXi Healthcare Waste Management.

Models a Lahore-based company providing:
- Healthcare waste collection, transport, incineration, and compliance
- Biomedical equipment sales, installation, and maintenance
- Government hospital waste management contracts (Punjab-wide)
- Fleet and logistics operations
- Training and capacity building

Generates 40+ CSV files and 9 JSON sidecar files covering all ERPNext modules.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "seed_output"

# ─── Volume Configuration ───────────────────────────────────────────────────────

@dataclass
class VolumeConfig:
    years: int = 2
    hospitals: int = 55
    suppliers_count: int = 35
    items_count: int = 500
    employees_count: int = 120
    vehicles_count: int = 35
    sales_orders: int = 1500
    purchase_orders: int = 300
    quotations: int = 600
    stock_entries: int = 400
    material_requests: int = 150
    delivery_notes: int = 800
    sales_invoices: int = 1000
    purchase_receipts: int = 280
    purchase_invoices: int = 250
    issues: int = 400
    projects: int = 20
    leads: int = 80
    opportunities: int = 60
    maintenance_visits: int = 200
    quality_inspections: int = 100
    waste_events: int = 3500
    incinerator_ops: int = 600
    transport_logs: int = 1200
    training_sessions: int = 150
    fuel_logs: int = 1500

# ─── Company Constants ──────────────────────────────────────────────────────────

COMPANY_NAME = "EnXi Biomedical & Waste Management (Pvt) Ltd"
COMPANY_ABBR = "ENXI"
COUNTRY = "Pakistan"
CURRENCY = "PKR"

# ─── Geographic Data ────────────────────────────────────────────────────────────

LAHORE_LOCALITIES = [
    "Johar Town", "Gulberg", "Model Town", "DHA Phase 1", "DHA Phase 5",
    "Iqbal Town", "Cantt", "Garden Town", "Wapda Town", "Shadman",
    "Township", "Faisal Town", "Samanabad", "Allama Iqbal Town", "Bahria Town",
    "Valencia Town", "EME Society", "Askari 10", "Cavalry Ground", "Gulshan-e-Ravi",
]

PUNJAB_CITIES = [
    "Lahore", "Rawalpindi", "Faisalabad", "Multan", "Gujranwala",
    "Sialkot", "Bahawalpur", "Sargodha", "Sahiwal", "Rahim Yar Khan",
]

# ─── Hospital & Customer Data ──────────────────────────────────────────────────

HOSPITAL_TYPES = [
    ("Tertiary Care Hospital", "Commercial", 18),
    ("District Hospital", "Commercial", 12),
    ("Teaching Hospital", "Institutional", 8),
    ("Private Hospital", "Commercial", 7),
    ("Diagnostic Laboratory", "Commercial", 5),
    ("Maternity Hospital", "Commercial", 3),
    ("Specialist Clinic", "Commercial", 2),
]

HOSPITAL_PREFIXES = [
    "Mayo", "Jinnah", "Services", "Shalimar", "Central Park", "City Care",
    "Noor", "Al-Rehman", "LifeLine", "Prime", "Medix", "Punjab",
    "Lahore General", "Sheikh Zayed", "Hameed Latif", "Shaukat Khanum",
    "National", "Allied", "Combined Military", "Gulab Devi",
    "Sir Ganga Ram", "Fatima Memorial", "Sharif Medical", "Ittefaq",
    "Doctors", "Surgimed", "Hafeez", "Aziz Fatimah", "Farooq",
    "Children", "Lady Aitchison", "Social Security", "Chughtai Lab",
    "IDC", "Agha Khan Lab", "Excel Labs", "Citi Lab", "Data Darbar Medical",
    "Pak Medical", "Al-Naeem", "Faisal", "Ghurki Trust", "Nawaz Sharif",
    "Mian Muhammad Trust", "Bahria International", "CMH", "PAF",
    "Wapda Teaching", "PGMI", "Institute of Nuclear Medicine",
    "Punjab Institute of Cardiology", "Lahore Eye", "KEMU Teaching",
]

# ─── Waste Management Data ──────────────────────────────────────────────────────

WASTE_CATEGORIES = [
    ("Infectious Waste", "Yellow", "infectious", 45),
    ("Pathological Waste", "Red", "pathological", 15),
    ("Sharps Waste", "White", "sharps", 20),
    ("Pharmaceutical Waste", "Brown", "pharmaceutical", 8),
    ("Chemical Waste", "Black", "chemical", 5),
    ("General Medical Waste", "Green", "general", 7),
]

CONTAINER_TYPES = [
    ("Yellow Bin 60L", "WC-YEL-060", "Nos", 1200, "Waste Containers"),
    ("Yellow Bin 120L", "WC-YEL-120", "Nos", 2400, "Waste Containers"),
    ("Red Bin 60L", "WC-RED-060", "Nos", 1500, "Waste Containers"),
    ("Sharps Container 5L", "WC-SHP-005", "Nos", 350, "Waste Containers"),
    ("Sharps Container 10L", "WC-SHP-010", "Nos", 550, "Waste Containers"),
    ("Chemical Waste Drum 50L", "WC-CHM-050", "Nos", 3500, "Waste Containers"),
    ("Biohazard Bag Roll (50pcs)", "WC-BAG-050", "Nos", 800, "Waste Containers"),
    ("Yellow Liner Bag Roll", "WC-LNR-YEL", "Nos", 600, "Waste Containers"),
    ("Red Liner Bag Roll", "WC-LNR-RED", "Nos", 600, "Waste Containers"),
]

# ─── Equipment & Product Catalogs ───────────────────────────────────────────────

EQUIPMENT_CATALOG = [
    ("ICU Monitors", "Biomedical Equipment"), ("Patient Monitors", "Biomedical Equipment"),
    ("Infusion Pumps", "Biomedical Equipment"), ("Ventilators", "Biomedical Equipment"),
    ("Ultrasound Machines", "Biomedical Equipment"), ("ECG Machines", "Biomedical Equipment"),
    ("Surgical Lights", "Biomedical Equipment"), ("Sterilization Equipment", "Biomedical Equipment"),
    ("Autoclaves", "Biomedical Equipment"), ("Laboratory Analyzers", "Biomedical Equipment"),
    ("Hospital Beds", "Biomedical Equipment"), ("Oxygen Concentrators", "Biomedical Equipment"),
    ("Defibrillators", "Biomedical Equipment"), ("Syringe Pumps", "Biomedical Equipment"),
    ("Pulse Oximeters", "Biomedical Equipment"), ("Nebulizers", "Biomedical Equipment"),
    ("Blood Gas Analyzers", "Biomedical Equipment"), ("X-Ray Machines", "Biomedical Equipment"),
    ("Dental Chairs", "Biomedical Equipment"), ("Endoscopy Systems", "Biomedical Equipment"),
]

PPE_ITEMS = [
    ("Nitrile Gloves Box (100)", "PPE-GLV-NIT", "Box", 850),
    ("Latex Gloves Box (100)", "PPE-GLV-LAT", "Box", 650),
    ("N95 Respirator Mask (20)", "PPE-MSK-N95", "Box", 1800),
    ("Surgical Mask Box (50)", "PPE-MSK-SUR", "Box", 450),
    ("Face Shield", "PPE-SHD-001", "Nos", 350),
    ("Safety Goggles", "PPE-GOG-001", "Nos", 420),
    ("Disposable Gown", "PPE-GWN-DIS", "Nos", 280),
    ("Heavy Duty Apron", "PPE-APR-HDY", "Nos", 950),
    ("Safety Boots Pair", "PPE-BOT-001", "Pair", 3500),
    ("Chemical Resistant Gloves", "PPE-GLV-CHM", "Pair", 1200),
]

SPARE_PARTS = [
    ("Monitor Display Panel", "Biomedical Spare Parts"), ("Infusion Pump Motor", "Biomedical Spare Parts"),
    ("ECG Lead Set 12-Lead", "Biomedical Spare Parts"), ("SpO2 Sensor Cable", "Biomedical Spare Parts"),
    ("Blood Pressure Cuff Adult", "Biomedical Spare Parts"), ("Ventilator Circuit Kit", "Biomedical Spare Parts"),
    ("Autoclave Gasket Set", "Biomedical Spare Parts"), ("Defibrillator Pads", "Biomedical Spare Parts"),
    ("Temperature Probe", "Biomedical Spare Parts"), ("Printer Paper Roll (Thermal)", "Biomedical Spare Parts"),
    ("Battery Pack (Medical Grade)", "Biomedical Spare Parts"), ("Fuse Kit (Assorted)", "Biomedical Spare Parts"),
]

INCINERATOR_ITEMS = [
    ("Incinerator Fuel (Diesel)", "INC-FUEL-DSL", "Ltr", 280),
    ("Refractory Brick", "INC-BRK-REF", "Nos", 4500),
    ("Emission Filter Cartridge", "INC-FLT-EMI", "Nos", 35000),
    ("Thermocouple Sensor", "INC-SNS-TMP", "Nos", 8500),
    ("Ash Collection Bag", "INC-BAG-ASH", "Nos", 450),
    ("Ignition Electrode", "INC-ELC-IGN", "Nos", 12000),
]

VEHICLE_PARTS = [
    ("Engine Oil 5L", "VPT-OIL-ENG", "Nos", 3200),
    ("Air Filter", "VPT-FLT-AIR", "Nos", 1800),
    ("Brake Pad Set", "VPT-BRK-PAD", "Set", 4500),
    ("Tyre 195/65R15", "VPT-TYR-195", "Nos", 12000),
    ("Battery 12V Heavy Duty", "VPT-BAT-12V", "Nos", 15000),
    ("Coolant 5L", "VPT-COL-005", "Nos", 1200),
    ("Wiper Blade Set", "VPT-WPR-SET", "Set", 800),
    ("Transmission Fluid 4L", "VPT-TRN-FLD", "Nos", 2500),
]

CLEANING_SUPPLIES = [
    ("Disinfectant Solution 5L", "CLN-DIS-005", "Nos", 1500),
    ("Bleach Solution 5L", "CLN-BLC-005", "Nos", 800),
    ("Spill Containment Kit", "CLN-SPL-KIT", "Nos", 4500),
    ("Surface Sanitizer Spray", "CLN-SAN-SPR", "Nos", 650),
]

BRANDS = [
    "Mindray", "Philips", "GE Healthcare", "Siemens Healthineers", "Nihon Kohden",
    "BPL Medical", "Draeger", "Medtronic", "B.Braun", "Hillrom",
    "ECOTECH", "Inciner8", "Elastec", "Matthews Environmental", "AddField",
]

# ─── Organization Data ──────────────────────────────────────────────────────────

DEPARTMENTS = [
    "Waste Operations", "Fleet & Transport", "Incinerator Operations",
    "Compliance & Environment", "Training & Development",
    "Sales & Business Development", "Finance & Accounts", "Human Resources",
    "Procurement", "IT & Systems", "Quality Assurance", "Administration",
    "Biomedical Services", "Maintenance & Repair",
]

DESIGNATIONS = [
    "Chief Executive Officer", "Chief Operating Officer", "Chief Financial Officer",
    "Director Operations", "Director Compliance", "Director Sales",
    "General Manager", "Regional Manager", "Operations Manager",
    "Finance Manager", "HR Manager", "Procurement Manager",
    "Waste Operations Supervisor", "Fleet Supervisor", "Incinerator Supervisor",
    "Biomedical Engineer", "Service Technician", "Maintenance Technician",
    "Waste Collector", "Driver", "Helper",
    "Compliance Officer", "Environmental Analyst", "Training Coordinator",
    "Sales Executive", "Account Manager", "Customer Support Executive",
    "Accountant", "HR Executive", "IT Support", "Quality Inspector",
    "Incinerator Operator", "Logistics Coordinator",
]

FIRST_NAMES = [
    "Ahmed", "Muhammad", "Ali", "Hassan", "Usman", "Bilal", "Asad", "Zain",
    "Hamza", "Omar", "Saad", "Faisal", "Kashif", "Imran", "Tanveer",
    "Fatima", "Ayesha", "Sana", "Sara", "Hina", "Amina", "Rabia",
    "Nadia", "Sadia", "Bushra", "Tahir", "Naveed", "Shakeel", "Amir", "Waqas",
]

LAST_NAMES = [
    "Khan", "Malik", "Ahmed", "Hassan", "Sheikh", "Qureshi", "Butt",
    "Chaudhry", "Rana", "Mirza", "Siddiqui", "Raza", "Iqbal", "Aslam", "Shah",
]

SUPPLIER_NAMES = [
    ("Medical Supplies Punjab", "Raw Material"),
    ("Bio-Equipment International", "Equipment Vendor"),
    ("Safety First PPE", "Raw Material"),
    ("Lahore Container Works", "Raw Material"),
    ("Eco-Disposal Systems", "Services"),
    ("Punjab Auto Parts", "Vehicle Parts"),
    ("National Chemical Corp", "Raw Material"),
    ("Al-Fatah Safety Products", "Raw Material"),
    ("Siemens Pakistan", "Equipment Vendor"),
    ("Philips Healthcare PK", "Equipment Vendor"),
    ("GE Health Pakistan", "Equipment Vendor"),
    ("Draeger Safety Pakistan", "Equipment Vendor"),
    ("Pakistan Petroleum Corp", "Fuel Supplier"),
    ("Shell Pakistan", "Fuel Supplier"),
    ("Total Parco", "Fuel Supplier"),
    ("Atlas Honda Parts", "Vehicle Parts"),
    ("Hino Pakistan Motors", "Vehicle Parts"),
    ("Isuzu Pakistan", "Vehicle Parts"),
    ("Waste Tech Industries", "Equipment Vendor"),
    ("Refractory Materials Lahore", "Raw Material"),
    ("Metropolitan Steel Works", "Raw Material"),
    ("Pharma Waste Solutions", "Services"),
    ("Clean Environment Services", "Services"),
    ("Kohinoor Chemical", "Raw Material"),
    ("Lahore Paper & Packaging", "Raw Material"),
    ("Digital Tracking Systems", "IT Services"),
    ("Punjab Insurance Brokers", "Insurance"),
    ("SafeGuard Uniforms", "Raw Material"),
    ("MedTech Training Institute", "Services"),
    ("Calibration Services Pakistan", "Services"),
    ("Fire Safety Equipment Co", "Raw Material"),
    ("Lahore Rubber Works", "Raw Material"),
    ("Ravi Engineering Works", "Services"),
    ("National Environmental Lab", "Services"),
    ("Punjab Revenue Board Consultants", "Services"),
]

VEHICLE_MAKES = [
    ("Hino", "300 Series", "Diesel", 8),
    ("Isuzu", "NPR 75", "Diesel", 6),
    ("Suzuki", "Carry", "Petrol", 5),
    ("Toyota", "Hilux", "Diesel", 4),
    ("Hyundai", "Porter H-100", "Diesel", 4),
    ("FAW", "CA1024", "Diesel", 3),
    ("JW Forland", "C311", "Diesel", 3),
    ("Suzuki", "Bolan", "Petrol", 2),
]

# ─── Helper Functions ────────────────────────────────────────────────────────────

def daterange(start: date, end: date, count: int) -> List[date]:
    if count <= 0:
        return []
    delta = max((end - start).days, 1)
    return sorted([start + timedelta(days=random.randint(0, delta)) for _ in range(count)])


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def pick_weighted(choices_with_weights):
    items, weights = zip(*[(c, w) for *c, w in choices_with_weights])
    return random.choices(items, weights=weights, k=1)[0]


# ─── Master Data Builders ───────────────────────────────────────────────────────

def build_companies():
    return [{
        "name": COMPANY_NAME, "abbr": COMPANY_ABBR,
        "country": COUNTRY, "default_currency": CURRENCY,
    }]


def build_branches():
    return [{"branch": b} for b in [
        "Head Office - Lahore", "North Punjab Depot - Rawalpindi",
        "Central Punjab Depot - Faisalabad", "South Punjab Depot - Multan",
        "Incinerator Facility - Lahore", "Incinerator Facility - Faisalabad",
    ]]


def build_departments():
    return [{"department_name": d, "company": COMPANY_NAME} for d in DEPARTMENTS]


def build_designations():
    return [{"designation": d} for d in DESIGNATIONS]


def build_warehouses():
    wh = [
        "Central Warehouse", "PPE Store", "Spare Parts Store",
        "Container Store", "Incinerator Supplies", "Quarantine Store",
        "Disposal Warehouse", "Vehicle Parts Store",
    ]
    return [{"warehouse_name": w, "name": f"{w} - {COMPANY_ABBR}", "company": COMPANY_NAME} for w in wh]


def build_cost_centers():
    cc = [
        "Main", "Waste Operations", "Fleet & Transport", "Incinerator Ops",
        "Biomedical Sales", "Biomedical Services", "Training",
        "Compliance", "Administration", "Procurement", "HR", "IT",
        "North Punjab", "Central Punjab", "South Punjab",
    ]
    return [{"cost_center_name": c, "company": COMPANY_NAME, "parent_cost_center": f"Main - {COMPANY_ABBR}" if c != "Main" else ""} for c in cc]


def build_customer_groups():
    return [
        {"customer_group_name": "Commercial", "parent_customer_group": "All Customer Groups", "is_group": 0},
        {"customer_group_name": "Institutional", "parent_customer_group": "All Customer Groups", "is_group": 0},
        {"customer_group_name": "Government", "parent_customer_group": "All Customer Groups", "is_group": 0},
    ]


def build_supplier_groups():
    groups = ["Raw Material", "Equipment Vendor", "Services", "Fuel Supplier",
              "Vehicle Parts", "IT Services", "Insurance"]
    return [{"supplier_group_name": g, "parent_supplier_group": "All Supplier Groups", "is_group": 0} for g in groups]


def build_territory():
    return [
        {"territory_name": "Pakistan", "parent_territory": "All Territories", "is_group": 1},
        {"territory_name": "Punjab", "parent_territory": "Pakistan", "is_group": 1},
        {"territory_name": "Lahore", "parent_territory": "Punjab", "is_group": 0},
        {"territory_name": "Rawalpindi", "parent_territory": "Punjab", "is_group": 0},
        {"territory_name": "Faisalabad", "parent_territory": "Punjab", "is_group": 0},
        {"territory_name": "Multan", "parent_territory": "Punjab", "is_group": 0},
    ]


def build_item_groups():
    groups = [
        ("Biomedical Equipment", 1), ("Biomedical Spare Parts", 0),
        ("Waste Containers", 0), ("PPE & Safety", 0),
        ("Cleaning & Disinfection", 0), ("Incinerator Supplies", 0),
        ("Vehicle Parts & Supplies", 0), ("Waste Management Services", 0),
        ("Biomedical Services", 0), ("Training Services", 0),
        ("Installation Services", 0), ("Compliance Services", 0),
    ]
    return [{"item_group_name": g, "parent_item_group": "All Item Groups", "is_group": ig} for g, ig in groups]


def build_brands():
    return [{"brand": b} for b in BRANDS]


# ─── Customer & Supplier Builders ────────────────────────────────────────────────

def build_customers(count: int) -> List[Dict]:
    rows = []
    idx = 0
    for hosp_type, group, weight in HOSPITAL_TYPES:
        n = max(1, round(count * weight / 100))
        for j in range(n):
            if idx >= count:
                break
            prefix = HOSPITAL_PREFIXES[idx % len(HOSPITAL_PREFIXES)]
            locality = random.choice(LAHORE_LOCALITIES)
            city = random.choice(PUNJAB_CITIES[:4]) if random.random() < 0.3 else "Lahore"
            rows.append({
                "customer_name": f"{prefix} {hosp_type.split()[0]} {hosp_type.split()[-1]} {idx + 1:02d}",
                "customer_type": "Company",
                "customer_group": group,
                "territory": city if city in ["Lahore", "Rawalpindi", "Faisalabad", "Multan"] else "Punjab",
                "default_currency": CURRENCY,
            })
            idx += 1
        if idx >= count:
            break
    # Fill remaining
    while idx < count:
        prefix = random.choice(HOSPITAL_PREFIXES)
        rows.append({
            "customer_name": f"{prefix} Medical Center {idx + 1:02d}",
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": "Lahore",
            "default_currency": CURRENCY,
        })
        idx += 1
    return rows


def build_suppliers() -> List[Dict]:
    return [{
        "supplier_name": name,
        "supplier_type": "Company",
        "supplier_group": group,
        "country": COUNTRY,
        "default_currency": CURRENCY,
    } for name, group in SUPPLIER_NAMES]


# ─── Item Builders ───────────────────────────────────────────────────────────────

def build_items(count: int) -> List[Dict]:
    rows = []
    idx = 1

    # Biomedical equipment items
    for i in range(min(count, 200)):
        equip, group = random.choice(EQUIPMENT_CATALOG)
        rows.append({
            "item_code": f"BIO-{idx:05d}", "item_name": f"{equip} Model {random.randint(100, 999)}",
            "item_group": group, "stock_uom": "Nos", "brand": random.choice(BRANDS[:10]),
            "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 1 if random.random() < 0.6 else 0, "warranty_period": random.choice([6, 12, 18, 24]),
        })
        idx += 1

    # Spare parts
    for i, (name, group) in enumerate(SPARE_PARTS):
        rows.append({
            "item_code": f"SPR-{i + 1:05d}", "item_name": f"{name} #{random.randint(10, 99)}",
            "item_group": group, "stock_uom": "Nos", "brand": random.choice(BRANDS[:10]),
            "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Waste containers
    for name, code, uom, price, group in CONTAINER_TYPES:
        rows.append({
            "item_code": code, "item_name": name, "item_group": group, "stock_uom": uom,
            "brand": "", "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # PPE items
    for name, code, uom, price, *_ in PPE_ITEMS:
        rows.append({
            "item_code": code, "item_name": name, "item_group": "PPE & Safety", "stock_uom": uom,
            "brand": "", "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Incinerator supplies
    for name, code, uom, price in INCINERATOR_ITEMS:
        rows.append({
            "item_code": code, "item_name": name, "item_group": "Incinerator Supplies", "stock_uom": uom,
            "brand": "", "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Vehicle parts
    for name, code, uom, price in VEHICLE_PARTS:
        rows.append({
            "item_code": code, "item_name": name, "item_group": "Vehicle Parts & Supplies", "stock_uom": uom,
            "brand": "", "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Cleaning supplies
    for name, code, uom, price in CLEANING_SUPPLIES:
        rows.append({
            "item_code": code, "item_name": name, "item_group": "Cleaning & Disinfection", "stock_uom": uom,
            "brand": "", "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Waste service items (non-stock)
    for cat, color, code_sfx, pct in WASTE_CATEGORIES:
        rows.append({
            "item_code": f"SVC-WASTE-{code_sfx.upper()}", "item_name": f"{cat} Collection Service",
            "item_group": "Waste Management Services", "stock_uom": "Kg", "brand": "",
            "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Biomedical service items (non-stock)
    svc_items = [
        ("Installation & Commissioning", "SVC-BIO-INST", "Nos"),
        ("Preventive Maintenance Visit", "SVC-BIO-PMV", "Nos"),
        ("Corrective Maintenance Service", "SVC-BIO-CMS", "Nos"),
        ("Calibration Service", "SVC-BIO-CAL", "Nos"),
        ("AMC - Annual Maintenance Contract", "SVC-BIO-AMC", "Nos"),
        ("CMC - Comprehensive Maintenance", "SVC-BIO-CMC", "Nos"),
        ("Equipment Training Session", "SVC-TRN-EQP", "Nos"),
        ("Waste Handling Training", "SVC-TRN-WST", "Nos"),
        ("Compliance Audit Service", "SVC-CMP-AUD", "Nos"),
        ("Environmental Monitoring", "SVC-CMP-ENV", "Nos"),
        ("Waste Management Consultancy", "SVC-CMP-CON", "Nos"),
        ("Incineration Service", "SVC-INC-001", "Kg"),
    ]
    for name, code, uom in svc_items:
        rows.append({
            "item_code": code, "item_name": name,
            "item_group": "Biomedical Services" if "BIO" in code else ("Training Services" if "TRN" in code else ("Compliance Services" if "CMP" in code else "Waste Management Services")),
            "stock_uom": uom, "brand": "", "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Fill remaining with more equipment
    while len(rows) < count:
        equip, group = random.choice(EQUIPMENT_CATALOG)
        rows.append({
            "item_code": f"BIO-{len(rows) + 1:05d}", "item_name": f"{equip} Variant {random.randint(1000, 9999)}",
            "item_group": group, "stock_uom": "Nos", "brand": random.choice(BRANDS[:10]),
            "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 1 if random.random() < 0.5 else 0, "warranty_period": random.choice([12, 24]),
        })

    return rows


def build_item_prices(items: List[Dict]) -> List[Dict]:
    rows = []
    for item in items:
        code = item["item_code"]
        uom = item["stock_uom"]

        # Selling price
        if item["is_sales_item"]:
            if item["is_stock_item"]:
                rate = random.randint(80000, 3500000) if "BIO" in code else random.randint(200, 15000)
            else:
                rate = random.randint(5000, 250000) if "SVC-BIO" in code else random.randint(180, 800)
            rows.append({"item_code": code, "price_list": "Standard Selling", "uom": uom, "price_list_rate": rate, "currency": CURRENCY})

        # Buying price
        if item["is_purchase_item"]:
            if "BIO" in code:
                rate = random.randint(60000, 3000000)
            elif any(pfx in code for pfx in ["WC-", "PPE-", "INC-", "VPT-", "CLN-", "SPR-"]):
                # Look up from catalog price or generate
                rate = random.randint(150, 40000)
            else:
                rate = random.randint(100, 500000)
            rows.append({"item_code": code, "price_list": "Standard Buying", "uom": uom, "price_list_rate": rate, "currency": CURRENCY})

    return rows


# ─── Employee & People Builders ──────────────────────────────────────────────────

def build_employees(departments: List[Dict], count: int) -> List[Dict]:
    dept_names = [d["department_name"] for d in departments]
    rows = []

    # Define role distribution
    role_dist = [
        ("Waste Operations", "Waste Collector", 25),
        ("Fleet & Transport", "Driver", 18),
        ("Waste Operations", "Waste Operations Supervisor", 6),
        ("Incinerator Operations", "Incinerator Operator", 8),
        ("Incinerator Operations", "Incinerator Supervisor", 2),
        ("Biomedical Services", "Biomedical Engineer", 6),
        ("Biomedical Services", "Service Technician", 8),
        ("Maintenance & Repair", "Maintenance Technician", 5),
        ("Sales & Business Development", "Sales Executive", 5),
        ("Sales & Business Development", "Account Manager", 3),
        ("Compliance & Environment", "Compliance Officer", 3),
        ("Compliance & Environment", "Environmental Analyst", 2),
        ("Training & Development", "Training Coordinator", 2),
        ("Quality Assurance", "Quality Inspector", 3),
        ("Finance & Accounts", "Accountant", 4),
        ("Human Resources", "HR Executive", 2),
        ("Procurement", "Procurement Manager", 2),
        ("IT & Systems", "IT Support", 2),
        ("Administration", "General Manager", 2),
        ("Fleet & Transport", "Logistics Coordinator", 3),
        ("Fleet & Transport", "Helper", 10),
        ("Administration", "Chief Executive Officer", 1),
        ("Administration", "Chief Operating Officer", 1),
        ("Finance & Accounts", "Chief Financial Officer", 1),
        ("Sales & Business Development", "Director Sales", 1),
        ("Waste Operations", "Director Operations", 1),
        ("Compliance & Environment", "Director Compliance", 1),
    ]

    idx = 0
    for dept, desig, n in role_dist:
        for _ in range(n):
            if idx >= count:
                break
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            gender = "Female" if first in ["Fatima", "Ayesha", "Sana", "Sara", "Hina", "Amina", "Rabia", "Nadia", "Sadia", "Bushra"] else "Male"
            dob = date(random.randint(1970, 2000), random.randint(1, 12), random.randint(1, 28))
            doj = date(random.randint(2019, 2025), random.randint(1, 12), random.randint(1, 28))
            rows.append({
                "employee_name": f"{first} {last}",
                "first_name": first, "last_name": last,
                "company": COMPANY_NAME, "department": dept, "designation": desig,
                "date_of_birth": dob.isoformat(), "date_of_joining": doj.isoformat(),
                "gender": gender, "employment_type": "Full-time", "status": "Active",
                "branch": random.choice(["Head Office - Lahore", "Incinerator Facility - Lahore"]),
            })
            idx += 1
        if idx >= count:
            break

    # Fill remaining
    while len(rows) < count:
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        gender = "Female" if first in ["Fatima", "Ayesha", "Sana", "Sara", "Hina", "Amina", "Rabia", "Nadia", "Sadia", "Bushra"] else "Male"
        dob = date(random.randint(1975, 1998), random.randint(1, 12), random.randint(1, 28))
        doj = date(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28))
        rows.append({
            "employee_name": f"{first} {last}",
            "first_name": first, "last_name": last,
            "company": COMPANY_NAME, "department": random.choice(dept_names),
            "designation": random.choice(DESIGNATIONS),
            "date_of_birth": dob.isoformat(), "date_of_joining": doj.isoformat(),
            "gender": gender, "employment_type": "Full-time", "status": "Active",
            "branch": "Head Office - Lahore",
        })

    return rows


def build_vehicles(count: int) -> List[Dict]:
    rows = []
    idx = 0
    for make, model, fuel, n in VEHICLE_MAKES:
        for j in range(n):
            if idx >= count:
                break
            rows.append({
                "license_plate": f"LE-{random.randint(1000, 9999)}-{random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')}",
                "make": make, "model": model, "fuel_type": fuel,
                "last_odometer": random.randint(5000, 180000),
                "uom": "Ltr",
                "acquisition_date": date(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28)).isoformat(),
                "vehicle_value": random.randint(800000, 6000000),
            })
            idx += 1
        if idx >= count:
            break
    return rows


def build_drivers(employees: List[Dict]) -> List[Dict]:
    driver_emps = [e for e in employees if e["designation"] in ("Driver", "Waste Operations Supervisor", "Fleet Supervisor")]
    rows = []
    for e in driver_emps:
        rows.append({
            "naming_series": "HR-DRI-.YYYY.-",
            "full_name": e["employee_name"],
            "status": "Active",
            "license_number": f"PB-{random.randint(100000, 999999)}",
            "issuing_date": date(random.randint(2018, 2023), random.randint(1, 12), 1).isoformat(),
            "expiry_date": date(random.randint(2026, 2030), random.randint(1, 12), 1).isoformat(),
        })
    return rows


def build_holiday_list():
    hl = [{"holiday_list_name": "Pakistan 2025", "from_date": "2025-01-01", "to_date": "2025-12-31", "company": COMPANY_NAME}]
    holidays = [
        ("2025-02-05", "Kashmir Day"), ("2025-03-23", "Pakistan Day"),
        ("2025-03-30", "Shab-e-Meraj"), ("2025-05-01", "Labour Day"),
        ("2025-03-31", "Eid ul-Fitr Day 1"), ("2025-04-01", "Eid ul-Fitr Day 2"),
        ("2025-04-02", "Eid ul-Fitr Day 3"), ("2025-06-07", "Eid ul-Adha Day 1"),
        ("2025-06-08", "Eid ul-Adha Day 2"), ("2025-06-09", "Eid ul-Adha Day 3"),
        ("2025-07-07", "Shab-e-Barat"), ("2025-08-14", "Independence Day"),
        ("2025-09-27", "Eid Milad-un-Nabi"), ("2025-11-09", "Iqbal Day"),
        ("2025-12-25", "Quaid-e-Azam Day"),
    ]
    h_rows = [{"holiday_list": "Pakistan 2025", "holiday_date": d, "description": desc} for d, desc in holidays]
    return hl, h_rows


# ─── Address & Contact Builders ──────────────────────────────────────────────────

def build_addresses(customers: List[Dict], suppliers: List[Dict]) -> List[Dict]:
    rows = []
    idx = 1
    for c in customers:
        locality = random.choice(LAHORE_LOCALITIES)
        city = random.choice(PUNJAB_CITIES[:4]) if random.random() < 0.3 else "Lahore"
        rows.append({
            "name": f"ADDR-CUST-{idx:04d}", "address_title": c["customer_name"],
            "address_type": "Billing",
            "address_line1": f"Block {random.randint(1, 25)}, {locality}",
            "city": city, "country": COUNTRY,
            "links": f"Customer::{c['customer_name']}",
        })
        idx += 1
    for s in suppliers:
        locality = random.choice(LAHORE_LOCALITIES)
        rows.append({
            "name": f"ADDR-SUP-{idx:04d}", "address_title": s["supplier_name"],
            "address_type": "Office",
            "address_line1": f"Plot {random.randint(1, 200)}, {locality}",
            "city": "Lahore", "country": COUNTRY,
            "links": f"Supplier::{s['supplier_name']}",
        })
        idx += 1
    return rows


def build_contacts(customers: List[Dict]) -> List[Dict]:
    rows = []
    for i, c in enumerate(customers):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        rows.append({
            "first_name": first, "last_name": last,
            "email_id": f"contact{i + 1:03d}@hospital.pk",
            "phone": f"+9242{random.randint(1000000, 9999999)}",
            "mobile_no": f"+923{random.randint(10, 49)}{random.randint(1000000, 9999999)}",
            "company_name": c["customer_name"],
            "link_doctype": "Customer", "link_name": c["customer_name"],
        })
    return rows


# ─── CRM Builders ────────────────────────────────────────────────────────────────

def build_leads(count: int) -> List[Dict]:
    sources = ["Walk In", "Website", "Referral", "Campaign", "Cold Calling"]
    rows = []
    for i in range(1, count + 1):
        prefix = random.choice(HOSPITAL_PREFIXES)
        locality = random.choice(LAHORE_LOCALITIES)
        rows.append({
            "first_name": prefix,
            "company_name": f"{prefix} Healthcare {locality}",
            "email_id": f"lead{i:04d}@healthcare.pk",
            "phone": f"+9242{random.randint(1000000, 9999999)}",
            "source": random.choice(sources),
            "territory": "Lahore",
            "status": random.choice(["Lead", "Open", "Replied", "Opportunity", "Interested"]),
            "company": COMPANY_NAME,
        })
    return rows


def build_opportunities(customers: List[Dict], items: List[Dict], count: int, years: int) -> Tuple:
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    svc_items = [i for i in items if not i["is_stock_item"]]

    opp_rows, oi_rows = [], []
    for i in range(count):
        name = f"OPP-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        opp_rows.append({
            "name": name, "naming_series": "OPP-.YYYY.-",
            "opportunity_from": "Customer", "party_name": cust["customer_name"],
            "status": random.choice(["Open", "Quotation", "Converted", "Lost", "Replied"]),
            "company": COMPANY_NAME, "transaction_date": dates[i].isoformat(),
            "opportunity_amount": random.randint(100000, 5000000),
        })
        item = random.choice(svc_items)
        oi_rows.append({
            "parent": name, "parenttype": "Opportunity", "parentfield": "items",
            "item_code": item["item_code"], "qty": random.randint(1, 12),
            "uom": item["stock_uom"], "rate": random.randint(10000, 300000),
        })
    return opp_rows, oi_rows


def build_contracts(customers: List[Dict], years: int) -> List[Dict]:
    rows = []
    # Government waste management contracts
    govt_customers = [c for c in customers if "Government" in c.get("customer_group", "") or random.random() < 0.3][:15]
    for i, cust in enumerate(govt_customers):
        start_dt = date.today() - timedelta(days=random.randint(180, 365 * years))
        end_dt = start_dt + timedelta(days=random.choice([365, 730, 1095]))
        rows.append({
            "party_type": "Customer", "party_name": cust["customer_name"],
            "start_date": start_dt.isoformat(), "end_date": end_dt.isoformat(),
            "status": "Active" if end_dt > date.today() else "Inactive",
            "contract_terms": f"Healthcare waste management services contract for {cust['customer_name']}. "
                              f"Scope: collection, transport, and incineration of infectious, pathological, "
                              f"sharps, pharmaceutical, and chemical waste. Contract value: PKR {random.randint(5, 50)}M/year. "
                              f"KPIs: 99% pickup compliance, max 24hr turnaround, monthly compliance reporting.",
        })
    return rows


# ─── Transaction Builders ────────────────────────────────────────────────────────

def build_quotations(customers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"] and "BIO" in i["item_code"]]
    svc_items = [i for i in items if not i["is_stock_item"]]

    q_rows, qi_rows = [], []
    for i in range(count):
        name = f"QTN-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        tx = dates[i]
        q_rows.append({
            "name": name, "naming_series": "QTN-.YYYY.-",
            "quotation_to": "Customer", "party_name": cust["customer_name"],
            "transaction_date": tx.isoformat(),
            "valid_till": (tx + timedelta(days=30)).isoformat(),
            "company": COMPANY_NAME,
        })
        # Equipment line
        if random.random() < 0.6:
            eq = random.choice(stock_items) if stock_items else random.choice(items)
            qi_rows.append({
                "parent": name, "parenttype": "Quotation", "parentfield": "items",
                "item_code": eq["item_code"], "qty": random.randint(1, 5),
                "uom": "Nos", "rate": random.randint(150000, 3500000),
            })
        # Service line
        if random.random() < 0.7:
            svc = random.choice(svc_items) if svc_items else random.choice(items)
            qi_rows.append({
                "parent": name, "parenttype": "Quotation", "parentfield": "items",
                "item_code": svc["item_code"], "qty": random.randint(1, 24),
                "uom": svc["stock_uom"], "rate": random.randint(5000, 300000),
            })
    return q_rows, qi_rows


def build_sales_orders(customers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"] and i["is_sales_item"]]
    waste_svc_items = [i for i in items if "SVC-WASTE" in i["item_code"]]
    bio_svc_items = [i for i in items if "SVC-BIO" in i["item_code"] or "SVC-TRN" in i["item_code"] or "SVC-INC" in i["item_code"]]

    so_rows, soi_rows = [], []
    for i in range(count):
        name = f"SO-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        tx = dates[i]
        so_rows.append({
            "name": name, "naming_series": "SO-.YYYY.-",
            "customer": cust["customer_name"],
            "transaction_date": tx.isoformat(),
            "delivery_date": (tx + timedelta(days=random.randint(2, 14))).isoformat(),
            "company": COMPANY_NAME,
        })

        # Determine order type: 50% waste service, 30% equipment, 20% biomedical service
        r = random.random()
        if r < 0.50 and waste_svc_items:
            # Waste collection order
            for wcat in random.sample(waste_svc_items, min(random.randint(1, 3), len(waste_svc_items))):
                soi_rows.append({
                    "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                    "item_code": wcat["item_code"], "qty": random.randint(100, 2000),
                    "uom": "Kg", "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                    "rate": random.randint(180, 650),
                })
        elif r < 0.80 and stock_items:
            eq = random.choice(stock_items)
            soi_rows.append({
                "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                "item_code": eq["item_code"], "qty": random.randint(1, 6),
                "uom": "Nos", "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(150000, 3500000),
            })
        elif bio_svc_items:
            svc = random.choice(bio_svc_items)
            soi_rows.append({
                "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                "item_code": svc["item_code"], "qty": random.randint(1, 12),
                "uom": svc["stock_uom"], "warehouse": "",
                "rate": random.randint(15000, 300000),
            })
        else:
            eq = random.choice(stock_items) if stock_items else random.choice(items)
            soi_rows.append({
                "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                "item_code": eq["item_code"], "qty": 1, "uom": "Nos",
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(100000, 2000000),
            })

    return so_rows, soi_rows


def build_purchase_orders(suppliers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    purchase_items = [i for i in items if i["is_purchase_item"]]

    po_rows, poi_rows = [], []
    for i in range(count):
        name = f"PO-DEMO-{i + 1:06d}"
        supplier = random.choice(suppliers)
        tx = dates[i]
        sched = (tx + timedelta(days=random.randint(7, 45))).isoformat()
        po_rows.append({
            "name": name, "naming_series": "PO-.YYYY.-",
            "supplier": supplier["supplier_name"],
            "transaction_date": tx.isoformat(), "schedule_date": sched,
            "company": COMPANY_NAME,
        })
        # 1-3 items per PO
        for _ in range(random.randint(1, 3)):
            item = random.choice(purchase_items)
            poi_rows.append({
                "parent": name, "parenttype": "Purchase Order", "parentfield": "items",
                "item_code": item["item_code"], "qty": random.randint(1, 50),
                "uom": item["stock_uom"],
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(500, 3000000),
                "schedule_date": sched,
            })
    return po_rows, poi_rows


def build_material_requests(items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"]]

    mr_rows, mri_rows = [], []
    for i in range(count):
        name = f"MR-DEMO-{i + 1:06d}"
        tx = dates[i]
        mr_type = random.choice(["Purchase", "Material Transfer", "Material Issue"])
        mr_rows.append({
            "name": name, "naming_series": "MAT-MR-.YYYY.-",
            "material_request_type": mr_type,
            "transaction_date": tx.isoformat(),
            "schedule_date": (tx + timedelta(days=random.randint(3, 14))).isoformat(),
            "company": COMPANY_NAME,
        })
        for _ in range(random.randint(1, 4)):
            item = random.choice(stock_items)
            mri_rows.append({
                "parent": name, "parenttype": "Material Request", "parentfield": "items",
                "item_code": item["item_code"], "qty": random.randint(1, 100),
                "uom": item["stock_uom"],
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "schedule_date": (tx + timedelta(days=random.randint(3, 14))).isoformat(),
            })
    return mr_rows, mri_rows


def build_purchase_receipts(suppliers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    purchase_items = [i for i in items if i["is_purchase_item"]]

    pr_rows, pri_rows = [], []
    for i in range(count):
        name = f"PR-DEMO-{i + 1:06d}"
        supplier = random.choice(suppliers)
        tx = dates[i]
        pr_rows.append({
            "name": name, "naming_series": "MAT-PRE-.YYYY.-",
            "supplier": supplier["supplier_name"],
            "posting_date": tx.isoformat(), "company": COMPANY_NAME,
        })
        for _ in range(random.randint(1, 3)):
            item = random.choice(purchase_items)
            pri_rows.append({
                "parent": name, "parenttype": "Purchase Receipt", "parentfield": "items",
                "item_code": item["item_code"], "qty": random.randint(1, 50),
                "uom": item["stock_uom"],
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(500, 3000000),
            })
    return pr_rows, pri_rows


def build_stock_entries(items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"]]

    se_rows, sed_rows = [], []
    for i in range(count):
        name = f"STE-DEMO-{i + 1:06d}"
        tx = dates[i]
        purpose = random.choices(
            ["Material Receipt", "Material Transfer", "Material Issue"],
            weights=[50, 30, 20], k=1
        )[0]
        se_rows.append({
            "name": name, "naming_series": "STE-.YYYY.-",
            "purpose": purpose, "posting_date": tx.isoformat(),
            "company": COMPANY_NAME,
        })
        item = random.choice(stock_items)
        entry = {
            "parent": name, "parenttype": "Stock Entry", "parentfield": "items",
            "item_code": item["item_code"], "qty": random.randint(1, 20),
            "uom": item["stock_uom"], "basic_rate": random.randint(500, 3000000),
        }
        if purpose == "Material Receipt":
            entry["t_warehouse"] = f"Central Warehouse - {COMPANY_ABBR}"
        elif purpose == "Material Issue":
            entry["s_warehouse"] = f"Central Warehouse - {COMPANY_ABBR}"
        else:
            entry["s_warehouse"] = f"Central Warehouse - {COMPANY_ABBR}"
            wh_targets = ["PPE Store", "Spare Parts Store", "Container Store", "Vehicle Parts Store"]
            entry["t_warehouse"] = f"{random.choice(wh_targets)} - {COMPANY_ABBR}"
        sed_rows.append(entry)
    return se_rows, sed_rows


def build_delivery_notes(customers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"] and i["is_sales_item"]]

    dn_rows, dni_rows = [], []
    for i in range(count):
        name = f"DN-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        tx = dates[i]
        dn_rows.append({
            "name": name, "naming_series": "MAT-DN-.YYYY.-",
            "customer": cust["customer_name"],
            "posting_date": tx.isoformat(), "company": COMPANY_NAME,
        })
        item = random.choice(stock_items)
        dni_rows.append({
            "parent": name, "parenttype": "Delivery Note", "parentfield": "items",
            "item_code": item["item_code"], "qty": random.randint(1, 5),
            "uom": item["stock_uom"],
            "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
            "rate": random.randint(50000, 3500000),
        })
    return dn_rows, dni_rows


def build_sales_invoices(customers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    saleable = [i for i in items if i["is_sales_item"]]

    si_rows, sii_rows = [], []
    for i in range(count):
        name = f"SI-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        tx = dates[i]
        si_rows.append({
            "name": name, "naming_series": "ACC-SINV-.YYYY.-",
            "customer": cust["customer_name"],
            "posting_date": tx.isoformat(),
            "due_date": (tx + timedelta(days=random.choice([15, 30, 45, 60]))).isoformat(),
            "company": COMPANY_NAME,
        })
        item = random.choice(saleable)
        sii_rows.append({
            "parent": name, "parenttype": "Sales Invoice", "parentfield": "items",
            "item_code": item["item_code"], "qty": random.randint(1, 10),
            "uom": item["stock_uom"],
            "rate": random.randint(5000, 3500000) if item["is_stock_item"] else random.randint(5000, 300000),
        })
    return si_rows, sii_rows


def build_purchase_invoices(suppliers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    purchase_items = [i for i in items if i["is_purchase_item"]]

    pi_rows, pii_rows = [], []
    for i in range(count):
        name = f"PI-DEMO-{i + 1:06d}"
        supplier = random.choice(suppliers)
        tx = dates[i]
        pi_rows.append({
            "name": name, "naming_series": "ACC-PINV-.YYYY.-",
            "supplier": supplier["supplier_name"],
            "posting_date": tx.isoformat(),
            "due_date": (tx + timedelta(days=random.choice([30, 45, 60]))).isoformat(),
            "company": COMPANY_NAME,
        })
        item = random.choice(purchase_items)
        pii_rows.append({
            "parent": name, "parenttype": "Purchase Invoice", "parentfield": "items",
            "item_code": item["item_code"], "qty": random.randint(1, 30),
            "uom": item["stock_uom"],
            "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
            "rate": random.randint(500, 3000000),
        })
    return pi_rows, pii_rows


# ─── Service & Maintenance Builders ─────────────────────────────────────────────

def build_issues(customers, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    issue_types = [
        "Equipment Malfunction", "Preventive Maintenance Due", "Calibration Required",
        "Waste Container Replacement", "Pickup Schedule Change", "Compliance Query",
        "Billing Inquiry", "Installation Support", "Training Request",
        "Emergency Waste Pickup", "Incinerator Issue", "Fleet Breakdown",
    ]

    rows = []
    for i in range(count):
        cust = random.choice(customers)
        rows.append({
            "subject": f"{random.choice(issue_types)} - {cust['customer_name'][:30]} #{i + 1:05d}",
            "customer": cust["customer_name"],
            "raised_by": f"support{i + 1:04d}@enxi.pk",
            "status": random.choice(["Open", "Replied", "Resolved", "Closed"]),
            "priority": random.choice(["Low", "Medium", "High", "Urgent"]),
            "opening_date": dates[i].isoformat(),
        })
    return rows


def build_projects(customers, years) -> Tuple[List[Dict], List[Dict]]:
    proj_templates = [
        ("Punjab Tertiary Hospitals Waste Management", "Waste Operations"),
        ("Lahore District Hospital Waste Contract", "Waste Operations"),
        ("Incinerator Facility Upgrade - Lahore", "Incinerator Operations"),
        ("Incinerator Facility Setup - Faisalabad", "Incinerator Operations"),
        ("Fleet Modernization Phase 1", "Fleet & Transport"),
        ("Fleet Modernization Phase 2", "Fleet & Transport"),
        ("Hospital Waste Training Program 2025", "Training & Development"),
        ("PPE Distribution Campaign", "Waste Operations"),
        ("GPS Tracking System Deployment", "IT & Systems"),
        ("Environmental Compliance Audit 2025", "Compliance & Environment"),
        ("Biomedical Equipment Installation - Mayo Hospital", "Biomedical Services"),
        ("AMC Rollout Q1 2025", "Biomedical Services"),
        ("Waste Segregation Training - Punjab", "Training & Development"),
        ("Route Optimization Project", "Fleet & Transport"),
        ("ERP System Implementation", "IT & Systems"),
        ("Quality Management System Setup", "Quality Assurance"),
        ("Incinerator Emissions Compliance Project", "Compliance & Environment"),
        ("New Hospital Onboarding Q2 2025", "Sales & Business Development"),
        ("Container Distribution Program", "Waste Operations"),
        ("Staff Capacity Building 2025", "Human Resources"),
    ]

    proj_rows, task_rows = [], []
    for i, (pname, dept) in enumerate(proj_templates):
        start_dt = date.today() - timedelta(days=random.randint(60, 365 * years))
        end_dt = start_dt + timedelta(days=random.randint(90, 365))
        status = "Open" if end_dt > date.today() else "Completed"
        proj_rows.append({
            "project_name": pname, "naming_series": "PROJ-.YYYY.-",
            "company": COMPANY_NAME, "status": status,
            "expected_start_date": start_dt.isoformat(),
            "expected_end_date": end_dt.isoformat(),
            "department": dept,
        })

        # Tasks per project
        task_names = [
            "Planning & Scoping", "Resource Allocation", "Procurement",
            "Execution Phase 1", "Execution Phase 2", "Testing & QA",
            "Training & Handover", "Closure & Reporting",
        ]
        for j, tname in enumerate(random.sample(task_names, random.randint(3, 6))):
            t_start = start_dt + timedelta(days=j * 15)
            t_end = t_start + timedelta(days=random.randint(10, 30))
            task_rows.append({
                "subject": f"{tname} - {pname[:40]}",
                "project": pname, "company": COMPANY_NAME,
                "status": random.choice(["Open", "Working", "Completed"]) if status == "Open" else "Completed",
                "priority": random.choice(["Low", "Medium", "High"]),
                "exp_start_date": t_start.isoformat(),
                "exp_end_date": t_end.isoformat(),
            })

    return proj_rows, task_rows


def build_maintenance(customers, items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    equip_items = [i for i in items if i["is_stock_item"] and "BIO" in i["item_code"]]

    mv_rows, mvp_rows = [], []
    for i in range(count):
        name = f"MV-DEMO-{i + 1:06d}"
        cust = random.choice(customers)
        tx = dates[i]
        mv_rows.append({
            "name": name, "naming_series": "MAT-MVS-.YYYY.-",
            "customer": cust["customer_name"],
            "mntc_date": tx.isoformat(),
            "company": COMPANY_NAME,
            "completion_status": random.choice(["Fully Completed", "Partially Completed"]),
            "maintenance_type": random.choice(["Scheduled", "Unscheduled", "Breakdown"]),
        })
        item = random.choice(equip_items) if equip_items else random.choice(items)
        mvp_rows.append({
            "parent": name, "parenttype": "Maintenance Visit", "parentfield": "purposes",
            "item_code": item["item_code"],
            "work_done": random.choice([
                "Preventive maintenance completed. All parameters within spec.",
                "Replaced faulty sensor. Calibration performed.",
                "Software update applied. Functionality verified.",
                "Cleaned and lubricated moving parts. Tested OK.",
                "Battery replaced. Full diagnostic run completed.",
                "Emergency repair - power supply unit replaced.",
                "Annual calibration performed. Certificate issued.",
            ]),
        })
    return mv_rows, mvp_rows


def build_quality_inspections(items, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    stock_items = [i for i in items if i["is_stock_item"]]

    rows = []
    for i in range(count):
        item = random.choice(stock_items)
        rows.append({
            "naming_series": "QI-.YYYY.-",
            "inspection_type": random.choice(["Incoming", "Outgoing", "In Process"]),
            "item_code": item["item_code"],
            "report_date": dates[i].isoformat(),
            "sample_size": random.randint(1, 10),
            "status": random.choices(["Accepted", "Rejected"], weights=[85, 15], k=1)[0],
            "company": COMPANY_NAME,
        })
    return rows


# ─── JSON Sidecar Builders (Operational Data) ───────────────────────────────────

def build_waste_events(customers, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    events = []
    for i in range(count):
        cust = random.choice(customers)
        cat, color, code, pct = random.choices(WASTE_CATEGORIES, weights=[c[3] for c in WASTE_CATEGORIES], k=1)[0]
        kg = round(random.uniform(5.0, 500.0), 2)
        events.append({
            "event_id": f"WASTE-EVT-{i + 1:07d}",
            "event_date": dates[i].isoformat(),
            "customer": cust["customer_name"],
            "waste_category": cat,
            "container_color": color,
            "weight_kg": kg,
            "pickup_status": random.choices(["Completed", "Partial", "Missed", "Rescheduled"], weights=[85, 8, 4, 3], k=1)[0],
            "crew_size": random.randint(2, 4),
            "vehicle_plate": f"LE-{random.randint(1000, 9999)}",
            "route_code": f"LHR-R{random.randint(1, 30):02d}",
            "disposal_certificate_no": f"DC-{dates[i].strftime('%Y%m')}-{i + 1:06d}",
            "manifest_no": f"MAN-{dates[i].strftime('%Y%m%d')}-{i + 1:05d}",
            "regulatory_note": "Punjab EPA compliant manifest captured",
        })
    return events


def build_incinerator_ops(count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)
    facilities = ["Incinerator Facility - Lahore", "Incinerator Facility - Faisalabad"]

    ops = []
    for i in range(count):
        dt = dates[i]
        total_kg = round(random.uniform(200, 2500), 1)
        ops.append({
            "batch_id": f"INC-BATCH-{i + 1:06d}",
            "facility": random.choice(facilities),
            "operation_date": dt.isoformat(),
            "start_time": f"{random.randint(6, 10):02d}:00",
            "end_time": f"{random.randint(14, 20):02d}:00",
            "total_waste_kg": total_kg,
            "waste_breakdown": {cat: round(total_kg * pct / 100, 1) for cat, _, _, pct in WASTE_CATEGORIES},
            "chamber_temperature_c": random.randint(850, 1200),
            "emissions_pm": round(random.uniform(5, 50), 1),
            "emissions_so2": round(random.uniform(1, 20), 1),
            "emissions_nox": round(random.uniform(5, 40), 1),
            "emissions_compliant": random.choices([True, False], weights=[95, 5], k=1)[0],
            "ash_generated_kg": round(total_kg * random.uniform(0.02, 0.08), 1),
            "operator": f"Operator-{random.randint(1, 8):03d}",
            "disposal_certificate": f"DISP-CERT-{dt.strftime('%Y%m')}-{i + 1:05d}",
        })
    return ops


def build_transport_logs(customers, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    logs = []
    for i in range(count):
        dt = dates[i]
        cust = random.choice(customers)
        logs.append({
            "trip_id": f"TRIP-{i + 1:07d}",
            "trip_date": dt.isoformat(),
            "vehicle_plate": f"LE-{random.randint(1000, 9999)}",
            "driver": f"Driver-{random.randint(1, 25):03d}",
            "route_code": f"LHR-R{random.randint(1, 30):02d}",
            "origin": "EnXi Depot - Lahore",
            "destination": cust["customer_name"],
            "waste_collected_kg": round(random.uniform(50, 800), 1),
            "containers_collected": random.randint(2, 15),
            "departure_time": f"{random.randint(5, 8):02d}:{random.randint(0, 59):02d}",
            "arrival_time": f"{random.randint(8, 12):02d}:{random.randint(0, 59):02d}",
            "return_time": f"{random.randint(12, 18):02d}:{random.randint(0, 59):02d}",
            "km_driven": random.randint(15, 120),
            "fuel_consumed_ltr": round(random.uniform(8, 45), 1),
            "incidents": random.choices(["None", "Minor Spill", "Vehicle Issue", "Access Delay"], weights=[90, 4, 3, 3], k=1)[0],
        })
    return logs


def build_training_sessions(customers, count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    programs = [
        "Waste Segregation at Source", "PPE Usage and Safety",
        "Biomedical Waste Handling SOP", "Sharps Safety Training",
        "Infection Control and Waste", "Regulatory Compliance Workshop",
        "Emergency Spill Response", "Incinerator Safety Training",
        "Vehicle Safety and Waste Transport", "Fire Safety Training",
    ]

    sessions = []
    for i in range(count):
        dt = dates[i]
        cust = random.choice(customers)
        sessions.append({
            "session_id": f"TRN-{i + 1:06d}",
            "session_date": dt.isoformat(),
            "program": random.choice(programs),
            "location": cust["customer_name"],
            "trainer": f"Trainer-{random.randint(1, 5):03d}",
            "participants": random.randint(10, 60),
            "duration_hours": random.choice([2, 3, 4, 6, 8]),
            "assessment_conducted": random.choices([True, False], weights=[70, 30], k=1)[0],
            "pass_rate_pct": random.randint(75, 100),
            "certificates_issued": random.randint(8, 55),
        })
    return sessions


def build_compliance_reports(years):
    reports = []
    for month_offset in range(years * 12):
        dt = date.today().replace(day=1) - timedelta(days=30 * month_offset)
        reports.append({
            "report_id": f"COMP-RPT-{dt.strftime('%Y%m')}",
            "report_month": dt.strftime("%B %Y"),
            "report_date": dt.isoformat(),
            "total_waste_collected_kg": round(random.uniform(40000, 120000), 0),
            "total_waste_incinerated_kg": round(random.uniform(38000, 115000), 0),
            "hospitals_served": random.randint(40, 55),
            "pickup_compliance_pct": round(random.uniform(96, 99.9), 1),
            "missed_pickups": random.randint(0, 8),
            "incidents_reported": random.randint(0, 5),
            "regulatory_audits": random.randint(0, 2),
            "audit_findings": random.choices(["None", "Minor", "Observation"], weights=[70, 20, 10], k=1)[0],
            "emissions_compliance_pct": round(random.uniform(94, 100), 1),
        })
    return reports


def build_disposal_certificates(count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    certs = []
    for i in range(count):
        dt = dates[i]
        certs.append({
            "certificate_no": f"DISP-CERT-{i + 1:06d}",
            "issue_date": dt.isoformat(),
            "facility": random.choice(["Incinerator Facility - Lahore", "Incinerator Facility - Faisalabad"]),
            "waste_category": random.choice([c[0] for c in WASTE_CATEGORIES]),
            "weight_kg": round(random.uniform(100, 2000), 1),
            "disposal_method": "Incineration",
            "chamber_temp_c": random.randint(850, 1200),
            "residue_disposed": True,
            "epa_reference": f"EPA-PB-{dt.strftime('%Y')}-{random.randint(1000, 9999)}",
        })
    return certs


def build_fuel_logs(count, years):
    start = date.today() - timedelta(days=365 * years)
    end = date.today()
    dates = daterange(start, end, count)

    logs = []
    for i in range(count):
        dt = dates[i]
        logs.append({
            "log_id": f"FUEL-{i + 1:07d}",
            "log_date": dt.isoformat(),
            "vehicle_plate": f"LE-{random.randint(1000, 9999)}",
            "fuel_type": random.choice(["Diesel", "Petrol"]),
            "quantity_ltr": round(random.uniform(20, 120), 1),
            "rate_per_ltr": round(random.uniform(270, 320), 2),
            "amount_pkr": 0,
            "odometer_reading": random.randint(10000, 250000),
            "fuel_station": random.choice(["Shell Gulberg", "PSO DHA", "Total Cantt", "Byco Johar Town", "Shell Wapda Town"]),
        })
        logs[-1]["amount_pkr"] = round(logs[-1]["quantity_ltr"] * logs[-1]["rate_per_ltr"], 0)
    return logs


def build_environmental_monitoring(years):
    records = []
    for week_offset in range(years * 52):
        dt = date.today() - timedelta(weeks=week_offset)
        for facility in ["Incinerator Facility - Lahore", "Incinerator Facility - Faisalabad"]:
            records.append({
                "record_id": f"ENV-{dt.strftime('%Y%m%d')}-{facility[:3]}",
                "monitoring_date": dt.isoformat(),
                "facility": facility,
                "ambient_air_pm25": round(random.uniform(20, 80), 1),
                "ambient_air_pm10": round(random.uniform(40, 150), 1),
                "stack_emission_pm": round(random.uniform(5, 45), 1),
                "stack_emission_so2": round(random.uniform(2, 25), 1),
                "stack_emission_nox": round(random.uniform(5, 35), 1),
                "noise_level_db": round(random.uniform(55, 85), 1),
                "water_quality_ph": round(random.uniform(6.5, 8.5), 1),
                "compliant": random.choices([True, False], weights=[92, 8], k=1)[0],
            })
    return records


def build_route_schedules(customers):
    routes = []
    # Cluster customers into routes
    for r in range(1, 31):
        route_customers = random.sample(customers, min(random.randint(3, 8), len(customers)))
        routes.append({
            "route_code": f"LHR-R{r:02d}",
            "route_name": f"Lahore Route {r:02d} - {random.choice(LAHORE_LOCALITIES)}",
            "day_of_week": random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]),
            "frequency": random.choice(["Daily", "3x/week", "2x/week", "Weekly"]),
            "stops": [{"stop_order": j + 1, "customer": c["customer_name"]} for j, c in enumerate(route_customers)],
            "estimated_duration_hrs": round(random.uniform(3, 8), 1),
            "vehicle_type": random.choice(["Hino 300", "Isuzu NPR", "Hyundai H-100"]),
        })
    return routes


# ─── Main Generation Function ────────────────────────────────────────────────────

def generate(cfg: VolumeConfig, out_dir: Path) -> None:
    random.seed(42)
    ensure_dir(out_dir)

    # ── Master Data ──
    companies = build_companies()
    branches = build_branches()
    departments = build_departments()
    designations = build_designations()
    warehouses = build_warehouses()
    cost_centers = build_cost_centers()
    customer_groups = build_customer_groups()
    supplier_groups = build_supplier_groups()
    territories = build_territory()
    item_groups = build_item_groups()
    brands = build_brands()
    customers = build_customers(cfg.hospitals)
    suppliers = build_suppliers()
    items = build_items(cfg.items_count)
    item_prices = build_item_prices(items)
    employees = build_employees(departments, cfg.employees_count)
    vehicles = build_vehicles(cfg.vehicles_count)
    drivers = build_drivers(employees)
    holiday_lists, holidays = build_holiday_list()
    addresses = build_addresses(customers, suppliers)
    contacts = build_contacts(customers)

    # ── CRM ──
    leads = build_leads(cfg.leads)
    opportunities, opportunity_items = build_opportunities(customers, items, cfg.opportunities, cfg.years)
    contracts = build_contracts(customers, cfg.years)

    # ── Transactions ──
    quotations, quotation_items = build_quotations(customers, items, cfg.quotations, cfg.years)
    sales_orders, so_items = build_sales_orders(customers, items, cfg.sales_orders, cfg.years)
    purchase_orders, po_items = build_purchase_orders(suppliers, items, cfg.purchase_orders, cfg.years)
    material_requests, mr_items = build_material_requests(items, cfg.material_requests, cfg.years)
    purchase_receipts, pr_items = build_purchase_receipts(suppliers, items, cfg.purchase_receipts, cfg.years)
    stock_entries, se_items = build_stock_entries(items, cfg.stock_entries, cfg.years)
    delivery_notes, dn_items = build_delivery_notes(customers, items, cfg.delivery_notes, cfg.years)
    sales_invoices, si_items = build_sales_invoices(customers, items, cfg.sales_invoices, cfg.years)
    purchase_invoices, pi_items = build_purchase_invoices(suppliers, items, cfg.purchase_invoices, cfg.years)

    # ── Service & Operations ──
    issues = build_issues(customers, cfg.issues, cfg.years)
    projects, tasks = build_projects(customers, cfg.years)
    maint_visits, maint_purposes = build_maintenance(customers, items, cfg.maintenance_visits, cfg.years)
    qi_rows = build_quality_inspections(items, cfg.quality_inspections, cfg.years)

    # ── JSON Sidecar ──
    waste_events = build_waste_events(customers, cfg.waste_events, cfg.years)
    incinerator_ops = build_incinerator_ops(cfg.incinerator_ops, cfg.years)
    transport_logs = build_transport_logs(customers, cfg.transport_logs, cfg.years)
    training_sessions = build_training_sessions(customers, cfg.training_sessions, cfg.years)
    compliance_reports = build_compliance_reports(cfg.years)
    disposal_certs = build_disposal_certificates(cfg.incinerator_ops, cfg.years)
    fuel_logs = build_fuel_logs(cfg.fuel_logs, cfg.years)
    env_monitoring = build_environmental_monitoring(cfg.years)
    route_schedules = build_route_schedules(customers)

    # ── Write CSVs ──
    write_csv(out_dir / "Company.csv", companies, ["name", "abbr", "country", "default_currency"])
    write_csv(out_dir / "Branch.csv", branches, ["branch"])
    write_csv(out_dir / "Department.csv", departments, ["department_name", "company"])
    write_csv(out_dir / "Designation.csv", designations, ["designation"])
    write_csv(out_dir / "Warehouse.csv", warehouses, ["warehouse_name", "name", "company"])
    write_csv(out_dir / "Cost_Center.csv", cost_centers, ["cost_center_name", "company", "parent_cost_center"])
    write_csv(out_dir / "Customer_Group.csv", customer_groups, ["customer_group_name", "parent_customer_group", "is_group"])
    write_csv(out_dir / "Supplier_Group.csv", supplier_groups, ["supplier_group_name", "parent_supplier_group", "is_group"])
    write_csv(out_dir / "Territory.csv", territories, ["territory_name", "parent_territory", "is_group"])
    write_csv(out_dir / "Item_Group.csv", item_groups, ["item_group_name", "parent_item_group", "is_group"])
    write_csv(out_dir / "Brand.csv", brands, ["brand"])
    write_csv(out_dir / "Customer.csv", customers, ["customer_name", "customer_type", "customer_group", "territory", "default_currency"])
    write_csv(out_dir / "Supplier.csv", suppliers, ["supplier_name", "supplier_type", "supplier_group", "country", "default_currency"])
    write_csv(out_dir / "Item.csv", items, ["item_code", "item_name", "item_group", "stock_uom", "brand", "is_stock_item", "is_sales_item", "is_purchase_item", "has_serial_no", "warranty_period"])
    write_csv(out_dir / "Item_Price.csv", item_prices, ["item_code", "price_list", "uom", "price_list_rate", "currency"])
    write_csv(out_dir / "Employee.csv", employees, ["employee_name", "first_name", "last_name", "company", "department", "designation", "date_of_birth", "date_of_joining", "gender", "employment_type", "status", "branch"])
    write_csv(out_dir / "Vehicle.csv", vehicles, ["license_plate", "make", "model", "fuel_type", "last_odometer", "uom", "acquisition_date", "vehicle_value"])
    write_csv(out_dir / "Driver.csv", drivers, ["naming_series", "full_name", "status", "license_number", "issuing_date", "expiry_date"])
    write_csv(out_dir / "Holiday_List.csv", holiday_lists, ["holiday_list_name", "from_date", "to_date", "company"])
    write_csv(out_dir / "Holiday.csv", holidays, ["holiday_list", "holiday_date", "description"])
    write_csv(out_dir / "Address.csv", addresses, ["name", "address_title", "address_type", "address_line1", "city", "country", "links"])
    write_csv(out_dir / "Contact.csv", contacts, ["first_name", "last_name", "email_id", "phone", "mobile_no", "company_name", "link_doctype", "link_name"])
    write_csv(out_dir / "Lead.csv", leads, ["first_name", "company_name", "email_id", "phone", "source", "territory", "status", "company"])
    write_csv(out_dir / "Opportunity.csv", opportunities, ["name", "naming_series", "opportunity_from", "party_name", "status", "company", "transaction_date", "opportunity_amount"])
    write_csv(out_dir / "Opportunity_Item.csv", opportunity_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Contract.csv", contracts, ["party_type", "party_name", "start_date", "end_date", "status", "contract_terms"])
    write_csv(out_dir / "Quotation.csv", quotations, ["name", "naming_series", "quotation_to", "party_name", "transaction_date", "valid_till", "company"])
    write_csv(out_dir / "Quotation_Item.csv", quotation_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Sales_Order.csv", sales_orders, ["name", "naming_series", "customer", "transaction_date", "delivery_date", "company"])
    write_csv(out_dir / "Sales_Order_Item.csv", so_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate"])
    write_csv(out_dir / "Purchase_Order.csv", purchase_orders, ["name", "naming_series", "supplier", "transaction_date", "schedule_date", "company"])
    write_csv(out_dir / "Purchase_Order_Item.csv", po_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate", "schedule_date"])
    write_csv(out_dir / "Material_Request.csv", material_requests, ["name", "naming_series", "material_request_type", "transaction_date", "schedule_date", "company"])
    write_csv(out_dir / "Material_Request_Item.csv", mr_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "schedule_date"])
    write_csv(out_dir / "Purchase_Receipt.csv", purchase_receipts, ["name", "naming_series", "supplier", "posting_date", "company"])
    write_csv(out_dir / "Purchase_Receipt_Item.csv", pr_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate"])
    write_csv(out_dir / "Stock_Entry.csv", stock_entries, ["name", "naming_series", "purpose", "posting_date", "company"])
    write_csv(out_dir / "Stock_Entry_Detail.csv", se_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "t_warehouse", "s_warehouse", "basic_rate"])
    write_csv(out_dir / "Delivery_Note.csv", delivery_notes, ["name", "naming_series", "customer", "posting_date", "company"])
    write_csv(out_dir / "Delivery_Note_Item.csv", dn_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate"])
    write_csv(out_dir / "Sales_Invoice.csv", sales_invoices, ["name", "naming_series", "customer", "posting_date", "due_date", "company"])
    write_csv(out_dir / "Sales_Invoice_Item.csv", si_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Purchase_Invoice.csv", purchase_invoices, ["name", "naming_series", "supplier", "posting_date", "due_date", "company"])
    write_csv(out_dir / "Purchase_Invoice_Item.csv", pi_items, ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "warehouse", "rate"])
    write_csv(out_dir / "Issue.csv", issues, ["subject", "customer", "raised_by", "status", "priority", "opening_date"])
    write_csv(out_dir / "Project.csv", projects, ["project_name", "naming_series", "company", "status", "expected_start_date", "expected_end_date", "department"])
    write_csv(out_dir / "Task.csv", tasks, ["subject", "project", "company", "status", "priority", "exp_start_date", "exp_end_date"])
    write_csv(out_dir / "Maintenance_Visit.csv", maint_visits, ["name", "naming_series", "customer", "mntc_date", "company", "completion_status", "maintenance_type"])
    write_csv(out_dir / "Maintenance_Visit_Purpose.csv", maint_purposes, ["parent", "parenttype", "parentfield", "item_code", "work_done"])
    write_csv(out_dir / "Quality_Inspection.csv", qi_rows, ["naming_series", "inspection_type", "item_code", "report_date", "sample_size", "status", "company"])

    # ── Write JSON Sidecars ──
    write_json(out_dir / "waste_collection_events.json", {"events": waste_events})
    write_json(out_dir / "incinerator_operations.json", {"operations": incinerator_ops})
    write_json(out_dir / "transport_logs.json", {"logs": transport_logs})
    write_json(out_dir / "training_sessions.json", {"sessions": training_sessions})
    write_json(out_dir / "compliance_reports.json", {"reports": compliance_reports})
    write_json(out_dir / "disposal_certificates.json", {"certificates": disposal_certs})
    write_json(out_dir / "vehicle_fuel_logs.json", {"logs": fuel_logs})
    write_json(out_dir / "environmental_monitoring.json", {"records": env_monitoring})
    write_json(out_dir / "route_schedules.json", {"routes": route_schedules})
    write_json(out_dir / "financial_events.json", {"entries": []})  # Placeholder for backward compat

    # ── Validation Report ──
    outputs = {
        "Company": len(companies), "Branch": len(branches), "Department": len(departments),
        "Designation": len(designations), "Warehouse": len(warehouses), "Cost Center": len(cost_centers),
        "Customer Group": len(customer_groups), "Supplier Group": len(supplier_groups),
        "Territory": len(territories), "Item Group": len(item_groups), "Brand": len(brands),
        "Customer": len(customers), "Supplier": len(suppliers), "Item": len(items),
        "Item Price": len(item_prices), "Employee": len(employees), "Vehicle": len(vehicles),
        "Driver": len(drivers), "Holiday List": len(holiday_lists), "Holiday": len(holidays),
        "Address": len(addresses), "Contact": len(contacts),
        "Lead": len(leads), "Opportunity": len(opportunities), "Contract": len(contracts),
        "Quotation": len(quotations), "Quotation Item": len(quotation_items),
        "Sales Order": len(sales_orders), "Sales Order Item": len(so_items),
        "Purchase Order": len(purchase_orders), "Purchase Order Item": len(po_items),
        "Material Request": len(material_requests), "Material Request Item": len(mr_items),
        "Purchase Receipt": len(purchase_receipts), "Purchase Receipt Item": len(pr_items),
        "Stock Entry": len(stock_entries), "Stock Entry Detail": len(se_items),
        "Delivery Note": len(delivery_notes), "Delivery Note Item": len(dn_items),
        "Sales Invoice": len(sales_invoices), "Sales Invoice Item": len(si_items),
        "Purchase Invoice": len(purchase_invoices), "Purchase Invoice Item": len(pi_items),
        "Issue": len(issues), "Project": len(projects), "Task": len(tasks),
        "Maintenance Visit": len(maint_visits), "Quality Inspection": len(qi_rows),
        "Waste Events (JSON)": len(waste_events), "Incinerator Ops (JSON)": len(incinerator_ops),
        "Transport Logs (JSON)": len(transport_logs), "Training Sessions (JSON)": len(training_sessions),
        "Compliance Reports (JSON)": len(compliance_reports), "Disposal Certificates (JSON)": len(disposal_certs),
        "Fuel Logs (JSON)": len(fuel_logs), "Environmental Monitoring (JSON)": len(env_monitoring),
        "Route Schedules (JSON)": len(route_schedules),
    }

    write_json(out_dir / "validation_report.json", {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "company": COMPANY_NAME,
        "location": "Lahore, Pakistan",
        "time_horizon_years": cfg.years,
        "domain": ["Healthcare waste management", "Biomedical equipment services", "Incinerator operations", "Fleet logistics"],
        "generated_counts": outputs,
        "total_csv_files": 48,
        "total_json_files": 10,
        "total_records": sum(v for v in outputs.values() if isinstance(v, int)),
    })

    print(f"Comprehensive seed generated in: {out_dir}")
    print(json.dumps(outputs, indent=2))


# ─── CLI ─────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Generate comprehensive EnXi healthcare waste management seed data")
    p.add_argument("--output", default=str(OUTPUT_DIR))
    p.add_argument("--years", type=int, default=2)
    p.add_argument("--hospitals", type=int, default=55)
    p.add_argument("--items", type=int, default=500)
    p.add_argument("--employees", type=int, default=120)
    p.add_argument("--vehicles", type=int, default=35)
    p.add_argument("--sales-orders", type=int, default=1500)
    p.add_argument("--purchase-orders", type=int, default=300)
    p.add_argument("--quotations", type=int, default=600)
    p.add_argument("--waste-events", type=int, default=3500)
    return p.parse_args()


def main():
    args = parse_args()
    cfg = VolumeConfig(
        years=args.years, hospitals=args.hospitals, items_count=args.items,
        employees_count=args.employees, vehicles_count=args.vehicles,
        sales_orders=args.sales_orders, purchase_orders=args.purchase_orders,
        quotations=args.quotations, waste_events=args.waste_events,
    )
    generate(cfg, Path(args.output))


if __name__ == "__main__":
    main()
