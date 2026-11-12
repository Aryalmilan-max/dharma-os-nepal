#!/usr/bin/env python3
"""Review organization findings and export a bounded decision report, offline."""
import argparse
from html import escape
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlparse

STATES = ('NOT_ASSESSED', 'GAP', 'PARTIAL', 'MET', 'NOT_APPLICABLE')
ROOT = Path(__file__).resolve().parents[1] / 'references/nepal-tech-intelligence'


def text(value):
    return isinstance(value, str) and bool(value.strip())


def valid_date(value, today):
    try:
        return isinstance(value, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)) and date.fromisoformat(value) <= today
    except ValueError:
        return False


def validate(plan, today=None):
    today = today or date.today()
    errors, warnings = [], []
    if not isinstance(plan, dict):
        return dict(errors=['Assessment must be an object'], warnings=[], valid=False)
    for key in ('scale', 'organization_type'):
        if not text(plan.get(key)):
            errors.append(key + ': text required')
    if plan.get('country') != 'Nepal':
        errors.append('country must be Nepal')
    if 'is_synthetic' in plan and type(plan['is_synthetic']) is not bool:
        errors.append('is_synthetic must be a boolean')
    requirements = plan.get('requirements')
    if not isinstance(requirements, list) or not requirements or len(requirements) > 100:
        return dict(errors=errors + ['requirements: 1–100 records required'], warnings=warnings, valid=False)
    known = {m['id'] for m in json.loads((ROOT / 'organization-needs.json').read_text())['modules']}
    ids = []
    for i, item in enumerate(requirements):
        p = f'requirements[{i}]'
        if not isinstance(item, dict):
            errors.append(p + ': object required'); continue
        key = item.get('id')
        if not isinstance(key, str) or key not in known:
            errors.append(p + ': known requirement ID required')
        ids.append(str(key))
        if not text(item.get('title')):
            errors.append(p + ': title required')
        for field in ('requirement', 'evidence_to_collect', 'deliverable', 'acceptance', 'owner', 'next_action', 'rationale', 'target_date', 'reviewer', 'reviewed_on', 'acceptance_evidence'):
            if field in item and not isinstance(item[field], str):
                errors.append(p + ': ' + field + ' must be text')
        state = item.get('assessment')
        if state not in STATES:
            errors.append(p + ': invalid assessment state')
        evidence = item.get('evidence', [])
        if not isinstance(evidence, list) or len(evidence) > 100:
            errors.append(p + ': evidence must be a list of at most 100 records'); evidence = []
        for j, e in enumerate(evidence):
            ep = f'{p}.evidence[{j}]'
            if not isinstance(e, dict):
                errors.append(ep + ': object required'); continue
            for f in ('reference', 'locator', 'finding'):
                if not text(e.get(f)):
                    errors.append(ep + ': ' + f + ' required')
            if not valid_date(e.get('checked_on'), today):
                errors.append(ep + ': valid non-future AD checked_on required')
            elif (today - date.fromisoformat(e['checked_on'])).days > 90:
                warnings.append(ep + ': evidence check older than 90 days; assess freshness for this use')
            if e.get('url'):
                if not isinstance(e['url'], str):
                    errors.append(ep + ': URL must be text')
                else:
                    try:
                        u = urlparse(e['url'])
                        safe = u.scheme in ('http', 'https') and bool(u.hostname) and u.username is None and u.password is None
                    except ValueError:
                        safe = False
                    if not safe:
                        errors.append(ep + ': only HTTP(S) source URLs without credentials are allowed')
        if state in ('GAP', 'PARTIAL', 'MET') and not evidence:
            errors.append(p + ': observed assessment needs evidence; otherwise retain NOT_ASSESSED')
        if state != 'NOT_ASSESSED' and not text(item.get('rationale')):
            errors.append(p + ': assessment rationale required')
        if state in ('MET', 'NOT_APPLICABLE'):
            if not text(item.get('reviewer')) or not valid_date(item.get('reviewed_on'), today):
                errors.append(p + ': reviewer role and valid review date required')
        if state == 'MET' and not text(item.get('acceptance_evidence')):
            errors.append(p + ': MET needs an actual acceptance evidence reference')
        if state == 'NOT_ASSESSED':
            warnings.append(p + ': unknown; investigate before making a purchase/readiness claim')
        if state in ('GAP', 'PARTIAL'):
            for f in ('owner', 'next_action'):
                if not text(item.get(f)) or item[f] == 'TO_BE_ASSIGNED':
                    warnings.append(p + ': assign ' + f)
            if not item.get('target_date'):
                warnings.append(p + ': agree an action target date')
        for f in ('impact', 'urgency'):
            if item.get(f) is not None and (type(item[f]) is not int or not 1 <= item[f] <= 5):
                errors.append(p + ': ' + f + ' must be an integer from 1 to 5 or null')
        if item.get('target_date'):
            if not valid_date(item['target_date'], date.max):
                errors.append(p + ': target_date must be AD YYYY-MM-DD')
        if evidence and state == 'NOT_ASSESSED':
            warnings.append(p + ': evidence recorded but assessment remains unresolved')
    if len(ids) != len(set(ids)):
        errors.append('Duplicate requirement IDs')
    if plan.get('is_synthetic'):
        warnings.insert(0, 'SYNTHETIC DEMONSTRATION — not real institutional or customer evidence')
    warnings.append('Only included requirements are reviewed; omitted requirements and sector obligations are not established as covered.')
    return dict(valid=not errors, errors=errors, warnings=warnings,
                meaning='Structural review only. Source truth, authority, applicability and acceptance adequacy need human review.')


