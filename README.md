# Performance-account policy research

Start with the **[Legacy 25K current findings](research/legacy_25k/OVERVIEW.md)**.
This repository contains a shared simulator and separate research entry points
for account products. It studies extraction, reserves and account purchases on
historical trade tapes; it does not establish future returns or a universal optimum.

| Read / do | Entry point |
|---|---|
| Understand the current conclusions | [Legacy 25K overview](research/legacy_25k/OVERVIEW.md) |
| Find the evidence for a question | [Legacy 25K study guide](research/legacy_25k/STUDIES.md) |
| Prepare the next product | [Legacy 50K placeholders](research/legacy_50k/README.md) |
| Run or configure experiments | [Study configuration guide](config/studies/README.md) |
| Understand accounting and assumptions | [Economic effects](ECONOMIC_EFFECTS.md), [assumptions](ASSUMPTIONS.md) |
| Check saved-result consistency | [Audit](results/CONSISTENCY_AUDIT.md) |
| Browse all historical output folders | [Results index](results/README.md) |
| Understand project organization | [Maintenance guide](research/MAINTENANCE.md) |

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
.\venv\Scripts\python.exe scripts/audit_study_results.py
```

`src/` and `tests/` are shared. `config/` contains product specifications,
rulebooks, policies, scenarios and study profiles. `research/` is the reader's
entry point; `results/` retains the original evidence paths. `baselines/`
contains sealed regression evidence, and `archives/` preserves superseded runs.
`1_sweeps/` supplies local input data and is not committed.

Existing `REPORT.md` and `report_breakdown.txt` files are reader-maintained.
Runners refresh `REPORT.generated.md` and machine-readable outputs. Reader notes
may describe an earlier run; the study guide identifies the current generated report.

The former introduction is preserved as [historical findings](research/legacy_25k/HISTORICAL_FINDINGS.md).
50K Legacy is not runnable yet. EOD accounts are outside this change.
