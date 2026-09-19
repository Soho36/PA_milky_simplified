"""Reports are named after their folder: spare_shelf/spare_shelf__REPORT.md.

Until 2026-09-20 every folder used fixed names (REPORT.md, FINDINGS.generated.md, ...).
results/RENAMES.json records that one-time rename: each report's old and new path with
its hash before and after links were rewritten, and each script edited for the new names.
Audits that pin hashes use `verified` so they accept exactly those recorded changes.

This replaces pa_milky.study_reports.write_study_report, which still writes the old
names; it is left unchanged because the engine fingerprint covers every file in src.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT_ROOT/'results/RENAMES.json'


def report_path(folder, kind):
    """kind is the old fixed name, e.g. 'REPORT.md' or 'FINDINGS.generated.md'."""
    folder = Path(folder)
    return folder/f'{folder.name}__{kind}'


def write_study_report(out, report):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    report_path(out, 'REPORT.generated.md').write_text(report, encoding='utf-8')
    # The plain report and report_breakdown.txt belong to the reader. Never replace them.
    reader = report_path(out, 'REPORT.md')
    if not reader.exists():
        reader.write_text(report, encoding='utf-8')


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def _ledger():
    return json.loads(LEDGER.read_text(encoding='utf-8')) if LEDGER.exists() else {'files': {}, 'scripts': {}}


def verified(path, digest):
    """True if `path` still has `digest`, or was renamed/edited exactly as the ledger records."""
    path = Path(path).resolve()
    if path.is_file() and _sha(path) == digest:
        return True
    key = path.relative_to(PROJECT_ROOT).as_posix()
    ledger = _ledger()
    if key in ledger['files']:
        record = ledger['files'][key]
        current = PROJECT_ROOT/record['renamed_to']
    elif key in ledger.get('scripts', {}):
        record = ledger['scripts'][key]
        current = path
    else:
        return False
    # Files edited in place record the committed content in both line-ending forms,
    # because earlier pins hashed whichever form the working copy happened to have.
    before = {record['old_sha256'], record.get('old_sha256_crlf')}
    return digest in before and current.is_file() and _sha(current) == record['new_sha256']