def summary(plan, today=None):
    check = validate(plan, today)
    if not check['valid']:
        raise ValueError('; '.join(check['errors']))
    counts = dict(Counter(m['assessment'] for m in plan['requirements']))
    actions = []
    for m in plan['requirements']:
        if m['assessment'] not in ('NOT_ASSESSED', 'GAP', 'PARTIAL'):
            continue
        score = (m.get('impact') or 0) * (m.get('urgency') or 0)
        actions.append(dict(id=m['id'], title=m['title'], state=m['assessment'],
                            action=m.get('next_action') or 'Collect current-state evidence',
                            owner=m.get('owner') or 'TO_BE_ASSIGNED', target_date=m.get('target_date') or 'NOT_AGREED',
                            priority='INVESTIGATE' if m['assessment'] == 'NOT_ASSESSED' else ('UNRANKED' if not score else ('IMMEDIATE_REVIEW' if score >= 16 else ('HIGH' if score >= 9 else 'PLANNED'))),
                            heuristic_score=score))
    actions.sort(key=lambda a: (a['state'] == 'NOT_ASSESSED', -a['heuristic_score'], a['id']))
    return dict(status='HUMAN_DECISION_REQUIRED', counts=counts, actions=actions, review=check,
                limitations=['No overall readiness/compliance percentage is calculated.',
                             'Impact × urgency is an owner-supplied ordering heuristic, not a calibrated risk model.',
                             'A recorded MET state does not certify legal compliance or authorize deployment/purchase.'])


def report(plan, today=None):
    s = summary(plan, today)
    lines = ['# Organization decision report', '', plan['scale'] + ' · ' + plan['organization_type'], '',
             '**HUMAN DECISION REQUIRED**', '', '## Evidence states', '']
    if plan.get('is_synthetic'):
        lines += ['**SYNTHETIC DEMONSTRATION — no real organization was assessed.**', '']
    lines += ['- ' + state + ': ' + str(s['counts'].get(state, 0)) for state in STATES]
    lines += ['', '## Action queue', '']
    for a in s['actions']:
        lines += [f"- {a['priority']} · {a['id']}: {a['action']} | Owner: {a['owner']} | Target: {a['target_date']}"]
    for m in plan['requirements']:
        lines += ['', '## ' + m['title'] + ' · ' + m['assessment'], '',
                  'Rationale: ' + (m.get('rationale') or 'Not established'),
                  'Acceptance criteria: ' + m.get('acceptance', 'Define before testing'),
                  'Acceptance evidence: ' + (m.get('acceptance_evidence') or 'Not recorded')]
        for e in m.get('evidence', []):
            lines += ['', '- ' + e['reference'] + ' · ' + e['locator'] + ' · checked ' + e['checked_on'] + ': ' + e['finding']]
            if e.get('url'):
                lines += ['  Source: ' + e['url']]
        if m.get('reviewer'):
            lines += ['Reviewer role: ' + m['reviewer'] + ' · ' + str(m.get('reviewed_on', 'NOT_RECORDED'))]
    lines += ['', '## Review limits and unresolved items', '']
    lines += ['- ' + x for x in s['review']['warnings'] + s['limitations']]
    return '\n'.join(lines) + '\n'


