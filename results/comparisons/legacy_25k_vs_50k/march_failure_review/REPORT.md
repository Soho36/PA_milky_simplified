# March 2026 failures: minimum versus maximum withdrawals

The records support the account-balance synchronization hypothesis. They do not support the premise that the March 30 maximum-withdrawal book recovered all 20 PAs within one month. The closest matching recovery is a different policy: the 25K daily-minimum ongoing-cash winner activated 19 replacements in April after earlier March failures.

This review replays 14 settings and eight supply interruptions. It changes no engine code or previous result files. Every replay reconciles cash and obeys the shared-seat cap. The two inherited minimum-policy winners reproduce their saved headline results. Sources are the repository's frozen tape, policy implementation and recorded histories; no new firm-rule assumptions are introduced.

## Correcting the linked explanation

The final trade was not a $6,780 loss. At a $6,700 reserve, all 20 maximum-policy PAs had their last payout on November 11, 2025, leaving $6,800 profit equity per PA ($6,700 above the frozen +$100 floor). Subsequent settled losses, including commissions, reduced that to $101.40 before the March 30 trade. The final trade's adverse excursion was $81.50, taking the modeled intratrade equity to $19.90.

Thus the $6,780.10 boundary reflects depletion over a sequence since the last withdrawal, followed by the last adverse excursion. It is not the size of one trade. At a $6,780.10 reserve, adverse profit equity is exactly $100 and fails because touching the floor fails. At $6,780.11, it is $100.01 and survives. The recorded failure time is the trade's exit time, 2026-03-30 06:00; exports do not supply an exact intratrade breach time.

## Where minimum daily ranked

In the previous shared-seat pipeline search, with $5,000 initial funding and $200 monthly contributions, daily minimum ranked first for ongoing net cash in both products:

| Product | Reserve | Ongoing net cash | Total including closing | PAs alive at horizon | Pipeline |
|---|---:|---:|---:|---:|---|
| 25K | $3,900 | $597,317 | $597,317 | 19 | Batch starts, concurrency 10, spare target 10 |
| 50K | $3,700 | $582,835 | $582,835 | 12 | One start per day, concurrency 20, spare target 2 |

The broad search allowed different pipelines for different policies; these winners therefore are not a controlled comparison of withdrawal mechanisms alone. Monthly minimum won total cash, including closing withdrawals. Daily minimum's best total was essentially tied with daily maximum's best total, with differences of cents, below monthly minimum. Full rankings by policy family are in `historical_policy_ranking.csv`.

The previous reserve-frontier experiment held daily maximum fixed, so it did not show that maximum was the best withdrawal mechanism. Its best ongoing reserve of $5,700 was conditional on that fixed mechanism and pipeline.

Under the newer first-daily-check activation-or-forfeiture assumption, replaying these same minimum winners gives $597,317 for 25K and $580,680 for 50K. The latter changes because unaffordable passed evaluations can no longer wait for cash. This review does not reoptimize the minimum-policy winner under the new assumption.

## Controlled comparison at a $6,700 reserve

For each product the following pair uses exactly the same funding, persistent demand, shared seats, evaluation size and first-check activation rule. Both use concurrency 20 and spare target 2. Starts are seven days apart for 25K and one day apart for 50K. Only the daily withdrawal amount rule changes.

| Product | Daily rule | Distinct profit balances before final trade | Profit equity range before final trade | Deaths on that trade | Ongoing net cash | Total net cash |
|---|---|---:|---:|---:|---:|---:|
| 25K | Maximum | 1 | $101.40–$101.40 | 20 | $520,426.12 | $520,426.12 |
| 25K | Minimum | 12 | $154.15–$637.90 | 1 | $533,857.00 | $624,208.89 |
| 50K | Maximum | 1 | $101.40–$101.40 | 20 | $529,946.40 | $529,946.40 |
| 50K | Minimum | 8 | $189.20–$556.50 | 0 | $548,470.00 | $641,764.81 |

Minimum requests the firm's $500 minimum when eligible. It does not pay $500 automatically every calendar day. Fixed withdrawal increments and different account histories preserve balance differences instead of repeatedly removing all available surplus down to a common target. At $6,800 both mechanisms avoid this final failure; minimum still has 12 distinct balances in 25K and eight in 50K.

However, minimum also retains more profit before this trade. The paired experiment demonstrates the combined effect of balance dispersion and additional retained equity; it does not isolate dispersion while holding actual retained capital constant. All PAs still share the same underlying trades. Different balances do not provide independent trading returns.

