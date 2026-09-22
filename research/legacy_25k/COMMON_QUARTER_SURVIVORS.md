# Search for survivors of the three shared failure quarters

Design recorded 2026-09-23 after examining the existing 0.25-step screen,
before calculating the finer grid. This is a targeted historical search,
not an out-of-sample test. RR and GG name strategies; r/r is risk/reward.

Search all available ordinary settings: 0.50 through 3.50 in 0.01 steps,
301 per strategy, 602 total. Independently start each account flat on
2022-04-01, 2024-07-01 and 2025-04-01 and follow it to the next quarter.
Ask both whether a setting survives all three quarters and which settings
survive any particular quarter. Report contiguous surviving bands without
assuming a narrow band generalizes.

Use the existing episode experiment unchanged: one MNQ, $1.05 round-trip
commission, $1,500 headroom above a fixed starting floor, native entries
accepted while flat. No withdrawals, replacements, transfers or deployment
sequence. Failure means the first MAE or net-close floor breach, including
equality. A surviving account must avoid a breach throughout the quarter;
a positive ending P&L after an earlier breach is not survival.

Only trades completed strictly before the horizon contribute settled P&L
or MAE. Report positions left open at the horizon. Intratrade breaches are
intervals, not exact observed timestamps. Analytical paths continue after
the first marker solely for diagnostics. Save minimum headroom along this
path, first-breach identity and interval, accepted/closed counts and the
hash of the accepted trade sequence.

For settings surviving at least one target quarter, also compute all 26
fresh quarters from January 2020 through June 2026. This puts their other
failures in context; these historical observations are not a holdout. Keep
the RR 0.50, RR 2.50 and GG 1.25 controls in that comparison and report
whether adding each survivor removes any of their three common failures.
This is failure-set analysis, not a capital-allocation or operating study.

Validate every source tape with the existing reconciliation and coverage
checks. Compare routing with the blocked router and first markers with
independent Decimal accounting. Reproduce all 78 target results already
present in the coarse cross-strategy study, including first-breach fields.
Pin all source hashes, inherited code and result files in a new manifest;
leave existing studies unchanged. RR1000 is a separate all-hours experiment
and is not part of the 602-setting ordinary grid.

Results: [survivor report](../../results/legacy_25k/common_quarter_survivors/REPORT.md).

Reproduce with:

```powershell
.\venv\Scripts\python.exe scripts/study_common_quarter_survivors.py
```
