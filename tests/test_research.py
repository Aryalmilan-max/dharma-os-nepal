import copy
import csv
from datetime import date
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'skills/dharma-os/scripts/research.py'
spec = importlib.util.spec_from_file_location('research', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
TODAY = date(2026, 11, 12)


class EvidenceWorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.study = copy.deepcopy(r.library()['studies'][0])

    def test_real_studies_retain_sources_and_export(self):
        for study in r.library()['studies']:
            result = r.validate(study, today=TODAY)
            self.assertTrue(result['structurally_valid'], result)
            self.assertEqual(result['review_status'], 'HUMAN_REVIEW_REQUIRED')
            self.assertGreater(result['evidence_links'], 0)
            self.assertIn('https://', r.report(study))
        ticket = r.library()['studies'][2]
        self.assertIn(f'{167933 * 1000000 / 75581982:,.2f}', ticket['claims'][1]['text'])

    def test_fact_without_support_and_unknown_source_rejected(self):
        self.study['claims'][0]['evidence'] = []
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])
        self.study = copy.deepcopy(r.library()['studies'][0])
        self.study['claims'][0]['evidence'][0]['source_id'] = 'invented'
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])

    def test_national_context_is_flagged_and_relabelling_rejected(self):
        self.study['geography'] = dict(country='Nepal', level='municipality', name='Banganga Municipality', code_source_url='https://censusresults.nsonepal.gov.np/local-level')
        honest = r.validate(self.study, TODAY)
        self.assertTrue(honest['structurally_valid'])
        self.assertTrue(any('geography differs' in w for w in honest['warnings']))
        self.study['claims'][0]['evidence'][0]['geography'] = 'Banganga Municipality'
        relabelled = r.validate(self.study, TODAY)
        self.assertFalse(relabelled['structurally_valid'])
        self.assertTrue(any('national-only' in e for e in relabelled['errors']))

    def test_contradictions_staleness_and_future_dates(self):
        e = self.study['claims'][0]['evidence'][0]
        e['checked_on'] = '2025-01-01'
        self.study['claims'][0]['evidence'].append(dict(e, relation='contradicts'))
        result = r.validate(self.study, TODAY)
        self.assertTrue(result['structurally_valid'])
        self.assertTrue(any('older' in w for w in result['warnings']))
        self.assertTrue(any('contradictory' in w for w in result['warnings']))
        e['checked_on'] = '2027-01-01'
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])
        e['checked_on'] = '2026-02-30'
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])

    def test_circular_and_missing_reasoning_basis(self):
        self.study['claims'][2]['basis'] = ['Q4']
        self.study['claims'][3]['basis'] = ['Q3']
        self.assertTrue(any('Circular' in e for e in r.validate(self.study, TODAY)['errors']))
        self.study['claims'][2]['basis'] = ['UNKNOWN']
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])

    def test_malformed_json_values_return_errors_not_crashes(self):
        for payload in [None, [], {}, {'schema_version': '1.0', 'domain_ids': [{}], 'claims': [None]}]:
            self.assertFalse(r.validate(payload, TODAY)['structurally_valid'])
        self.study['claims'][0]['evidence'][0]['source_id'] = []
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])
        self.study = copy.deepcopy(r.library()['studies'][0])
        self.study['protocol'] = {'invalid': 'object'}
        self.assertFalse(r.validate(self.study, TODAY)['structurally_valid'])

    def test_chronology_and_units_are_checked_before_comparison(self):
        result = r.compare('NRB-qr-volume-202509', 'NRB-qr-volume-202609')
        self.assertAlmostEqual(result['percentage_change'], 83.9523344735, places=6)
        self.assertEqual(result['absolute_change'], 34494174)
        for a, b in [('NRB-qr-volume-202609', 'NRB-qr-volume-202509'),
                     ('NRB-qr-volume-202509', 'NRB-qr-amount-202609'),
                     ('NRB-qr-volume-202509', 'NRB-wallet-volume-202609')]:
            with self.assertRaises(ValueError):
                r.compare(a, b)

    def test_csv_has_fifty_traceable_unique_records_and_sample_overlap(self):
        rows = list(csv.DictReader(io.StringIO(r.dataset_csv())))
        self.assertEqual(len(rows), 50)
        self.assertEqual(len({row['id'] for row in rows}), 50)
        self.assertTrue(all(row['locator'] and row['source_id'] and row['definition'] for row in rows))
        self.assertEqual(len({row['period_order'] for row in rows}), 5)
        # All eight overlapping old sample values must retain the exact original number/unit.
        old = r.read('statistical-observations.json')['observations']
        current = {(o['value'], o['unit']) for o in r.library()['observations'] if o['period_order'] == 202609}
        self.assertEqual(sum((o[2], o[3]) in current for o in old), 8)

    def test_search_finds_nepali_and_documented_smartboard_alias(self):
        self.assertTrue(any(s['id'] == 'D39' for s in r.search('smartboard')['results']))
        self.assertTrue(r.search('भुक्तानी', kind='observation')['results'])
        text = subprocess.check_output([sys.executable, str(SCRIPT.parent / 'nepal.py'), 'find', 'smartboard'], text=True)
        self.assertTrue(json.loads(text))

    def test_create_validate_export_cycle_outside_repository_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'study.json'
            args = [sys.executable, str(SCRIPT), 'init', '--template', 'school-readiness', '--question', 'Is this room ready?', '--locality', 'Banganga Municipality', '--out', str(path)]
            subprocess.run(args, check=True, capture_output=True, text=True, cwd=tmp)
            original = path.read_bytes()
            repeat = subprocess.run(args, capture_output=True, text=True, cwd=tmp)
            self.assertNotEqual(repeat.returncode, 0)
            self.assertEqual(path.read_bytes(), original)
            check = subprocess.run([sys.executable, str(SCRIPT), 'validate', str(path), '--as-of', '2026-11-12'], capture_output=True, text=True, cwd=tmp)
            self.assertEqual(check.returncode, 0)
            self.assertIn('research plan', check.stdout)
            study = json.loads(original)
            study['claims'] = self.study['claims']
            path.write_text(json.dumps(study))
            rendered = subprocess.check_output([sys.executable, str(SCRIPT), 'report', str(path)], text=True, cwd=tmp)
            self.assertIn('https://www.nrb.org.np/', rendered)
            study['claims'][0]['evidence'] = []
            path.write_text(json.dumps(study))
            bad = subprocess.run([sys.executable, str(SCRIPT), 'report', str(path)], capture_output=True, text=True, cwd=tmp)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn('Cannot render', bad.stderr)

    def test_source_citations_do_not_invent_publication_year(self):
        for fmt in ['ris', 'bibtex']:
            citation = r.citation('NP-BIZ-NRB-PAYMENTS-BHADRA2083', fmt)
            self.assertIn('nrb.org.np', citation)
            self.assertIn('2026-11-12', citation)
        self.assertNotIn('year =', r.citation('NP-BIZ-NRB-PAYMENTS-BHADRA2083', 'bibtex'))


if __name__ == '__main__':
    unittest.main()
