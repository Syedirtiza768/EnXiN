# EnXi Demo Seed Data

Enterprise-grade demo dataset for **EnXi Biomedical & Waste Management (Pvt) Ltd** — a Pakistan-based healthcare waste management and support-services company modeled on ARAR Innovations.

## Quick Start

```bash
# 1. Generate seed data (standalone Python, no Frappe needed)
python scripts/seed/generate_comprehensive_seed.py --output seed_output

# 2. Validate referential integrity
python scripts/seed/validate_demo_seed.py --input seed_output

# 3. Import into a Frappe/ERPNext site
bench --site <sitename> import-demo-seed
```

## Architecture

```
generate_comprehensive_seed.py   →   seed_output/   →   import_executor.py
        (standalone)                  (CSV + JSON)        (Frappe ORM)
```

| Component | Path | Purpose |
|-----------|------|---------|
| Generator | `scripts/seed/generate_comprehensive_seed.py` | Produces all CSV/JSON files |
| Validator | `scripts/seed/validate_demo_seed.py` | Checks referential integrity & volumes |
| Importer  | `erpnext/seed/import_executor.py` | Frappe ORM upsert into live site |
| CLI hook  | `erpnext/commands/seed.py` | `bench import-demo-seed` command |
| Bash wrapper | `scripts/seed/import_to_site.sh` | Docker-based import shortcut |

## Timeline & Scale

- **Period**: March 2023 – March 2026 (36 months)
- **Company**: EnXi Biomedical & Waste Management (Pvt) Ltd (abbr: ENXI)
- **Currency**: PKR / Country: Pakistan

### Volume Summary (~60,500 total records)

| Category | DocType | Count |
|----------|---------|------:|
| **Master Data** | Company, Branch, Dept, Designation, Warehouse, Cost Center | 91 |
| **Parties** | Customer (130), Supplier (40), Lead (120) | 290 |
| **Items** | Item (462), Item Price (871), Brand (15), Item Group (12) | 1,360 |
| **Workforce** | Employee (341), Vehicle (50), Driver (45) | 436 |
| **CRM** | Opportunity (100), Quotation (800), Contract (80), Project (35), Task (197) | 1,212 |
| **Selling** | Sales Order (2,500 + 3,496 items), Delivery Note (1,200 + items) | 8,396 |
| **Buying** | Purchase Order (600 + items), Material Request (400 + items) | 3,221 |
| **Stock** | Purchase Receipt (500 + items), Stock Entry (600 + details) | 2,200 |
| **Invoicing** | Sales Invoice (2,000 + items), Purchase Invoice (500 + items) | 5,725 |
| **Fleet** | Delivery Trip (2,500), Delivery Stop (13,789) | 16,289 |
| **Support** | Issue (800), Maintenance Visit (400), Maintenance Schedule (200), QI (300) | 1,900 |
| **Contacts** | Address (250), Contact (170), Holiday List (4 + 64 holidays) | 488 |
| **JSON Sidecars** | Waste events, incinerator ops, transport, training, compliance, etc. | 17,115 |

## Entity Dependency Map

```
Company
  ├── Branch, Designation, Department, Warehouse, Cost Center
  ├── Customer Group, Supplier Group, Territory, Item Group, Brand
  ├── Customer → Address, Contact
  ├── Supplier → Address, Contact
  ├── Item → Item Price
  ├── Employee, Vehicle, Driver
  ├── Holiday List → Holiday
  ├── Lead → Opportunity → Quotation
  ├── Contract, Project → Task
  ├── Sales Order → Delivery Note → Sales Invoice
  ├── Purchase Order → Purchase Receipt → Purchase Invoice
  ├── Material Request, Stock Entry
  ├── Delivery Trip → Delivery Stop (→ Address, Customer, Vehicle, Driver)
  ├── Maintenance Visit, Maintenance Schedule
  ├── Issue, Quality Inspection
  └── JSON Sidecars (waste events, incinerator ops, transport, fuel, training, …)
```

## Domain Model

### Customers (130)
- **Hospital types**: Tertiary/Teaching (15%), District (25%), Tehsil (20%), Private (15%), Military (5%), Specialized (10%), Labs/Blood Banks (10%)
- **Geography**: Lahore, Faisalabad, Rawalpindi, Multan, Islamabad, Peshawar, Karachi, Quetta, and smaller Punjab cities
- **Customer groups**: Commercial, Institutional, Government

### Waste Categories
Infectious (Red), Pathological (Yellow), Sharps (Blue), Pharmaceutical (White), Chemical (Orange), Radioactive (Silver), General Medical (Green), Cytotoxic (Purple)

### Fleet & Routes
- 50 vehicles (Hino, Isuzu, Mitsubishi, Toyota — 20-ft/14-ft containers, maintenance vans, pickup trucks)
- 45 drivers across 54 route codes in 4 cities (LHR, FSD, RWP, MUL)
- 2,500 delivery trips with 3-8 stops each (13,789 stops total)

### Incinerator Network
28 facilities across Punjab with rated capacities 200-1500 kg/day, operating temperatures 850-1200°C

### Items (462)
- Waste collection containers & bins (color-coded by category)
- PPE: gloves, masks, suits, boots, goggles, face shields
- Cleaning & janitorial supplies
- Vehicle spare parts by make
- Incinerator spare parts
- Fuel items (diesel, petrol, CNG)
- Training program items
- Environmental monitoring equipment

## JSON Sidecars

These files store domain-specific operational data that goes beyond standard ERPNext DocTypes:

| File | Key | Records | Purpose |
|------|-----|--------:|---------|
| `waste_collection_events.json` | events | 8,000 | Per-pickup waste weights, categories, container counts |
| `incinerator_operations.json` | operations | 1,500 | Burn cycles, temperatures, ash output, emissions |
| `transport_logs.json` | logs | 3,000 | Route completion, distances, fuel used per trip |
| `training_sessions.json` | sessions | 500 | Staff training records, certifications |
| `compliance_reports.json` | reports | 37 | Monthly regulatory compliance snapshots |
| `disposal_certificates.json` | certificates | 1,500 | Per-customer disposal certification records |
| `vehicle_fuel_logs.json` | logs | 2,000 | Vehicle fueling records, odometer readings |
| `environmental_monitoring.json` | records | 726 | Emission levels, groundwater, ambient air readings |
| `route_schedules.json` | routes | 52 | Weekly collection schedules by route code |
| `financial_events.json` | entries | 300 | Revenue/expense accounting events |

## Regeneration

The generator uses a fixed random seed (`42`) for reproducibility. Re-running produces identical output.

```bash
# Custom output directory
python scripts/seed/generate_comprehensive_seed.py --output /tmp/test_seed

# Validate
python scripts/seed/validate_demo_seed.py --input /tmp/test_seed
```

## Import Behavior

- **Idempotent**: The importer uses upsert logic — re-running skips existing records.
- **Company remapping**: If the target site has a different company name/abbreviation, warehouse suffixes and department names are automatically remapped.
- **Currency**: All transactions use the target company's default currency (PKR) to avoid Currency Exchange errors.
- **Dependency order**: Master data first, then parties, then transactions, then child docs.
