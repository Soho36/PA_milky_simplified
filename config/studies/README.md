# Study profiles

`legacy_25k_routing_growth.json` is the dedicated matched-budget growth design
for `scripts/study_routing_growth.py`. It starts each arm with five paid accounts,
then uses monthly growth plus funded death replacements and daily minimum
withdrawals. See [growth findings](../../research/legacy_25k/ROUTING_GROWTH.md).

The dedicated `legacy_25k_routing_reuse.json` experiment uses
`scripts/study_legacy_routing.py --profile PATH` (its own schema, not `--study`).
It freezes reference trade-copy demand and buys only the entry-time free-slot
shortfall. `legacy_25k_fixed_pool.json` uses `scripts/study_fixed_routing_pool.py`
for R=1–4, initial K=5R and a 20-live-account cap. The older
`legacy_25k_routing.json` retains the superseded five-per-purchase control. See
[routing findings and limitations](../../research/legacy_25k/ROUTING_REUSE.md).

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

Reports are named after their folder (`<folder>__REPORT.md`; see `scripts/report_names.py`).
Reader-maintained `<folder>__REPORT.md` and report_breakdown.txt are not replaced by runs.
Current generated reports live in `<folder>__REPORT.generated.md`. Budgeted cadence's
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
the headline winners and refresh the shorter `reserve_by_policy__FINDINGS.generated.md`, including
account turnover, purchase fees, owner-excluded account deficits and detailed
winner ledgers. It also checks the selected winners under the stricter later-payout
minimum, without re-optimizing them. Existing `reserve_by_policy__FINDINGS.md` is kept as reader-maintained commentary.

For side-by-side presentation, run `venv/Scripts/python.exe scripts/format_legacy_comparison_reports.py`
after generating the reports. It pairs 25K on the left with 50K on the right,
without rerunning simulations or changing saved evidence. An identical reader copy
is refreshed; a reader copy with additional notes is preserved.
The linked Excel workbook includes the same paired comparisons, four budget tabs,
matched observations, reserve ties and all simulation settings.

### Blocked-copying twin

A spec with `"execution": "blocking"` runs the same study with one position per
account: an account copies a signal only while flat. A spec without the key is
non-blocking, as before. Blocking specs must write under
`results/comparisons_blocking/`, and non-blocking specs under
`results/comparisons/`, so the two trees never mix. The non-blocking tree is
the preserved reference and is not rerun.

```powershell
.\venv\Scripts\python.exe scripts/study_legacy_reserve_comparison.py config/studies/legacy_reserve_comparison_blocking.json
.\venv\Scripts\python.exe scripts/explain_legacy_reserve_comparison.py config/studies/legacy_reserve_comparison_blocking.json
.\venv\Scripts\python.exe scripts/format_legacy_comparison_reports.py results/comparisons_blocking/legacy_25k_vs_50k/reserve_by_policy
```

Then the spare shelf, which reads the blocked reserve comparison through its
`prior` key (a study may only read a predecessor from its own tree):

```powershell
.\venv\Scripts\python.exe scripts/study_legacy_spare_shelf.py config/studies/legacy_spare_shelf_blocking.json
```

Its unlimited-supply anchors and unbound rows must reproduce the blocked
reserve comparison, including per-trade account assignments.

`legacy_reserve_comparison_blocking.json` keeps the non-blocking grid. Its
controls are the settings it shares with the 25K blocked-copying optimization,
which must reproduce exactly, including per-trade account assignments. The
explainer also checks each replayed winner independently for overlapping trades.

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

## Fixed-inventory routing comparison

The separate joint optimization uses `legacy_25k_blocked_optimization.json`
and the user-selected budget $1,000 initially plus $200/month. Run
`venv/Scripts/python.exe scripts/optimize_blocked_copying.py`, followed by
`venv/Scripts/python.exe scripts/audit_blocked_optimization.py`.
It exhausts a declared coarse grid, locally refines reserves, then transfers
frozen winners across other budgets and historical starts. Checkpoints can
resume only with identical code, settings and inputs. The bound on the
optimization claim is documented in the profile and research notes.

The follow-up hybrid experiment uses `legacy_25k_routing_hybrid.json`.
Run `venv/Scripts/python.exe scripts/study_routing_hybrid.py`, followed by
`venv/Scripts/python.exe scripts/audit_routing_hybrid.py`. It tests minimum
participation of one/two copies and caps of four/eight/twelve, with max-headroom
selection, 20 initial seats and no replacements. The prior fixed-inventory
controls must exist and reproduce; their artifacts are preserved.

Run `venv/Scripts/python.exe scripts/study_routing_fixed_inventory.py`, then
`venv/Scripts/python.exe scripts/audit_routing_fixed_inventory.py`.
The profile is `legacy_25k_routing_fixed_inventory.json`; output goes to
`results/legacy_25k/routing_fixed_inventory/`. All seats are purchased before
trading, with no subsequent purchases or replacements. Twenty-account
resource controls are separate from exact per-trade reference exposure
replays and full-tape R=20 capacity trials. The latter search in steps of 20;
first success is sufficient on this tape, not necessarily a global minimum.
All arms within each case share the daily minimum withdrawal policy.

## Evaluation pipeline capacity

Run `venv/Scripts/python.exe scripts/study_legacy_pipeline_capacity.py`.
The design is in `legacy_pipeline_capacity.json`; new evidence goes to
`results/comparisons/legacy_25k_vs_50k/pipeline_capacity/`. Existing study
outputs are hashed and checked for preservation, and 16 historical winners
must reproduce before the new search starts.

The main budget is $5,000 initial plus $200/month, matching the earlier 57/44
funded-account winners. The full screening matrix varies persistent demand,
2/5/10/20 concurrent subscriptions, batch/one-per-day/one-per-week launches,
0/2/5/10 spare targets, and the evaluation seat-reservation assumption.
Three preselected withdrawal anchors screen each pipeline. Pipeline leaders
at each concurrency under both cash objectives nominate a common shortlist
for both products. That shortlist receives the full configured reserve,
withdrawal and cadence grid, followed by paired local refinement. This is a
staged search, not an exhaustive joint optimum. Selected shared-seat winners
are also replayed at the other three budgets without further optimization.

`screening.csv` holds the frozen-policy experiment; `reserve_search.csv`
holds the retuning; `frontier.csv` compares each concurrency at its own limit
(it is not a monotone envelope). `all_settings.csv` includes service and
financing diagnostics. Each of eight final winner folders contains daily
pipeline states and FIFO replacement waits in addition to the account ledger.
The runner's immutable contract and checkpoint rules are the same as above.

After completion, run `venv/Scripts/python.exe scripts/explain_legacy_pipeline_capacity.py`
for a compact interpretation, matched pipeline deltas and the observed 95%
replacement-service check. `plot_legacy_pipeline_capacity.py` produces a
standalone SVG chart using ReportLab; optional bundled Node/Sharp paths produce
the matching PNG. See that script's docstring for optional dependency arguments.
Run `venv/Scripts/python.exe scripts/audit_pipeline_capacity.py` after generating
the report and chart to verify the completed rows, paired search, code/input
contract and artifact hashes in `AUDIT.json`.
