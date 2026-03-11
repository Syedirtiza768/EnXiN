-- Rollback template for EnXi biomedical demo imports.
-- IMPORTANT:
-- 1) Use only after taking full DB backup.
-- 2) Adjust date / naming filters to your import batch.
-- 3) Execute in transaction where possible.

-- Example patterns used by generated data:
-- Sales Orders: SO-DEMO-%
-- Waste events in JSON are external references, not DB rows.

-- Draft cleanup examples (adapt to your environment):
-- DELETE FROM `tabSales Order Item` WHERE parent LIKE 'SO-DEMO-%';
-- DELETE FROM `tabSales Order` WHERE name LIKE 'SO-DEMO-%';
-- DELETE FROM `tabIssue` WHERE subject LIKE 'Biomedical Service Ticket %';

-- Master rollback (only if created solely for demo):
-- DELETE FROM `tabItem Price` WHERE item_code LIKE 'BIO-%' OR item_code LIKE 'WASTE-%';
-- DELETE FROM `tabItem` WHERE item_code LIKE 'BIO-%' OR item_code LIKE 'WASTE-%';
-- DELETE FROM `tabCustomer` WHERE customer_name LIKE '%Hospital %' OR customer_name LIKE '%Clinic %' OR customer_name LIKE '%Diagnostic Lab %';
-- DELETE FROM `tabSupplier` WHERE supplier_name LIKE 'BioMed Supplier %' OR supplier_name LIKE 'Waste Disposal Partner %';

-- Keep this file as a template and verify dependencies before executing.
