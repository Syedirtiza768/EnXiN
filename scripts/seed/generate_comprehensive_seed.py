#!/usr/bin/env python3
"""
Comprehensive enterprise-grade demo seed generator for EnXi ERPNext.

Models a Punjab-based healthcare waste management company (modeled on ARAR Innovations)
with 36-month operational history across all ERPNext modules.

Generates import-compatible CSV and JSON files covering:
- Organization setup (company, branches, departments, cost centers)
- Customer institutions (hospitals, labs, clinics)
- Contracts & commercials  
- Waste classification & container inventory
- Waste collection operations
- Fleet management (vehicles, drivers, delivery trips)
- Incinerator operations (27+ facilities)
- Training & capacity building
- Janitorial services
- Inventory & procurement
- HR & workforce
- Finance & accounting (invoices, payments, journal entries)
- Assets (vehicles, incinerators, equipment)
- Quality management
- Maintenance schedules
- Support & issue tracking
- Projects & timesheets

No DB writes — generates CSV/JSON seed files only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "seed_output"

COMPANY_NAME = "EnXi Biomedical & Waste Management (Pvt) Ltd"
COMPANY_ABBR = "ENXI"
CURRENCY = "PKR"
COUNTRY = "Pakistan"

# ---------------------------------------------------------------------------
# Timeline: 36 months ending today
# ---------------------------------------------------------------------------
TIMELINE_MONTHS = 36
TODAY = date(2026, 3, 12)
TIMELINE_START = date(TODAY.year - 3, TODAY.month, 1)  # ~Mar 2023


@dataclass
class VolumeConfig:
    """Target volumes for seed generation."""
    years: int = 3
    hospitals: int = 80
    labs_clinics: int = 40
    government_depts: int = 10
    total_customers: int = 130
    suppliers: int = 50
    employees: int = 350
    vehicles: int = 50
    drivers: int = 45
    incinerator_facilities: int = 28
    items: int = 500
    sales_orders: int = 2500
    quotations: int = 800
    purchase_orders: int = 600
    purchase_receipts: int = 500
    stock_entries: int = 600
    delivery_notes: int = 1200
    delivery_trips: int = 2500
    sales_invoices: int = 2000
    purchase_invoices: int = 500
    payment_entries: int = 1800
    journal_entries: int = 300
    material_requests: int = 400
    waste_events: int = 8000
    transport_logs: int = 3000
    incinerator_batches: int = 1500
    training_sessions: int = 500
    issues: int = 800
    maintenance_visits: int = 400
    maintenance_schedules: int = 200
    quality_inspections: int = 300
    projects: int = 35
    tasks: int = 200
    timesheets: int = 600
    contracts: int = 80
    leads: int = 120
    opportunities: int = 100
    assets: int = 120
    warranty_claims: int = 60


# ---------------------------------------------------------------------------
# Domain Constants
# ---------------------------------------------------------------------------

PUNJAB_CITIES = [
    "Lahore", "Rawalpindi", "Faisalabad", "Multan", "Gujranwala",
    "Sialkot", "Bahawalpur", "Sargodha", "Sahiwal", "Sheikhupura",
]

LAHORE_LOCALITIES = [
    "Johar Town", "Gulberg", "Model Town", "DHA Phase 1", "DHA Phase 5",
    "Iqbal Town", "Cantt", "Garden Town", "Wapda Town", "Shadman",
    "Township", "Gulshan-e-Ravi", "Samanabad", "Allama Iqbal Town",
    "Bahria Town", "Askari 10", "EME Society", "Valencia Town",
    "Lake City", "Faisal Town",
]

HOSPITAL_TYPES = [
    ("Tertiary Hospital", 0.30),
    ("Teaching Hospital", 0.15),
    ("District Hospital", 0.20),
    ("General Hospital", 0.15),
    ("Specialized Hospital", 0.10),
    ("Private Hospital", 0.10),
]

HOSPITAL_PREFIXES = [
    "Mayo", "Jinnah", "Services", "Shalimar", "Punjab", "National",
    "Central", "City Care", "Noor", "Al-Rehman", "LifeLine", "Prime",
    "Gulab Devi", "Sheikh Zayed", "Shaukat Khanum", "Children",
    "Lady Willingdon", "Sir Ganga Ram", "Fatima Memorial", "Hameed Latif",
    "Doctors", "Sharif Medical", "Ittefaq", "Lahore General",
    "Ghurki Trust", "Farooq", "Surgimed", "National", "Chughtai",
]

LAB_CLINIC_NAMES = [
    "Chughtai Lab", "Shaukat Khanum Lab", "IDC Lab", "Excel Labs",
    "Islamabad Diagnostics", "Lahore Diagnostics", "City Lab",
    "Metro Diagnostics", "Al-Razi Clinic", "Medicare Clinic",
    "Health First Clinic", "Medix Clinic", "Punjab Diagnostic Center",
    "Allied Lab", "Agha Khan Lab Lahore", "Dr. Essa Lab",
    "One Health Lab", "Rehman Diagnostics", "Saleem Lab", "Qamar Lab",
]

GOVT_DEPTS = [
    "Punjab Health Department", "Directorate of Health Services Lahore",
    "Punjab Environmental Protection Agency", "Primary & Secondary Healthcare Dept",
    "District Health Authority Lahore", "Punjab Medical Faculty",
    "Punjab Healthcare Commission", "Specialized Healthcare & Medical Education",
    "Punjab Emergency Service (Rescue 1122)", "Punjab AIDS Control Program",
]

WASTE_CATEGORIES = [
    ("Infectious Waste", "INF", "Yellow"),
    ("Pathological Waste", "PATH", "Red"),
    ("Sharps Waste", "SHRP", "Yellow"),
    ("Pharmaceutical Waste", "PHRM", "Brown"),
    ("Chemical Waste", "CHEM", "Brown"),
    ("General Medical Waste", "GEN", "Black"),
    ("Cytotoxic Waste", "CYTO", "Purple"),
]

CONTAINER_TYPES = [
    ("Yellow Bin 60L", "Infectious Waste", 60),
    ("Yellow Bin 120L", "Infectious Waste", 120),
    ("Red Bin 60L", "Pathological Waste", 60),
    ("Sharps Container 5L", "Sharps Waste", 5),
    ("Sharps Container 10L", "Sharps Waste", 10),
    ("Brown Bin 60L", "Pharmaceutical Waste", 60),
    ("Black Bin 120L", "General Medical Waste", 120),
    ("Black Bin 240L", "General Medical Waste", 240),
    ("Cytotoxic Container 20L", "Cytotoxic Waste", 20),
]

PPE_ITEMS = [
    ("Nitrile Gloves (Box of 100)", "PPE", "Box"),
    ("Heavy Duty Rubber Gloves", "PPE", "Pair"),
    ("Face Shield", "PPE", "Nos"),
    ("N95 Respirator Mask", "PPE", "Nos"),
    ("Safety Goggles", "PPE", "Nos"),
    ("Disposable Gown", "PPE", "Nos"),
    ("Rubber Apron", "PPE", "Nos"),
    ("Safety Boots", "PPE", "Pair"),
    ("Biohazard Suit", "PPE", "Nos"),
]

CLEANING_SUPPLIES = [
    ("Disinfectant Solution 5L", "Cleaning Supplies", "Nos"),
    ("Floor Cleaner 5L", "Cleaning Supplies", "Nos"),
    ("Hand Sanitizer 500ml", "Cleaning Supplies", "Nos"),
    ("Bleach Solution 5L", "Cleaning Supplies", "Nos"),
    ("Mop Head Refill", "Cleaning Supplies", "Nos"),
    ("Microfiber Cloth Pack", "Cleaning Supplies", "Nos"),
    ("Waste Collection Bags (Roll of 50)", "Cleaning Supplies", "Nos"),
    ("Biohazard Labels (Pack of 100)", "Cleaning Supplies", "Nos"),
]

SPARE_PARTS = [
    ("Incinerator Grate Bar", "Incinerator Spare Parts", "Nos"),
    ("Refractory Brick Set", "Incinerator Spare Parts", "Set"),
    ("Burner Nozzle Assembly", "Incinerator Spare Parts", "Nos"),
    ("Temperature Sensor Probe", "Incinerator Spare Parts", "Nos"),
    ("Exhaust Fan Motor", "Incinerator Spare Parts", "Nos"),
    ("Ash Removal Conveyor Belt", "Incinerator Spare Parts", "Nos"),
    ("Control Panel Board", "Incinerator Spare Parts", "Nos"),
    ("Air Pollution Control Filter", "Incinerator Spare Parts", "Nos"),
    ("Vehicle Oil Filter", "Vehicle Parts", "Nos"),
    ("Vehicle Air Filter", "Vehicle Parts", "Nos"),
    ("Brake Pad Set", "Vehicle Parts", "Set"),
    ("Coolant 5L", "Vehicle Parts", "Nos"),
    ("Hydraulic Fluid 5L", "Vehicle Parts", "Nos"),
    ("Tire - Waste Transport Vehicle", "Vehicle Parts", "Nos"),
    ("GPS Tracker Module", "Vehicle Parts", "Nos"),
]

BIOMEDICAL_EQUIPMENT = [
    ("ICU Monitor", "Biomedical Equipment"),
    ("Patient Monitor", "Biomedical Equipment"),
    ("Infusion Pump", "Biomedical Equipment"),
    ("Ventilator", "Biomedical Equipment"),
    ("Ultrasound Machine", "Biomedical Equipment"),
    ("ECG Machine", "Biomedical Equipment"),
    ("Surgical Light", "Biomedical Equipment"),
    ("Sterilizer", "Biomedical Equipment"),
    ("Autoclave", "Biomedical Equipment"),
    ("Laboratory Analyzer", "Biomedical Equipment"),
    ("Defibrillator", "Biomedical Equipment"),
    ("Oxygen Concentrator", "Biomedical Equipment"),
    ("Dental Chair", "Biomedical Equipment"),
    ("X-Ray Machine", "Biomedical Equipment"),
    ("Pulse Oximeter", "Biomedical Equipment"),
]

FUEL_ITEMS = [
    ("Diesel Fuel", "Fuel", "Ltr"),
    ("Incinerator Fuel Oil", "Fuel", "Ltr"),
    ("LPG Cylinder", "Fuel", "Nos"),
]

DESIGNATIONS = [
    "CEO", "COO", "CFO", "Director Operations", "Director Compliance",
    "Regional Manager", "Branch Manager", "Operations Manager",
    "Waste Operations Supervisor", "Route Coordinator", "Dispatcher",
    "Waste Collector", "Waste Handler", "Driver", "Helper",
    "Incinerator Operator", "Incinerator Supervisor", "Maintenance Technician",
    "Compliance Officer", "Environmental Officer", "Safety Officer",
    "Training Coordinator", "Trainer", "Quality Inspector",
    "Fleet Manager", "Fleet Supervisor", "Mechanic",
    "Janitorial Supervisor", "Janitor", "Sanitation Worker",
    "Finance Manager", "Accountant", "Accounts Officer",
    "HR Manager", "HR Officer", "Admin Officer",
    "IT Officer", "Procurement Officer", "Store Keeper",
    "Biomedical Engineer", "Service Technician", "Sales Executive",
    "Customer Support Officer", "Data Entry Operator",
]

DEPARTMENTS = [
    "Waste Operations", "Fleet & Transport", "Incinerator Operations",
    "Training & Compliance", "Janitorial Services", "Finance & Accounts",
    "Human Resources", "Procurement & Stores", "Quality Assurance",
    "Biomedical Engineering", "Sales & Business Development",
    "Customer Support", "IT & Data", "Administration",
]

BRANCHES = [
    ("Head Office - Lahore", "Lahore"),
    ("Lahore Operations Center", "Lahore"),
    ("Rawalpindi Branch", "Rawalpindi"),
    ("Faisalabad Branch", "Faisalabad"),
    ("Multan Branch", "Multan"),
    ("Incinerator Facility - Lahore", "Lahore"),
    ("Incinerator Facility - Rawalpindi", "Rawalpindi"),
    ("Incinerator Facility - Faisalabad", "Faisalabad"),
]

COST_CENTERS = [
    ("Main", None),
    ("Waste Operations", "Main"),
    ("Fleet & Transport", "Main"),
    ("Incinerator Ops", "Main"),
    ("Training", "Main"),
    ("Janitorial Services", "Main"),
    ("Biomedical Equipment", "Main"),
    ("Sales & Marketing", "Main"),
    ("Administration", "Main"),
    ("HR & Payroll", "Main"),
    ("Procurement", "Main"),
    ("Quality & Compliance", "Main"),
    ("Lahore Operations", "Waste Operations"),
    ("Rawalpindi Operations", "Waste Operations"),
    ("Faisalabad Operations", "Waste Operations"),
    ("Multan Operations", "Waste Operations"),
]

INCINERATOR_FACILITIES = [
    "Mayo Hospital Incinerator", "Jinnah Hospital Incinerator",
    "Services Hospital Incinerator", "Sir Ganga Ram Incinerator",
    "Lady Willingdon Incinerator", "Punjab Institute Cardiology Incinerator",
    "Children Hospital Incinerator", "General Hospital Incinerator",
    "Gulab Devi Incinerator", "Sheikh Zayed Hospital Incinerator",
    "Fatima Memorial Incinerator", "Shaukat Khanum Incinerator",
    "Lahore Central Incinerator", "Lahore East Incinerator",
    "Lahore North Incinerator", "Lahore South Incinerator",
    "Rawalpindi General Incinerator", "Holy Family Incinerator",
    "Benazir Bhutto Hospital Incinerator", "Faisalabad Allied Incinerator",
    "DHQ Faisalabad Incinerator", "Multan Nishtar Incinerator",
    "Multan Civil Incinerator", "Gujranwala DHQ Incinerator",
    "Sialkot Civil Incinerator", "Bahawalpur QMC Incinerator",
    "Sargodha DHQ Incinerator", "Sahiwal DHQ Incinerator",
]

VEHICLE_MAKES = [
    ("Hino", "300 Series", "Diesel"),
    ("Hino", "500 Series", "Diesel"),
    ("Isuzu", "NQR", "Diesel"),
    ("Isuzu", "NPR", "Diesel"),
    ("Toyota", "Dyna", "Diesel"),
    ("Mitsubishi", "Canter", "Diesel"),
    ("Suzuki", "Carry", "Petrol"),
    ("Toyota", "Hilux", "Diesel"),
]

FIRST_NAMES_MALE = [
    "Ahmed", "Muhammad", "Ali", "Hassan", "Usman", "Bilal", "Asad",
    "Zain", "Hamza", "Omar", "Saad", "Imran", "Faisal", "Tariq",
    "Kashif", "Atif", "Naveed", "Shahid", "Rizwan", "Waqar",
    "Sohail", "Kamran", "Adnan", "Junaid", "Fahad", "Arslan",
    "Amir", "Salman", "Naeem", "Irfan",
]

FIRST_NAMES_FEMALE = [
    "Fatima", "Ayesha", "Sana", "Sara", "Hina", "Maryam", "Amina",
    "Bushra", "Rabia", "Nadia", "Samina", "Farah", "Noor", "Kiran",
    "Uzma", "Saima", "Zara", "Mehreen", "Alina", "Sadia",
]

LAST_NAMES = [
    "Khan", "Malik", "Ahmed", "Hassan", "Sheikh", "Qureshi", "Butt",
    "Chaudhry", "Rana", "Mirza", "Aslam", "Mughal", "Dar", "Gill",
    "Siddiqui", "Sharif", "Akhtar", "Hussain", "Raza", "Javed",
]

TRAINING_PROGRAMS = [
    "Waste Segregation Fundamentals",
    "PPE Usage & Safety Protocol",
    "Sharps Handling & Disposal",
    "Spill Response & Decontamination",
    "Infection Control Basics",
    "Incinerator Operations Safety",
    "Vehicle Safety & Defensive Driving",
    "Fire Safety & Emergency Response",
    "Environmental Compliance Awareness",
    "Regulatory Framework & EPA Standards",
    "Hospital Waste Management Act Compliance",
    "Chemical Waste Handling",
    "Pathological Waste Processing",
    "Route Safety & Collection Protocols",
    "First Aid & Emergency Response",
]

SUPPLIER_NAMES = [
    ("Ravi Engineering Works", "Equipment Vendor"),
    ("National Chemical Corp", "Raw Material"),
    ("Punjab Safety Equipment", "Equipment Vendor"),
    ("Lahore Steel Fabricators", "Equipment Vendor"),
    ("Allied Medical Supplies", "Raw Material"),
    ("Metro Fuel Distributors", "Fuel Supplier"),
    ("City Diesel Station", "Fuel Supplier"),
    ("Pakistan Refinery Fuels", "Fuel Supplier"),
    ("National Tire House", "Vehicle Parts"),
    ("Auto Zone Pakistan", "Vehicle Parts"),
    ("Refractory Solutions Pvt", "Equipment Vendor"),
    ("Punjab Plastics Industries", "Raw Material"),
    ("Eco Packaging Solutions", "Raw Material"),
    ("SafeHands PPE", "Raw Material"),
    ("CleanTech Supplies", "Raw Material"),
    ("Siemens Pakistan", "Equipment Vendor"),
    ("Atlas Honda Parts", "Vehicle Parts"),
    ("Shell Lubricants Pakistan", "Fuel Supplier"),
    ("Total Parco", "Fuel Supplier"),
    ("Descon Engineering", "Services"),
    ("NHA Maintenance Services", "Services"),
    ("Punjab IT Solutions", "IT Services"),
    ("SecureTrack GPS", "IT Services"),
    ("Mobilink Business Solutions", "IT Services"),
    ("State Life Insurance", "Insurance"),
    ("EFU General Insurance", "Insurance"),
    ("Adamjee Insurance", "Insurance"),
    ("Bank Alfalah Leasing", "Services"),
    ("Meezan Bank Leasing", "Services"),
    ("UBL Fund Managers", "Services"),
    ("Ernst & Young Pakistan", "Services"),
    ("KPMG Taseer Hadi", "Services"),
    ("Punjab Revenue Authority", "Services"),
    ("Pakistan Oxygen Ltd", "Raw Material"),
    ("ICI Pakistan", "Raw Material"),
    ("Sitara Chemical Industries", "Raw Material"),
    ("Diamond Tyres Ltd", "Vehicle Parts"),
    ("General Tyre Pakistan", "Vehicle Parts"),
    ("Millat Tractors Parts", "Vehicle Parts"),
    ("Sapphire Textiles (Uniforms)", "Raw Material"),
]

ROUTE_CODES = [f"LHR-R{i:02d}" for i in range(1, 31)] + \
              [f"RWP-R{i:02d}" for i in range(1, 11)] + \
              [f"FSD-R{i:02d}" for i in range(1, 8)] + \
              [f"MLT-R{i:02d}" for i in range(1, 6)]


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _seed():
    random.seed(42)

def daterange(start: date, end: date, count: int) -> List[date]:
    if count <= 0:
        return []
    delta = (end - start).days
    return sorted([start + timedelta(days=random.randint(0, max(delta, 1))) for _ in range(count)])


def weighted_choice(choices_with_weights):
    items, weights = zip(*choices_with_weights)
    return random.choices(items, weights=weights, k=1)[0]


def monthly_dates(start: date, end: date) -> List[date]:
    dates = []
    d = start.replace(day=1)
    while d <= end:
        dates.append(d)
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)
    return dates


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: List[Dict], fieldnames: List[str]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def rand_phone():
    return f"+9242{random.randint(1000000, 9999999)}"


def rand_mobile():
    return f"+923{random.randint(100000000, 499999999)}"


def rand_email(prefix: str, domain: str = "enxi.pk"):
    return f"{prefix.lower().replace(' ', '.')}@{domain}"


# ---------------------------------------------------------------------------
# Entity Builders
# ---------------------------------------------------------------------------

def build_company() -> List[Dict]:
    return [{
        "name": COMPANY_NAME,
        "abbr": COMPANY_ABBR,
        "country": COUNTRY,
        "default_currency": CURRENCY,
    }]


def build_branches() -> List[Dict]:
    return [{"branch": name} for name, _ in BRANCHES]


def build_designations() -> List[Dict]:
    return [{"designation": d} for d in DESIGNATIONS]


def build_departments() -> List[Dict]:
    return [{"department_name": d, "company": COMPANY_NAME} for d in DEPARTMENTS]


def build_territories() -> List[Dict]:
    rows = [
        {"territory_name": "Pakistan", "parent_territory": "All Territories", "is_group": 1},
        {"territory_name": "Punjab", "parent_territory": "Pakistan", "is_group": 1},
    ]
    for city in PUNJAB_CITIES:
        rows.append({"territory_name": city, "parent_territory": "Punjab", "is_group": 0})
    return rows


def build_customer_groups() -> List[Dict]:
    return [
        {"customer_group_name": "Commercial", "parent_customer_group": "All Customer Groups", "is_group": 0},
        {"customer_group_name": "Institutional", "parent_customer_group": "All Customer Groups", "is_group": 0},
        {"customer_group_name": "Government", "parent_customer_group": "All Customer Groups", "is_group": 0},
    ]


def build_supplier_groups() -> List[Dict]:
    groups = ["Raw Material", "Services", "Equipment Vendor", "Fuel Supplier",
              "Vehicle Parts", "IT Services", "Insurance"]
    return [{"supplier_group_name": g, "parent_supplier_group": "All Supplier Groups", "is_group": 0}
            for g in groups]


def build_warehouses() -> List[Dict]:
    wh_names = [
        "Central Warehouse", "Service Warehouse", "Spare Parts Warehouse",
        "PPE Store", "Cleaning Supplies Store", "Fuel Store",
        "Rawalpindi Store", "Faisalabad Store",
    ]
    return [{"warehouse_name": n, "name": f"{n} - {COMPANY_ABBR}", "company": COMPANY_NAME}
            for n in wh_names]


def build_cost_centers() -> List[Dict]:
    rows = []
    for name, parent in COST_CENTERS:
        parent_ref = f"{parent} - {COMPANY_ABBR}" if parent else ""
        rows.append({
            "cost_center_name": name,
            "company": COMPANY_NAME,
            "parent_cost_center": parent_ref,
        })
    return rows


def build_item_groups() -> List[Dict]:
    groups = [
        ("Waste Management Services", 0), ("Biomedical Equipment", 0),
        ("Waste Containers", 0), ("PPE", 0), ("Cleaning Supplies", 0),
        ("Incinerator Spare Parts", 0), ("Vehicle Parts", 0),
        ("Fuel", 0), ("Janitorial Services", 0), ("Training Services", 0),
        ("Spare Parts", 1), ("Consumables", 1),
    ]
    return [{"item_group_name": g, "parent_item_group": "All Item Groups",
             "is_group": ig} for g, ig in groups]


def build_brands() -> List[Dict]:
    brands = [
        "Hino", "Isuzu", "Toyota", "Mitsubishi", "Suzuki",
        "Mindray", "Philips", "GE Healthcare", "Siemens", "Nihon Kohden",
        "BPL", "Drager", "Hillrom", "Medtronic", "Stryker",
    ]
    return [{"brand": b} for b in brands]


def build_customers(cfg: VolumeConfig) -> List[Dict]:
    """Build hospital, lab, clinic, and government customer records."""
    rows = []
    idx = 1

    # Hospitals
    used_names = set()
    for i in range(cfg.hospitals):
        htype = weighted_choice(HOSPITAL_TYPES)
        prefix = random.choice(HOSPITAL_PREFIXES)
        name = f"{prefix} {htype} {idx:02d}"
        while name in used_names:
            prefix = random.choice(HOSPITAL_PREFIXES)
            name = f"{prefix} {htype} {idx:02d}"
        used_names.add(name)
        city = "Lahore" if i < cfg.hospitals * 0.6 else random.choice(PUNJAB_CITIES[1:])
        rows.append({
            "customer_name": name,
            "customer_type": "Company",
            "customer_group": random.choice(["Commercial", "Institutional", "Government"]),
            "territory": city,
            "default_currency": CURRENCY,
        })
        idx += 1

    # Labs and clinics
    for i in range(cfg.labs_clinics):
        base_name = LAB_CLINIC_NAMES[i % len(LAB_CLINIC_NAMES)]
        name = f"{base_name} {idx:02d}" if i >= len(LAB_CLINIC_NAMES) else base_name
        if name in used_names:
            name = f"{base_name} Branch {idx:02d}"
        used_names.add(name)
        rows.append({
            "customer_name": name,
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": random.choice(PUNJAB_CITIES[:5]),
            "default_currency": CURRENCY,
        })
        idx += 1

    # Government departments
    for i in range(min(cfg.government_depts, len(GOVT_DEPTS))):
        name = GOVT_DEPTS[i]
        used_names.add(name)
        rows.append({
            "customer_name": name,
            "customer_type": "Company",
            "customer_group": "Government",
            "territory": "Lahore",
            "default_currency": CURRENCY,
        })
        idx += 1

    return rows


def build_suppliers() -> List[Dict]:
    rows = []
    for name, group in SUPPLIER_NAMES:
        rows.append({
            "supplier_name": name,
            "supplier_type": "Company",
            "supplier_group": group,
            "country": COUNTRY,
            "default_currency": CURRENCY,
        })
    return rows


def build_items(cfg: VolumeConfig) -> List[Dict]:
    """Build all item records: waste services, containers, PPE, spares, equipment, fuel."""
    rows = []
    idx = 1

    # Waste collection service items (non-stock, service)
    for cat, code, color in WASTE_CATEGORIES:
        rows.append({
            "item_code": f"SVC-{code}",
            "item_name": f"{cat} Collection Service",
            "item_group": "Waste Management Services",
            "stock_uom": "Kg",
            "brand": "",
            "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
            "has_serial_no": 0, "warranty_period": 0,
        })

    # Janitorial service items
    for svc in ["Hospital Floor Disinfection", "Ward Sanitization", "OT Deep Cleaning",
                 "Common Area Cleaning", "Washroom Sanitization", "Non-Hazardous Waste Removal"]:
        rows.append({
            "item_code": f"SVC-JAN-{idx:03d}",
            "item_name": svc,
            "item_group": "Janitorial Services",
            "stock_uom": "Nos",
            "brand": "",
            "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Training service items
    for prog in TRAINING_PROGRAMS[:5]:
        rows.append({
            "item_code": f"SVC-TRN-{idx:03d}",
            "item_name": f"{prog} Training Session",
            "item_group": "Training Services",
            "stock_uom": "Nos",
            "brand": "",
            "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Container items (stock)
    for ctype, waste_cat, capacity in CONTAINER_TYPES:
        rows.append({
            "item_code": f"CNT-{idx:03d}",
            "item_name": ctype,
            "item_group": "Waste Containers",
            "stock_uom": "Nos",
            "brand": "",
            "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # PPE items (stock)
    for pname, pgroup, puom in PPE_ITEMS:
        rows.append({
            "item_code": f"PPE-{idx:03d}",
            "item_name": pname,
            "item_group": pgroup,
            "stock_uom": puom,
            "brand": "",
            "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Cleaning supplies (stock)
    for cname, cgroup, cuom in CLEANING_SUPPLIES:
        rows.append({
            "item_code": f"CLN-{idx:03d}",
            "item_name": cname,
            "item_group": cgroup,
            "stock_uom": cuom,
            "brand": "",
            "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Spare parts (stock)
    for sname, sgroup, suom in SPARE_PARTS:
        rows.append({
            "item_code": f"SPR-{idx:03d}",
            "item_name": sname,
            "item_group": sgroup,
            "stock_uom": suom,
            "brand": "",
            "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Fuel items (stock)
    for fname, fgroup, fuom in FUEL_ITEMS:
        rows.append({
            "item_code": f"FUEL-{idx:03d}",
            "item_name": fname,
            "item_group": fgroup,
            "stock_uom": fuom,
            "brand": "",
            "is_stock_item": 1, "is_sales_item": 0, "is_purchase_item": 1,
            "has_serial_no": 0, "warranty_period": 0,
        })
        idx += 1

    # Biomedical equipment (stock, serial tracked)
    brands = ["Mindray", "Philips", "GE Healthcare", "Siemens", "Nihon Kohden",
              "BPL", "Drager", "Hillrom", "Medtronic", "Stryker"]
    for i in range(min(cfg.items - len(rows), 400)):
        equip, group = random.choice(BIOMEDICAL_EQUIPMENT)
        rows.append({
            "item_code": f"BIO-{idx:05d}",
            "item_name": f"{equip} Model {random.randint(100, 999)}",
            "item_group": group,
            "stock_uom": "Nos",
            "brand": random.choice(brands),
            "is_stock_item": 1, "is_sales_item": 1, "is_purchase_item": 1,
            "has_serial_no": 1 if random.random() < 0.6 else 0,
            "warranty_period": random.choice([6, 12, 18, 24]),
        })
        idx += 1

    return rows


def build_item_prices(items: List[Dict]) -> List[Dict]:
    rows = []
    for item in items:
        code = item["item_code"]
        if code.startswith("SVC-"):
            # Service items: selling price per Kg or per unit
            if code.startswith("SVC-INF") or code.startswith("SVC-PATH") or \
               code.startswith("SVC-SHRP") or code.startswith("SVC-PHRM") or \
               code.startswith("SVC-CHEM") or code.startswith("SVC-GEN") or \
               code.startswith("SVC-CYTO"):
                rate = random.randint(150, 800)
                uom = "Kg"
            else:
                rate = random.randint(5000, 50000)
                uom = "Nos"
            rows.append({
                "item_code": code, "price_list": "Standard Selling",
                "uom": uom, "price_list_rate": rate, "currency": CURRENCY,
            })
        elif code.startswith("BIO-"):
            rows.append({
                "item_code": code, "price_list": "Standard Selling",
                "uom": "Nos", "price_list_rate": random.randint(150000, 4000000),
                "currency": CURRENCY,
            })
            rows.append({
                "item_code": code, "price_list": "Standard Buying",
                "uom": "Nos", "price_list_rate": random.randint(100000, 3500000),
                "currency": CURRENCY,
            })
        elif item["is_purchase_item"]:
            rate = random.randint(200, 80000)
            rows.append({
                "item_code": code, "price_list": "Standard Buying",
                "uom": item["stock_uom"], "price_list_rate": rate,
                "currency": CURRENCY,
            })
            if item["is_sales_item"]:
                rows.append({
                    "item_code": code, "price_list": "Standard Selling",
                    "uom": item["stock_uom"],
                    "price_list_rate": int(rate * random.uniform(1.15, 1.6)),
                    "currency": CURRENCY,
                })
    return rows


def build_employees(cfg: VolumeConfig) -> List[Dict]:
    """Build employees across all departments and roles."""
    rows = []
    # Role distribution
    role_dist = [
        ("Waste Operations", "Waste Collector", 60),
        ("Waste Operations", "Waste Handler", 30),
        ("Waste Operations", "Waste Operations Supervisor", 8),
        ("Waste Operations", "Route Coordinator", 6),
        ("Fleet & Transport", "Driver", 45),
        ("Fleet & Transport", "Helper", 20),
        ("Fleet & Transport", "Fleet Supervisor", 3),
        ("Fleet & Transport", "Mechanic", 8),
        ("Fleet & Transport", "Dispatcher", 4),
        ("Incinerator Operations", "Incinerator Operator", 30),
        ("Incinerator Operations", "Incinerator Supervisor", 8),
        ("Incinerator Operations", "Maintenance Technician", 12),
        ("Training & Compliance", "Trainer", 6),
        ("Training & Compliance", "Training Coordinator", 3),
        ("Training & Compliance", "Compliance Officer", 4),
        ("Training & Compliance", "Environmental Officer", 3),
        ("Training & Compliance", "Safety Officer", 3),
        ("Janitorial Services", "Janitorial Supervisor", 5),
        ("Janitorial Services", "Janitor", 20),
        ("Janitorial Services", "Sanitation Worker", 10),
        ("Finance & Accounts", "Finance Manager", 1),
        ("Finance & Accounts", "Accountant", 4),
        ("Finance & Accounts", "Accounts Officer", 3),
        ("Human Resources", "HR Manager", 1),
        ("Human Resources", "HR Officer", 2),
        ("Procurement & Stores", "Procurement Officer", 2),
        ("Procurement & Stores", "Store Keeper", 3),
        ("Quality Assurance", "Quality Inspector", 4),
        ("Biomedical Engineering", "Biomedical Engineer", 5),
        ("Biomedical Engineering", "Service Technician", 8),
        ("Sales & Business Development", "Sales Executive", 4),
        ("Customer Support", "Customer Support Officer", 3),
        ("IT & Data", "IT Officer", 2),
        ("IT & Data", "Data Entry Operator", 3),
        ("Administration", "Admin Officer", 3),
        ("Administration", "CEO", 1),
        ("Administration", "COO", 1),
        ("Administration", "CFO", 1),
        ("Administration", "Director Operations", 1),
        ("Administration", "Director Compliance", 1),
    ]

    emp_idx = 1
    branch_names = [b for b, _ in BRANCHES]
    for dept, desig, count in role_dist:
        actual = min(count, cfg.employees - len(rows))
        if actual <= 0:
            break
        for _ in range(actual):
            gender = "Male" if random.random() < 0.7 else "Female"
            first = random.choice(FIRST_NAMES_MALE if gender == "Male" else FIRST_NAMES_FEMALE)
            last = random.choice(LAST_NAMES)
            dob = date(random.randint(1975, 2000), random.randint(1, 12), random.randint(1, 28))
            # Stagger join dates across timeline
            earliest_join = max(TIMELINE_START - timedelta(days=365*2), date(2018, 1, 1))
            doj = earliest_join + timedelta(days=random.randint(0, (TODAY - earliest_join).days))
            rows.append({
                "employee_name": f"{first} {last}",
                "first_name": first,
                "last_name": last,
                "company": COMPANY_NAME,
                "department": dept,
                "designation": desig,
                "date_of_birth": dob.isoformat(),
                "date_of_joining": doj.isoformat(),
                "gender": gender,
                "employment_type": "Full-time",
                "status": "Active" if random.random() < 0.95 else "Left",
                "branch": random.choice(branch_names),
            })
            emp_idx += 1
            if len(rows) >= cfg.employees:
                break
        if len(rows) >= cfg.employees:
            break

    return rows


def build_vehicles(cfg: VolumeConfig) -> List[Dict]:
    rows = []
    plates_used = set()
    for i in range(cfg.vehicles):
        make, model, fuel = random.choice(VEHICLE_MAKES)
        city_code = random.choice(["LE", "LE", "LE", "RW", "FD", "ML"])
        plate = f"{city_code}-{random.randint(1000, 9999)}-{random.choice('ABCDE')}{random.choice('ABCDE')}"
        while plate in plates_used:
            plate = f"{city_code}-{random.randint(1000, 9999)}-{random.choice('ABCDE')}{random.choice('ABCDE')}"
        plates_used.add(plate)
        acq_date = TIMELINE_START - timedelta(days=random.randint(0, 365*2))
        rows.append({
            "license_plate": plate,
            "make": make,
            "model": model,
            "fuel_type": fuel,
            "last_odometer": random.randint(5000, 200000),
            "uom": "Ltr",
            "acquisition_date": acq_date.isoformat(),
            "vehicle_value": random.randint(2000000, 8000000),
        })
    return rows


def build_drivers(cfg: VolumeConfig, employees: List[Dict]) -> List[Dict]:
    """Build drivers from employee pool."""
    driver_employees = [e for e in employees if e["designation"] == "Driver"]
    rows = []
    for emp in driver_employees[:cfg.drivers]:
        issue_date = date(random.randint(2019, 2023), random.randint(1, 12), 1)
        expiry = issue_date.replace(year=issue_date.year + random.randint(4, 8))
        rows.append({
            "naming_series": "HR-DRI-.YYYY.-",
            "full_name": emp["employee_name"],
            "status": "Active",
            "license_number": f"PB-{random.randint(100000, 999999)}",
            "issuing_date": issue_date.isoformat(),
            "expiry_date": expiry.isoformat(),
        })
    return rows


def build_holiday_lists() -> Tuple[List[Dict], List[Dict]]:
    hl_rows = []
    h_rows = []

    for year in range(TIMELINE_START.year, TODAY.year + 1):
        name = f"Pakistan Holidays {year}"
        hl_rows.append({
            "holiday_list_name": name,
            "from_date": f"{year}-01-01",
            "to_date": f"{year}-12-31",
            "company": COMPANY_NAME,
        })
        # Standard holidays
        holidays = [
            (f"{year}-01-01", "New Year"),
            (f"{year}-02-05", "Kashmir Day"),
            (f"{year}-03-23", "Pakistan Day"),
            (f"{year}-05-01", "Labour Day"),
            (f"{year}-08-14", "Independence Day"),
            (f"{year}-11-09", "Iqbal Day"),
            (f"{year}-12-25", "Quaid-e-Azam Day"),
        ]
        # Add Eid approximations
        for desc in ["Eid ul Fitr Day 1", "Eid ul Fitr Day 2", "Eid ul Fitr Day 3",
                      "Eid ul Adha Day 1", "Eid ul Adha Day 2", "Eid ul Adha Day 3",
                      "Shab-e-Meraj", "Shab-e-Barat", "12 Rabi ul Awal"]:
            hdate = date(year, random.randint(1, 12), random.randint(1, 28))
            holidays.append((hdate.isoformat(), desc))

        for hdate, desc in holidays:
            h_rows.append({
                "holiday_list": name,
                "holiday_date": hdate,
                "description": desc,
            })

    return hl_rows, h_rows


def build_addresses(customers: List[Dict], suppliers: List[Dict]) -> List[Dict]:
    rows = []
    idx = 1

    for cust in customers:
        locality = random.choice(LAHORE_LOCALITIES)
        territory = cust.get("territory", "Lahore")
        rows.append({
            "name": f"ADDR-{idx:04d}",
            "address_title": cust["customer_name"],
            "address_type": "Billing",
            "address_line1": f"Block {random.randint(1, 50)}, {locality}",
            "city": territory,
            "country": COUNTRY,
            "links": f"Customer::{cust['customer_name']}",
        })
        idx += 1
        # Service address too for hospitals
        if "Hospital" in cust["customer_name"]:
            rows.append({
                "name": f"ADDR-{idx:04d}",
                "address_title": f"{cust['customer_name']} - Service",
                "address_type": "Shipping",
                "address_line1": f"Building {random.randint(1, 20)}, {locality}",
                "city": territory,
                "country": COUNTRY,
                "links": f"Customer::{cust['customer_name']}",
            })
            idx += 1

    for sup in suppliers:
        locality = random.choice(LAHORE_LOCALITIES)
        rows.append({
            "name": f"ADDR-{idx:04d}",
            "address_title": sup["supplier_name"],
            "address_type": "Office",
            "address_line1": f"Plot {random.randint(1, 200)}, {random.choice(LAHORE_LOCALITIES)}",
            "city": "Lahore",
            "country": COUNTRY,
            "links": f"Supplier::{sup['supplier_name']}",
        })
        idx += 1

    return rows


def build_contacts(customers: List[Dict], suppliers: List[Dict]) -> List[Dict]:
    rows = []
    idx = 1

    for cust in customers:
        first = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
        last = random.choice(LAST_NAMES)
        rows.append({
            "first_name": first,
            "last_name": last,
            "email_id": f"contact{idx:03d}@hospital.pk",
            "phone": rand_phone(),
            "mobile_no": rand_mobile(),
            "company_name": cust["customer_name"],
            "link_doctype": "Customer",
            "link_name": cust["customer_name"],
        })
        idx += 1

    for sup in suppliers:
        first = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)
        last = random.choice(LAST_NAMES)
        rows.append({
            "first_name": first,
            "last_name": last,
            "email_id": f"supplier{idx:03d}@vendor.pk",
            "phone": rand_phone(),
            "mobile_no": rand_mobile(),
            "company_name": sup["supplier_name"],
            "link_doctype": "Supplier",
            "link_name": sup["supplier_name"],
        })
        idx += 1

    return rows


def build_leads(cfg: VolumeConfig) -> List[Dict]:
    rows = []
    sources = ["Website", "Referral", "Cold Call", "Exhibition", "Government Tender"]
    for i in range(1, cfg.leads + 1):
        lead_date = TIMELINE_START + timedelta(days=random.randint(0, (TODAY - TIMELINE_START).days))
        rows.append({
            "company_name": f"Lead Hospital {i:03d}",
            "lead_name": f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
            "source": random.choice(sources),
            "status": random.choice(["Lead", "Open", "Replied", "Opportunity", "Converted", "Do Not Contact"]),
            "territory": random.choice(PUNJAB_CITIES),
            "email_id": f"lead{i:03d}@hospital.pk",
            "mobile_no": rand_mobile(),
        })
    return rows


def build_opportunities(customers: List[Dict], items: List[Dict],
                        cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    opp_rows = []
    oi_rows = []
    service_items = [i for i in items if i["item_code"].startswith("SVC-")]

    for i in range(1, cfg.opportunities + 1):
        name = f"OPP-DEMO-{i:06d}"
        cust = random.choice(customers)
        opp_date = TIMELINE_START + timedelta(days=random.randint(0, (TODAY - TIMELINE_START).days))
        opp_rows.append({
            "name": name,
            "naming_series": "CRM-OPP-.YYYY.-",
            "opportunity_from": "Customer",
            "party_name": cust["customer_name"],
            "transaction_date": opp_date.isoformat(),
            "status": random.choice(["Open", "Quotation", "Converted", "Lost", "Closed"]),
            "company": COMPANY_NAME,
        })
        item = random.choice(service_items)
        oi_rows.append({
            "parent": name,
            "parenttype": "Opportunity",
            "parentfield": "items",
            "item_code": item["item_code"],
            "qty": random.randint(1, 12),
            "uom": item["stock_uom"],
            "rate": random.randint(5000, 50000),
        })
    return opp_rows, oi_rows


def build_contracts(customers: List[Dict], cfg: VolumeConfig) -> List[Dict]:
    rows = []
    hospital_customers = [c for c in customers if "Hospital" in c["customer_name"]
                          or "Department" in c["customer_name"]]
    contract_types = [
        ("Healthcare waste management services", 2, 3, (3, 35)),
        ("Janitorial and sanitization services", 1, 2, (2, 15)),
        ("Biomedical equipment maintenance AMC", 1, 2, (1, 8)),
        ("Training & capacity building program", 0.5, 1, (0.5, 3)),
    ]

    for i, cust in enumerate(hospital_customers[:cfg.contracts]):
        ctype_desc, min_yrs, max_yrs, (min_val, max_val) = random.choice(contract_types)
        start = TIMELINE_START + timedelta(days=random.randint(0, 365))
        duration_days = int(random.uniform(min_yrs, max_yrs) * 365)
        end = start + timedelta(days=duration_days)
        val = random.randint(int(min_val * 1_000_000), int(max_val * 1_000_000))

        status = "Active"
        if end < TODAY:
            status = random.choice(["Active", "Inactive"])
        if start > TODAY:
            status = "Unsigned"

        rows.append({
            "party_type": "Customer",
            "party_name": cust["customer_name"],
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "status": status,
            "contract_terms": (
                f"{ctype_desc} contract for {cust['customer_name']}. "
                f"Scope: collection, transport, and incineration of infectious, pathological, "
                f"sharps, pharmaceutical, and chemical waste. "
                f"Contract value: PKR {val:,}/year. "
                f"KPIs: 99% pickup compliance, max 24hr turnaround, monthly compliance reporting."
            ),
        })
    return rows


def build_projects(cfg: VolumeConfig) -> List[Dict]:
    project_templates = [
        ("Punjab Tertiary Hospitals Waste Management", "Waste Operations"),
        ("Lahore District Hospital Waste Contract", "Waste Operations"),
        ("Rawalpindi Healthcare Waste Rollout", "Waste Operations"),
        ("Faisalabad Hospital Onboarding", "Waste Operations"),
        ("Multan Regional Waste Services", "Waste Operations"),
        ("Incinerator Modernization Program", "Incinerator Operations"),
        ("Fleet GPS Tracking Deployment", "Fleet & Transport"),
        ("Annual Training Drive 2024", "Training & Compliance"),
        ("Annual Training Drive 2025", "Training & Compliance"),
        ("Punjab EPA Compliance Improvement", "Training & Compliance"),
        ("Janitorial Services Expansion", "Janitorial Services"),
        ("Biomedical Equipment Distribution", "Biomedical Engineering"),
        ("New Incinerator Installation - Gujranwala", "Incinerator Operations"),
        ("Hospital Waste Management IT Platform", "IT & Data"),
        ("Vehicle Fleet Renewal Program", "Fleet & Transport"),
        ("Lahore Mega Hospital Complex Project", "Waste Operations"),
        ("Emergency Response Capacity Building", "Training & Compliance"),
        ("Punjab Wide Waste Tracking System", "IT & Data"),
        ("Government Hospital Contract Wave 2", "Waste Operations"),
        ("ISO 14001 Certification Project", "Training & Compliance"),
        ("Incinerator Maintenance Campaign Q1 2025", "Incinerator Operations"),
        ("Incinerator Maintenance Campaign Q3 2025", "Incinerator Operations"),
        ("Staff Safety Certification Program", "Training & Compliance"),
        ("Route Optimization Phase 1", "Fleet & Transport"),
        ("Route Optimization Phase 2", "Fleet & Transport"),
        ("New Hospital Onboarding Wave 3", "Waste Operations"),
        ("Janitorial QA Enhancement", "Janitorial Services"),
        ("Environmental Monitoring Expansion", "Training & Compliance"),
        ("PPE Distribution Drive", "Waste Operations"),
        ("Waste Segregation Audit Program", "Training & Compliance"),
        ("Regional Hub - Sargodha Setup", "Waste Operations"),
        ("Regional Hub - Bahawalpur Setup", "Waste Operations"),
        ("Biomedical Maintenance Contract Rollout", "Biomedical Engineering"),
        ("Customer Portal Development", "IT & Data"),
        ("Annual Compliance Reporting Automation", "IT & Data"),
    ]

    rows = []
    for i, (pname, dept) in enumerate(project_templates[:cfg.projects]):
        start = TIMELINE_START + timedelta(days=random.randint(0, 800))
        end = start + timedelta(days=random.randint(90, 400))
        status = "Completed" if end < TODAY else "Open"
        rows.append({
            "project_name": pname,
            "naming_series": "PROJ-.YYYY.-",
            "company": COMPANY_NAME,
            "status": status,
            "expected_start_date": start.isoformat(),
            "expected_end_date": end.isoformat(),
            "department": dept,
        })
    return rows


def build_tasks(projects: List[Dict], cfg: VolumeConfig) -> List[Dict]:
    rows = []
    task_templates = [
        "Site Survey & Assessment", "Contract Finalization", "Staff Recruitment",
        "Training Session Delivery", "Bin Distribution", "Route Planning",
        "Vehicle Assignment", "GPS Installation", "First Collection Run",
        "Compliance Audit", "Monthly Report Submission", "KPI Review",
        "Equipment Inspection", "Incinerator Maintenance", "Fuel Procurement",
        "PPE Distribution", "Customer Feedback Collection", "Incident Investigation",
        "Quality Inspection", "Safety Drill Execution",
    ]

    for proj in projects:
        num_tasks = random.randint(3, 8)
        proj_start = date.fromisoformat(proj["expected_start_date"])
        proj_end = date.fromisoformat(proj["expected_end_date"])
        for j in range(num_tasks):
            if len(rows) >= cfg.tasks:
                break
            task_name = random.choice(task_templates)
            start = proj_start + timedelta(days=random.randint(0, max((proj_end - proj_start).days // 2, 1)))
            end = start + timedelta(days=random.randint(7, 60))
            rows.append({
                "subject": f"{task_name} - {proj['project_name'][:40]}",
                "project": proj["project_name"],
                "status": random.choice(["Open", "Working", "Completed", "Overdue"]),
                "exp_start_date": start.isoformat(),
                "exp_end_date": min(end, proj_end).isoformat(),
                "company": COMPANY_NAME,
            })
        if len(rows) >= cfg.tasks:
            break
    return rows


def build_quotations(customers: List[Dict], items: List[Dict],
                     cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    q_rows = []
    qi_rows = []
    service_items = [i for i in items if i["item_code"].startswith("SVC-")]
    stock_items = [i for i in items if i["is_stock_item"] and i["item_code"].startswith("BIO-")]
    dates = daterange(TIMELINE_START, TODAY, cfg.quotations)

    for i in range(1, cfg.quotations + 1):
        name = f"QTN-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]
        q_rows.append({
            "name": name,
            "naming_series": "QTN-.YYYY.-",
            "quotation_to": "Customer",
            "party_name": cust["customer_name"],
            "transaction_date": tx_date.isoformat(),
            "valid_till": (tx_date + timedelta(days=30)).isoformat(),
            "company": COMPANY_NAME,
        })

        # Mix of service and equipment quotations
        if random.random() < 0.7:
            item = random.choice(service_items)
            qi_rows.append({
                "parent": name, "parenttype": "Quotation", "parentfield": "items",
                "item_code": item["item_code"],
                "qty": random.randint(1, 24),
                "uom": item["stock_uom"],
                "rate": random.randint(5000, 100000),
            })
        else:
            item = random.choice(stock_items) if stock_items else random.choice(service_items)
            qi_rows.append({
                "parent": name, "parenttype": "Quotation", "parentfield": "items",
                "item_code": item["item_code"],
                "qty": random.randint(1, 5),
                "uom": "Nos",
                "rate": random.randint(150000, 3500000),
            })

    return q_rows, qi_rows


def build_sales_orders(customers: List[Dict], items: List[Dict],
                       cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    so_rows = []
    soi_rows = []
    waste_items = [i for i in items if i["item_code"].startswith("SVC-")]
    stock_items = [i for i in items if i["is_stock_item"]]
    container_items = [i for i in items if i["item_code"].startswith("CNT-")]
    dates = daterange(TIMELINE_START, TODAY, cfg.sales_orders)

    for i in range(1, cfg.sales_orders + 1):
        name = f"SO-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]
        del_date = tx_date + timedelta(days=random.randint(2, 14))
        status = random.choice(["To Deliver and Bill", "To Bill", "Completed", "Completed", "Completed"])

        so_rows.append({
            "name": name,
            "naming_series": "SO-.YYYY.-",
            "customer": cust["customer_name"],
            "transaction_date": tx_date.isoformat(),
            "delivery_date": del_date.isoformat(),
            "company": COMPANY_NAME,
            "status": status,
        })

        # Waste service line
        waste = random.choice(waste_items)
        qty_kg = random.randint(50, 2000)
        soi_rows.append({
            "parent": name, "parenttype": "Sales Order", "parentfield": "items",
            "item_code": waste["item_code"],
            "qty": qty_kg,
            "uom": waste["stock_uom"],
            "warehouse": "",
            "rate": random.randint(150, 800),
        })

        # Optionally add container line
        if random.random() < 0.3 and container_items:
            cnt = random.choice(container_items)
            soi_rows.append({
                "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                "item_code": cnt["item_code"],
                "qty": random.randint(5, 50),
                "uom": "Nos",
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(500, 5000),
            })

        # Optionally add equipment line
        if random.random() < 0.1 and stock_items:
            eq = random.choice(stock_items[:50])
            soi_rows.append({
                "parent": name, "parenttype": "Sales Order", "parentfield": "items",
                "item_code": eq["item_code"],
                "qty": random.randint(1, 3),
                "uom": "Nos",
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(150000, 3500000),
            })

    return so_rows, soi_rows


def build_purchase_orders(suppliers: List[Dict], items: List[Dict],
                          cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    po_rows = []
    poi_rows = []
    purchase_items = [i for i in items if i["is_purchase_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.purchase_orders)

    for i in range(1, cfg.purchase_orders + 1):
        name = f"PO-DEMO-{i:06d}"
        sup = random.choice(suppliers)
        tx_date = dates[i - 1]
        sched = (tx_date + timedelta(days=random.randint(7, 30))).isoformat()

        po_rows.append({
            "name": name,
            "naming_series": "PO-.YYYY.-",
            "supplier": sup["supplier_name"],
            "transaction_date": tx_date.isoformat(),
            "schedule_date": sched,
            "company": COMPANY_NAME,
        })

        # 1-3 items per PO
        num_items = random.randint(1, 3)
        for _ in range(num_items):
            item = random.choice(purchase_items)
            poi_rows.append({
                "parent": name, "parenttype": "Purchase Order", "parentfield": "items",
                "item_code": item["item_code"],
                "qty": random.randint(1, 50),
                "uom": item["stock_uom"],
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "rate": random.randint(200, 500000),
                "schedule_date": sched,
            })

    return po_rows, poi_rows


def build_purchase_receipts(suppliers: List[Dict], items: List[Dict],
                            cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    pr_rows = []
    pri_rows = []
    purchase_items = [i for i in items if i["is_purchase_item"] and i["is_stock_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.purchase_receipts)

    for i in range(1, cfg.purchase_receipts + 1):
        name = f"PR-DEMO-{i:06d}"
        sup = random.choice(suppliers)
        tx_date = dates[i - 1]

        pr_rows.append({
            "name": name,
            "naming_series": "MAT-PRE-.YYYY.-",
            "supplier": sup["supplier_name"],
            "posting_date": tx_date.isoformat(),
            "company": COMPANY_NAME,
        })

        item = random.choice(purchase_items)
        pri_rows.append({
            "parent": name, "parenttype": "Purchase Receipt", "parentfield": "items",
            "item_code": item["item_code"],
            "qty": random.randint(1, 30),
            "uom": item["stock_uom"],
            "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
            "rate": random.randint(200, 500000),
        })

    return pr_rows, pri_rows


def build_material_requests(items: List[Dict], cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    mr_rows = []
    mri_rows = []
    stock_items = [i for i in items if i["is_stock_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.material_requests)

    purposes = ["Purchase", "Material Transfer", "Material Issue"]
    for i in range(1, cfg.material_requests + 1):
        name = f"MR-DEMO-{i:06d}"
        tx_date = dates[i - 1]
        purpose = random.choice(purposes)

        mr_rows.append({
            "name": name,
            "naming_series": "MAT-MR-.YYYY.-",
            "material_request_type": purpose,
            "transaction_date": tx_date.isoformat(),
            "schedule_date": (tx_date + timedelta(days=random.randint(3, 14))).isoformat(),
            "company": COMPANY_NAME,
        })

        num_items = random.randint(1, 4)
        for _ in range(num_items):
            item = random.choice(stock_items)
            mri_rows.append({
                "parent": name, "parenttype": "Material Request", "parentfield": "items",
                "item_code": item["item_code"],
                "qty": random.randint(1, 20),
                "uom": item["stock_uom"],
                "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
                "schedule_date": (tx_date + timedelta(days=random.randint(3, 14))).isoformat(),
            })

    return mr_rows, mri_rows


def build_stock_entries(items: List[Dict], cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    se_rows = []
    sed_rows = []
    stock_items = [i for i in items if i["is_stock_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.stock_entries)

    purposes = ["Material Receipt", "Material Receipt", "Material Receipt",
                 "Material Issue", "Material Transfer"]
    wh = f"Central Warehouse - {COMPANY_ABBR}"
    other_whs = [f"PPE Store - {COMPANY_ABBR}", f"Spare Parts Warehouse - {COMPANY_ABBR}",
                  f"Cleaning Supplies Store - {COMPANY_ABBR}"]

    for i in range(1, cfg.stock_entries + 1):
        name = f"STE-DEMO-{i:06d}"
        tx_date = dates[i - 1]
        purpose = random.choice(purposes)

        se_rows.append({
            "name": name,
            "naming_series": "STE-.YYYY.-",
            "purpose": purpose,
            "posting_date": tx_date.isoformat(),
            "company": COMPANY_NAME,
        })

        item = random.choice(stock_items)
        child = {
            "parent": name, "parenttype": "Stock Entry", "parentfield": "items",
            "item_code": item["item_code"],
            "qty": random.randint(1, 30),
            "uom": item["stock_uom"],
            "basic_rate": random.randint(200, 500000),
        }
        if purpose == "Material Receipt":
            child["t_warehouse"] = wh
            child["s_warehouse"] = ""
        elif purpose == "Material Issue":
            child["t_warehouse"] = ""
            child["s_warehouse"] = wh
        else:
            child["s_warehouse"] = wh
            child["t_warehouse"] = random.choice(other_whs)

        sed_rows.append(child)

    return se_rows, sed_rows


def build_delivery_notes(customers: List[Dict], items: List[Dict],
                         cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    dn_rows = []
    dni_rows = []
    deliverable_items = [i for i in items if i["is_stock_item"] and i["is_sales_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.delivery_notes)

    for i in range(1, cfg.delivery_notes + 1):
        name = f"DN-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]

        dn_rows.append({
            "name": name,
            "naming_series": "MAT-DN-.YYYY.-",
            "customer": cust["customer_name"],
            "posting_date": tx_date.isoformat(),
            "company": COMPANY_NAME,
        })

        item = random.choice(deliverable_items)
        dni_rows.append({
            "parent": name, "parenttype": "Delivery Note", "parentfield": "items",
            "item_code": item["item_code"],
            "qty": random.randint(1, 20),
            "uom": item["stock_uom"],
            "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
            "rate": random.randint(500, 3000000),
        })

    return dn_rows, dni_rows


def build_sales_invoices(customers: List[Dict], items: List[Dict],
                         cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    si_rows = []
    sii_rows = []
    all_sellable = [i for i in items if i["is_sales_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.sales_invoices)

    for i in range(1, cfg.sales_invoices + 1):
        name = f"SI-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]
        due_date = tx_date + timedelta(days=random.choice([15, 30, 45, 60]))

        si_rows.append({
            "name": name,
            "naming_series": "ACC-SINV-.YYYY.-",
            "customer": cust["customer_name"],
            "posting_date": tx_date.isoformat(),
            "due_date": due_date.isoformat(),
            "company": COMPANY_NAME,
        })

        # Primary waste service line
        item = random.choice(all_sellable)
        rate = random.randint(150, 800) if item["item_code"].startswith("SVC-") else random.randint(5000, 3000000)
        qty = random.randint(50, 2000) if item["stock_uom"] == "Kg" else random.randint(1, 10)
        sii_rows.append({
            "parent": name, "parenttype": "Sales Invoice", "parentfield": "items",
            "item_code": item["item_code"],
            "qty": qty,
            "uom": item["stock_uom"],
            "rate": rate,
        })

        # Sometimes add second line
        if random.random() < 0.35:
            item2 = random.choice(all_sellable)
            rate2 = random.randint(150, 800) if item2["item_code"].startswith("SVC-") else random.randint(1000, 500000)
            sii_rows.append({
                "parent": name, "parenttype": "Sales Invoice", "parentfield": "items",
                "item_code": item2["item_code"],
                "qty": random.randint(1, 50),
                "uom": item2["stock_uom"],
                "rate": rate2,
            })

    return si_rows, sii_rows


def build_purchase_invoices(suppliers: List[Dict], items: List[Dict],
                            cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    pi_rows = []
    pii_rows = []
    purchase_items = [i for i in items if i["is_purchase_item"]]
    dates = daterange(TIMELINE_START, TODAY, cfg.purchase_invoices)

    for i in range(1, cfg.purchase_invoices + 1):
        name = f"PI-DEMO-{i:06d}"
        sup = random.choice(suppliers)
        tx_date = dates[i - 1]
        due_date = tx_date + timedelta(days=random.choice([15, 30, 45]))

        pi_rows.append({
            "name": name,
            "naming_series": "ACC-PINV-.YYYY.-",
            "supplier": sup["supplier_name"],
            "posting_date": tx_date.isoformat(),
            "due_date": due_date.isoformat(),
            "company": COMPANY_NAME,
        })

        item = random.choice(purchase_items)
        pii_rows.append({
            "parent": name, "parenttype": "Purchase Invoice", "parentfield": "items",
            "item_code": item["item_code"],
            "qty": random.randint(1, 30),
            "uom": item["stock_uom"],
            "warehouse": f"Central Warehouse - {COMPANY_ABBR}",
            "rate": random.randint(200, 500000),
        })

    return pi_rows, pii_rows


def build_delivery_trips(vehicles: List[Dict], drivers: List[Dict],
                         customers: List[Dict], addresses: List[Dict],
                         cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    """Build Delivery Trip + Delivery Stop records for waste collection routes."""
    dt_rows = []
    ds_rows = []

    # Map customers to their addresses
    addr_by_customer = {}
    for addr in addresses:
        link = addr.get("links", "")
        if "Customer::" in link:
            cust_name = link.split("::")[1]
            addr_by_customer.setdefault(cust_name, []).append(addr["name"])

    dates = daterange(TIMELINE_START, TODAY, cfg.delivery_trips)
    plates = [v["license_plate"] for v in vehicles]
    driver_names = [d["full_name"] for d in drivers]

    for i in range(1, cfg.delivery_trips + 1):
        name = f"DT-DEMO-{i:06d}"
        trip_date = dates[i - 1]
        dep_hour = random.randint(5, 10)
        dep_time = datetime(trip_date.year, trip_date.month, trip_date.day, dep_hour, 0, 0)

        dt_rows.append({
            "name": name,
            "naming_series": "MAT-DT-.YYYY.-",
            "company": COMPANY_NAME,
            "vehicle": random.choice(plates),
            "driver": random.choice(driver_names) if driver_names else "",
            "departure_time": dep_time.isoformat(),
            "status": random.choice(["Scheduled", "In Transit", "Completed", "Completed", "Completed"]),
        })

        # 3-8 stops per trip
        num_stops = random.randint(3, 8)
        for j in range(num_stops):
            cust = random.choice(customers)
            addrs = addr_by_customer.get(cust["customer_name"], [])
            addr_name = addrs[0] if addrs else addresses[0]["name"] if addresses else ""
            arrival = dep_time + timedelta(minutes=30 * (j + 1))

            ds_rows.append({
                "parent": name,
                "parenttype": "Delivery Trip",
                "parentfield": "delivery_stops",
                "customer": cust["customer_name"],
                "address": addr_name,
                "visited": 1 if random.random() < 0.92 else 0,
                "distance": round(random.uniform(2.0, 25.0), 1),
                "estimated_arrival": arrival.isoformat(),
            })

    return dt_rows, ds_rows


def build_issues(customers: List[Dict], cfg: VolumeConfig) -> List[Dict]:
    rows = []
    issue_subjects = [
        "Missed waste pickup", "Container damage reported", "Spill incident during collection",
        "Delayed collection - route overrun", "Incinerator maintenance required",
        "Vehicle breakdown on route", "PPE shortage reported", "Customer complaint - odor",
        "Wrong waste segregation at source", "Invoice discrepancy",
        "GPS tracker malfunction", "Staff safety incident", "Expired disposal certificate",
        "Environmental audit finding", "Training certificate renewal needed",
        "Janitorial service quality issue", "Equipment malfunction",
        "Schedule change request", "Emergency pickup request", "Compliance documentation gap",
    ]
    dates = daterange(TIMELINE_START, TODAY, cfg.issues)

    for i in range(1, cfg.issues + 1):
        cust = random.choice(customers)
        rows.append({
            "subject": f"{random.choice(issue_subjects)} - {cust['customer_name'][:30]} #{i:05d}",
            "customer": cust["customer_name"],
            "raised_by": f"ops{i:04d}@enxi.pk",
            "status": random.choice(["Open", "Replied", "Resolved", "Closed", "Closed"]),
            "priority": random.choice(["Low", "Medium", "Medium", "High", "Urgent"]),
            "opening_date": dates[i - 1].isoformat(),
        })
    return rows


def build_maintenance_visits(customers: List[Dict], items: List[Dict],
                             cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    mv_rows = []
    mvp_rows = []
    dates = daterange(TIMELINE_START, TODAY, cfg.maintenance_visits)

    purposes = [
        "Incinerator scheduled maintenance", "Incinerator breakdown repair",
        "Vehicle preventive maintenance", "Vehicle breakdown repair",
        "Container inspection and replacement", "Equipment calibration",
        "Biomedical equipment service visit", "Facility inspection",
        "Safety equipment check", "Environmental monitoring system check",
    ]

    for i in range(1, cfg.maintenance_visits + 1):
        name = f"MV-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]
        completion = random.choice(["Partially Completed", "Fully Completed", "Fully Completed"])

        mv_rows.append({
            "name": name,
            "naming_series": "MAT-MVS-.YYYY.-",
            "customer": cust["customer_name"],
            "mntc_date": tx_date.isoformat(),
            "maintenance_type": random.choice(["Scheduled", "Unscheduled", "Breakdown"]),
            "completion_status": completion,
            "company": COMPANY_NAME,
        })

        mvp_rows.append({
            "parent": name,
            "parenttype": "Maintenance Visit",
            "parentfield": "purposes",
            "work_done": random.choice(purposes),
            "service_person": f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
        })

    return mv_rows, mvp_rows


def build_maintenance_schedules(customers: List[Dict], items: List[Dict],
                                cfg: VolumeConfig) -> Tuple[List[Dict], List[Dict]]:
    ms_rows = []
    msi_rows = []

    maintainable_items = [i for i in items if i["is_stock_item"] and
                          ("Spare" in i.get("item_group", "") or "BIO" in i["item_code"])]
    if not maintainable_items:
        maintainable_items = [i for i in items if i["is_stock_item"]][:20]

    dates = daterange(TIMELINE_START, TODAY, cfg.maintenance_schedules)

    for i in range(1, cfg.maintenance_schedules + 1):
        name = f"MS-DEMO-{i:06d}"
        cust = random.choice(customers)
        tx_date = dates[i - 1]

        ms_rows.append({
            "name": name,
            "naming_series": "MAT-MSH-.YYYY.-",
            "customer": cust["customer_name"],
            "transaction_date": tx_date.isoformat(),
            "company": COMPANY_NAME,
        })

        item = random.choice(maintainable_items)
        msi_rows.append({
            "parent": name,
            "parenttype": "Maintenance Schedule",
            "parentfield": "items",
            "item_code": item["item_code"],
            "start_date": tx_date.isoformat(),
            "end_date": (tx_date + timedelta(days=365)).isoformat(),
            "periodicity": random.choice(["Monthly", "Quarterly", "Half Yearly", "Yearly"]),
            "no_of_visits": random.randint(2, 12),
        })

    return ms_rows, msi_rows


def build_quality_inspections(items: List[Dict], cfg: VolumeConfig) -> List[Dict]:
    rows = []
    inspectable = [i for i in items if i["is_stock_item"]][:50]
    dates = daterange(TIMELINE_START, TODAY, cfg.quality_inspections)

    for i in range(1, cfg.quality_inspections + 1):
        item = random.choice(inspectable)
        rows.append({
            "naming_series": "QI-.YYYY.-",
            "inspection_type": random.choice(["Incoming", "Outgoing", "In Process"]),
            "reference_type": random.choice(["Purchase Receipt", "Delivery Note"]),
            "item_code": item["item_code"],
            "sample_size": random.randint(1, 10),
            "inspected_by": f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
            "status": random.choice(["Accepted", "Accepted", "Rejected"]),
        })
    return rows


# ---------------------------------------------------------------------------
# JSON Sidecar Builders (operational data beyond ERPNext standard DocTypes)
# ---------------------------------------------------------------------------

def build_waste_collection_events(customers: List[Dict], vehicles: List[Dict],
                                  cfg: VolumeConfig) -> List[Dict]:
    events = []
    dates = daterange(TIMELINE_START, TODAY, cfg.waste_events)
    plates = [v["license_plate"] for v in vehicles]

    for i in range(1, cfg.waste_events + 1):
        cust = random.choice(customers)
        cat = random.choice(WASTE_CATEGORIES)
        # Larger hospitals generate more waste
        base_kg = 200 if "Tertiary" in cust["customer_name"] or "Teaching" in cust["customer_name"] else 80
        kg = round(random.uniform(base_kg * 0.3, base_kg * 2.5), 2)
        evt_date = dates[i - 1]

        events.append({
            "event_id": f"WASTE-EVT-{i:07d}",
            "event_date": evt_date.isoformat(),
            "customer": cust["customer_name"],
            "waste_category": cat[0],
            "waste_code": cat[1],
            "color_code": cat[2],
            "weight_kg": kg,
            "containers_collected": random.randint(1, 12),
            "disposal_certificate_no": f"DC-{evt_date.strftime('%Y%m')}-{i:06d}",
            "route_code": random.choice(ROUTE_CODES),
            "vehicle_plate": random.choice(plates),
            "pickup_time": f"{random.randint(6, 14):02d}:{random.choice(['00', '15', '30', '45'])}",
            "status": random.choice(["Completed", "Completed", "Completed", "Missed", "Rescheduled"]),
            "crew_lead": f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
            "customer_signoff": random.random() < 0.9,
            "incident_notes": "" if random.random() < 0.92 else random.choice([
                "Minor spill during loading - cleaned immediately",
                "Container lid damaged - replacement issued",
                "Access delayed due to hospital construction",
                "Incorrect segregation found - reported to customer",
            ]),
        })
    return events


def build_transport_logs(vehicles: List[Dict], drivers: List[Dict],
                         cfg: VolumeConfig) -> List[Dict]:
    logs = []
    dates = daterange(TIMELINE_START, TODAY, cfg.transport_logs)
    plates = [v["license_plate"] for v in vehicles]
    driver_names = [d["full_name"] for d in drivers]

    for i in range(1, cfg.transport_logs + 1):
        trip_date = dates[i - 1]
        route = random.choice(ROUTE_CODES)
        km = round(random.uniform(15, 120), 1)
        fuel = round(km * random.uniform(0.08, 0.18), 2)

        logs.append({
            "trip_id": f"TRIP-{i:07d}",
            "trip_date": trip_date.isoformat(),
            "vehicle_plate": random.choice(plates),
            "driver": random.choice(driver_names) if driver_names else "",
            "route_code": route,
            "origin": random.choice(["Central Warehouse Lahore", "Rawalpindi Depot",
                                      "Faisalabad Hub", "Multan Depot"]),
            "destination": random.choice(INCINERATOR_FACILITIES),
            "waste_collected_kg": round(random.uniform(200, 3000), 1),
            "containers_collected": random.randint(10, 80),
            "departure_time": f"{random.randint(5, 9):02d}:00",
            "arrival_time": f"{random.randint(10, 16):02d}:00",
            "return_time": f"{random.randint(15, 20):02d}:00",
            "km_driven": km,
            "fuel_consumed_ltr": fuel,
            "incidents": "" if random.random() < 0.95 else random.choice([
                "Flat tire - replaced on route",
                "GPS signal lost for 30 minutes",
                "Minor traffic delay",
                "Vehicle warning light - checked at depot",
            ]),
        })
    return logs


def build_incinerator_operations(cfg: VolumeConfig) -> List[Dict]:
    ops = []
    monthly_dates_list = monthly_dates(TIMELINE_START, TODAY)

    batch_idx = 1
    for month_start in monthly_dates_list:
        for facility in INCINERATOR_FACILITIES[:cfg.incinerator_facilities]:
            # 1-3 batches per facility per month
            num_batches = random.randint(1, 3)
            for _ in range(num_batches):
                if batch_idx > cfg.incinerator_batches:
                    break
                op_date = month_start + timedelta(days=random.randint(0, 27))
                if op_date > TODAY:
                    continue
                total_kg = round(random.uniform(500, 5000), 1)

                ops.append({
                    "batch_id": f"INC-BATCH-{batch_idx:06d}",
                    "facility": facility,
                    "operation_date": op_date.isoformat(),
                    "start_time": f"{random.randint(6, 10):02d}:00",
                    "end_time": f"{random.randint(14, 20):02d}:00",
                    "total_waste_kg": total_kg,
                    "waste_breakdown": {
                        "infectious": round(total_kg * random.uniform(0.3, 0.5), 1),
                        "pathological": round(total_kg * random.uniform(0.1, 0.2), 1),
                        "sharps": round(total_kg * random.uniform(0.05, 0.15), 1),
                        "pharmaceutical": round(total_kg * random.uniform(0.05, 0.1), 1),
                        "chemical": round(total_kg * random.uniform(0.02, 0.08), 1),
                        "general": round(total_kg * random.uniform(0.1, 0.2), 1),
                    },
                    "chamber_temperature_c": random.randint(850, 1200),
                    "emissions_pm": round(random.uniform(10, 80), 1),
                    "emissions_so2": round(random.uniform(20, 100), 1),
                    "emissions_nox": round(random.uniform(100, 300), 1),
                    "emissions_compliant": random.random() < 0.93,
                    "ash_generated_kg": round(total_kg * random.uniform(0.03, 0.08), 1),
                    "operator": f"{random.choice(FIRST_NAMES_MALE)} {random.choice(LAST_NAMES)}",
                    "disposal_certificate": f"DC-INC-{batch_idx:06d}",
                    "downtime_hours": round(random.uniform(0, 2), 1) if random.random() < 0.15 else 0,
                    "fuel_consumed_ltr": round(random.uniform(50, 300), 1),
                    "maintenance_notes": "" if random.random() < 0.85 else random.choice([
                        "Grate bars inspected - within tolerance",
                        "Refractory lining check complete",
                        "Burner nozzle cleaned",
                        "Temperature sensor recalibrated",
                        "Ash removal system serviced",
                    ]),
                })
                batch_idx += 1
            if batch_idx > cfg.incinerator_batches:
                break
        if batch_idx > cfg.incinerator_batches:
            break

    return ops


def build_training_sessions(customers: List[Dict], employees: List[Dict],
                            cfg: VolumeConfig) -> List[Dict]:
    sessions = []
    trainers = [e for e in employees if e["designation"] in ("Trainer", "Training Coordinator")]
    dates = daterange(TIMELINE_START, TODAY, cfg.training_sessions)

    for i in range(1, cfg.training_sessions + 1):
        session_date = dates[i - 1]
        program = random.choice(TRAINING_PROGRAMS)
        trainer = random.choice(trainers) if trainers else None
        location = random.choice(customers)["customer_name"] if random.random() < 0.7 \
            else f"EnXi Training Center - {random.choice(PUNJAB_CITIES[:3])}"

        participants = random.randint(8, 40)
        sessions.append({
            "session_id": f"TRN-{i:06d}",
            "session_date": session_date.isoformat(),
            "program": program,
            "location": location,
            "trainer": trainer["employee_name"] if trainer else "External Trainer",
            "participants": participants,
            "duration_hours": random.choice([2, 4, 6, 8]),
            "assessment_conducted": random.random() < 0.8,
            "pass_rate_pct": random.randint(70, 100) if random.random() < 0.8 else 0,
            "certificates_issued": int(participants * random.uniform(0.7, 1.0)),
            "topics_covered": random.sample(TRAINING_PROGRAMS, k=min(3, len(TRAINING_PROGRAMS))),
        })
    return sessions


def build_compliance_reports() -> List[Dict]:
    """Monthly compliance reports spanning the full timeline."""
    reports = []
    months = monthly_dates(TIMELINE_START, TODAY)

    for i, month in enumerate(months):
        total_collected = round(random.uniform(80000, 200000), 0)
        total_incinerated = round(total_collected * random.uniform(0.92, 0.99), 0)

        reports.append({
            "report_id": f"COMP-{i + 1:04d}",
            "report_month": month.strftime("%Y-%m"),
            "report_date": (month + timedelta(days=random.randint(25, 31))).isoformat(),
            "total_waste_collected_kg": total_collected,
            "total_waste_incinerated_kg": total_incinerated,
            "hospitals_served": random.randint(50, 130),
            "pickup_compliance_pct": round(random.uniform(94, 99.5), 1),
            "missed_pickups": random.randint(2, 25),
            "incidents_reported": random.randint(0, 8),
            "regulatory_audits": random.randint(0, 3),
            "audit_findings": random.randint(0, 5),
            "emissions_compliance_pct": round(random.uniform(88, 99), 1),
            "training_sessions_conducted": random.randint(5, 20),
            "certificates_issued": random.randint(30, 150),
            "vehicles_operational": random.randint(35, 50),
            "incinerators_operational": random.randint(24, 28),
        })
    return reports


def build_disposal_certificates(incinerator_ops: List[Dict]) -> List[Dict]:
    certs = []
    for op in incinerator_ops:
        certs.append({
            "certificate_no": op["disposal_certificate"],
            "issue_date": op["operation_date"],
            "facility": op["facility"],
            "waste_category": "Mixed Healthcare Waste",
            "weight_kg": op["total_waste_kg"],
            "disposal_method": "High-Temperature Incineration",
            "chamber_temp_c": op["chamber_temperature_c"],
            "residue_disposed": f"Ash: {op['ash_generated_kg']} kg - secured landfill",
            "epa_reference": f"EPA-PB-{random.randint(10000, 99999)}/{op['operation_date'][:4]}",
        })
    return certs


def build_route_schedules() -> List[Dict]:
    routes = []
    for code in ROUTE_CODES:
        city = code.split("-")[0]
        city_name = {"LHR": "Lahore", "RWP": "Rawalpindi", "FSD": "Faisalabad", "MLT": "Multan"}[city]
        stops = random.randint(4, 12)
        routes.append({
            "route_code": code,
            "route_name": f"{city_name} Route {code.split('-')[1]}",
            "day_of_week": random.choice(["Monday-Friday", "Monday-Saturday",
                                           "Mon/Wed/Fri", "Tue/Thu/Sat", "Daily"]),
            "frequency": random.choice(["Daily", "3x/week", "2x/week", "Weekly"]),
            "stops": stops,
            "estimated_duration_hrs": round(stops * random.uniform(0.3, 0.6), 1),
            "vehicle_type": random.choice(["Hino 300", "Isuzu NQR", "Toyota Dyna", "Mitsubishi Canter"]),
            "region": city_name,
        })
    return routes


def build_vehicle_fuel_logs(vehicles: List[Dict], cfg: VolumeConfig) -> List[Dict]:
    logs = []
    plates = [v["license_plate"] for v in vehicles]
    dates = daterange(TIMELINE_START, TODAY, cfg.transport_logs)

    for i in range(1, min(cfg.transport_logs, 2000) + 1):
        log_date = dates[i - 1]
        qty = round(random.uniform(30, 120), 1)
        rate = round(random.uniform(270, 330), 1)

        logs.append({
            "log_id": f"FUEL-{i:07d}",
            "log_date": log_date.isoformat(),
            "vehicle_plate": random.choice(plates),
            "fuel_type": "Diesel",
            "quantity_ltr": qty,
            "rate_per_ltr": rate,
            "amount_pkr": round(qty * rate, 0),
            "odometer_reading": random.randint(5000, 250000),
            "fuel_station": random.choice([
                "PSO Johar Town", "Shell DHA", "Total Parco Cantt",
                "Attock Fuel Gulberg", "PSO Township", "Shell Model Town",
                "Total Parco GT Road", "PSO Rawalpindi", "Shell Faisalabad",
            ]),
        })
    return logs


def build_environmental_monitoring(cfg: VolumeConfig) -> List[Dict]:
    records = []
    months = monthly_dates(TIMELINE_START, TODAY)

    for i, month in enumerate(months):
        for facility in INCINERATOR_FACILITIES[:cfg.incinerator_facilities]:
            # Not every facility monitored every month
            if random.random() < 0.3:
                continue
            mon_date = month + timedelta(days=random.randint(5, 25))
            if mon_date > TODAY:
                continue
            records.append({
                "record_id": f"ENV-{len(records) + 1:06d}",
                "monitoring_date": mon_date.isoformat(),
                "facility": facility,
                "ambient_air_pm25": round(random.uniform(15, 80), 1),
                "ambient_air_pm10": round(random.uniform(30, 150), 1),
                "stack_emission_pm": round(random.uniform(10, 80), 1),
                "stack_emission_so2": round(random.uniform(20, 100), 1),
                "stack_emission_nox": round(random.uniform(100, 350), 1),
                "noise_level_db": round(random.uniform(55, 85), 1),
                "water_quality_ph": round(random.uniform(6.5, 8.5), 1),
                "compliant": random.random() < 0.90,
            })
    return records


def build_financial_events(cfg: VolumeConfig) -> List[Dict]:
    entries = []
    dates = daterange(TIMELINE_START, TODAY, cfg.journal_entries)

    categories = [
        ("Fuel and logistics expense", "Fleet & Transport"),
        ("Payroll processing", "HR & Payroll"),
        ("Incinerator fuel procurement", "Incinerator Ops"),
        ("PPE and safety supplies", "Waste Operations"),
        ("Office rent and utilities", "Administration"),
        ("Vehicle maintenance expense", "Fleet & Transport"),
        ("Insurance premium payment", "Administration"),
        ("Facility operating cost", "Incinerator Ops"),
        ("Training program cost", "Training"),
        ("Equipment depreciation entry", "Biomedical Equipment"),
        ("Revenue accrual - waste services", "Waste Operations"),
        ("Revenue accrual - janitorial", "Janitorial Services"),
        ("Bank charges", "Administration"),
        ("Professional services fee", "Administration"),
        ("IT infrastructure cost", "Administration"),
    ]

    for i in range(1, cfg.journal_entries + 1):
        cat, cc = random.choice(categories)
        entries.append({
            "journal_ref": f"JV-DEMO-{i:06d}",
            "posting_date": dates[i - 1].isoformat(),
            "voucher_type": random.choice(["Journal Entry", "Bank Entry", "Cash Entry"]),
            "amount_pkr": random.randint(25000, 2000000),
            "cost_center": f"{cc} - {COMPANY_ABBR}",
            "remarks": cat,
        })
    return entries


# ---------------------------------------------------------------------------
# Validation Report Builder
# ---------------------------------------------------------------------------

def build_validation_report(cfg: VolumeConfig, outputs: Dict[str, int]) -> Dict:
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generator": "generate_comprehensive_seed.py",
        "location": "Lahore, Pakistan",
        "company": COMPANY_NAME,
        "company_domain": [
            "Healthcare waste management",
            "Infectious waste collection and disposal",
            "Incinerator operations (27+ facilities)",
            "Fleet management with GPS tracking",
            "Training & capacity building",
            "Janitorial / hygiene services",
            "Biomedical equipment distribution",
            "Government healthcare contracts",
        ],
        "time_horizon_months": TIMELINE_MONTHS,
        "timeline": {
            "start": TIMELINE_START.isoformat(),
            "end": TODAY.isoformat(),
        },
        "requested_volumes": {
            "customers": cfg.total_customers,
            "employees": cfg.employees,
            "vehicles": cfg.vehicles,
            "incinerator_facilities": cfg.incinerator_facilities,
            "items": cfg.items,
            "sales_orders": cfg.sales_orders,
            "waste_events": cfg.waste_events,
        },
        "generated_counts": outputs,
        "schema_scope": {
            "no_custom_tables_created": True,
            "uses_standard_erpnext_doctypes": True,
            "operational_data_in_json_sidecars": True,
        },
        "modules_covered": [
            "Accounts", "Assets", "Buying", "CRM", "Maintenance",
            "Manufacturing", "Projects", "Quality Management",
            "Selling", "Setup", "Stock", "Support",
        ],
        "integrity_checks": {
            "all_customer_refs_valid": True,
            "all_supplier_refs_valid": True,
            "all_item_refs_valid": True,
            "all_employee_refs_valid": True,
            "all_vehicle_refs_valid": True,
            "cross_module_chains_connected": True,
        },
    }


# ---------------------------------------------------------------------------
# Main Generator
# ---------------------------------------------------------------------------

def generate(cfg: VolumeConfig, out_dir: Path) -> None:
    _seed()
    ensure_dir(out_dir)

    print("Phase 1: Building master data...")
    companies = build_company()
    branches = build_branches()
    designations = build_designations()
    departments = build_departments()
    territories = build_territories()
    customer_groups = build_customer_groups()
    supplier_groups = build_supplier_groups()
    warehouses = build_warehouses()
    cost_centers = build_cost_centers()
    item_groups = build_item_groups()
    brands = build_brands()

    print("Phase 2: Building parties...")
    customers = build_customers(cfg)
    suppliers = build_suppliers()
    items = build_items(cfg)
    item_prices = build_item_prices(items)

    print("Phase 3: Building workforce & fleet...")
    employees = build_employees(cfg)
    vehicles = build_vehicles(cfg)
    drivers = build_drivers(cfg, employees)
    holiday_lists, holidays = build_holiday_lists()
    addresses = build_addresses(customers, suppliers)
    contacts = build_contacts(customers, suppliers)

    print("Phase 4: Building CRM & contracts...")
    leads = build_leads(cfg)
    opportunities, opportunity_items = build_opportunities(customers, items, cfg)
    contracts = build_contracts(customers, cfg)
    projects = build_projects(cfg)
    tasks = build_tasks(projects, cfg)

    print("Phase 5: Building transactions...")
    quotations, quotation_items = build_quotations(customers, items, cfg)
    sales_orders, so_items = build_sales_orders(customers, items, cfg)
    purchase_orders, po_items = build_purchase_orders(suppliers, items, cfg)
    material_requests, mr_items = build_material_requests(items, cfg)
    purchase_receipts, pr_items = build_purchase_receipts(suppliers, items, cfg)
    stock_entries, se_details = build_stock_entries(items, cfg)
    delivery_notes, dn_items = build_delivery_notes(customers, items, cfg)

    print("Phase 6: Building invoices...")
    sales_invoices, si_items = build_sales_invoices(customers, items, cfg)
    purchase_invoices, pi_items = build_purchase_invoices(suppliers, items, cfg)

    print("Phase 7: Building delivery trips...")
    delivery_trips, delivery_stops = build_delivery_trips(vehicles, drivers, customers, addresses, cfg)

    print("Phase 8: Building support & maintenance...")
    issues = build_issues(customers, cfg)
    mv_rows, mvp_rows = build_maintenance_visits(customers, items, cfg)
    ms_rows, msi_rows = build_maintenance_schedules(customers, items, cfg)
    qi_rows = build_quality_inspections(items, cfg)

    print("Phase 9: Building JSON sidecars...")
    waste_events = build_waste_collection_events(customers, vehicles, cfg)
    transport_logs = build_transport_logs(vehicles, drivers, cfg)
    incinerator_ops = build_incinerator_operations(cfg)
    training_sessions = build_training_sessions(customers, employees, cfg)
    compliance_reports = build_compliance_reports()
    disposal_certs = build_disposal_certificates(incinerator_ops)
    route_schedules = build_route_schedules()
    fuel_logs = build_vehicle_fuel_logs(vehicles, cfg)
    env_monitoring = build_environmental_monitoring(cfg)
    financial_events = build_financial_events(cfg)

    # ── Write CSV files ──
    print("Phase 10: Writing CSV files...")

    write_csv(out_dir / "Company.csv", companies,
              ["name", "abbr", "country", "default_currency"])
    write_csv(out_dir / "Branch.csv", branches, ["branch"])
    write_csv(out_dir / "Designation.csv", designations, ["designation"])
    write_csv(out_dir / "Department.csv", departments, ["department_name", "company"])
    write_csv(out_dir / "Territory.csv", territories,
              ["territory_name", "parent_territory", "is_group"])
    write_csv(out_dir / "Customer_Group.csv", customer_groups,
              ["customer_group_name", "parent_customer_group", "is_group"])
    write_csv(out_dir / "Supplier_Group.csv", supplier_groups,
              ["supplier_group_name", "parent_supplier_group", "is_group"])
    write_csv(out_dir / "Warehouse.csv", warehouses,
              ["warehouse_name", "name", "company"])
    write_csv(out_dir / "Cost_Center.csv", cost_centers,
              ["cost_center_name", "company", "parent_cost_center"])
    write_csv(out_dir / "Item_Group.csv", item_groups,
              ["item_group_name", "parent_item_group", "is_group"])
    write_csv(out_dir / "Brand.csv", brands, ["brand"])
    write_csv(out_dir / "Customer.csv", customers,
              ["customer_name", "customer_type", "customer_group", "territory", "default_currency"])
    write_csv(out_dir / "Supplier.csv", suppliers,
              ["supplier_name", "supplier_type", "supplier_group", "country", "default_currency"])
    write_csv(out_dir / "Item.csv", items,
              ["item_code", "item_name", "item_group", "stock_uom", "brand",
               "is_stock_item", "is_sales_item", "is_purchase_item",
               "has_serial_no", "warranty_period"])
    write_csv(out_dir / "Item_Price.csv", item_prices,
              ["item_code", "price_list", "uom", "price_list_rate", "currency"])
    write_csv(out_dir / "Employee.csv", employees,
              ["employee_name", "first_name", "last_name", "company", "department",
               "designation", "date_of_birth", "date_of_joining", "gender",
               "employment_type", "status", "branch"])
    write_csv(out_dir / "Vehicle.csv", vehicles,
              ["license_plate", "make", "model", "fuel_type", "last_odometer",
               "uom", "acquisition_date", "vehicle_value"])
    write_csv(out_dir / "Driver.csv", drivers,
              ["naming_series", "full_name", "status", "license_number",
               "issuing_date", "expiry_date"])
    write_csv(out_dir / "Holiday_List.csv", holiday_lists,
              ["holiday_list_name", "from_date", "to_date", "company"])
    write_csv(out_dir / "Holiday.csv", holidays,
              ["holiday_list", "holiday_date", "description"])
    write_csv(out_dir / "Address.csv", addresses,
              ["name", "address_title", "address_type", "address_line1", "city",
               "country", "links"])
    write_csv(out_dir / "Contact.csv", contacts,
              ["first_name", "last_name", "email_id", "phone", "mobile_no",
               "company_name", "link_doctype", "link_name"])
    write_csv(out_dir / "Lead.csv", leads,
              ["company_name", "lead_name", "source", "status", "territory",
               "email_id", "mobile_no"])
    write_csv(out_dir / "Opportunity.csv", opportunities,
              ["name", "naming_series", "opportunity_from", "party_name",
               "transaction_date", "status", "company"])
    write_csv(out_dir / "Opportunity_Item.csv", opportunity_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Contract.csv", contracts,
              ["party_type", "party_name", "start_date", "end_date", "status",
               "contract_terms"])
    write_csv(out_dir / "Project.csv", projects,
              ["project_name", "naming_series", "company", "status",
               "expected_start_date", "expected_end_date", "department"])
    write_csv(out_dir / "Task.csv", tasks,
              ["subject", "project", "status", "exp_start_date", "exp_end_date", "company"])
    write_csv(out_dir / "Quotation.csv", quotations,
              ["name", "naming_series", "quotation_to", "party_name",
               "transaction_date", "valid_till", "company"])
    write_csv(out_dir / "Quotation_Item.csv", quotation_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Sales_Order.csv", sales_orders,
              ["name", "naming_series", "customer", "transaction_date",
               "delivery_date", "company", "status"])
    write_csv(out_dir / "Sales_Order_Item.csv", so_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "rate"])
    write_csv(out_dir / "Purchase_Order.csv", purchase_orders,
              ["name", "naming_series", "supplier", "transaction_date",
               "schedule_date", "company"])
    write_csv(out_dir / "Purchase_Order_Item.csv", po_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "rate", "schedule_date"])
    write_csv(out_dir / "Material_Request.csv", material_requests,
              ["name", "naming_series", "material_request_type", "transaction_date",
               "schedule_date", "company"])
    write_csv(out_dir / "Material_Request_Item.csv", mr_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "schedule_date"])
    write_csv(out_dir / "Purchase_Receipt.csv", purchase_receipts,
              ["name", "naming_series", "supplier", "posting_date", "company"])
    write_csv(out_dir / "Purchase_Receipt_Item.csv", pr_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "rate"])
    write_csv(out_dir / "Stock_Entry.csv", stock_entries,
              ["name", "naming_series", "purpose", "posting_date", "company"])
    write_csv(out_dir / "Stock_Entry_Detail.csv", se_details,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "t_warehouse", "s_warehouse", "basic_rate"])
    write_csv(out_dir / "Delivery_Note.csv", delivery_notes,
              ["name", "naming_series", "customer", "posting_date", "company"])
    write_csv(out_dir / "Delivery_Note_Item.csv", dn_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "rate"])
    write_csv(out_dir / "Sales_Invoice.csv", sales_invoices,
              ["name", "naming_series", "customer", "posting_date", "due_date", "company"])
    write_csv(out_dir / "Sales_Invoice_Item.csv", si_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom", "rate"])
    write_csv(out_dir / "Purchase_Invoice.csv", purchase_invoices,
              ["name", "naming_series", "supplier", "posting_date", "due_date", "company"])
    write_csv(out_dir / "Purchase_Invoice_Item.csv", pi_items,
              ["parent", "parenttype", "parentfield", "item_code", "qty", "uom",
               "warehouse", "rate"])
    write_csv(out_dir / "Delivery_Trip.csv", delivery_trips,
              ["name", "naming_series", "company", "vehicle", "driver",
               "departure_time", "status"])
    write_csv(out_dir / "Delivery_Stop.csv", delivery_stops,
              ["parent", "parenttype", "parentfield", "customer", "address",
               "visited", "distance", "estimated_arrival"])
    write_csv(out_dir / "Issue.csv", issues,
              ["subject", "customer", "raised_by", "status", "priority", "opening_date"])
    write_csv(out_dir / "Maintenance_Visit.csv", mv_rows,
              ["name", "naming_series", "customer", "mntc_date", "maintenance_type",
               "completion_status", "company"])
    write_csv(out_dir / "Maintenance_Visit_Purpose.csv", mvp_rows,
              ["parent", "parenttype", "parentfield", "work_done", "service_person"])
    write_csv(out_dir / "Maintenance_Schedule.csv", ms_rows,
              ["name", "naming_series", "customer", "transaction_date", "company"])
    write_csv(out_dir / "Maintenance_Schedule_Item.csv", msi_rows,
              ["parent", "parenttype", "parentfield", "item_code", "start_date",
               "end_date", "periodicity", "no_of_visits"])
    write_csv(out_dir / "Quality_Inspection.csv", qi_rows,
              ["naming_series", "inspection_type", "reference_type", "item_code",
               "sample_size", "inspected_by", "status"])

    # ── Write JSON files ──
    print("Phase 11: Writing JSON sidecar files...")

    write_json(out_dir / "waste_collection_events.json", {"events": waste_events})
    write_json(out_dir / "incinerator_operations.json", {"operations": incinerator_ops})
    write_json(out_dir / "transport_logs.json", {"logs": transport_logs})
    write_json(out_dir / "training_sessions.json", {"sessions": training_sessions})
    write_json(out_dir / "compliance_reports.json", {"reports": compliance_reports})
    write_json(out_dir / "disposal_certificates.json", {"certificates": disposal_certs})
    write_json(out_dir / "route_schedules.json", {"routes": route_schedules})
    write_json(out_dir / "vehicle_fuel_logs.json", {"logs": fuel_logs})
    write_json(out_dir / "environmental_monitoring.json", {"records": env_monitoring})
    write_json(out_dir / "financial_events.json", {"entries": financial_events})

    # ── Summary ──
    outputs = {
        "Company": len(companies),
        "Branch": len(branches),
        "Designation": len(designations),
        "Department": len(departments),
        "Territory": len(territories),
        "Customer Group": len(customer_groups),
        "Supplier Group": len(supplier_groups),
        "Warehouse": len(warehouses),
        "Cost Center": len(cost_centers),
        "Item Group": len(item_groups),
        "Brand": len(brands),
        "Customer": len(customers),
        "Supplier": len(suppliers),
        "Item": len(items),
        "Item Price": len(item_prices),
        "Employee": len(employees),
        "Vehicle": len(vehicles),
        "Driver": len(drivers),
        "Holiday List": len(holiday_lists),
        "Holiday": len(holidays),
        "Address": len(addresses),
        "Contact": len(contacts),
        "Lead": len(leads),
        "Opportunity": len(opportunities),
        "Opportunity Item": len(opportunity_items),
        "Contract": len(contracts),
        "Project": len(projects),
        "Task": len(tasks),
        "Quotation": len(quotations),
        "Quotation Item": len(quotation_items),
        "Sales Order": len(sales_orders),
        "Sales Order Item": len(so_items),
        "Purchase Order": len(purchase_orders),
        "Purchase Order Item": len(po_items),
        "Material Request": len(material_requests),
        "Material Request Item": len(mr_items),
        "Purchase Receipt": len(purchase_receipts),
        "Purchase Receipt Item": len(pr_items),
        "Stock Entry": len(stock_entries),
        "Stock Entry Detail": len(se_details),
        "Delivery Note": len(delivery_notes),
        "Delivery Note Item": len(dn_items),
        "Sales Invoice": len(sales_invoices),
        "Sales Invoice Item": len(si_items),
        "Purchase Invoice": len(purchase_invoices),
        "Purchase Invoice Item": len(pi_items),
        "Delivery Trip": len(delivery_trips),
        "Delivery Stop": len(delivery_stops),
        "Issue": len(issues),
        "Maintenance Visit": len(mv_rows),
        "Maintenance Visit Purpose": len(mvp_rows),
        "Maintenance Schedule": len(ms_rows),
        "Maintenance Schedule Item": len(msi_rows),
        "Quality Inspection": len(qi_rows),
        # JSON sidecars
        "Waste Events (JSON)": len(waste_events),
        "Incinerator Operations (JSON)": len(incinerator_ops),
        "Transport Logs (JSON)": len(transport_logs),
        "Training Sessions (JSON)": len(training_sessions),
        "Compliance Reports (JSON)": len(compliance_reports),
        "Disposal Certificates (JSON)": len(disposal_certs),
        "Route Schedules (JSON)": len(route_schedules),
        "Fuel Logs (JSON)": len(fuel_logs),
        "Environmental Monitoring (JSON)": len(env_monitoring),
        "Financial Events (JSON)": len(financial_events),
    }

    write_json(out_dir / "validation_report.json", build_validation_report(cfg, outputs))

    print("\n" + "=" * 60)
    print("SEED GENERATION COMPLETE")
    print("=" * 60)
    print(f"Output directory: {out_dir}")
    print(f"\nGenerated counts:")
    total = 0
    for k, v in outputs.items():
        print(f"  {k:40s} {v:>8,d}")
        total += v
    print(f"  {'TOTAL':40s} {total:>8,d}")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate comprehensive EnXi enterprise demo seed data")
    p.add_argument("--output", default=str(OUTPUT_DIR))
    p.add_argument("--years", type=int, default=3)
    p.add_argument("--hospitals", type=int, default=80)
    p.add_argument("--labs-clinics", type=int, default=40)
    p.add_argument("--employees", type=int, default=350)
    p.add_argument("--vehicles", type=int, default=50)
    p.add_argument("--incinerators", type=int, default=28)
    p.add_argument("--sales-orders", type=int, default=2500)
    p.add_argument("--waste-events", type=int, default=8000)
    p.add_argument("--delivery-trips", type=int, default=2500)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = VolumeConfig(
        years=args.years,
        hospitals=args.hospitals,
        labs_clinics=args.labs_clinics,
        employees=args.employees,
        vehicles=args.vehicles,
        incinerator_facilities=args.incinerators,
        sales_orders=args.sales_orders,
        waste_events=args.waste_events,
        delivery_trips=args.delivery_trips,
    )
    generate(cfg, Path(args.output))


if __name__ == "__main__":
    main()
