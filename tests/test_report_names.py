"""Reports are named after their folder, and the one-time rename stays verifiable."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import report_names


class ReportNameTests(unittest.TestCase):
    def test_reports_are_named_after_their_folder(self):
        folder = Path('results/comparisons_blocking/legacy_25k_vs_50k/spare_shelf')
        self.assertEqual(report_names.report_path(folder, 'REPORT.generated.md').name,
                         'spare_shelf__REPORT.generated.md')

    def test_every_saved_report_follows_the_convention(self):
        stray = [p for p in (ROOT/'results').rglob('*.md') if not p.name.startswith(p.parent.name+'__')]
        self.assertEqual(stray, [])

    def test_reader_report_is_created_once_and_then_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'study'
            report_names.write_study_report(out, 'first')
            reader = out/'study__REPORT.md'
            reader.write_text('my notes', encoding='utf-8')
            report_names.write_study_report(out, 'second')
            self.assertEqual(reader.read_text(encoding='utf-8'), 'my notes')
            self.assertEqual((out/'study__REPORT.generated.md').read_text(encoding='utf-8'), 'second')
            self.assertFalse((out/'REPORT.md').exists())

    def test_ledger_accepts_only_recorded_renames_and_edits(self):
        ledger = json.loads(report_names.LEDGER.read_text(encoding='utf-8'))
        old, record = next(iter(ledger['files'].items()))
        self.assertFalse((ROOT/old).exists())
        self.assertTrue(report_names.verified(ROOT/old, record['old_sha256']))
        self.assertFalse(report_names.verified(ROOT/old, '0'*64))
        script, record = next(iter(ledger['scripts'].items()))
        self.assertTrue(report_names.verified(ROOT/script, record['old_sha256']))
        self.assertFalse(report_names.verified(ROOT/script, '0'*64))


if __name__ == '__main__':
    unittest.main()
