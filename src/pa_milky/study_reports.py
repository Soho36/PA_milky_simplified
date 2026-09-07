"""Keep reader-edited study reports separate from regenerated output."""
from pathlib import Path


def write_study_report(out: Path, report: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / 'REPORT.generated.md').write_text(report, encoding='utf-8')
    # REPORT.md and report_breakdown.txt belong to the reader. Never replace them.
    if not (out / 'REPORT.md').exists():
        (out / 'REPORT.md').write_text(report, encoding='utf-8')
