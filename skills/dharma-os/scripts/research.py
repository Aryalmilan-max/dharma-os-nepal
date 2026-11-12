#!/usr/bin/env python3
"""Offline evidence library, reproducible studies and review checks. Python 3.10+."""
import argparse
import csv
from datetime import date
import io
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / 'references/nepal-tech-intelligence'
VERSION = '0.2.0'
ALIASES = {'smartboard': 'classroom', 'स्मार्टबोर्ड': 'classroom', 'स्मार्ट कक्षा': 'classroom', 'भुक्तानी': 'payment',
           'तथ्याङ्क': 'statistics', 'जनशक्ति': 'human resource', 'बोलपत्र': 'procurement',
           'इन्टरनेट': 'internet', 'अनुसन्धान': 'research', 'साइबर': 'cybersecurity',
           'क्यूआर': 'QR', 'वालेट': 'wallet', 'शिक्षा': 'education', 'बजार': 'market'}


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def library():
    return read('research-library.json')


def safe_url(value):
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in ('https', 'http') and bool(parsed.hostname) and not parsed.username


def search(query, kind='all', limit=30):
    """Rank searchable records without implying that a hit is verified evidence."""
    records = []
    for d in read('domains.json'):
        records.append(dict(d, type='domain', title=d['name']))
        for leaf in d['leaves']:
            records.append(dict(leaf, type='topic', title=leaf['name'], domain_id=d['id']))
    records += [dict(s, type='source') for s in read('source-registry.json')]
    records += [dict(m, type='method', title=m['name']) for m in read('principles-and-methods.json')['methods']]
    data = library()
    for group, record_type in [('observations', 'observation'), ('studies', 'study'), ('templates', 'template')]:
        records += [dict(r, type=record_type) for r in data[group]]
    queries = {query.strip().casefold()}
    for ne, en in ALIASES.items():
        if ne.casefold() in query.casefold():
            queries.add(query.casefold().replace(ne.casefold(), en.casefold()))
    ranked = []
    for r in records:
        if kind != 'all' and r['type'] != kind:
            continue
        text = json.dumps(r, ensure_ascii=False).casefold()
        label = str(r.get('title', r.get('indicator', ''))).casefold()
        score = max((100 if q == r['id'].casefold() else 0) + (20 if q in label else 0)
                    + (5 if q and q in text else 0) for q in queries)
        if score:
            ranked.append((score, r))
    ranked.sort(key=lambda item: (-item[0], item[1]['id']))
    return {'query': query, 'total': len(ranked), 'results': [r for _, r in ranked[:limit]],
            'interpretation': 'Topic/source matches are discovery routes, not established findings.'}


def iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def validate(study, today=None, max_age=90):
    """Check evidence structure; never certify source accuracy or research quality."""
    today = today or date.today()
    errors, warnings = [], []
    if not isinstance(study, dict):
        return {'structurally_valid': False, 'errors': ['Study must be a JSON object.'], 'warnings': [],
                'review_status': 'HUMAN_REVIEW_REQUIRED', 'evidence_links': 0}
    for key in ('schema_version', 'id', 'title', 'question', 'reference_period', 'status'):
        if not isinstance(study.get(key), str) or not study[key].strip():
            errors.append(f'{key}: non-empty text required')
    if study.get('schema_version') != '1.0':
        errors.append('schema_version must be 1.0')
    if study.get('status') not in ('draft', 'desk_review', 'field_review'):
        errors.append('status must be draft, desk_review or field_review; no automatic verified state')
    geo = study.get('geography')
    if not isinstance(geo, dict) or geo.get('country') != 'Nepal' or not geo.get('name') or geo.get('level') not in ('national', 'province', 'district', 'municipality', 'ward', 'institution'):
        errors.append('geography: Nepal, a name and an explicit supported level required')
        geo = {}
    if geo.get('level') != 'national' and not geo.get('code_source_url'):
        warnings.append('Local identity/boundary has no owning-source link; resolve it before joining data.')
    if geo.get('code_source_url') and not safe_url(geo['code_source_url']):
        errors.append('geography.code_source_url must be an HTTP(S) URL')
    for field in ('protocol', 'questions', 'limitations', 'next_actions'):
        if field in study and (not isinstance(study[field], list) or any(not isinstance(item, str) for item in study[field])):
            errors.append(f'{field}: list of text entries required')
    domain_ids = study.get('domain_ids', [])
    known_domains = {d['id'] for d in read('domains.json')}
    if not isinstance(domain_ids, list) or not domain_ids or any(not isinstance(d, str) or d not in known_domains for d in domain_ids):
        errors.append('domain_ids: non-empty list of known domain IDs required')
    claims = study.get('claims')
    if not isinstance(claims, list):
        errors.append('claims must be a list')
        claims = []
    if not claims:
        warnings.append('No claims/evidence yet. This is a research plan, not a finding.')
    if len(claims) > 500:
        errors.append('A study may contain at most 500 claims; split larger studies into scoped artifacts')
        claims = claims[:500]
    ids = [c.get('id') for c in claims if isinstance(c, dict)]
    if len(set(str(i) for i in ids)) != len(ids) or any(not isinstance(i, str) or not i for i in ids):
        errors.append('Claim IDs must be unique non-empty strings')
    source_map = {s['id']: s for s in read('source-registry.json')}
    links = 0
    for n, claim in enumerate(claims):
        p = f'claims[{n}]'
        if not isinstance(claim, dict):
            errors.append(f'{p}: object required'); continue
        if not isinstance(claim.get('text'), str) or not claim['text'].strip():
            errors.append(f'{p}.text required')
        kind = claim.get('kind')
        if kind not in ('fact', 'inference', 'hypothesis', 'recommendation'):
            errors.append(f'{p}.kind: use fact, inference, hypothesis or recommendation')
        evidence = claim.get('evidence', [])
        if not isinstance(evidence, list):
            errors.append(f'{p}.evidence must be a list'); evidence = []
        if kind == 'fact' and not any(isinstance(e, dict) and e.get('relation') == 'supports' for e in evidence):
            errors.append(f'{p}: fact needs supporting evidence')
        if kind in ('inference', 'recommendation') and not claim.get('basis'):
            errors.append(f'{p}: inference/recommendation needs claim IDs in basis')
        basis = claim.get('basis', [])
        if not isinstance(basis, list) or any(b not in ids or b == claim.get('id') for b in basis):
            errors.append(f'{p}.basis: use other existing claim IDs')
        if not claim.get('limitations'):
            warnings.append(f'{p}: explain uncertainty/limitations')
        if kind == 'hypothesis':
            warnings.append(f'{p}: hypothesis is untested')
        for j, e in enumerate(evidence):
            ep = f'{p}.evidence[{j}]'
            if not isinstance(e, dict):
                errors.append(f'{ep}: object required'); continue
            source = source_map.get(e.get('source_id')) if isinstance(e.get('source_id'), str) else None
            if not source:
                errors.append(f'{ep}: unknown source_id; register its provenance first')
            elif not safe_url(source.get('url')):
                errors.append(f'{ep}: source URL must be HTTP(S)')
            if source and source.get('supported_evidence_levels') == ['national'] and e.get('geography') not in ('Nepal', 'Nepal national'):
                errors.append(f'{ep}: registered source supplies national-only evidence; it cannot be relabelled as local')
            for field in ('locator', 'reference_period', 'geography'):
                if not isinstance(e.get(field), str) or not e[field].strip():
                    errors.append(f'{ep}.{field} required')
            if e.get('relation') not in ('supports', 'contradicts', 'context'):
                errors.append(f'{ep}.relation must be supports, contradicts or context')
            if e.get('relation') == 'contradicts':
                warnings.append(f'{ep}: contradictory evidence needs explicit reconciliation')
            checked = iso_date(e.get('checked_on'))
            if not checked or checked > today:
                errors.append(f'{ep}.checked_on: valid non-future AD YYYY-MM-DD required')
            elif (today - checked).days > max_age:
                warnings.append(f'{ep}: check is older than {max_age} days; assess freshness for this use')
            if geo.get('level') != 'national' and e.get('geography') != geo.get('name'):
                warnings.append(f'{ep}: source geography differs from study; no automatic local inference')
            links += 1
    # Detect circular reasoning across derived claims.
    graph = {c['id']: c.get('basis', []) for c in claims if isinstance(c, dict) and isinstance(c.get('id'), str) and isinstance(c.get('basis', []), list)}
    def cyclic():
        active, done = set(), set()
        for root in graph:
            stack = [(root, False)]
            while stack:
                key, exiting = stack.pop()
                if exiting:
                    active.discard(key); done.add(key); continue
                if key in active:
                    return True
                if key in done:
                    continue
                active.add(key); stack.append((key, True))
                stack.extend((b, False) for b in graph[key] if isinstance(b, str) and b in graph)
        return False
    if cyclic():
        errors.append('Circular claim basis: derived conclusions cannot support one another in a cycle')
    return {'structurally_valid': not errors, 'errors': errors, 'warnings': warnings,
            'review_status': 'HUMAN_REVIEW_REQUIRED', 'evidence_links': links,
            'meaning': 'Checks completeness and consistency, not truth, representativeness, legal compliance or peer review.'}


