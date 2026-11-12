import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REF = REPO / 'skills/dharma-os/references/nepal-tech-intelligence'
CLI = REPO / 'skills/dharma-os/scripts/nepal.py'


class PublicSkillTests(unittest.TestCase):
    def invoke(self, *args):
        with tempfile.TemporaryDirectory() as cwd:
            return json.loads(subprocess.check_output([sys.executable, str(CLI), *args], cwd=cwd, text=True))

    def test_portable_lookup_and_source_links(self):
        domains = self.invoke('domain', 'D39')
        self.assertEqual(len(domains), 1)
        registry = json.loads((REF / 'source-registry.json').read_text())
        source_ids = {record['id'] for record in registry}
        for domain in json.loads((REF / 'domains.json').read_text()):
            self.assertTrue(set(domain['candidate_source_ids']) <= source_ids)
            self.assertTrue((REF / 'domains' / (domain['id'] + '.md')).is_file())

    def test_brief_preserves_unverified_locality_and_claim_status(self):
        brief = self.invoke('brief', '--domain', 'D39', '--locality', 'Example locality')
        self.assertEqual(brief['status'], 'RESEARCH_BRIEF_NOT_A_MARKET_FINDING')
        self.assertIn('NOT_VERIFIED', brief['locality_validation'])
        self.assertEqual(brief['locality_supplied_by_user'], 'Example locality')
        self.assertTrue(brief['candidate_sources'])

    def test_unknown_domain_fails_with_useful_message(self):
        result = subprocess.run([sys.executable, str(CLI), 'brief', '--domain', 'INVALID', '--locality', 'Example'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unknown domain', result.stderr)

    def test_statistics_retain_interpretation_limits(self):
        result = self.invoke('observations')
        self.assertIn('reference_periods', result)
        self.assertTrue(any('unique people' in caveat for caveat in result['caveats']))
        self.assertTrue(any('card' in caveat.lower() for caveat in result['caveats']))
        self.assertEqual(len(result['observations']), 10)

    def test_coverage_does_not_claim_unbundled_registers(self):
        result = self.invoke('coverage')
        self.assertFalse(result['continuous_monitoring_deployed'])
        self.assertFalse(result['complete_sector_coverage'])
        self.assertNotIn('local_levels', result['packaged'])
        self.assertFalse((REF / 'locality-coverage.csv').exists())
        self.assertFalse((REF / 'media-pcn-online.csv').exists())

    def test_public_tree_has_no_machine_paths_or_private_archives(self):
        for path in REPO.rglob('*'):
            if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
                continue
            self.assertFalse(path.is_symlink(), str(path))
            self.assertNotIn(path.suffix, {'.sqlite3', '.db', '.jsonl', '.pem', '.key'}, str(path))
            if path != Path(__file__).resolve():
                text = path.read_text(encoding='utf-8')
                # This exact official documentation URL contains a public /home/ section.
                scanned = text.replace('https://kubernetes.io/docs/home/supported-doc-versions', '')
                self.assertFalse('/Users/' in scanned, str(path))
                self.assertFalse('/home/' in scanned, str(path))
                self.assertFalse('BEGIN PRIVATE KEY' in scanned, str(path))


if __name__ == '__main__':
    unittest.main()
