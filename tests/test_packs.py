import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/dharma-os/scripts/packs.py'
spec = importlib.util.spec_from_file_location('packs', SCRIPT)
packs = importlib.util.module_from_spec(spec); spec.loader.exec_module(packs)


class PackTests(unittest.TestCase):
    def test_every_pack_exports_blank_distinct_working_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            for pack in packs.catalog():
                path = Path(tmp) / pack['id']
                result = packs.export(pack['id'], path)
                self.assertEqual(result['templates'], 4)
                self.assertEqual(len(pack['workflows']), 6)
                for t in pack['templates']:
                    with (path / (t['name'] + '.csv')).open() as handle:
                        rows = list(csv.reader(handle))
                    self.assertEqual(rows, [t['columns']])
                    self.assertEqual(len(set(t['columns'])), len(t['columns']))
                original = (path / 'README.md').read_bytes()
                with self.assertRaises(FileExistsError):
                    packs.export(pack['id'], path)
                self.assertEqual((path / 'README.md').read_bytes(), original)

    def test_unknown_pack_cannot_create_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'output'
            with self.assertRaises(ValueError):
                packs.export('../unknown', path)
            self.assertFalse(path.exists())

    def test_bank_sources_and_research_limits_survive_export(self):
        self.assertIn('nrb.org.np/bfr/it-guidelines-2012', packs.markdown(packs.get('commercial-bank')))
        self.assertIn('NOT_ASSESSED', packs.markdown(packs.get('school')))
        self.assertIn('AI checks are not described as peer review', packs.markdown(packs.get('researcher')))
