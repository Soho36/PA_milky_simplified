# Blocked copying: operating-policy optimization

**Primary funding: $1,000 initially plus $200/month.** One MNQ per accepted setup per account; accounts accept entries only while flat. Cash-funded purchases, 20 live seats, inherited $200 instant funded-seat fee. Account evaluation costs/delays are not modeled in this search. Both cash objectives exclude owner contributions and subtract every purchase fee. Total adds one firm-permitted terminal request.

Completed 3,120 exhaustive coarse-grid combinations, 740 additional local refinement settings, and a focused fixed-amount/backlog extension. Starting inventory, purchase family, withdrawal amount family, cadence and reserve are searched jointly on the coarse grid. Refinement keeps each selected seed fixed. The result is a best tested policy and an exhaustive-grid optimum within the declared coarse domain, **not a proven global optimum over arbitrary policies or continuous reserves**.

Coarse headroom above the $25,100 frozen floor: [0, 2000, 4000, 4900, 6000, 6800, 10000, 15000]. Five initial inventories (1–5), 13 purchase configurations, minimum/maximum withdrawals and three cadences. Initial inventory replaces the first monthly purchase; weekly purchases can still occur on a Monday. Replace-N maintains a target of N at daily checks; reinvest budgets its stated fraction of cumulative receipts and restarts with one account when empty and affordable. Scheduled purchases without replacement clauses do not automatically replace deaths. The two monthly replacement variants either add replacements to growth or let a replacement consume an unused current-month slot.

## Winners on the full dataset

| Start | Budget | Seed | Purchases | Withdraw / cadence | Reserve | Bought / deaths | Coverage | Ongoing net | Total net |
|---:|---|---:|---|---|---:|---:|---:|---:|---:|
| 2020 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 531 / 511 | 73.18% | $665,420.55 | $665,420.55 |
| 2020 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 531 / 511 | 73.18% | $665,420.55 | $665,420.55 |

## Inherited blocked-copy controls at the primary budget

| Start | Budget | Seed | Purchases | Withdraw / cadence | Reserve | Bought / deaths | Coverage | Ongoing net | Total net |
|---:|---|---:|---|---|---:|---:|---:|---:|---:|
| 2020 | 1000 + 200/mo | 5 | monthly_plus_replacements | minimum  / daily | $30,000 | 87 / 67 | 73.09% | $334,100.00 | $334,100.00 |
| 2020 | 1000 + 200/mo | 5 | monthly_plus_replacements | minimum  / daily | $31,900 | 67 / 47 | 73.10% | $268,600.00 | $268,600.00 |

## Frozen-policy historical transfers

Winners are selected only from the primary full-tape search and applied unchanged below. Later starts overlap the selection dataset; these are historical sensitivity checks, not unseen out-of-sample evidence. Other budgets receive the same initial seat count and policy, not a new search.

| Start | Budget | Seed | Purchases | Withdraw / cadence | Reserve | Bought / deaths | Coverage | Ongoing net | Total net |
|---:|---|---:|---|---|---:|---:|---:|---:|---:|
| 2020 | 1000 + 0/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 5 / 5 | 2.29% | $-1,000.00 | $-1,000.00 |
| 2020 | 5000 + 0/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 539 / 519 | 73.18% | $670,285.60 | $670,285.60 |
| 2020 | 5000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 539 / 519 | 73.18% | $670,285.60 | $670,285.60 |
| 2021 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 435 / 415 | 73.21% | $620,933.40 | $620,933.40 |
| 2022 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 356 / 336 | 73.26% | $566,273.55 | $566,273.55 |
| 2023 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 278 / 258 | 72.94% | $478,798.55 | $478,798.55 |
| 2024 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 218 / 198 | 72.16% | $310,833.39 | $310,833.39 |
| 2025 | 1000 + 200/mo | 1 | monthly_current_slot_replacements | fixed 1500 / weekly | $25,100 | 126 / 108 | 72.51% | $97,846.26 | $97,846.26 |

## Search and evidence limits

No search over contract size, signal filters, calendar phase, product, dynamic reserve functions, firm rules or evaluation supply. Fixed requests accrue monthly even when checks are daily/weekly; the focused fixed-amount extension is not a complete joint search of those families. Failed-account extrema are booked at exported exits; pending-order reservation times are absent. Cash and capacity reconcile in every run. Selected details include accounts, entries, receipts and funding ledgers. Every inherited blocked-copy control reproduces before search. Ties and tested reserve bounds are in best_by_family.csv. A boundary or near-best setting is not a confidence interval.
