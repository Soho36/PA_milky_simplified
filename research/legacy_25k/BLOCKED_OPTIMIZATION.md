# Blocked copying: joint operating-policy optimization

**Best tested ongoing and terminal-inclusive net cash: $665,420.55.** The
search completed 3,932 primary-budget settings. Three policies tie at that
score. A representative is one initial account, monthly growth plus funded
death replacements, maximum weekly withdrawals, and a $25,100 retained
balance. It buys 531 accounts over the dataset and loses 511, while never
exceeding 20 live accounts. The result is conditional on immediate $200
funded-account supply; it is not an established optimum for an evaluation pipeline.

[Generated search tables](../../results/legacy_25k/blocked_optimization/blocked_optimization__REPORT.generated.md),
[all settings](../../results/legacy_25k/blocked_optimization/all_settings.csv),
[independent audit](../../results/legacy_25k/blocked_optimization/AUDIT.generated.json),
[all tied-policy transfers](../../results/legacy_25k/blocked_optimization/tied_transfers.csv).

## Result at the chosen budget

All figures cover January 2020 through July 2026 and subtract account fees.
Both the old and new policies below enforce one position per account.

| Metric | Earlier baseline | Representative tied leader |
|---|---:|---:|
| Initial accounts | 5 | 1 |
| Purchases | Monthly plus replacements | Monthly plus replacements |
| Withdrawal checks | Daily minimum | Weekly maximum |
| Retained balance | $31,900 | $25,100 |
| Lifetime purchases | 67 | 531 |
| Account deaths | 47 | 511 |
| Ending live accounts | 20 | 20 |
| Account fees | $13,400 | $106,200 |
| Payout receipts | $282,000 | $771,620.55 |
| Ongoing net cash | $268,600 | $665,420.55 |
| Terminal receipts | $0 | $0 |
| Total net cash | $268,600 | $665,420.55 |

The improvement is $396,820.55, or 147.74%. Relative to the earlier
$30,000-reserve baseline ($334,100), the improvement is $331,320.55.
Starting with one account spends $200 initially and leaves $800 available
for later needs. The $200 monthly contributions continue; the search does
not introduce extra owner funding. Total owner contributions are $16,600,
which are excluded from the net-cash score.

Weekly maximum means request as much as the configured rules allow at each
weekly check. The $25,100 target does not permit withdrawing through the
trailing floor: the firm model still preserves its mandatory touch margin.
It leaves very little voluntary protection once the floor freezes. The
model can consequently withdraw cash and then lose an account soon afterward.

There were 158,970 accepted trade copies on 9,263 of 12,658 exported signals
(73.18% signal participation). Forty-eight signals arrived with no live
accounts; other misses reflect busy accounts. The median lifetime among
failed accounts was about 36 days. Purchases peaked at 60 in one calendar
month, reached in May 2022, March 2025 and March 2026. A 20-live-account limit
does not constrain this cumulative turnover.

## Ties and unchanged-policy transfers

These three primary-budget policies produce exactly the same cash totals,
purchase/death counts and per-trade account assignments on the full tape:

1. Monthly growth plus replacements; maximum weekly withdrawals.
2. Monthly growth with replacements consuming an unused current-month slot;
   maximum weekly withdrawals.
3. The same current-slot purchase policy; $1,500 monthly accrual with backlog,
   checked weekly.

All start with one account and retain $25,100. The generated report's single
representative is the third policy because of its deterministic display
tie-break; it is not financially superior to the first two. The separate
tie check transfers all three policies, not just that displayed row.

The two maximum-weekly policies remain equal in all eight transfer cases.
Their unchanged-policy outcomes at $1,000 + $200/month are:

| Fresh start | Net cash through July 2026 |
|---:|---:|
| 2021 | $620,933.40 |
| 2022 | $566,273.55 |
| 2023 | $479,040.15 |
| 2024 | $311,074.99 |
| 2025 | $99,146.26 |

The fixed-$1,500 variant ties in 2021/2022, trails by $241.60 in 2023/2024,
and trails by $1,300 in 2025. These overlapping, unequal-length periods
cannot be compared as annual returns or treated as independent validation.

With only $1,000 and no monthly contribution, all three policies fail and
finish at -$1,000. With $5,000 initially, they produce $670,285.60 with either
$0 or $200/month. The contribution matters during the cash-constrained
startup, but is not itself profit.

## Less turnover gives different cash trade-offs

Examples drawn from the completed search, without imposing a new execution
constraint or retuning for a lifetime-purchase cap:

