# School and college technology: teaching through maintenance

Nepal school/college technology assessment. Institution, funding and procurement stages need verification; equipment purchase is not proof of learning improvement.

**Authored playbook and blank working templates. No organization has been assessed by generating this pack.**

## Identify accountable roles

- School leadership
- Teachers and actual operators
- IT/support role
- Finance/procurement authority
- Accessibility/data responsibility role

Record the actual institution, locality, users, sites, scope, period, approvals and evidence gaps before applying these workflows. Assign real owners only with verified authority. Prioritize by observed impact, dependencies and feasible resources.

## 1. Teaching need and baseline

**Decision:** Which lesson or administrative task needs improvement?

**Collect:** Teacher workflow, existing equipment/use, class context and accessibility barriers; avoid identifiable student records.

**Produce:** Problem statement, baseline and alternatives including non-purchase options.

**Acceptance:** Teachers can explain the intended use and observable success criteria before a product is selected.

**Status:** NOT_ASSESSED

## 2. Room, power and connectivity readiness

**Decision:** Can the equipment be installed and used safely and reliably?

**Collect:** Room layout, sightlines, acoustics, mounting, measured load conditions and connectivity; competent personnel for safety assessment.

**Produce:** Site survey and unresolved readiness risks.

**Acceptance:** Demonstrate visibility, sound and intended interaction under actual room conditions; address safety issues before installation.

**Status:** NOT_ASSESSED

## 3. Funding and procurement evidence

**Decision:** Is this an idea, allocation, released funding or an actual purchase process?

**Collect:** Actual institution identity, budget/notice, approval authority, applicable process and amendments.

**Produce:** Evidence-stage register and specification/offer matrix.

**Acceptance:** Every funding/procurement status points to its own dated document; no jump from announcement to confirmed purchase.

**Status:** NOT_ASSESSED

## 4. Content, software and student data

**Decision:** Are content rights, accessibility and data handling appropriate?

**Collect:** Licence terms, renewal cost, language/accessibility needs, account roles and any data collection/sharing.

**Produce:** Licence/data/access register and renewal responsibilities.

**Acceptance:** Test intended lesson content and access boundaries; resolve unsupported permissions and hidden renewals.

**Status:** NOT_ASSESSED

## 5. Training and acceptance

**Decision:** Can teachers operate the delivered system in their workflow?

**Collect:** Agreed tasks, training time, support materials, actual equipment configuration and installation tests.

**Produce:** Teacher task demonstration, installation acceptance and support handover.

**Acceptance:** Representative operators deliver an agreed task and recover from a common problem without installer assistance.

**Status:** NOT_ASSESSED

## 6. Use and outcome follow-up

**Decision:** Is the system used, and what does the evidence say about outcomes?

**Collect:** Usage definitions, baseline/follow-up periods, downtime, support events and limitations of comparison.

**Produce:** Usage/maintenance review separating association from causal learning claims.

**Acceptance:** Reported results preserve periods, denominators, missingness and study-design limits.

**Status:** NOT_ASSESSED

## Working templates

Export using `python3 skills/dharma-os/scripts/packs.py export school --out my-pack` from the repository root. From an installed skill, use `scripts/packs.py`. The output folder must not already exist. CSVs contain headers only: populate them with actual evidence, never fabricated sample results.

### site-readiness.csv

Record room evidence before choosing a display or network.

[Open blank CSV](site-readiness.csv)

Fields: institution_ref, room_id, teaching_task, existing_assets, sightline_test_ref, acoustic_test_ref, power_assessment_ref, mounting_review_ref, connectivity_test_ref, accessibility_gap, owner_role, status.

### funding-stage.csv

Keep need, budget and procurement stages separate.

[Open blank CSV](funding-stage.csv)

Fields: institution_ref, need_evidence_ref, stage, document_title, official_url, fiscal_year, page_clause, amount_as_printed, unit, amendment_ref, authority_review, unknown, status.

### teacher-acceptance.csv

Record task-based acceptance rather than box delivery.

[Open blank CSV](teacher-acceptance.csv)

Fields: task_id, operator_role, configuration_ref, training_ref, expected_result, observed_result, evidence_ref, accessibility_issue, support_escalation_test, acceptance_authority, status.

### usage-review.csv

No named students in public contributions.

[Open blank CSV](usage-review.csv)

Fields: asset_or_room_id, period, usage_definition, numerator, denominator, downtime, support_event_ref, baseline_ref, followup_ref, missingness, alternative_explanation, interpretation_limit, status.

## Source routes and verification limits

- [CEHRD educational technology branch](https://old.cehrd.gov.np/section_details/div/17): Official search discovery 2026-11-12; direct page timed out. Not a verified school procurement rule or approved equipment specification.

## Review before use

- Retain dates, units, geography, original source locators and contradictory evidence.
- Do not publish private operational, customer, employee or participant data in this public repository.
- An acceptance plan is not an observed test result. Record actual evidence and authorized review separately.
- Recheck changing rules, technical versions, contracts and prices before decisions.
