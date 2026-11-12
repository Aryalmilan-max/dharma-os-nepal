# Small technology shop: sales, repair and support

Nepal technology retail/repair operating workflow. No invented stock, prices, margins, warranties, tax rates or customers.

**Authored playbook and blank working templates. No organization has been assessed by generating this pack.**

## Identify accountable roles

- Shop owner
- Sales/stock operator
- Repair technician
- Accounts/support role

Record the actual institution, locality, users, sites, scope, period, approvals and evidence gaps before applying these workflows. Assign real owners only with verified authority. Prioritize by observed impact, dependencies and feasible resources.

## 1. Enquiry to comparable offer

**Decision:** What problem, configuration and support does the buyer actually need?

**Collect:** Use case, budget authority, exact SKU/configuration, dated supplier evidence and included/excluded services.

**Produce:** Requirements-to-offer comparison and quotation assumptions.

**Acceptance:** Buyer requirements map to the exact offered configuration; price validity and support exclusions are explicit.

**Status:** NOT_ASSESSED

## 2. Purchase and stock receipt

**Decision:** Did the shop receive the expected, traceable configuration?

**Collect:** Purchase reference, quantities, exact variants, serial records where appropriate and physical condition.

**Produce:** Stock/serial receipt and discrepancy log.

**Acceptance:** Count and configuration reconcile with receipt evidence; discrepant units are not silently sold as verified.

**Status:** NOT_ASSESSED

## 3. Repair intake and device custody

**Decision:** What work and data access did the customer authorize?

**Collect:** Device condition, fault description, accessories, consent scope and custody handovers; keep identifiers private.

**Produce:** Repair job, authorization and custody record.

**Acceptance:** Technician work stays inside authorization; return condition, accessories and agreed tests are recorded.

**Status:** NOT_ASSESSED

## 4. Job and unit economics

**Decision:** Does the sale or repair cover its actual acquisition and delivery obligations?

**Collect:** Dated purchase cost, labour time/cost basis, transport, returns, warranty reserve assumptions and consistent tax treatment.

**Produce:** Cost worksheet separating observed amounts from estimates.

**Acceptance:** Every amount has currency, unit and evidence/assumption basis; unknowns are not replaced with made-up margins.

**Status:** NOT_ASSESSED

## 5. Warranty and after-sales

**Decision:** Who is responsible when a sold device or repair fails?

**Collect:** Exact warranty document, supplier route, exclusions, service history and promised response.

**Produce:** Warranty/support case and supplier escalation log.

**Acceptance:** A test support case reaches the responsible role; promises match actual documented coverage.

**Status:** NOT_ASSESSED

## 6. Records, backup and owner review

**Decision:** Can the owner reconcile stock, jobs, receipts and essential records?

**Collect:** Opening/closing balances, sales/return/job records, access ownership and restore test.

**Produce:** Daily reconciliation, exception queue and recovery instructions.

**Acceptance:** A sample sale, return and repair reconcile across records; an essential backup is restored successfully.

**Status:** NOT_ASSESSED

## Working templates

Export using `python3 skills/dharma-os/scripts/packs.py export tech-shop --out my-pack` from the repository root. From an installed skill, use `scripts/packs.py`. The output folder must not already exist. CSVs contain headers only: populate them with actual evidence, never fabricated sample results.

### repair-custody.csv

Keep real device/customer records private; use job IDs in shared research.

[Open blank CSV](repair-custody.csv)

Fields: job_id, device_category, condition_ref, accessories_ref, fault_description, authorized_work_ref, data_access_consent_ref, custody_handover_ref, diagnosis, approval_for_extra_work_ref, repair_test_ref, return_acceptance_ref, status.

### stock-ledger.csv

Trace exact variants and physical movements.

[Open blank CSV](stock-ledger.csv)

Fields: movement_id, date, SKU, variant, private_serial_ref, movement_type, quantity, purchase_or_sale_ref, condition, discrepancy, operator_role, status.

### cost-and-quote.csv

Supply real values or explicit assumptions, never default market prices.

[Open blank CSV](cost-and-quote.csv)

Fields: offer_id, cost_item, amount, currency, unit, observed_or_assumption, source_ref, tax_treatment_basis, valid_until, included_service, excluded_service, unknown, review_status.

### support-case.csv

Follow actual warranty responsibility.

[Open blank CSV](support-case.csv)

Fields: case_id, sale_or_job_ref, warranty_document_ref, reported_fault, support_owner_role, supplier_case_ref, promised_response_basis, action, acceptance_ref, status.

## Source routes and verification limits

This pack supplies authored methods and blank records. Retrieve the actual owning documents, supplier terms, institutional rules and source studies for the case; no current legal rates or sector-wide empirical results are supplied.


## Review before use

- Retain dates, units, geography, original source locators and contradictory evidence.
- Do not publish private operational, customer, employee or participant data in this public repository.
- An acceptance plan is not an observed test result. Record actual evidence and authorized review separately.
- Recheck changing rules, technical versions, contracts and prices before decisions.