def create_study(template_id, question, locality='Nepal'):
    template = next((t for t in library()['templates'] if t['id'] == template_id), None)
    if not template:
        raise ValueError('Unknown template; list templates first.')
    return {'schema_version': '1.0', 'id': 'my-study', 'title': question, 'question': question,
            'audience': template['audience'], 'domain_ids': template['domain_ids'],
            'geography': {'country': 'Nepal', 'level': 'national' if locality == 'Nepal' else 'municipality', 'name': locality},
            'reference_period': 'TO_BE_ESTABLISHED', 'status': 'draft', 'template_id': template_id,
            'protocol': template['steps'], 'questions': template['questions'],
            'claims': [], 'limitations': ['Locality, period and baseline require verification.'],
            'next_actions': template['deliverables']}


def report(study, as_of=None):
    check = validate(study, today=as_of)
    lines = [f"# {study.get('title', 'Untitled study')}", '', f"Question: {study.get('question', '')}",
             f"Status: {study.get('status', 'UNKNOWN')} · Period: {study.get('reference_period', 'UNKNOWN')}",
             f"Geography: {study.get('geography', {}).get('name', 'UNKNOWN')}", '',
             '**Research artifact — human source and method review required.**', '', '## Claims and evidence', '']
    registry = {s['id']: s for s in read('source-registry.json')}
    for c in study.get('claims', []):
        lines += [f"### {c['id']} · {c['kind']}", '', c['text'], '']
        if c.get('basis'):
            lines += ['Basis: ' + ', '.join(c['basis']), '']
        for e in c.get('evidence', []):
            s = registry.get(e['source_id'], {})
            lines += [f"- {e['relation']}: [{s.get('title', e['source_id'])}]({s.get('url', '')}); {e['locator']}; period {e['reference_period']}; geography {e['geography']}; checked {e['checked_on']}."]
        lines += ['', 'Limitations: ' + str(c.get('limitations', 'Not supplied')), '']
    for key, heading in [('protocol', 'Research protocol'), ('questions', 'Questions to resolve'), ('limitations', 'Study limitations'), ('next_actions', 'Next actions')]:
        if study.get(key):
            lines += [f'## {heading}', ''] + [f'- {item}' for item in study[key]] + ['']
    lines += ['## Structural review', '', 'Errors: ' + str(len(check['errors'])), '']
    lines += ['- ' + x for x in check['errors'] + check['warnings']]
    lines += ['', check['meaning'], '']
    return '\n'.join(lines)


def compare(a_id, b_id):
    records = {o['id']: o for o in library()['observations']}
    if a_id not in records or b_id not in records:
        raise ValueError('Unknown observation ID; use search or dataset.')
    a, b = records[a_id], records[b_id]
    fields = ['indicator', 'unit', 'period_type', 'geography', 'definition', 'series_id']
    if any(a.get(k) != b.get(k) for k in fields):
        raise ValueError('Observations differ in indicator, unit, basis, definition, series or geography.')
    if a['id'] == b['id'] or a['period_order'] >= b['period_order']:
        raise ValueError('Select two distinct observations in chronological order.')
    if a['value'] == 0:
        raise ValueError('Percentage change is undefined for a zero baseline.')
    if not all(isinstance(o['value'], (int, float)) and not isinstance(o['value'], bool) and math.isfinite(o['value']) for o in (a, b)):
        raise ValueError('Finite numeric values required.')
    return {'from': a_id, 'to': b_id, 'absolute_change': b['value'] - a['value'], 'unit': a['unit'],
            'percentage_change': (b['value'] / a['value'] - 1) * 100,
            'caveats': ['Descriptive change, not a causal effect, forecast or count of unique people.',
                        'Monthly flows are unadjusted; month length, seasonality and revisions may affect comparisons.']}


