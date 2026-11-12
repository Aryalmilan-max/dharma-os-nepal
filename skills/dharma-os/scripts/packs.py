#!/usr/bin/env python3
"""Inspect or export a sector working pack. No network or third-party packages."""
import argparse
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'references/nepal-tech-intelligence'


def catalog():
    return json.loads((ROOT / 'sector-packs.json').read_text(encoding='utf-8'))['packs']


def get(pack_id):
    pack = next((p for p in catalog() if p['id'] == pack_id), None)
    if pack is None:
        raise ValueError('Unknown pack; use list.')
    return pack


def markdown(pack):
    lines = ['# ' + pack['title'], '', pack['scope'], '',
             '**Authored playbook and blank working templates. No organization has been assessed by generating this pack.**',
             '', '## Identify accountable roles', ''] + ['- ' + x for x in pack['owners']]
    lines += ['', 'Record the actual institution, locality, users, sites, scope, period, approvals and evidence gaps before applying these workflows. Assign real owners only with verified authority. Prioritize by observed impact, dependencies and feasible resources.', '']
    for i, w in enumerate(pack['workflows'], 1):
        lines += ['## ' + str(i) + '. ' + w['title'], '', '**Decision:** ' + w['decision'], '',
                  '**Collect:** ' + w['evidence'], '', '**Produce:** ' + w['deliverable'], '',
                  '**Acceptance:** ' + w['acceptance'], '', '**Status:** NOT_ASSESSED', '']
    lines += ['## Working templates', '', 'Export using `python3 skills/dharma-os/scripts/packs.py export ' + pack['id'] + ' --out my-pack` from the repository root. From an installed skill, use `scripts/packs.py`. The output folder must not already exist. CSVs contain headers only: populate them with actual evidence, never fabricated sample results.', '']
    for t in pack['templates']:
        lines += ['### ' + t['name'] + '.csv', '', t['purpose'], '', '[Open blank CSV](' + t['name'] + '.csv)', '', 'Fields: ' + ', '.join(t['columns']) + '.', '']
    lines += ['## Source routes and verification limits', '']
    if not pack['sources']:
        lines += ['This pack supplies authored methods and blank records. Retrieve the actual owning documents, supplier terms, institutional rules and source studies for the case; no current legal rates or sector-wide empirical results are supplied.', '']
    for s in pack['sources']:
        lines += ['- [' + s['title'] + '](' + s['url'] + '): ' + s['check']]
    lines += ['', '## Review before use', '', '- Retain dates, units, geography, original source locators and contradictory evidence.',
              '- Do not publish private operational, customer, employee or participant data in this public repository.',
              '- An acceptance plan is not an observed test result. Record actual evidence and authorized review separately.',
              '- Recheck changing rules, technical versions, contracts and prices before decisions.', '']
    return '\n'.join(lines)


def export(pack_id, destination):
    pack = get(pack_id)
    for t in pack['templates']:
        if not re.fullmatch(r'[a-z0-9-]+', t['name']):
            raise ValueError('Invalid template filename')
    out = Path(destination)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'README.md').write_text(markdown(pack), encoding='utf-8')
    (out / 'pack.json').write_text(json.dumps(pack, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for t in pack['templates']:
        with (out / (t['name'] + '.csv')).open('x', newline='', encoding='utf-8') as handle:
            csv.writer(handle, lineterminator='\n').writerow(t['columns'])
    return dict(created=str(out), status='BLANK_WORKING_PACK_NOT_COMPLETED_ASSESSMENT', templates=len(pack['templates']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('list')
    show = commands.add_parser('show'); show.add_argument('pack_id')
    out = commands.add_parser('export'); out.add_argument('pack_id'); out.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        if args.action == 'show':
            print(markdown(get(args.pack_id))); return
        result = catalog() if args.action == 'list' else export(args.pack_id, args.out)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
