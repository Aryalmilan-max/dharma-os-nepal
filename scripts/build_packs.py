#!/usr/bin/env python3
"""Generate public playbooks and blank CSV templates from maintained pack definitions."""
import csv
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'skills/dharma-os/scripts'))
import packs

for pack in packs.catalog():
    folder = REPO / 'docs/packs' / pack['id']
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'README.md').write_text(packs.markdown(pack), encoding='utf-8')
    for template in pack['templates']:
        with (folder / (template['name'] + '.csv')).open('w', encoding='utf-8', newline='') as handle:
            csv.writer(handle, lineterminator='\n').writerow(template['columns'])
