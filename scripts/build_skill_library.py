#!/usr/bin/env python3
"""Generate portable task skills and offline navigation from bundled authored data.

No network access. To refresh discovery explicitly, use collect_reference_indexes.py.
"""
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build():
    definitions = json.loads((ROOT / 'catalog/skill-definitions.json').read_text())['skills']
    sources = json.loads((ROOT / 'catalog/source-records.json').read_text())
    manifest = json.loads((ROOT / 'catalog/source-manifest.json').read_text())
    curated = json.loads((ROOT / 'catalog/task-reference-map.json').read_text())
    catalog = []
    for item in definitions:
        folder = ROOT / 'skills' / item['id']
        (folder / 'assets').mkdir(parents=True, exist_ok=True)
        selected = curated.get(item['id'], [])
        references = '\n'.join(f"- [{s['label']}]({s['url']}) — {s['publisher']}; {s['verification_state']}." for s in selected) or 'No external reference is preselected for this task. Start with the actual case documents and owning primary sources; do not substitute a vaguely related catalog entry for task evidence.'
        steps = '\n'.join(f'{i}. {step}.' for i, step in enumerate(item['steps'], 1))
        text = f'''---
name: {item['id']}
description: {json.dumps(item['title'] + '. Use when ' + item['trigger'][0].lower() + item['trigger'][1:], ensure_ascii=False)}
metadata:
  version: "{item['version']}"
  license: MIT
---

# {item['title']}

Complete this specific task for a technology organization or research project in Nepal. Agree the actual organization, locality, systems, reference period and decision owner before drawing conclusions. Scale the work to the case; do not impose enterprise infrastructure on a small shop.

## Inputs and task

Obtain: {item['inputs']}. Start from available evidence and identify missing inputs explicitly; request only what materially blocks the decision. Use role identifiers and redacted extracts rather than unnecessary customer, student or account data.

{steps}

Use [the blank working record](assets/working-record.csv) as a starting point. Adapt fields to the case while preserving source references and unknowns. Add an evidence register with source URL/file, exact page/row/test locator, observation date, period, geography and limitations. Preserve BS/AD calendar labels and original units when relevant; document conversions.

## Deliverable and acceptance

Return the completed working record plus a short decision note: scope, established findings, unknowns, next actions, responsible role, due date and verification method. Empty cells are not evidence. Mark absent evidence UNKNOWN and ambiguous interpretations REVIEW_REQUIRED. Separate observed facts, assumptions and recommendations. Never fill an example template with fabricated business facts.

Acceptance: **{item['acceptance']}**

If acceptance cannot be demonstrated, deliver a provisional result and the specific missing evidence or test; do not label the task passed. Regulatory interpretations require current owning documents and applicable amendments. A policy date or technical manual alone does not establish current Nepal compliance. Seek an authorized domain reviewer where the decision requires one.

## Reference starting points

Select references that actually govern the case. Retrieve and inspect the relevant passage before citing a claim; these links are discovery aids, not prevalidated conclusions. Technical documents apply only if the corresponding product/version is actually used; they are not evidence of Nepal market demand. Search the official source again if a link moves.

{references}

## Execution boundary

This skill prepares and reviews the task artifact. Obtain explicit authorization before public posting, external messages, bid submission, pricing commitments or production changes. Use approved test environments for intrusive checks. Never put secrets or unredacted private records in a public repository. Preserve existing work and provide recovery steps for authorized changes.

Original Dharma OS authored workflow · MIT · {item['version']}. This folder is self-contained; it does not require other Dharma OS skills, an API key or proprietary tools. Live research uses the tools available in the user's environment.
'''
        (folder / 'SKILL.md').write_text(text, encoding='utf-8')
        stream = io.StringIO(); csv.writer(stream, lineterminator='\n').writerow(item['artifact_columns'])
        (folder / 'assets/working-record.csv').write_text(stream.getvalue(), encoding='utf-8')
        catalog.append({**item, 'path': f"skills/{item['id']}/SKILL.md", 'supporting_references': selected})
    result = dict(schema_version='1.0', release='0.4.0', task_skills=len(catalog), router_skills=1,
                  unique_reference_urls=len(sources), families=sorted({s['family'] for s in catalog}), skills=catalog)
    (ROOT / 'catalog/skills.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for filename in ('source-records.json', 'skill-definitions.json', 'task-reference-map.json'):
        manifest.setdefault('bundled_sha256', {})[filename] = hashlib.sha256((ROOT / 'catalog' / filename).read_bytes()).hexdigest()
    (ROOT / 'catalog/source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    payload = dict(skills=catalog, sources=sources, summary={k:v for k,v in result.items() if k != 'skills'}, provenance=manifest)
    (ROOT / 'web/library-catalog.js').write_text('"use strict";\nwindow.DHARMA_LIBRARY = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n')
    lines = ['# Task skill catalog', '', '100 task skills plus the Dharma OS router. Each task folder includes a blank working record. Select only the skills needed for your work; copying all 101 into every agent adds unnecessary routing noise.', '', '| Family | Skill |', '| --- | --- |']
    for item in catalog:
        lines.append(f"| {item['family']} | [{item['title']}](../{item['path']}) |")
    (ROOT / 'docs/task-skills.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'skills'}))

if __name__ == '__main__':
    build()
