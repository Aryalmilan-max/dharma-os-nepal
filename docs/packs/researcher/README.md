# Student and professional researcher: protocol to reproducible report

Nepal technology-business research across quantitative, qualitative, engineering and mixed-method questions. Adapt to the discipline and institutional requirements; no universal research validity claim.

**Authored playbook and blank working templates. No organization has been assessed by generating this pack.**

## Identify accountable roles

- Researcher
- Supervisor or subject reviewer
- Data steward
- Ethics/permission authority where applicable

Record the actual institution, locality, users, sites, scope, period, approvals and evidence gaps before applying these workflows. Assign real owners only with verified authority. Prioritize by observed impact, dependencies and feasible resources.

## 1. Question and literature gap

**Decision:** What answerable question is missing, and for whom does it matter?

**Collect:** Original studies, definitions, scope, dates, methods and conflicting findings.

**Produce:** Literature/evidence matrix and bounded research question.

**Acceptance:** A reviewer can trace the gap to the cited work; a topic list is not presented as a literature review.

**Status:** NOT_ASSESSED

## 2. Design and sampling

**Decision:** Which design can answer the question without unsupported extrapolation?

**Collect:** Target population, frame, inclusion rules, selection, feasibility, confounders and missing-data plan.

**Produce:** Protocol and justified sampling/analysis plan.

**Acceptance:** The design matches descriptive, comparative or causal claims; convenience samples are not labelled Nepal-representative.

**Status:** NOT_ASSESSED

## 3. Ethics, permissions and collection

**Decision:** What may be collected, and how are participants or confidential systems protected?

**Collect:** Institutional requirements, required consent/permissions, minimization, retention and access roles.

**Produce:** Permission/ethics decision and collection instrument.

**Acceptance:** Required approvals precede relevant collection; public artifacts omit identifiable/confidential records.

**Status:** NOT_ASSESSED

## 4. Data provenance and analysis

**Decision:** Can another researcher reproduce the transformations?

**Collect:** Source editions, raw-to-derived mapping, units, calendars, code versions, exclusions and analysis logs.

**Produce:** Data dictionary, transformation log and executable analysis references.

**Acceptance:** Re-run on authorized data and reconcile output; distinguish unavailable data from zero.

**Status:** NOT_ASSESSED

## 5. Robustness and interpretation

**Decision:** Could selection, definitions or another explanation change the result?

**Collect:** Missingness, sensitivity checks, contradictions, uncertainty and alternative explanations.

**Produce:** Robustness review and claims-to-evidence ledger.

**Acceptance:** Conclusions remain bounded by evidence/design; unresolved contradictions stay visible.

**Status:** NOT_ASSESSED

## 6. Writing, review and dissemination

**Decision:** Can readers distinguish methods, results and interpretation?

**Collect:** Claim citations/locators, institution format, reviewer comments, rights and reproducibility limits.

**Produce:** Report, bibliography, reproducibility checklist and correction record.

**Acceptance:** Supervisor/subject reviewer can trace material claims and methods; AI checks are not described as peer review.

**Status:** NOT_ASSESSED

## Working templates

Export using `python3 skills/dharma-os/scripts/packs.py export researcher --out my-pack` from the repository root. From an installed skill, use `scripts/packs.py`. The output folder must not already exist. CSVs contain headers only: populate them with actual evidence, never fabricated sample results.

### literature-matrix.csv

Capture study methods and limits, not just titles.

[Open blank CSV](literature-matrix.csv)

Fields: source_id, title, publisher_author, original_url, reference_period, geography, question, design, population_sample, finding_locator, finding_paraphrase, limitation, contradiction, gap_relevance, checked_on.

### protocol.csv

Plan before collecting or interpreting results.

[Open blank CSV](protocol.csv)

Fields: question_id, research_question, unit_of_analysis, target_population, sampling_frame, selection_method, inclusion_exclusion, measure_definition, analysis_plan, confounder, missing_data_plan, permission_ref, review_status.

### data-dictionary.csv

Retain original definitions and transformations.

[Open blank CSV](data-dictionary.csv)

Fields: variable, definition, unit, stock_or_flow, reference_period_calendar, geography_boundary, source_locator, allowed_values, missingness_code, transformation_ref, data_access_class, version.

### reproducibility-review.csv

Track independent review and unresolved findings honestly.

[Open blank CSV](reproducibility-review.csv)

Fields: claim_or_output_id, input_version_ref, code_command_ref, expected_output_ref, reproduced_result_ref, difference, sensitivity_check_ref, reviewer_role, review_date, correction, remaining_limit, status.

## Source routes and verification limits

This pack supplies authored methods and blank records. Retrieve the actual owning documents, supplier terms, institutional rules and source studies for the case; no current legal rates or sector-wide empirical results are supplied.


## Review before use

- Retain dates, units, geography, original source locators and contradictory evidence.
- Do not publish private operational, customer, employee or participant data in this public repository.
- An acceptance plan is not an observed test result. Record actual evidence and authorized review separately.
- Recheck changing rules, technical versions, contracts and prices before decisions.
