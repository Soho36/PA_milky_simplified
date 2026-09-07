from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from pa_milky.study_reports import write_study_report


class TestStudyReports(unittest.TestCase):
    def test_regeneration_preserves_reader_files_exactly(self):
        with TemporaryDirectory() as root:
            out = Path(root)
            write_study_report(out, 'first generation')
            notes = b'User notes\r\n\xc3\xa4\r\n'
            (out/'REPORT.md').write_bytes(notes)
            (out/'report_breakdown.txt').write_bytes(notes)
            write_study_report(out, 'new results')
            self.assertEqual((out/'REPORT.md').read_bytes(), notes)
            self.assertEqual((out/'report_breakdown.txt').read_bytes(), notes)
            self.assertEqual((out/'REPORT.generated.md').read_text(), 'new results')
