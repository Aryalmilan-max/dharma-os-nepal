import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/dharma-os/scripts/organizations.py'
spec = importlib.util.spec_from_file_location('organizations', SCRIPT)
org = importlib.util.module_from_spec(spec)
spec.loader.exec_module(org)


class OrganizationTests(unittest.TestCase):
    def test_all_profiles_produce_traceable_unassessed_requirements(self):
        data = org.catalog()
        for scale in data['scales']:
            for sector in data['organization_types']:
                plan = org.assess(scale['id'], sector['id'])
                ids = {m['id'] for m in plan['requirements']}
                self.assertTrue(set(data['baseline']) <= ids)
                self.assertEqual(len(ids), len(plan['requirements']))
                for m in plan['requirements']:
                    self.assertEqual(m['assessment'], 'NOT_ASSESSED')
                    self.assertEqual(m['evidence'], [])
                    self.assertTrue(m['evidence_to_collect'] and m['acceptance'])

    def test_small_critical_operations_do_not_lose_continuity_controls(self):
        small = org.assess('solo', 'repair')
        critical = org.assess('solo', 'repair', critical=True, sensitive=True)
        self.assertLess(len(small['requirements']), len(critical['requirements']))
        self.assertTrue({'security', 'continuity', 'governance'} <= {m['id'] for m in critical['requirements']})
        bank = org.assess('micro', 'finance')
        self.assertTrue({'security', 'continuity'} <= {m['id'] for m in bank['requirements']})

    def test_invalid_profile_is_rejected_and_report_preserves_status(self):
        with self.assertRaises(ValueError):
            org.assess('invented', 'repair')
        self.assertIn('NOT_ASSESSED', org.markdown(org.assess('enterprise', 'manufacturing')))


if __name__ == '__main__':
    unittest.main()
