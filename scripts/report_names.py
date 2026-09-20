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
# Later edits to scripts that saved audits pin, each with its verification.
SCRIPT_EDITS = PROJECT_ROOT/'results/SCRIPT_EDITS.json'
# Deliberate src/pa_milky changes, old engine digest to new. See its own purpose text.
ENGINE_CHANGES = PROJECT_ROOT/'results/ENGINE_CHANGES.json'


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


def _shas(path):
    # A checkout with core.autocrlf rewrites LF files as CRLF without changing their content,
    # so a file also matches through its LF-normalized bytes.
    data = Path(path).read_bytes()
    return {hashlib.sha256(data).hexdigest(), hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()}


@lru_cache(maxsize=None)
def _ledger():
    return json.loads(LEDGER.read_text(encoding='utf-8')) if LEDGER.exists() else {'files': {}, 'scripts': {}}


@lru_cache(maxsize=None)
def _script_edits():
    return json.loads(SCRIPT_EDITS.read_text(encoding='utf-8'))['edits'] if SCRIPT_EDITS.exists() else []


def verified(path, digest):
    """True if `path` still has `digest`, or was renamed/edited exactly as the ledgers record."""
    path = Path(path).resolve()
    if path.is_file() and digest in _shas(path):
        return True
    key = path.relative_to(PROJECT_ROOT).as_posix()
    ledger = _ledger()
    if key in ledger['files']:
        record = ledger['files'][key]
        current = PROJECT_ROOT/record['renamed_to']
    elif key in ledger.get('scripts', {}):
        # Follow the recorded edits, in order, from the pinned hash to the file as it is now.
        edits = [ledger['scripts'][key]] + [e for e in _script_edits() if e['path'] == key]
        reached = digest
        for edit in edits:
            if edit['old_sha256'] == reached:
                reached = edit['new_sha256']
        return path.is_file() and reached in _shas(path)
    else:
        return False
    # Files edited in place record the committed content in both line-ending forms,
    # because earlier pins hashed whichever form the working copy happened to have.
    before = {record['old_sha256'], record.get('old_sha256_crlf')}
    return digest in before and current.is_file() and record['new_sha256'] in _shas(current)


@lru_cache(maxsize=None)
def _engine_changes():
    if not ENGINE_CHANGES.exists():
        return []
    return json.loads(ENGINE_CHANGES.read_text(encoding='utf-8'))['transitions']


def engine_accepted(pinned, current):
    """True if `pinned` is `current`, or reaches it through recorded engine changes.

    A saved contract pins the engine digest of the day it ran. Editing src changes
    that digest without necessarily changing a single number, so an audit would
    fail on the fingerprint alone. results/ENGINE_CHANGES.json records each such
    change; this follows the chain from the pinned digest forward. A digest that
    is not in the chain is still a failure -- unrecorded drift is exactly what the
    assertion is for.
    """
    pinned_sha = pinned['combined_sha256'] if isinstance(pinned, dict) else pinned
    current_sha = current['combined_sha256'] if isinstance(current, dict) else current
    if pinned_sha == current_sha:
        return True
    reached = pinned_sha
    for change in _engine_changes():
        if change['old_combined_sha256'] == reached:
            reached = change['new_combined_sha256']
    return reached == current_sha
