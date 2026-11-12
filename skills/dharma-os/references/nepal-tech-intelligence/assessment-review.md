# From organization needs to a decision report

Use this workflow when a user needs a practical assessment, remediation queue or handoff rather than a blank list of requirements. It works for the included bank, shop, school and research contexts; it does not prove that every requirement or professional obligation is covered.

## Browser workflow

1. Open `web/index.html`, choose **Organizations**, select the operating scale/type and actual criticality/data context, then **Build assessment**.
2. Choose **Review findings**. The initial report contains unknowns and investigation tasks. It does not recommend buying a product.
3. Select a requirement. Read its evidence needs and acceptance criteria. Record an actual evidence reference/title, page/record/test locator, AD check date and what it establishes. An original HTTP(S) source URL is optional; an authorized private test record can be referenced without uploading its contents.
4. Record the finding rationale, state, responsible role, next action and agreed target. Keep facts separate from assumptions and preserve contradictory findings in evidence records. Optional impact/urgency values from 1 to 5 are judgments supplied by the user, not automatically measured risk.
5. Click **Save finding** before switching requirements or navigating away. This saves the session only. Use **Save locally** or **Download JSON** for persistence.
6. Export Markdown or printable HTML. Open the HTML file in a browser and use its normal print/save-PDF flow if needed. The report retains evidence states, unknowns, action ownership, targets, acceptance references, review roles and unresolved warnings.

The form edits the first evidence link and retains additional imported links. For multiple sources, add further evidence objects in the JSON file and import it. Existing assessment JSON exports from Organizations can be imported directly. Files larger than 2 MB and structurally invalid imports are rejected. No file is sent to a server.

## Evidence states

| State | Required interpretation and record |
| --- | --- |
| NOT_ASSESSED | Current state is unresolved. No purchase, compliance or readiness conclusion follows. |
| GAP | An observed unmet requirement; needs evidence and a rationale. Assign a remediation/investigation owner. |
| PARTIAL | Evidence establishes only partial fulfilment; record what remains missing. |
| MET | Needs supporting evidence, actual acceptance evidence reference, rationale, reviewer role and non-future review date. This is the user's recorded assessment, not software certification. |
| NOT_APPLICABLE | Needs the reason for exclusion and a reviewer role/date. Do not use it to hide an uninvestigated requirement. |

Each evidence object contains `reference`, `locator`, `finding`, `checked_on` (AD `YYYY-MM-DD`), and an optional `url`. The check detects invalid/future dates, unsafe URL schemes or embedded credentials, unknown/duplicate requirement IDs, invalid ratings and malformed records. Evidence checks older than 90 days are flagged for contextual freshness review. A reference can still be wrong, a test can be inadequate and a reviewer role can be misrepresented; human assessment of the actual source and authority remains necessary.

## Action ordering and limits

Observed gaps/partial findings are presented before unknown items. When both ratings are supplied, `impact × urgency` gives an ordering heuristic: 16–25 → immediate review, 9–15 → high, 1–8 → planned. Missing ratings remain unranked. Unknown requirements remain **INVESTIGATE** even if rated highly. These thresholds are authored workflow choices, not Nepal risk standards, financial advice, or a validated model. A high-ranked item does not authorize spending or a production change.

No overall readiness or compliance percentage is computed. Counts concern only the requirements actually included. Missing context, omitted obligations, independently unverified sources and professional review remain open. An all-unknown bank report must not become a procurement recommendation. A passing restore test must not become a claim that every system or school has adequate backups.

## CLI workflow

From the repository root:

```bash
python3 skills/dharma-os/scripts/organizations.py assess --scale micro --type repair > assessment.json
python3 skills/dharma-os/scripts/assessments.py validate assessment.json
python3 skills/dharma-os/scripts/assessments.py summary assessment.json
python3 skills/dharma-os/scripts/assessments.py report assessment.json > report.md
python3 skills/dharma-os/scripts/assessments.py report assessment.json --format html > report.html
```

Use `--as-of YYYY-MM-DD` for a reproducible check date. Invalid assessment reports are refused. `validate` returns a nonzero exit code on structural errors; warnings can remain even when the input is valid. Shell redirection can replace an existing destination file, so choose output filenames deliberately. The CLI does not overwrite the assessment input while reviewing it.

## Inspect the demonstration

`examples/assessment-review/synthetic-shop.json` is explicitly synthetic: one invented failed restore exercise and seven unassessed requirements. The derived report prioritizes reviewing the failed restore and investigating unknowns. There is no real shop, client, incident, acceptance or measured business outcome behind the fixture. The example is a software/workflow demonstration, not added empirical Nepal coverage.

```bash
python3 skills/dharma-os/scripts/assessments.py report examples/assessment-review/synthetic-shop.json --as-of 2026-11-12
```

Keep actual customer, student, employee and banking records in the authorized private system. Public contributions should use redacted references or appropriately authorized public evidence. Browser storage is unencrypted and can be cleared; exported JSON is the portable backup. This workflow never publishes, contacts institutions, changes production or approves bids/prices.
