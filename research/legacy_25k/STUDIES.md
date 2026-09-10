# Legacy 25K study guide

Read [current findings](OVERVIEW.md) first. Detailed evidence remains at stable
paths; there is no need to browse the full results tree to follow the research.

| Question | Evidence | Scope |
|---|---|---|
| Which reserve works best for each policy and account size? | [Paired 25K/50K reserve search](../../results/comparisons/legacy_25k_vs_50k/reserve_by_policy/REPORT.generated.md) | Same grids per pair; funded cap 20; minimum/maximum withdrawal families; both cash objectives |
| Which purchase policy works with our cash budget? | [Current purchase report](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.generated.md) | 132 candidates; cap 20; four budgets |
| Which withdrawal cadence works with monthly purchases? | [Current capped cadence report](../../results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets/REPORT.generated.md) | 372 candidates; matched budgets and controls |
| How did cadence affect the original book? | [Historical cadence report and notes](../../results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/REPORT.md) | Uncapped monthly purchases |
| How do withdrawal amounts and reserves interact? | [Amount/cushion report](../../results/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/REPORT.md) | Uncapped monthly purchases |
| Which firm restrictions matter under a fixed/adapted policy? | [Rule-effect report](../../results/full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search/report.txt) | Historical cushion-only adaptation |
| What does a cash difference actually represent? | [Economic definitions](../../ECONOMIC_EFFECTS.md) | Accounting identities and timing limits |
| How were the original conclusions developed? | [Historical introduction](HISTORICAL_FINDINGS.md) | Preserved earlier narrative |

Reader explanations are preserved separately:
[purchase breakdown](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/report_breakdown.txt)
and [cadence breakdown](../../results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/report_breakdown.txt).
They describe their original runs; use the generated purchase report for the
monthly-two and weekly-one additions. The [complete results index](../../results/README.md)
also contains single-scenario and coarse/fine sweep history.

## Plain-language operating notes

These describe what happens month by month and how to read the results, without listing every tested setting.

- [Withdrawal amount and reserve](../../results/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/HOW_THIS_STUDY_WORKS.md)
- [Historical withdrawal cadence](../../results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/HOW_THIS_STUDY_WORKS.md)
- [Capped, budget-matched cadence](../../results/study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets/HOW_THIS_STUDY_WORKS.md)
- [Account purchases](../../results/study__full_rulebook__RR__account_purchases__cash_budgets/HOW_THIS_STUDY_WORKS.md)

The current purchase report separates one-account scheduled purchases
(quarterly-one, monthly-one, weekly-one), monthly-two expansion, replacement/
reinvestment, and historical quarterly-three batches. All 132 simulation rows
are retained; quarterly-three is excluded from main rankings.

## Monthly purchases with earlier replacements

[Replacement comparison](../../results/study__full_rulebook__RR__monthly_replacements__cap_20__cash_budgets/REPORT.generated.md): 48 candidates, comparing monthly-one and
weekly-one with replacements consuming an unused current-month slot or added to normal
monthly growth. All 24 existing-policy controls reproduce exactly.

The current-month replacement rule never cancels future purchases. The former
future-slot experiment is retained in `archives/studies/monthly_replacements_future_slots`.
