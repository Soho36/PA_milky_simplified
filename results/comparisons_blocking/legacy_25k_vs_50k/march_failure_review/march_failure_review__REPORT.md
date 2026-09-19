# March 2026 failures: minimum versus maximum withdrawals — blocked copying

With blocked copying, the March 30, 2026 trade kills no PA in any of the 14 replays. The synchronized failure the [non-blocking review](../../../comparisons/legacy_25k_vs_50k/march_failure_review/march_failure_review__REPORT.md) found there came from overlapping positions draining identical books before that trade. Synchronized failure itself remains: the $5,700 daily-maximum books lose all 20 PAs together on March 26, and the daily-minimum winners lose their books on March 5–6.

This review replays the same 14 settings and eight supply interruptions as the non-blocking review, with each funded account holding at most one position. The frozen cases are unchanged: daily maximum at $5,700, $6,700 and $6,800, and daily minimum at $6,700 and $6,800, on the reserve-frontier pipelines. The two minimum-policy winners are the best daily-minimum ongoing-cash settings of the [blocked pipeline study](../pipeline_capacity/pipeline_capacity__REPORT.md), and both reproduce its saved rows, including per-trade account assignments. Every replay reconciles cash and obeys the shared-seat cap. An independent check found that none of the 1,240 PA histories across the 14 replays held two trades at once. No earlier result file changed.

## The March 30 trade under blocking

The pairs below use the same funding, persistent demand, shared seats, evaluation size, first-check activation and pipeline (20 subscriptions, two spares; starts seven days apart for 25K and one day apart for 50K). Only the daily withdrawal rule changes.

| Product | Reserve | Daily rule | Distinct profit balances before the trade | Profit equity range before the trade | Deaths on that trade | Ongoing net cash | Total net cash |
|---|---:|---|---:|---:|---:|---:|---:|
| 25K | $6,700 | Maximum | 2 | $695.55–$809.50 | 0 | $185,072.95 | $321,673.10 |
| 25K | $6,700 | Minimum | 16 | $515.85–$906.20 | 0 | $182,864.00 | $182,864.00 |
| 25K | $6,800 | Maximum | 1 | $909.50–$909.50 | 0 | $173,731.15 | $312,331.30 |
| 25K | $6,800 | Minimum | 16 | $629.05–$1,102.30 | 0 | $174,331.00 | $174,331.00 |
| 50K | $6,700 | Maximum | 1 | $809.50–$809.50 | 0 | $175,530.60 | $312,416.39 |
| 50K | $6,700 | Minimum | 9 | $515.85–$980.95 | 0 | $180,395.00 | $180,395.00 |
| 50K | $6,800 | Maximum | 1 | $909.50–$909.50 | 0 | $176,765.60 | $315,651.39 |
| 50K | $6,800 | Minimum | 10 | $629.05–$1,061.70 | 0 | $173,695.00 | $173,695.00 |

Without blocking, every $6,700 maximum PA entered this trade with $101.40 of profit equity, and all 20 failed on its $81.50 adverse excursion. With blocking, the same books enter with at least $695.55. Accounts that skip signals while in a position do not stack the losses of overlapping trades. Daily maximum still leaves one or two balances; daily minimum still spreads them (9 to 16 distinct balances). At these reserves, neither mechanism needs that dispersion to survive March 30.

All four minimum runs receive no closing withdrawal: their total equals ongoing cash. Their balances at the end of June are similar to the maximum runs' ($6,052–$6,442 of profit per 25K PA at $6,700, against $5,893). A replay of the 25K $6,700 minimum run shows why. Each PA had just been paid under the daily minimum, and all 20 closing requests are denied by the firm's minimum-trading-days rule. The maximum PAs had not been paid recently, so their closing requests pass. In that replay, the total-cash gap comes from this timing rule, not from a weaker book.

## Where the synchronized failure went

| Product | Setting | March deaths | Live PAs at the horizon | Ongoing net cash | Total net cash |
|---|---|---|---:|---:|---:|
| 25K | Daily maximum, $5,700 | 20 together on March 26 | 3 | $215,439.75 | $219,939.75 |
| 50K | Daily maximum, $5,700 | 20 together on March 26 | 12 | $204,851.00 | $224,851.00 |
| 25K | Daily minimum winner, $3,000 | 6, 8, 1 and 5 on March 5–6 | 10 | $406,936.00 | $406,936.00 |
| 50K | Daily minimum winner, $3,000 | 2, 5, 8 and 5 on March 5–6; 3 on March 20 | 16 | $443,290.00 | $443,290.00 |