Desynchronization is also not immunity. The low-reserve minimum winners lose their established book earlier in March. The inherited 25K $3,900 winner has March death clusters of 6, 9, 6, 2, 2 and 1 PAs on March 6–16, including failed replacements, and has no live PAs by March 16 after the last cluster. The inherited 50K $3,700 winner loses 16 together on March 6 and is also empty by March 18. More conservative reserves remain relevant under minimum withdrawals.

## What actually recovered

For the $6,700 daily-maximum runs from the reserve-frontier study:

| Product | March 30 deaths matched to a replacement within 30 days | Live PAs at April 30 midnight | Live PAs at July horizon | Returned to 20 live by horizon? |
|---|---:|---:|---:|---|
| 25K | 2 of 20 | 1 | 4 | No |
| 50K | 6 of 20 | 6 | 7 | No |

Replacement matching is FIFO and cumulative; a replacement can itself die. Consequently cumulative replacements and current live capacity are different metrics. In 50K, all original March 30 deaths are eventually matched to deployments, but many replacements fail and the live book never returns to 20. In 25K, nine original March 30 replacement demands remain unfilled at the horizon, alongside newer outstanding replacement demands.

Both $6,700 maximum runs receive **zero operating withdrawals after March 30** through July 13. Their large lifetime cash totals were banked before the crash. The $6,800 maximum runs do not need to rebuild after this event because all 20 survive it.

The likely source of the one-month recovery memory is the 25K daily-minimum winner: nine evaluations pass on April 13, one on April 14, and nine on April 16, activating on the next daily checks. This brings the trading book to 19, not 20. It is a real example of clustered replacement success, but a different policy and earlier March failure episode. The 50K minimum winner has 10 live PAs at April 30, not 20.

## What if evaluation supply became unavailable?

A small counterfactual stops **new evaluation trade entries** starting March 30 at 06:00, either for 30 days or through the remaining horizon (implemented as 365 days). Pre-existing positions settle normally. PA trades, evaluation subscriptions, renewals, demand and activation rules continue. This is a supply interruption experiment, not a probability model of worse market luck. It may avoid losing evaluation trades as well as winning ones.

For the same low-reserve minimum winners, using first-check activation:

| Product | Baseline ongoing/total net | 30-day pause net | Pause through horizon net | PAs alive after horizon-long pause |
|---|---:|---:|---:|---:|
| 25K | $597,317 | $583,848 | $585,098 | 0 |
| 50K | $580,680 | $576,230 | $576,970 | 0 |

There are no terminal withdrawals in these rows. Full-history cash falls by $12,219 and $3,710 with the horizon-long pause, respectively, even though future trading capacity is eliminated. A shorter pause can cost more net cash because it still spends money activating PAs; more activity is not automatically more net profit on a short, unfavorable tail.

For maximum at $6,700, the horizon-long pause actually raises net cash by $913 for 25K and $1,900 for 50K: the baseline replacements generated no withdrawals before the horizon, so avoiding some activation spending improves this short-horizon cash score while leaving zero earning capacity. This is not an argument to abandon replacements in a continuing profitable strategy.

The $6,800 maximum controls are unchanged under the pause, because their full PA books survive and need no replacement evaluations during that period. Pre-shock net cash is identical in every counterfactual. All eight scenarios reconcile; full details are in `recovery_stress.csv` and `STRESS_AUDIT.json`.

## Interpretation and next useful comparison

There are two separate risks: common PA losses and common evaluation outcomes. Minimum withdrawals can reduce simultaneous PA liquidation at the same reserve, but low reserves still permit a complete book loss across several days. Batched evaluations can qualify together, and can also fail together. Successful qualification alone does not ensure replacement PAs survive or pay out.

The late position of this crash makes lifetime cash an incomplete robustness measure. Slower recovery cannot remove cash already paid out, and only a few months remain for missing capacity to affect the totals. Repeated interruptions earlier in the history could have a much larger effect; this diagnostic has not measured that distribution.

The next comparison should include both minimum and maximum withdrawals, frozen common pipeline settings, matched reserve grids, and a second comparison at similar average actual retained capital. Apply common blocks of market outcomes to both evaluations and PAs, preserving cross-account dependence. Report cash, living capacity, time empty, replacement shortfalls and performance for a substantial period after each shock. Compare all policies on the same stress paths and do not reoptimize separately for each path. A single favorable April, or a single favorable historical reserve, should not determine the operating choice.

Evidence files: `baselines.csv`, `historical_policy_ranking.csv`, `recovery_stress.csv`, and the per-setting folders containing account snapshots, replacement matches, evaluation pass dates, daily capacity, and victims' last payouts.