| Tested policy | Bought | Ongoing net | Terminal receipts | Total net |
|---|---:|---:|---:|---:|
| One initial; monthly two; minimum weekly; retain $27,500 | 96 | $367,300 | $0 | $367,300 |
| One initial; monthly plus replacements; minimum monthly; retain $29,100 | 71 | $254,300 | $198,951.93 | $453,251.93 |
| One initial; current-slot replacements; minimum monthly; retain $25,100 | 185 | $356,000 | $153,740.80 | $509,740.80 |
| Representative cash leader | 531 | $665,420.55 | $0 | $665,420.55 |

The 71-account result is attractive on terminal-inclusive cash but delivers
less ongoing cash than the old $31,900 baseline. This is why the two cash
objectives remain separate. The higher-turnover winner has no terminal
windfall in its score.

The primary budget is $1,000 initially plus $200 per subsequent calendar
month. Every free live account copies each signal; occupied accounts skip
it. Contract size remains one MNQ per account. This study optimizes the
operating policy around that realistic single-position execution constraint.

The search ranks both ongoing net cash and total net cash including one
firm-permitted terminal request. Both subtract all purchase fees and exclude
owner contributions. Unwithdrawn account balances are not counted as cash.

## Search contract

The exhaustive coarse grid contains 3,120 joint combinations:

- Initial inventory: one, two, three, four or five funded accounts.
- Thirteen purchase configurations: monthly one/two, weekly one, quarterly
  one, monthly growth plus replacements, current-month-slot replacements,
  replacement targets of 1/5/10/20, and restarting reinvestment using
  25%/50%/100% of cumulative payout receipts.
- Minimum or maximum withdrawals, checked daily, weekly or monthly.
- Reserve headroom above the frozen $25,100 floor of $0, $2,000, $4,000,
  $4,900, $6,000, $6,800, $10,000 or $15,000.

Initial purchases replace the ordinary first-month purchase. Weekly
scheduling still acts on Mondays. Subsequent purchases require available
owner cash, including prior receipts, and obey the 20-live-account cap.
Replacement targets are desired live inventory, not a mandate to borrow
money. Reinvestment fractions limit spending from cumulative receipts;
restarting an empty book buys one account if affordable.

After the coarse grid, each purchase/withdrawal/cadence family's winner for
each objective receives a reserve refinement of +/-$500 in $100 steps,
within the original bounds. Its initial inventory remains fixed during
that refinement. The union of the resulting overall winners then receives
a focused check of fixed monthly accruals of $500/$1,000/$1,500 with backlog,
across all three request cadences and the coarse reserve grid. Daily fixed
requests do not create new daily entitlements: accrual remains monthly.

This design identifies an exhaustive coarse-grid optimum and a best policy
among all additional tested settings. It does not establish an optimum over
continuous reserves, arbitrary dynamic policies or every fixed-amount
combination. Refinement is local, and the fixed-amount extension is focused.

## Validation and interpretation

The full 2020–July 2026 dataset selects the policies. Selected settings then
transfer unchanged to fresh 2021–2025 starts and the other three historical
budgets. Those starts overlap the selection data: they are sensitivity
checks, not independent out-of-sample validation. Other budgets do not
receive a new optimization or a larger initial inventory.

The inherited 16 blocked-copying controls must reproduce both financial
results and account-by-account trade assignments. Search checkpoints have
an immutable contract covering source, settings and inputs. An independent
audit checks coarse-grid completeness, both objective winners, frozen
transfers, historical-file preservation and selected account/cash ledgers.

All 16 controls reproduced. The completed search consists of 3,120 coarse
combinations, 740 additional refinements and 72 fixed-amount checks. The
main audit verifies all 3,932 settings, both objective maxima, eight primary
transfers and 158,970 detailed winner trade copies. An additional tie check
covers 24 frozen transfers across all three co-winners. All 279 tests pass.

Account supply retains the previous $200 instant-funded-seat assumption.
Evaluation fees, waiting times and real replacement availability are not
optimized here. A strategy that replaces many accounts may be financially
attractive in this model while being difficult to supply operationally.
The 20-live-account cap is not a cap on lifetime purchases.

As in the preceding studies, failure uses exported per-trade extrema at
exit, and pending-order reservations are absent. Products, firm rules,
contract size, signal selection, calendar phase and evaluation pipelines
remain unchanged or outside this search.

## Reproduction

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/optimize_blocked_copying.py
.\venv\Scripts\python.exe scripts/audit_blocked_optimization.py
.\venv\Scripts\python.exe scripts/check_blocked_ties.py
```

The runner resumes completed jobs only when its source/settings/input
contract matches. Detailed evidence is written separately under
`results/legacy_25k/blocked_optimization`; earlier results remain preserved.
