#!/usr/bin/env python3
"""Read the portable Nepal technology-business knowledge tree; no network access."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'references/nepal-tech-intelligence'


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def matches(record, query):
    return query.casefold() in json.dumps(record, ensure_ascii=False).casefold()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    commands.add_parser('coverage')
    commands.add_parser('observations')
    for action in ['find', 'domain', 'sources', 'methods', 'media']:
        command = commands.add_parser(action)
        command.add_argument('query')
        command.add_argument('--limit', type=int, default=12)
    brief = commands.add_parser('brief')
    brief.add_argument('--domain', required=True)
    brief.add_argument('--locality', required=True)
    args = parser.parse_args()
    if args.action == 'coverage':
        result = load('coverage.json')
    elif args.action == 'observations':
        result = load('statistical-observations.json')
    elif args.action == 'media':
        with (ROOT / 'checked-media-outlets.csv').open(encoding='utf-8', newline='') as handle:
            result = [r for r in csv.DictReader(handle) if matches(r, args.query)]
        result = {'results': result[:max(1, min(args.limit, 100))], 'limitations': 'Publisher snapshot only; no bulk registry, validated municipality coverage, or active monitoring is bundled.'}
    elif args.action == 'sources':
        result = [s for s in load('source-registry.json') if matches(s, args.query)][:max(1, min(args.limit, 100))]
    elif args.action == 'methods':
        result = [m for m in load('principles-and-methods.json')['methods'] if matches(m, args.query)][:max(1, min(args.limit, 100))]
    else:
        domains = load('domains.json')
        if args.action == 'domain':
            result = [d for d in domains if d['id'].casefold() == args.query.casefold() or args.query.casefold() in d['name'].casefold()][:max(1, min(args.limit, 60))]
        elif args.action == 'find':
            result = []
            for domain in domains:
                if matches({k: v for k, v in domain.items() if k != 'leaves'}, args.query):
                    result.append({'id': domain['id'], 'domain': domain['name'], 'reference': 'domains/' + domain['id'] + '.md'})
                for leaf in domain['leaves']:
                    if matches(leaf['name'], args.query):
                        result.append({'id': leaf['id'], 'topic': leaf['name'], 'knowledge_status': leaf['knowledge_status']})
            result = result[:max(1, min(args.limit, 100))]
        else:
            domain = next((d for d in domains if d['id'].casefold() == args.domain.casefold()), None)
            if domain is None:
                parser.error('Unknown domain ID; use find or domain.')
            source_ids = set(domain['candidate_source_ids'])
            result = {
                'status': 'RESEARCH_BRIEF_NOT_A_MARKET_FINDING',
                'locality_supplied_by_user': args.locality,
                'locality_validation': 'NOT_VERIFIED; official-code directory is not bundled.',
                'domain': domain,
                'candidate_sources': [s for s in load('source-registry.json') if s['id'] in source_ids],
                'required_evidence': ['Resolve official locality codes and current boundaries', 'Current institution, need and baseline', 'Official budget/notice and actual procurement stage where relevant', 'Local reporting and corroboration', 'Power, connectivity, skills, access and support constraints'],
            }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
