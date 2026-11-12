# Evidence workbench

The toolkit supports a transparent sequence: question → protocol → evidence → interpretation → review → export. A draft with no claims is a research plan. `desk_review` means an authored analysis of documented sources; it is not an independent peer review or field validation.

## Start without an API key

Open the repository's `web/index.html` in a modern browser. The interface loads bundled local JavaScript, makes no network requests and works without a server. English and Nepali navigation labels are available; source content is not automatically translated. Search accepts selected Nepali terms and common aliases such as `smartboard`.

If a browser blocks local scripts, serve just the public repository on loopback with `python3 -m http.server 8765 --bind 127.0.0.1`, then open `http://127.0.0.1:8765/web/`. Do not run that server from a folder containing private files or expose it to a network.

The command-line examples below assume the repository root. From an installed skill, use `scripts/research.py` instead of the longer path.

```bash
python3 skills/dharma-os/scripts/research.py search स्मार्टबोर्ड
python3 skills/dharma-os/scripts/research.py search भुक्तानी --kind observation
python3 skills/dharma-os/scripts/research.py templates
python3 skills/dharma-os/scripts/research.py studies
python3 skills/dharma-os/scripts/research.py report qr-growth
python3 skills/dharma-os/scripts/research.py dataset --format csv
python3 skills/dharma-os/scripts/research.py compare NRB-qr-volume-202509 NRB-qr-volume-202609
python3 skills/dharma-os/scripts/research.py cite NP-BIZ-NRB-PAYMENTS-BHADRA2083 --format bibtex
```

## Create a study

```bash
python3 skills/dharma-os/scripts/research.py init --template student-thesis --question "What explains the observed technology-use difference in my defined sample?" --out study.json
python3 skills/dharma-os/scripts/research.py validate study.json
python3 skills/dharma-os/scripts/research.py report study.json
```

Other protocol IDs: `ict-market`, `tender-review`, `school-readiness`, `engineering-review`, `media-verification`. A protocol supplies question prompts, a work sequence and expected artifacts; the researcher still designs the study, collects evidence and justifies the analysis. No hypothetical survey results, prices, clients or budgets are inserted.

Edit the JSON or use the browser to add claims. The CLI refuses to overwrite an existing study. Redirect a report or CSV only to an output file you intend to replace. The browser can export JSON/Markdown and print a worked study; it is not a word processor or institutional thesis-template generator.

## Study format 1.0

Required study fields: `schema_version` (`1.0`), `id`, `title`, `question`, `domain_ids` (known D01–D60 IDs), `geography`, `reference_period`, `status`, and `claims`. Geography retains `country: Nepal`, a name and `level` (national, province, district, municipality, ward or institution). For local joins, attach `code_source_url` and independently resolve codes and boundary versions. Source registry IDs are not local geography codes.

Each claim retains a unique `id`, `text`, `kind` and `limitations`. A fact needs at least one supporting evidence link. An inference or recommendation needs a list of other claim IDs in `basis`. A hypothesis stays explicitly untested. Evidence links contain `source_id`, `locator` (page/table/clause), `reference_period`, `geography`, `checked_on` (AD `YYYY-MM-DD`) and `relation` (`supports`, `contradicts`, `context`). Add multiple links to preserve independent corroboration and contradictory records. Do not turn a context link into supporting evidence by relabelling it without reading the source.

Example fact inside a study:

```json
{
  "id": "C1",
  "kind": "fact",
  "text": "NRB reports 75,581,982 QR transactions in Bhadra 2083.",
  "limitations": "National monthly transactions, not unique people or a local market estimate.",
  "evidence": [{
    "source_id": "NP-BIZ-NRB-PAYMENTS-BHADRA2083",
    "locator": "Page 1, B13, transaction column, 2083 Bhadra",
    "reference_period": "Mid Aug 2026–Mid Sept 2026",
    "geography": "Nepal national",
    "checked_on": "2026-11-12",
    "relation": "supports"
  }]
}
```

New sources must first be registered with publisher, URL, check method/date, geographic scope and limitations. Source IDs must exist in `source-registry.json`; an invented ID cannot pass structural validation. Use the contribution process for a public new source. Keep private sources in a separately scoped private project.

## What validation does

The Python and browser checks detect missing fields, unknown source/domain IDs, unsupported facts, invalid dates, invalid evidence relations, broken/circular claim bases, and unsafe source URL schemes. They flag stale check dates, national evidence attached to local work and contradictions. CLI `validate` returns exit code 1 for structural errors and 0 for structural validity; warnings still require human judgment. `--as-of` and `--max-age` allow a reproducible freshness assessment.

There is no computed truth score. Passing does not prove that the source supports the words, that a sample represents Nepal, that two publications are independent, or that a recommendation is justified. Inspect original sources, definitions, statistical uncertainty, selection bias and local conditions. The classroom audit intentionally relies on inherited source-check annotations and states that limitation.

## Payment dataset and calculations

`research-library.json` contains ten selected NRB series over five printed periods: 50 observations. The periods are not consecutive months. The original `statistical-observations.json` remains available for compatibility; eight of its ten observations overlap this expanded dataset, so there are 52 distinct measurements across both representations, not 60. Prefer the new dataset for these comparisons.

Preserve the original NPR-million unit, stock/flow distinction, definitions and geography. Percentage change is `(later / earlier − 1) × 100`; comparisons require the same series, indicator, unit, definition, geography and time basis, ordered periods and a nonzero baseline. Values are descriptive, unadjusted and potentially revised. There is no automatic causal model, seasonal adjustment, local disaggregation or forecast. Ratios must use matching categories/periods; the QR ticket example shows the million-to-NPR conversion explicitly.

## Source and citation exports

RIS and BibTeX exports identify the publisher, title, URL and recorded check date. The check date is an access/check date, not an invented publication year. Review generated citations against the original publication and your institution's required style. For software citation, use the repository's `CITATION.cff`; no DOI or academic endorsement is claimed.

## Rebuild and review

Maintainers can run `python3 scripts/build_library.py` from the repository. It deterministically regenerates the authored library, worked-study Markdown, payment CSV, domain coverage CSV and browser catalog using fixed reviewed inputs. It does not retrieve sources or refresh verification dates automatically. A new source check requires revisiting the original publication and explicitly editing the maintained inputs and provenance. Run the Python and browser-core regression suites after a change.
