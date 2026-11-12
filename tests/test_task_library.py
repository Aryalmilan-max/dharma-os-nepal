import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('library', ROOT / 'scripts/library.py')
library = importlib.util.module_from_spec(spec); spec.loader.exec_module(library)

class TaskLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = json.loads((ROOT / 'catalog/skills.json').read_text())['skills']
        cls.sources = json.loads((ROOT / 'catalog/source-records.json').read_text())
        cls.manifest = json.loads((ROOT / 'catalog/source-manifest.json').read_text())

    def test_actual_portable_skills_and_distinct_deliverables(self):
        self.assertEqual(len(self.skills), 100)
        self.assertEqual(len(list((ROOT / 'skills').glob('*/SKILL.md'))), 101)
        for key in ('id', 'title', 'trigger', 'acceptance'):
            self.assertEqual(len({s[key] for s in self.skills}), 100, key)
        for s in self.skills:
            folder = ROOT / 'skills' / s['id']
            text = (folder / 'SKILL.md').read_text()
            self.assertTrue(text.startswith('---\nname: ' + s['id'] + '\n'))
            self.assertIn('UNKNOWN', text); self.assertIn(s['acceptance'], text)
            self.assertEqual(next(csv.reader((folder / 'assets/working-record.csv').read_text().splitlines())), s['artifact_columns'])
            self.assertEqual(len((folder / 'assets/working-record.csv').read_text().splitlines()), 1)

    def test_source_identity_count_provenance_and_review_boundaries(self):
        self.assertGreaterEqual(len(self.sources), 10000)
        self.assertEqual(len(self.sources), self.manifest['unique_reference_urls'])
        self.assertEqual(len({s['url'] for s in self.sources}), len(self.sources))
        self.assertEqual(len({s['id'] for s in self.sources}), len(self.sources))
        indexes = {s['id']:s for s in self.manifest['source_indexes'] if 'id' in s}
        for s in self.sources:
            self.assertIsNone(s['page_reviewed_on'])
            if s['kind'] == 'international_technical_reference':
                self.assertFalse(s['nepal_market_evidence'])
                self.assertEqual(s['verification_state'], 'PUBLISHER_INDEX_DISCOVERED_NOT_PAGE_REVIEWED')
                self.assertIn(s['discovery_index'], indexes)
                self.assertNotIn('#', s['url']); self.assertNotIn('?', s['url'])
        for snapshot in indexes.values():
            self.assertEqual(len(snapshot['sha256']), 64)
            self.assertGreater(snapshot['bytes'], 0)
        for filename, digest in self.manifest['bundled_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / 'catalog' / filename).read_bytes()).hexdigest(), digest)

    def test_export_is_portable_and_never_overwrites_or_traverses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'skill.zip'
            library.export_skill('np-shop-repair-intake', path)
            with zipfile.ZipFile(path) as z:
                self.assertEqual(set(z.namelist()), {'np-shop-repair-intake/SKILL.md','np-shop-repair-intake/assets/working-record.csv'})
            with self.assertRaises(FileExistsError): library.export_skill('np-shop-repair-intake', path)
            with self.assertRaises(ValueError): library.export_skill('../dharma-os', Path(tmp) / 'bad.zip')

    def test_task_references_are_curated_not_broad_topic_guesses(self):
        repair = next(s for s in self.skills if s['id'] == 'np-shop-repair-intake')
        self.assertEqual(repair['supporting_references'], [])
        self.assertTrue({'device_identifier','custody_received_at','authorization_ref'} <= set(repair['artifact_columns']))
        bank = next(s for s in self.skills if s['id'] == 'np-bank-regulatory-crosswalk')
        self.assertTrue(any('it-guidelines-2012' in s['url'] for s in bank['supporting_references']))
        self.assertFalse(any('macro' in s['url'] for s in bank['supporting_references']))
        self.assertEqual(library.search(self.skills, 'repair intake', family='shop')[0]['id'], 'np-shop-repair-intake')

if __name__ == '__main__': unittest.main()
