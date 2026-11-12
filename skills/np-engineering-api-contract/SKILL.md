---
name: np-engineering-api-contract
description: "Review an integration API contract. Use when a team needs predictable interfaces and failure handling."
metadata:
  version: "0.4.0"
  license: MIT
---

# Review an integration API contract

Complete this specific task for a technology organization or research project in Nepal. Agree the actual organization, locality, systems, reference period and decision owner before drawing conclusions. Scale the work to the case; do not impose enterprise infrastructure on a small shop.

## Inputs and task

Obtain: Current endpoint/schema documentation, authorized test environment and data ownership. Start from available evidence and identify missing inputs explicitly; request only what materially blocks the decision. Use role identifiers and redacted extracts rather than unnecessary customer, student or account data.

1. Specify identity, payload, version and error semantics.
2. Test valid, rejected, duplicate and retried requests within scope.
3. Record reconciliation and compatibility gaps.

Use [the blank working record](assets/working-record.csv) as a starting point. Adapt fields to the case while preserving source references and unknowns. Add an evidence register with source URL/file, exact page/row/test locator, observation date, period, geography and limitations. Preserve BS/AD calendar labels and original units when relevant; document conversions.

## Deliverable and acceptance

Return the completed working record plus a short decision note: scope, established findings, unknowns, next actions, responsible role, due date and verification method. Empty cells are not evidence. Mark absent evidence UNKNOWN and ambiguous interpretations REVIEW_REQUIRED. Separate observed facts, assumptions and recommendations. Never fill an example template with fabricated business facts.

Acceptance: **A successful happy-path request is not treated as complete integration acceptance.**

If acceptance cannot be demonstrated, deliver a provisional result and the specific missing evidence or test; do not label the task passed. Regulatory interpretations require current owning documents and applicable amendments. A policy date or technical manual alone does not establish current Nepal compliance. Seek an authorized domain reviewer where the decision requires one.

## Reference starting points

Select references that actually govern the case. Retrieve and inspect the relevant passage before citing a claim; these links are discovery aids, not prevalidated conclusions. Technical documents apply only if the corresponding product/version is actually used; they are not evidence of Nepal market demand. Search the official source again if a link moves.

- [HTTP response status codes; use for the actual HTTP API contract](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status) — Mozilla Contributors / MDN; CURATED_STARTING_POINT_REQUIRES_PASSAGE_AND_APPLICABILITY_REVIEW.

## Execution boundary

This skill prepares and reviews the task artifact. Obtain explicit authorization before public posting, external messages, bid submission, pricing commitments or production changes. Use approved test environments for intrusive checks. Never put secrets or unredacted private records in a public repository. Preserve existing work and provide recovery steps for authorized changes.

Original Dharma OS authored workflow · MIT · 0.4.0. This folder is self-contained; it does not require other Dharma OS skills, an API key or proprietary tools. Live research uses the tools available in the user's environment.
