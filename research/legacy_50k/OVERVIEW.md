# Legacy 50K: initial operating-policy findings

**Extension:** the [paired reserve findings](../../results/comparisons/legacy_25k_vs_50k/reserve_by_policy/FINDINGS.generated.md)
give both products equal reserve coverage within each budget and operating-policy
family. Read them for best-tested reserve comparisons; the initial matched controls
and monthly-purchase-led shortlist below retain their original scope.

The first focused comparison is complete. It uses the same RR tape, contract exposure, four owner budgets and 20-live-account cap as 25K, with the user-specified $250 fee for 50K versus $200 for 25K. The comparison is therefore of account product **and its acquisition cost**, not drawdown alone.

## Matched policy: monthly purchases, daily $500 requests

Both products retain $6,800 above their frozen floor: $31,900 for 25K and $56,900 for 50K. These are equal-dollar-headroom controls, not equal fractions of drawdown.

| Initial cash | Monthly funding | 25K total | 50K total | Difference |
|---|---:|---:|---:|---:|
| $1,000 | $0 | $302,287.21 | $411,697.22 | $109,410.01 |
| $1,000 | $200 | $464,311.75 | $500,863.44 | $36,551.69 |
| $5,000 | $0 | $464,511.75 | $452,027.93 | $-12,483.82 |
| $5,000 | $200 | $464,311.75 | $512,702.00 | $48,390.25 |

Larger drawdown does not guarantee more owner cash under a fixed operating policy. Changed survival, purchase timing and affordability can offset that benefit. Fifty-thousand is nominal account size, not twice the dollars earned per trade.

## Selected 50K operating bundles

The fresh reserve/cadence search used monthly-one, followed by a shortlist comparison under monthly-one, weekly-one and current-month replacement buying. Local search is not an exhaustive optimization of every acquisition policy.

| Initial / monthly funding | Purchase rule | Withdrawal | Reserve | Ongoing cash | Total cash | Same policy, stricter later-payout balance |
|---|---|---|---:|---:|---:|---:|
| $1,000 / $0 | monthly_current_slot_replacements | maximum / weekly | $56,600 | $399,197.64 | $491,378.26 | $442,948.90 |
| $1,000 / $200 | monthly_current_slot_replacements | maximum / weekly | $56,600 | $501,396.01 | $588,123.19 | $542,886.55 |
| $5,000 / $0 | monthly_current_slot_replacements | minimum / calendar_month | $52,900 | $409,250.00 | $596,879.32 | $551,879.41 |
| $5,000 / $200 | monthly_current_slot_replacements | maximum / daily | $56,900 | $512,603.03 | $612,413.39 | $567,413.58 |

All cash deducts purchase fees and excludes owner contributions. Total includes one terminal request. The final column applies the alternative retained-minimum interpretation from payout six, without re-optimizing the policy. It is a sensitivity result, not the optimum under that interpretation.

## What is established and what remains open

The selected purchase/withdrawal bundles differ across budgets. Current-month replacement leads total cash among the three acquisition choices and shortlisted withdrawals here; this is not evidence that it dominates other dates, tapes or unsearched policies. A new monthly reserve search can select much lower dollar headroom than the translated 25K anchors.

The later-payout interpretation materially changes terminal-inclusive totals. Existing 25K results are retained under their original interpretation, and paired strict controls for both products are available. We should resolve this interpretation before treating any terminal total as a real-world extraction claim. Original profit-split wording also remains ambiguous; these runs consistently use the inherited cumulative interpretation.

We did not repeat rule ablations. Similar rule-effect rankings are still a hypothesis: different survival and payout histories may change which rules bind. Contract scaling, full concurrent floating equity, evaluation costs, processing time, actual product availability and other compliance conditions remain outside the comparison.

Validation: 36 saved 25K controls reproduce exactly; 296 50K reserve/cadence settings, 60 purchase-shortlist settings, and 96 paired sensitivity runs. The preservation check confirms 177 existing result files unchanged. Full regression suite: 200 passing tests.

See the [study guide](STUDIES.md), [generated report](../../results/legacy_50k/operating_policies/REPORT.generated.md), and [source/interpretation record](SOURCES.md).