def html_report(plan, today=None):
    s = summary(plan, today)
    h = lambda x: escape(str(x), quote=True)
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Organization decision report</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#193d31;max-width:1000px;margin:40px auto;padding:0 24px}h1,h2{line-height:1.25}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #ccd7cb;padding:10px;text-align:left;vertical-align:top}th{background:#edf2e7}section{border-top:1px solid #ccd7cb;padding:20px 0}a{overflow-wrap:anywhere}.notice{background:#fff0de;padding:16px}@media print{body{margin:0}h2{break-after:avoid}tr{break-inside:avoid}}</style><h1>Organization decision report</h1>',
             '<p>' + h(plan['scale']) + ' · ' + h(plan['organization_type']) + '</p><p><b>HUMAN DECISION REQUIRED</b></p>']
    if plan.get('is_synthetic'):
        parts += ['<p class="notice"><b>SYNTHETIC DEMONSTRATION — no real organization was assessed.</b></p>']
    parts += ['<h2>Evidence states</h2><p>' + ' · '.join(h(k) + ': ' + str(s['counts'].get(k, 0)) for k in STATES) + '</p>',
              '<h2>Action queue</h2><table><thead><tr><th>Priority</th><th>Action</th><th>Owner</th><th>Target</th></tr></thead><tbody>']
    for item in s['actions']:
        parts += ['<tr>' + ''.join('<td>' + h(v) + '</td>' for v in (item['priority'], item['title'] + ': ' + item['action'], item['owner'], item['target_date'])) + '</tr>']
    parts += ['</tbody></table>']
    for m in plan['requirements']:
        parts += ['<section><h2>' + h(m['title']) + ' · ' + h(m['assessment']) + '</h2><p><b>Rationale:</b> ' + h(m.get('rationale') or 'Not established') + '</p><p><b>Acceptance criteria:</b> ' + h(m.get('acceptance') or 'Define before testing') + '</p><p><b>Acceptance evidence:</b> ' + h(m.get('acceptance_evidence') or 'Not recorded') + '</p>']
        for e in m.get('evidence', []):
            parts += ['<p>' + h(e['reference']) + ' · ' + h(e['locator']) + ' · checked ' + h(e['checked_on']) + '<br>' + h(e['finding']) + '</p>']
            if e.get('url'):
                parts += ['<p><a href="' + h(e['url']) + '">' + h(e['url']) + '</a></p>']
        if m.get('reviewer'):
            parts += ['<p>Reviewer role: ' + h(m['reviewer']) + ' · ' + h(m.get('reviewed_on') or 'NOT_RECORDED') + '</p>']
        parts += ['</section>']
    parts += ['<h2>Review limits and unresolved items</h2><ul>']
    parts += ['<li>' + h(w) + '</li>' for w in s['review']['warnings'] + s['limitations']]
    return ''.join(parts) + '</ul></html>\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['validate', 'summary', 'report'])
    p.add_argument('file', type=Path)
    p.add_argument('--as-of', type=date.fromisoformat)
    p.add_argument('--format', choices=['markdown', 'html'], default='markdown', help='Report output format')
    a = p.parse_args()
    try:
        plan = json.loads(a.file.read_text(encoding='utf-8'))
        result = validate(plan, a.as_of) if a.action == 'validate' else summary(plan, a.as_of) if a.action == 'summary' else html_report(plan, a.as_of) if a.format == 'html' else report(plan, a.as_of)
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if a.action == 'validate' and not result['valid'] else 0
    except (ValueError, OSError) as e:
        p.error(str(e))


if __name__ == '__main__':
    raise SystemExit(main())