def dataset_csv():
    rows = library()['observations']
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
    return out.getvalue()


def citation(source_id, fmt):
    source = next((s for s in read('source-registry.json') if s['id'] == source_id), None)
    if not source:
        raise ValueError('Unknown source ID.')
    if fmt == 'ris':
        clean = lambda s: str(s).replace('\r', ' ').replace('\n', ' ')
        return '\n'.join(['TY  - ELEC', 'ID  - ' + clean(source_id), 'TI  - ' + clean(source['title']),
                          'AU  - ' + clean(source['publisher']), 'UR  - ' + clean(source['url']),
                          'Y2  - ' + clean(source.get('verification_date', '')), 'ER  - ', ''])
    def tex(value):
        return re.sub(r'([\\{}%&#_$])', r'\\\1', str(value)).replace('\n', ' ')
    return f"@misc{{{source_id},\n  title = {{{tex(source['title'])}}},\n  author = {{{{{tex(source['publisher'])}}}}},\n  howpublished = {{\\url{{{tex(source['url'])}}}}},\n  note = {{Source checked {tex(source.get('verification_date', 'UNKNOWN'))}; publication date not inferred}}\n}}\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='action', required=True)
    s = commands.add_parser('search'); s.add_argument('query'); s.add_argument('--kind', choices=['all', 'domain', 'topic', 'source', 'method', 'observation', 'study', 'template'], default='all'); s.add_argument('--limit', type=int, default=30)
    commands.add_parser('templates')
    commands.add_parser('studies')
    d = commands.add_parser('dataset'); d.add_argument('--format', choices=['json', 'csv'], default='json')
    c = commands.add_parser('compare'); c.add_argument('earlier'); c.add_argument('later')
    c = commands.add_parser('cite'); c.add_argument('source_id'); c.add_argument('--format', choices=['ris', 'bibtex'], default='ris')
    n = commands.add_parser('init'); n.add_argument('--template', required=True); n.add_argument('--question', required=True); n.add_argument('--locality', default='Nepal'); n.add_argument('--out', required=True)
    for action in ['validate', 'report']:
        v = commands.add_parser(action); v.add_argument('study', help='Bundled study ID or a local JSON file')
        if action == 'validate':
            v.add_argument('--as-of', type=date.fromisoformat); v.add_argument('--max-age', type=int, default=90)
    args = p.parse_args()
    try:
        if args.action == 'search':
            result = search(args.query, args.kind, max(1, min(args.limit, 1000)))
        elif args.action in ('templates', 'studies'):
            result = library()[args.action]
        elif args.action == 'dataset':
            result = dataset_csv() if args.format == 'csv' else library()['observations']
        elif args.action == 'compare':
            result = compare(args.earlier, args.later)
        elif args.action == 'cite':
            result = citation(args.source_id, args.format)
        elif args.action == 'init':
            result = create_study(args.template, args.question, args.locality)
            # Exclusive creation prevents accidental destruction of an existing study.
            with Path(args.out).open('x', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2); f.write('\n')
            result = {'created': args.out, 'status': 'draft', 'next': 'Add source-backed claims, then validate and report.'}
        else:
            study = next((s for s in library()['studies'] if s['id'] == args.study), None)
            if study is None:
                study = json.loads(Path(args.study).read_text(encoding='utf-8'))
            if args.action == 'report':
                check = validate(study)
                if check['errors']:
                    raise ValueError('Cannot render an invalid study: ' + '; '.join(check['errors']))
                result = report(study)
            else:
                if args.max_age < 1:
                    raise ValueError('--max-age must be positive')
                result = validate(study, args.as_of, args.max_age)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0 if result['structurally_valid'] else 1
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    sys.exit(main())
