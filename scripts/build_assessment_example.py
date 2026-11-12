#!/usr/bin/env python3
"""Render the explicitly synthetic assessment fixture at its fixed review date."""
from datetime import date
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'skills/dharma-os/scripts'))
import assessments

folder = REPO / 'examples/assessment-review'
plan = json.loads((folder / 'synthetic-shop.json').read_text(encoding='utf-8'))
assert plan['is_synthetic'] is True
for extension, renderer in [('md', assessments.report), ('html', assessments.html_report)]:
    (folder / ('synthetic-shop-report.' + extension)).write_text(renderer(plan, date(2026, 11, 12)), encoding='utf-8')
