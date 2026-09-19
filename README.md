# Performance-account policy research

Start with the **[Legacy 25K current findings](research/legacy_25k/OVERVIEW.md)**.
This repository contains a shared simulator and separate research entry points
for account products. It studies extraction, reserves and account purchases on
historical trade tapes; it does not establish future returns or a universal optimum.

| Read / do | Entry point |
|---|---|
| Understand the current conclusions | [Legacy 25K overview](research/legacy_25k/OVERVIEW.md) |
| Add evaluation supply to blocked copying | [Blocked pipeline findings](results/legacy_25k/blocked_pipeline/blocked_pipeline__FINDINGS.generated.md), [protocol](research/legacy_25k/BLOCKED_PIPELINE.md) |
| Optimize blocked copying for $1,000 + $200/month | [Joint operating-policy search](research/legacy_25k/BLOCKED_OPTIMIZATION.md) |
| Test minimum coverage with variable copies | [Hybrid routing findings](research/legacy_25k/ROUTING_HYBRID.md) |
| Compare 20 initial accounts and separately match exposure | [Fixed-inventory routing findings](research/legacy_25k/ROUTING_FIXED_INVENTORY.md) |
| Compare corrected routing and fixed-R pools | [Capacity-reuse findings](research/legacy_25k/ROUTING_REUSE.md) |
| Compare routing and copying under the same growth policy | [Funded monthly growth findings](research/legacy_25k/ROUTING_GROWTH.md) |
| Find the evidence for a question | [Legacy 25K study guide](research/legacy_25k/STUDIES.md) |
| Compare the next product | [Legacy 50K research](research/legacy_50k/README.md) |
| Compare reserves for both account sizes | [Paired reserve findings](results/comparisons/legacy_25k_vs_50k/reserve_by_policy/reserve_by_policy__FINDINGS.generated.md) |
| Can evaluations supply replacements fast enough? | [Pipeline-capacity findings](results/comparisons/legacy_25k_vs_50k/pipeline_capacity/pipeline_capacity__FINDINGS.generated.md) |
| Run or configure experiments | [Study configuration guide](config/studies/README.md) |
| Understand accounting and assumptions | [Economic effects](ECONOMIC_EFFECTS.md), [assumptions](ASSUMPTIONS.md) |
| Check saved-result consistency | [Audit](results/results__CONSISTENCY_AUDIT.md) |
| Browse all historical output folders | [Results index](results/results__README.md) |
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

Reports are named after their folder, e.g. `spare_shelf/spare_shelf__REPORT.md`.
Existing `<folder>__REPORT.md` and `report_breakdown.txt` files are reader-maintained.
Runners refresh `<folder>__REPORT.generated.md` and machine-readable outputs. Reader notes
may describe an earlier run; the study guide identifies the current generated report.

The former introduction is preserved as [historical findings](research/legacy_25k/HISTORICAL_FINDINGS.md).
50K Legacy has a separate focused operating study and source audit. EOD accounts remain deferred.
