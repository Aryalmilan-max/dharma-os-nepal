#!/usr/bin/env python3
"""Create a Nepal organization technology-needs assessment, offline."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'references/nepal-tech-intelligence'


def catalog():
    return json.loads((ROOT / 'organization-needs.json').read_text(encoding='utf-8'))


def assess(scale, sector, critical=False, sensitive=False):
    data = catalog()
    size = next((s for s in data['scales'] if s['id'] == scale), None)
    org = next((s for s in data['organization_types'] if s['id'] == sector), None)
    if size is None or org is None:
        raise ValueError('Unknown scale or organization type; list profiles first.')
    selected = set(size['modules']) | set(org['modules'])
    if critical:
        selected.update(['continuity', 'security', 'governance', 'delivery'])
    if sensitive:
        selected.update(['security', 'governance'])
    return dict(status='ASSESSMENT_PLAN_NOT_AN_AUDIT', country='Nepal', scale=size['title'],
                organization_type=org['title'], critical_service=critical, sensitive_data=sensitive,
                sector_question=org['sector_question'], context_questions=data['context_questions'],
                requirements=[dict(m, assessment='NOT_ASSESSED', evidence=[], owner='TO_BE_ASSIGNED',
                                   priority='TO_BE_JUSTIFIED', gap='Current-state evidence required')
                              for m in data['modules'] if m['id'] in selected],
                required_outputs=data['required_outputs'], limitations=data['limits'])


def markdown(plan):
    lines = ['# Organization technology-needs assessment', '', plan['scale'] + ' · ' + plan['organization_type'],
             '', '**' + plan['status'] + '**', '', plan['sector_question'], '', '## Context to establish', '']
    lines += ['- ' + q for q in plan['context_questions']]
    for m in plan['requirements']:
        lines += ['', '## ' + m['title'], '', m['requirement'], '', 'Evidence: ' + m['evidence_to_collect'],
                  '', 'Deliverable: ' + m['deliverable'], '', 'Acceptance: ' + m['acceptance'],
                  '', 'Assessment: NOT_ASSESSED · Owner: TO_BE_ASSIGNED · Priority: TO_BE_JUSTIFIED']
    lines += ['', '## Limits', ''] + ['- ' + l for l in plan['limitations']]
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='action', required=True)
    commands.add_parser('profiles')
    a = commands.add_parser('assess')
    a.add_argument('--scale', required=True)
    a.add_argument('--type', dest='sector', required=True)
    a.add_argument('--critical', action='store_true')
    a.add_argument('--sensitive-data', action='store_true')
    a.add_argument('--format', choices=['json', 'markdown'], default='json')
    args = p.parse_args()
    if args.action == 'profiles':
        result = catalog()
    else:
        try:
            result = assess(args.scale, args.sector, args.critical, args.sensitive_data)
        except ValueError as e:
            p.error(str(e))
        if args.format == 'markdown':
            print(markdown(result), end='')
            return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
