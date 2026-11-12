# Commercial bank technology and service operations

Nepal commercial-bank technology assessment; not credit decisions, a completed IS audit or a regulatory compliance opinion.

**Authored playbook and blank working templates. No organization has been assessed by generating this pack.**

## Identify accountable roles

- Business service owner
- IT operations
- Information security
- Risk/compliance
- Procurement
- Internal audit; independent from implementation

Record the actual institution, locality, users, sites, scope, period, approvals and evidence gaps before applying these workflows. Assign real owners only with verified authority. Prioritize by observed impact, dependencies and feasible resources.

## 1. Service and branch dependency mapping

**Decision:** Which customer services must survive a branch or provider outage?

**Collect:** Service hours, channels, branch dependencies, owners and observed outage records.

**Produce:** Service-to-system/site/provider dependency map and business-impact assessment.

**Acceptance:** Business owners confirm dependencies and approve service-specific recovery objectives.

**Status:** NOT_ASSESSED

## 2. Access and transaction integrity

**Decision:** Who can initiate, approve, change and reconcile a sensitive transaction?

**Collect:** Role permissions, joiner/leaver records, privileged accounts, approval paths and exception records; use redacted or synthetic samples.

**Produce:** Access/segregation matrix and review exceptions.

**Acceptance:** Demonstrate permitted and prohibited actions in an authorized test environment; reconcile an approved test transaction.

**Status:** NOT_ASSESSED

## 3. Continuity and recovery exercise

**Decision:** Can the service recover within owner-approved data-loss and time limits?

**Collect:** Backup/replication configuration, restore evidence, recovery dependencies and actual exercise timestamps.

**Produce:** Recovery scenario, exercise log, measured recovery gap and remediation ownership.

**Acceptance:** Recover a representative service safely in an isolated or explicitly approved exercise and compare measured results with targets.

**Status:** NOT_ASSESSED

## 4. Supplier and outsourced service assurance

**Decision:** What happens if the platform or connectivity supplier fails or changes?

**Collect:** Service scope, subcontractors, data access/location, support escalation, contract evidence and exit dependencies.

**Produce:** Supplier due-diligence/exit matrix linked to service criticality.

**Acceptance:** Walk through an outage and termination/export scenario with accountable owners; unsupported supplier claims remain open.

**Status:** NOT_ASSESSED

## 5. System change and migration

**Decision:** Can a release or migration preserve records and allow recovery?

**Collect:** Source/target mappings, reconciliation totals, test results, approvals and rollback dependencies.

**Produce:** Change record, reconciliation tests and go/no-go criteria.

**Acceptance:** Test duplicates, rejected records, rollback and reconciled totals before authorized release.

**Status:** NOT_ASSESSED

## 6. Regulatory and audit evidence

**Decision:** Which current instrument and exact provision apply to this bank and service?

**Collect:** Original NRB documents, applicable later directives/circulars, bank policies and independent review.

**Produce:** Provision-to-control-to-evidence mapping with applicability and amendment fields.

**Acceptance:** The bank risk/compliance reviewer resolves current applicability; the toolkit never marks a bank compliant automatically.

**Status:** NOT_ASSESSED

## Working templates

Export using `python3 skills/dharma-os/scripts/packs.py export commercial-bank --out my-pack` from the repository root. From an installed skill, use `scripts/packs.py`. The output folder must not already exist. CSVs contain headers only: populate them with actual evidence, never fabricated sample results.

### service-recovery.csv

Map services and record actual recovery tests.

[Open blank CSV](service-recovery.csv)

Fields: service_id, channel_or_branch, business_owner_role, dependency, criticality_basis, approved_RTO, approved_RPO, target_approval_ref, exercise_date, measured_restore_time, measured_data_loss, evidence_ref, gap, remediation_owner, review_status.

### access-review.csv

Review roles and conflicting powers without publishing customer data.

[Open blank CSV](access-review.csv)

Fields: system_id, role_id, permission, initiate_or_approve, conflict_rule_ref, review_evidence_ref, exception, authorized_reviewer_role, remediation, due_date, status.

### regulatory-evidence.csv

Keep exact instruments and later amendments distinct.

[Open blank CSV](regulatory-evidence.csv)

Fields: instrument_title, issuer, original_url, publication_date, effective_period, entity_and_service_scope, clause_page, later_amendment_ref, applicability_decision, control_id, evidence_ref, gap, reviewer_role, review_date, status.

### supplier-change.csv

Trace providers, data exposure, change tests and exit.

[Open blank CSV](supplier-change.csv)

Fields: service_id, supplier_role, contract_ref, data_access_scope, subcontractor_dependency, exit_export_test_ref, change_id, test_ref, rollback_ref, approval_ref, unresolved_risk, status.

## Source routes and verification limits

- [NRB IT Guidelines, August 2012](https://www.nrb.org.np/bfr/it-guidelines-2012/): Official 19-page PDF opened 2026-11-12; content/navigation inspected. Historical instrument; current amendments/applicability are not exhaustively audited.
- [NRB policies and guidelines index](https://www.nrb.org.np/category/policies-guidelines/): Official index opened 2026-11-12. Discovery route, not a complete instrument/applicability audit.

## Review before use

- Retain dates, units, geography, original source locators and contradictory evidence.
- Do not publish private operational, customer, employee or participant data in this public repository.
- An acceptance plan is not an observed test result. Record actual evidence and authorized review separately.
- Recheck changing rules, technical versions, contracts and prices before decisions.
