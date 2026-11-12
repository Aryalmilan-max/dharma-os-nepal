import copy
from datetime import date
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/dharma-os/scripts/assessments.py'
spec = importlib.util.spec_from_file_location('assessments', SCRIPT)
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
TODAY = date(2026, 11, 12)


class AssessmentReviewTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((REPO / 'examples/assessment-review/synthetic-shop.json').read_text())
        self.gap = next(m for m in self.plan['requirements'] if m['id'] == 'backup')

    def test_unknowns_remain_in_report_and_cannot_become_readiness_score(self):
        s = a.summary(self.plan, TODAY)
        self.assertEqual(s['counts']['GAP'], 1)
        self.assertEqual(s['counts']['NOT_ASSESSED'], 7)
        self.assertEqual(s['actions'][0]['id'], 'backup')
        self.assertEqual(s['actions'][0]['priority'], 'IMMEDIATE_REVIEW')
        self.assertEqual(len(s['actions']), 8)
        report = a.report(self.plan, TODAY)
        self.assertIn('SYNTHETIC DEMONSTRATION', report)
        self.assertIn('not a calibrated risk model', report)
        self.assertIn('NOT_ASSESSED: 7', report)
        self.assertNotIn('readiness_score', s)

    def test_gap_without_evidence_is_rejected(self):
        self.gap['evidence'] = []
        self.assertFalse(a.validate(self.plan, TODAY)['valid'])
        with self.assertRaises(ValueError):
            a.report(self.plan, TODAY)

    def test_met_needs_acceptance_and_reviewer(self):
        self.gap['assessment'] = 'MET'
        self.assertFalse(a.validate(self.plan, TODAY)['valid'])
        self.gap.update(acceptance_evidence='SYNTHETIC-RETEST-02', reviewer='Synthetic reviewer role', reviewed_on='2026-11-12')
        self.assertTrue(a.validate(self.plan, TODAY)['valid'])
        report = a.report(self.plan, TODAY)
        self.assertIn('SYNTHETIC-RETEST-02', report)
        self.assertIn('does not certify legal compliance', report)

    def test_exclusion_is_not_a_free_pass(self):
        self.gap['assessment'] = 'NOT_APPLICABLE'
        self.assertFalse(a.validate(self.plan, TODAY)['valid'])
        self.gap.update(reviewer='Synthetic reviewer role', reviewed_on='2026-11-12')
        self.assertTrue(a.validate(self.plan, TODAY)['valid'])

    def test_dates_urls_and_ratings_reject_unsafe_or_invalid_values(self):
        for field, value in [('url','javascript:alert(1)'), ('url','https://[bad'), ('url','https://:secret@example.com'), ('checked_on','2027-01-01'), ('checked_on','2026-02-30')]:
            p = copy.deepcopy(self.plan)
            next(m for m in p['requirements'] if m['id']=='backup')['evidence'][0][field]=value
            self.assertFalse(a.validate(p, TODAY)['valid'], (field,value))
        for value in [True, 0, 6, '4', 2.5]:
            self.gap['impact'] = value
            self.assertFalse(a.validate(self.plan, TODAY)['valid'])

    def test_malformed_input_does_not_render_or_crash_validator(self):
        for p in [None, [], {}, {'country':'Nepal','requirements':[None]}]:
            self.assertFalse(a.validate(p, TODAY)['valid'])
        for field,value in [('acceptance', []), ('evidence',None), ('reviewer',{}), ('assessment', ['MET'])]:
            p=copy.deepcopy(self.plan);p['requirements'][0][field]=value
            self.assertFalse(a.validate(p,TODAY)['valid'])
        self.plan['requirements'].append(copy.deepcopy(self.gap))
        self.assertFalse(a.validate(self.plan,TODAY)['valid'])

    def test_cli_preserves_statuses_and_refuses_invalid_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'assessment.json';p.write_text(json.dumps(self.plan))
            result=subprocess.run([sys.executable,str(SCRIPT),'report',str(p),'--as-of','2026-11-12'],capture_output=True,text=True,cwd=tmp)
            self.assertEqual(result.returncode,0);self.assertIn('GAP: 1',result.stdout)
            self.gap['evidence']=[];p.write_text(json.dumps(self.plan))
            invalid=subprocess.run([sys.executable,str(SCRIPT),'report',str(p),'--as-of','2026-11-12'],capture_output=True,text=True,cwd=tmp)
            self.assertNotEqual(invalid.returncode,0);self.assertIn('needs evidence',invalid.stderr)

    def test_printable_report_escapes_content_and_retains_unknowns(self):
        self.gap['rationale'] = '<script>unsafe()</script>'
        html = a.html_report(self.plan, TODAY)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn('NOT_ASSESSED: 7', html)
        self.assertIn('SYNTHETIC DEMONSTRATION', html)
        self.assertIn('not a calibrated risk model', html)
