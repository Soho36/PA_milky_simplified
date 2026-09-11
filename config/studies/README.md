# Study profiles

The study runners accept `--study PATH`. Paths inside a profile resolve
from the repository root. The default is `config/studies/legacy_25k.json`.
Existing commands and output locations are retained.

```powershell
.\venv\Scripts\python.exe scripts/study_withdrawal_amount.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_withdrawal_cadence.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_account_purchases.py --study config/studies/legacy_25k.json
.\venv\Scripts\python.exe scripts/study_budgeted_withdrawal_cadence.py --study config/studies/legacy_25k.json
```

Run purchases before budgeted cadence, which verifies shared controls against
its saved source. The amount runner also supports `--workers` and `--out`.
Worker processes read the same command-line profile. New simulation outputs
embed the profile and its hash alongside resolved scenario/input provenance.
Older saved outputs retain their original provenance; this refactor does not
retroactively label them as reruns.

Profiles specify scenario, output folders, budgets, live cap, amount-policy
family, headroom/refinement grid, cadence grid and purchase withdrawal shortlist.
The eleven acquisition algorithms and common simulation conventions remain code;
this is not an arbitrary workflow language. Use separate output locations for a
new product or changed experiment design. A ready profile must use distinct
folders for its studies.

`legacy_50k.json` is now ready for the focused account-product study. It uses
separate product/rulebook files and output folders under `results/legacy_50k/`.
The loader rejects output overlap across ready product profiles. See
[50K source verification](../../research/legacy_50k/SOURCES.md) for model limits.
Run `venv/Scripts/python.exe scripts/study_legacy_50k_operating.py` for the
focused search and matched comparisons, rather than repeating every historical study.

Reader-maintained REPORT.md and report_breakdown.txt are not replaced by runs.
Current generated reports live in REPORT.generated.md. Budgeted cadence's
`--refresh-purchase-tables` refreshes presentation from saved cadence rows and
rechecks purchase controls; it is not a new cadence simulation.

The replacement comparison uses the `replacements` output key:
`venv/Scripts/python.exe scripts/study_monthly_replacements.py --study config/studies/legacy_25k.json`.

## Paired account-size reserve search

Run `venv/Scripts/python.exe scripts/study_legacy_reserve_comparison.py`.
Its dedicated experiment specification is `legacy_reserve_comparison.json`;
this is not a product profile to pass to `--study`. It loads both ready product
profiles and writes only to
`results/comparisons/legacy_25k_vs_50k/reserve_by_policy/`.

Both products receive the same coarse grid and the union of local refinements
within every budget/purchase/withdrawal/cadence family. The search covers minimum
and maximum withdrawals with both ongoing and terminal-inclusive objectives.
It does not re-optimize the optional stricter payout interpretation.

Completed rows are checkpointed. Re-running the unchanged experiment resumes
missing simulations and rebuilds generated outputs. Changes to the experiment,
resolved scenarios, tape, engine, evaluator or runner require a new output
directory; stale checkpoints are rejected rather than silently mixed.

After the search, run
`venv/Scripts/python.exe scripts/explain_legacy_reserve_comparison.py` to replay
the headline winners and refresh the shorter `FINDINGS.generated.md`, including
account turnover, purchase fees, owner-excluded account deficits and detailed
winner ledgers. It also checks the selected winners under the stricter later-payout
minimum, without re-optimizing them. Existing `FINDINGS.md` is kept as reader-maintained commentary.

For side-by-side presentation, run `venv/Scripts/python.exe scripts/format_legacy_comparison_reports.py`
after generating the reports. It pairs 25K on the left with 50K on the right,
without rerunning simulations or changing saved evidence. An identical reader copy
is refreshed; a reader copy with additional notes is preserved.
The linked Excel workbook includes the same paired comparisons, four budget tabs,
matched observations, reserve ties and all simulation settings.

## Limited supply of funded accounts (spare shelf)

Run `venv/Scripts/python.exe scripts/study_legacy_spare_shelf.py`. The
specification is `legacy_spare_shelf.json`; results go to
`results/comparisons/legacy_25k_vs_50k/spare_shelf/`.

The paired reserve search assumes every purchase becomes a funded account at
once. This study limits that supply:

- At most N accounts pass per calendar month, each paid when it passes.
- Surplus passes wait dormant on a shelf of K spares.
- Spares count toward the 20-account cap.

It re-searches reserves for every (K, N) with the replacement policy, and
weekly and monthly purchasing run without spares as comparators. The mechanism
and its biases are in [ASSUMPTIONS.md](../../ASSUMPTIONS.md#supply-of-funded-accounts).
With the shelf switched off, the engine reproduces the unlimited-supply study
exactly, and the runner re-checks every row that supply cannot bind against
that study's checkpoint. Checkpointing and contract rules are the same as
above.

## Funded accounts from traded evaluations

Run `venv/Scripts/python.exe scripts/study_legacy_eval_supply.py`. The
specification is `legacy_eval_supply.json`; results go to
`results/comparisons/legacy_25k_vs_50k/eval_supply/`.

This replaces the fixed pass rate with evaluations traded on the same tape:

- One position at a time: 25K at 3 MNQ ($1,500 target / $1,500 drawdown) and
  50K at 5 MNQ ($3,000 / $2,500), the sizes the EODMAE study chose.
- Monthly fees ($33 / $40) with a free reset at renewal, plus $125 activation.
- Up to 5 evaluations at once, started only while the book is short. Each one
  in flight holds one of the 20 seats.

Before searching, the runner checks two things:

- With evaluations switched off, the engine still reproduces the
  unlimited-supply winners.
- One evaluation started on every weekday reproduces EODMAE's pass rates and
  days to pass (the reconciliation table in the report).