At $5,700 the daily-maximum books are still synchronized, and they fail four days before the non-blocking cliff. The minimum winners run with a much smaller reserve and lose their whole books early in March. Blocking changes where the book fails; it does not make common losses independent. All PAs still share the same underlying trades.

## Where minimum daily ranked

In the blocked pipeline search ($5,000 initial, $200 monthly, shared seats), daily minimum ranks **second** for ongoing cash in both products, behind weekly minimum. It ranks sixth of six for total cash; monthly minimum leads that.

| Product | Daily-minimum winner | Pipeline | Ongoing net cash | Best family for ongoing cash | Best family for total cash |
|---|---|---|---:|---|---|
| 25K | $3,000 reserve | Batch starts, 10 subscriptions, 2 spares, day-only demand | $406,936 | Weekly minimum, $2,400: $453,544 | Monthly minimum, $1,700: $507,353 |
| 50K | $3,000 reserve | One start per day, 20 subscriptions, 5 spares, day-only demand | $443,290 | Weekly minimum, $0: $469,400 | Monthly minimum, $0: $518,683 |

These winners come from a broad search that allowed different pipelines for different policies, so they are not a controlled comparison of withdrawal mechanisms. Replaying them under first-check activation gives the same cash as the older wait-for-cash rule: $406,936 and $443,290. Full rankings by policy family are in `historical_policy_ranking.csv`.

## What recovered

The $6,700 and $6,800 daily-maximum books lose nothing on March 30, so there is nothing to rebuild. The $6,700 books keep earning after the event: $18,933 (25K) and $19,047 (50K) of operating withdrawals from March 30 to the July horizon. Without blocking, the same settings received nothing after the crash.

The daily-minimum winners must rebuild after emptying their books in early March. The 25K winner has no live PAs on March 31 or April 30. It is back to 20 on May 9, then falls to 10 by the end of June and ends with 10. It receives no operating withdrawals after March 30 and spends $6,980 on evaluations and activations. The 50K winner has 9 live PAs on April 30, 15 on May 31 and 16 at the horizon. It receives $18,500 after March 30 and spends $3,775.

## What if evaluation supply became unavailable?

The counterfactual stops new evaluation trade entries from March 30 at 06:00, for 30 days or through the remaining horizon (implemented as 365 days). Pre-existing positions settle normally; PA trades, subscriptions, renewals, demand and activation rules continue. This is a supply-interruption experiment, not a model of worse market luck.

For the daily-minimum winners, with first-check activation:

| Product | Baseline net | 30-day pause net | Pause through horizon net | PAs alive after horizon-long pause |
|---|---:|---:|---:|---:|
| 25K | $406,936 | $421,346 (+$14,410) | $412,596 (+$5,660) | 0 |
| 50K | $443,290 | $445,265 (+$1,975) | $425,965 (−$17,325) | 0 |

There are no terminal withdrawals in these rows. Only the horizon-long pause for 50K costs cash; for 25K, both pauses raise the full-history total. The 25K replacements bought after the early-March losses cost more than they earned before the tape ends. The 50K replacements earn their cost back over the full horizon, but not within the first 30 days. Avoiding replacements can therefore help a short-horizon cash score while leaving no earning capacity. This is not an argument to abandon replacements in a continuing profitable strategy.

All four daily-maximum books at $6,700 and $6,800 are unchanged under the pause, because they run no evaluations after the event. Without blocking, only the two $6,800 books qualified. Pre-shock net cash is identical in every counterfactual. Details are in `recovery_stress.csv` and `STRESS_AUDIT.json`.

## Interpretation

Two risks remain separate: common PA losses and common evaluation outcomes. Blocking removes the stacked losses that made March 30 a cliff, and a $6,100 reserve already clears that trade (see the [blocked reserve frontier](../reserve_frontier/reserve_frontier__REPORT.md)). But it does not stop synchronized failure at lower reserves, and daily-maximum cash is roughly half the non-blocking level at the same reserves. Minimum withdrawals still spread balances, but at $6,700–$6,800 they are not needed for March 30; there, the closing-withdrawal timing matters more for total cash.

As in the non-blocking review, the late position of this crash makes lifetime cash an incomplete robustness measure. Repeated interruptions earlier in the history, and common blocks of outcomes applied to both evaluations and PAs, remain the next useful stress.

Evidence files: `baselines.csv`, `historical_policy_ranking.csv`, `recovery_stress.csv`, and the per-setting folders with account snapshots, replacement matches, evaluation pass dates, daily capacity and the March victims' last payouts. `AUDIT.json` records the one-position checks.
