---
name: np-engineering-dependency-review
description: "Review software dependencies and update readiness. Use when a team needs to understand dependency/version exposure before changing software."
metadata:
  version: "0.4.0"
  license: MIT
---

# Review software dependencies and update readiness

Complete this specific task for a technology organization or research project in Nepal. Agree the actual organization, locality, systems, reference period and decision owner before drawing conclusions. Scale the work to the case; do not impose enterprise infrastructure on a small shop.

## Inputs and task

Obtain: Actual manifests, locked versions, owning advisories and supported runtime requirements. Start from available evidence and identify missing inputs explicitly; request only what materially blocks the decision. Use role identifiers and redacted extracts rather than unnecessary customer, student or account data.

1. Reconcile installed/declared versions and dependency scope.
2. Check relevant owning advisories and compatibility evidence.
3. Prepare a tested update/rollback plan with unresolved risks.

Use [the blank working record](assets/working-record.csv) as a starting point. Adapt fields to the case while preserving source references and unknowns. Add an evidence register with source URL/file, exact page/row/test locator, observation date, period, geography and limitations. Preserve BS/AD calendar labels and original units when relevant; document conversions.

## Deliverable and acceptance

Return the completed working record plus a short decision note: scope, established findings, unknowns, next actions, responsible role, due date and verification method. Empty cells are not evidence. Mark absent evidence UNKNOWN and ambiguous interpretations REVIEW_REQUIRED. Separate observed facts, assumptions and recommendations. Never fill an example template with fabricated business facts.

Acceptance: **An advisory mention is not automatically a confirmed exploitable condition in the actual system.**

If acceptance cannot be demonstrated, deliver a provisional result and the specific missing evidence or test; do not label the task passed. Regulatory interpretations require current owning documents and applicable amendments. A policy date or technical manual alone does not establish current Nepal compliance. Seek an authorized domain reviewer where the decision requires one.

## Reference starting points

Select references that actually govern the case. Retrieve and inspect the relevant passage before citing a claim; these links are discovery aids, not prevalidated conclusions. Technical documents apply only if the corresponding product/version is actually used; they are not evidence of Nepal market demand. Search the official source again if a link moves.

No external reference is preselected for this task. Start with the actual case documents and owning primary sources; do not substitute a vaguely related catalog entry for task evidence.

## Execution boundary

This skill prepares and reviews the task artifact. Obtain explicit authorization before public posting, external messages, bid submission, pricing commitments or production changes. Use approved test environments for intrusive checks. Never put secrets or unredacted private records in a public repository. Preserve existing work and provide recovery steps for authorized changes.

Original Dharma OS authored workflow · MIT · 0.4.0. This folder is self-contained; it does not require other Dharma OS skills, an API key or proprietary tools. Live research uses the tools available in the user's environment.
