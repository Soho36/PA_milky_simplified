# Results index

For a shorter reading path, start with the
[Legacy 25K current findings](../research/legacy_25k/OVERVIEW.md) and
[study guide](../research/legacy_25k/STUDIES.md). This index retains the complete
historical output inventory. Product-specific study settings now live in
[study profiles](../config/studies/README.md).

Folder names show rulebook, withdrawal policy, retained balance, and closing action.
`terminal_request` is one firm-permitted request; `terminal_idealized` bypasses
payout restrictions for the closing profit withdrawal. `no_terminal` leaves
remaining account profit unwithdrawn. `retain_N` is nominal account balance,
not headroom above liquidation. Fixed monthly policies here accrue backlog.
The single-scenario runs below buy one account monthly without a live-account cap
and use RR; sweep files identify their tape. The purchase study has separate
funding and capacity assumptions, described below.

## Consistency and reader notes

See the [saved-results consistency audit](CONSISTENCY_AUDIT.md) before comparing
study totals. The amount/cushion and cadence studies are historical **uncapped**
experiments; the purchase study uses **20 live accounts** and explicit owner cash.
Their overlapping withdrawal settings agree, but acquisition-study totals are not
direct comparisons against those earlier experiments. The new
[budget-matched capped cadence study](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets/REPORT.md)
provides that comparison: 372 settings, four identical funding scenarios, a
20-live-account cap and 12 exact shared controls against monthly purchases in
the purchase study. It also shows purchase comparisons with withdrawal settings
held fixed. Historical uncapped studies retain their original scope.

The study runners write refreshed prose to `REPORT.generated.md`.
Existing `REPORT.md` and `report_breakdown.txt` files are reader-maintained and
are never overwritten. A new result directory also gets an initial `REPORT.md`.
After a rerun, review generated numbers before updating reader notes; those notes
may still describe the earlier run. The runners still replace generated CSV/JSON
and detailed run ledgers, so use a separate output directory for changed study designs.

Retained explanatory notes:
[purchase breakdown](study__full_rulebook__RR__account_purchases__cash_budgets/report_breakdown.txt)
and [cadence breakdown](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/report_breakdown.txt).

Repeat the read-only checks with `venv/Scripts/python.exe scripts/audit_study_results.py`
(only the audit document itself is regenerated).

`full_rulebook` means the configured rulebook, with processing delay OFF.
`no_payout_rules` still enforces account drawdown mechanics.
`legacy_rules` enables only minimum balance and the historical safety net
(with its $100 encroachment allowance). Config IDs and sealed baselines retain their historical names. Each folder has
a `RUN.md` with its regeneration command.

| Result/report | Stable config path under config/ |
|---|---|
| [full_rulebook__monthly_500__no_cushion__no_terminal](full_rulebook__monthly_500__no_cushion__no_terminal/report.txt) | `scenarios/full_rulebook_monthly_500.json` |
| [full_rulebook__monthly_500__retain_30000__terminal_request](full_rulebook__monthly_500__retain_30000__terminal_request/report.txt) | `scenarios/monthly_500_cushion_liquidated.json` |
| [full_rulebook__monthly_maximum__no_cushion__no_terminal](full_rulebook__monthly_maximum__no_cushion__no_terminal/report.txt) | `scenarios/full_rulebook_monthly_maximum.json` |
| [full_rulebook__hold__terminal_request](full_rulebook__hold__terminal_request/report.txt) | `scenarios/hold_then_firm_permitted.json` |
| [no_payout_rules__hold__terminal_idealized](no_payout_rules__hold__terminal_idealized/report.txt) | `scenarios/hold_then_liquidate.json` |
| [no_payout_rules__hold__no_terminal](no_payout_rules__hold__no_terminal/report.txt) | `bricks/brick1_ideal_world.json` |
| [legacy_rules__monthly_100__no_cushion__no_terminal](legacy_rules__monthly_100__no_cushion__no_terminal/report.txt) | `bricks/brick2_monthly_100.json` |
| [no_payout_rules__monthly_500__retain_26100__no_terminal](no_payout_rules__monthly_500__retain_26100__no_terminal/report.txt) | `scenarios/no_rules_monthly_500_cushion.json` |
| [full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search](full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search/report.txt) | `scenarios/full_rulebook_monthly_500.json` |

The `adapted_search` folder contains the same fixed-policy baseline plus the
cushion re-optimization experiment; its baseline cash is intentionally identical.
The other folders contain single-policy experiments and optional fixed ablations.

## Cushion searches

See `sweeps/`: filenames identify rulebook, tape, monthly withdrawal policy,
and whether the retained-balance grid is coarse or fine. These are historical
search outputs, not newly optimized policies. Terminal withdrawal is absent.

## Withdrawal amount x cushion study

[Compare monthly withdrawal policies and retained balances](study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/REPORT.md).
The study scores ongoing net cash and cash including one permitted terminal
request on each candidate's identical trading path. Account purchases remain
monthly. Every candidate also carries a trading-neutral flag and a ceiling
capture, both read against the hold benchmark's path. A withdrawal only lowers a
balance, so no candidate outlives that path, but it can out-earn it: trades an
early death avoids can be losing ones, and a capture above 100% would say so.
Neutrality is decided on a per-account fingerprint of the trades actually taken,
not on matching earnings totals, which two different paths can share.
`study.json` includes full provenance and `candidates.csv` contains
all tested settings. These are in-sample search results, not validated optima.

Reproduce: `venv/Scripts/python.exe scripts/study_withdrawal_amount.py`.

## Withdrawal cadence study

[Monthly, weekly and daily eligibility checks](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/REPORT.md)
with monthly account purchases and monthly fixed-target entitlement unchanged.
The 93 candidates cover the $31,600-$32,100 band plus the minimum-policy $30,000
control. Minimum requests mean $500 per eligible check, not a monthly budget.
Reproduce: `venv/Scripts/python.exe scripts/study_withdrawal_cadence.py`.

For capped, budget-matched comparisons, reproduce with
`venv/Scripts/python.exe scripts/study_budgeted_withdrawal_cadence.py`.
`Accounts` in study tables means total purchases over the full dataset;
`Alive` means survivors before the terminal request. Total purchases can exceed
20 while respecting a maximum of 20 simultaneously live accounts.

## Account purchase study

[Purchase policies under cash budgets — latest generated results](study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.generated.md):
monthly purchases, quarterly purchases, failure replacements, and payout
reinvestment. Four approved funding scenarios ($1,000/$5,000 initially, with
$0/$200 monthly thereafter) use the same 20-live-account modelled capacity cap.
Owner contributions are excluded from net cash created; unused principal remains
in ending owner cash. Each candidate uses one of the three previously studied
withdrawal policies without re-optimizing its cushion.

The expanded study has 132 candidates and includes `monthly_two` (up to two
on each month's first day) and `weekly_one` (one each Monday at midnight, no
extra opening purchase). Missed purchases expire. All 108 original candidates
reproduce exactly. Faster schedules change planned volume as well as timing.
The original reader report and breakdown remain intact; the pre-expansion
outputs are archived in `archives/studies/account_purchases_before_faster_schedules`.
The capped cadence study's
[refreshed fixed-withdrawal purchase tables](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets/REPORT.generated.md)
also include both additions, with the original cadence simulations retained.

Reproduce: `venv/Scripts/python.exe scripts/study_account_purchases.py`.

The current purchase report separates one-account scheduled purchases
(quarterly-one, monthly-one, weekly-one), monthly-two expansion, replacement/
reinvestment, and historical quarterly-three batches. All 132 simulation rows
are retained; quarterly-three is excluded from main rankings.
