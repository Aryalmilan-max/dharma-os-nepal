#!/usr/bin/env python3
"""Search bundled task skills and reference metadata, or export one portable skill."""
import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def search(rows, query='', **filters):
    words = query.casefold().split()
    return [r for r in rows if all(w in json.dumps(r, ensure_ascii=False).casefold() for w in words)
            and all(not value or (value in r.get(key, []) if isinstance(r.get(key), list) else r.get(key) == value)
                    for key, value in filters.items())]

def export_skill(skill_id, output):
    known = {s['id'] for s in json.loads((ROOT / 'catalog/skills.json').read_text())['skills']}
    if skill_id not in known:
        raise ValueError('Unknown task skill ID')
    # Exclusive create: never overwrite user work.
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted((ROOT / 'skills' / skill_id).rglob('*')):
            if path.is_file() and not path.is_symlink():
                archive.write(path, path.relative_to(ROOT / 'skills'))
    return dict(skill=skill_id, output=str(output))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    subs.add_parser('counts')
    for name in ('skills', 'sources'):
        p = subs.add_parser(name); p.add_argument('query', nargs='?', default='')
        p.add_argument('--offset', type=int, default=0); p.add_argument('--limit', type=int, default=25)
        if name == 'skills': p.add_argument('--family', default='')
        else:
            p.add_argument('--topic', default=''); p.add_argument('--kind', default=''); p.add_argument('--publisher', default='')
    p = subs.add_parser('export'); p.add_argument('skill_id'); p.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        catalog = json.loads((ROOT / 'catalog/skills.json').read_text())
        if args.command == 'counts':
            result = {k:v for k,v in catalog.items() if k != 'skills'}
        elif args.command == 'export':
            result = export_skill(args.skill_id, args.output)
        else:
            if args.offset < 0 or not 1 <= args.limit <= 100:
                parser.error('offset must be nonnegative and limit must be 1–100')
            if args.command == 'skills':
                rows = search(catalog['skills'], args.query, family=args.family)
            else:
                rows = search(json.loads((ROOT / 'catalog/source-records.json').read_text()), args.query,
                              topics=args.topic, kind=args.kind, publisher=args.publisher)
            result = dict(total=len(rows), offset=args.offset, records=rows[args.offset:args.offset + args.limit])
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, FileExistsError) as exc:
        parser.error(str(exc))

if __name__ == '__main__':
    main()
