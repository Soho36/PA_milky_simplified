# Legacy 25K versus 50K when funded accounts come from evaluations — blocked copying

6,240 simulations. With evaluations switched off, the engine still reproduces the 8 headline winners of the unlimited-supply study exactly, including per-trade account assignments.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. Evaluations already traded one position at a time, so the evaluation check below is unchanged from the [non-blocking study](../../../comparisons/legacy_25k_vs_50k/eval_supply/eval_supply__REPORT.md). The 123 settings shared with the 25K [blocked-pipeline study](../../../legacy_25k/blocked_pipeline/blocked_pipeline__REPORT.generated.md) reproduce it exactly, including per-trade account assignments. The unlimited-supply reference is the [blocked reserve comparison](../reserve_by_policy/reserve_by_policy__REPORT.md).

## How supply works here

Every funded account comes from an evaluation traded on the same RR signals, one position at a time, so the target-to-drawdown ratio plays out on the actual trades.

| Product | Evaluation size | Target / drawdown | Ratio | Monthly fee | Activation |
|---|---:|---:|---:|---:|---:|
| legacy_25k | 3 MNQ | $1,500 / $1,500 | 1.0 | $33 | $125 |
| legacy_50k | 5 MNQ | $3,000 / $2,500 | 1.2 | $40 | $125 |

- The drawdown trails peak equity, open profit included, and never freezes. An evaluation passes when a closed balance reaches the target.
- The fee is paid at the start and at each monthly renewal. A blown evaluation waits for renewal, which resets it.
- Up to 5 evaluations run at once, started only while the book is short: deaths not yet replaced, a missed scheduled purchase, or spares below target. An evaluation no longer needed is cancelled at renewal. Each one in flight holds one of the 20 seats.
- A pass is activated at the next daily check and joins the spare shelf; the purchase policy deploys it from there.
- Fees and pass timing come from the tape instead of the $200 / $250 average. Funded accounts keep every earlier convention, and copy a signal only while flat.

## Check against EODMAE

One evaluation started on every weekday with a full 180-day horizon, renewed until it passes.

| Evaluation | Starts | Passed in 180 days | EODMAE, worst point first | Passed in the first month | EODMAE, resolved paths | Median days | EODMAE, resolved paths | Cost per activation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k × 3 MNQ | 1,575 | 97.1% | 97.3% | 39.5% | 38.4% | 35.3 | 35.6 | $202 |
| legacy_50k × 5 MNQ | 1,575 | 93.3% | 93.7% | 31.6% | 30.7% | 39.7 | 40.4 | $239 |

This project assumes the worst point of every trade comes first, so the comparable EODMAE pass rate is its worst-point-first bound. EODMAE resolves most trades from their exit instead, and its 30-day cycles leave a trade spanning a renewal unbooked, so small differences are expected.

## $1,000 initial; $0/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $200,400 (68 bought) vs 50K $268,478 (56 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $25,100 | $422,850 | 118 / 20 | 125 / 219 | $186 | 11 | 12 of 31 |
| legacy_50k | Weekly, 5 spares; minimum / calendar_month; reserve $55,200 | $401,406 | 22 / 20 | 25 / 72 | $256 | 5 | 6 of 13 |

50K minus 25K: $-21,443.

## $1,000 initial; $200/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $665,421 (531 bought) vs 50K $585,935 (265 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $29,700 | $445,315 | 66 / 20 | 72 / 126 | $188 | 10 | 14 of 28 |
| legacy_50k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $50,100 | $483,065 | 52 / 20 | 56 / 153 | $243 | 10 | 21 of 31 |

50K minus 25K: $37,750.

## $5,000 initial; $0/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $670,286 (539 bought) vs 50K $550,450 (236 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / weekly; reserve $26,900 | $441,242 | 93 / 5 | 101 / 201 | $196 | 15 | 15 of 31 |
| legacy_50k | Weekly, 5 spares; minimum / calendar_month; reserve $50,100 | $450,387 | 54 / 20 | 61 / 190 | $266 | 7 | 19 of 35 |

50K minus 25K: $9,145.

## $5,000 initial; $200/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $670,286 (539 bought) vs 50K $603,596 (283 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $26,800 | $475,288 | 102 / 20 | 102 / 199 | $189 | 10 | 9 of 28 |
| legacy_50k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $50,100 | $490,210 | 55 / 20 | 55 / 122 | $214 | 10 | 9 of 16 |

50K minus 25K: $14,922.

## Best total by purchasing and spares

| Budget | Product | Monthly + replacements, 0 spares | Monthly + replacements, 5 spares | Monthly + replacements, 10 spares | Weekly, 0 spares | Weekly, 5 spares | Weekly, 10 spares | Monthly, 0 spares | Monthly, 5 spares | Monthly, 10 spares |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1,000 + $0/mo | legacy_25k | $172,267 (140) | $422,850 (118) | $368,777 (38) | $82,176 (30) | $-988 (5) | $-988 (5) | $-988 (5) | $215,597 (68) | $214,906 (67) |
| $1,000 + $0/mo | legacy_50k | $189,487 (48) | $304,230 (66) | $290,759 (65) | $132,040 (24) | $401,406 (22) | $397,433 (22) | $99,400 (18) | $234,020 (46) | $343,215 (33) |
| $1,000 + $200/mo | legacy_25k | $375,547 (61) | $445,315 (66) | $439,909 (61) | $80,879 (33) | $437,327 (75) | $412,930 (71) | $64,519 (25) | $315,088 (70) | $314,619 (69) |
| $1,000 + $200/mo | legacy_50k | $336,985 (33) | $483,065 (52) | $454,070 (56) | $197,735 (27) | $465,482 (45) | $461,337 (60) | $99,155 (19) | $372,759 (47) | $424,446 (47) |
| $5,000 + $0/mo | legacy_25k | $351,627 (61) | $441,242 (93) | $425,202 (127) | $93,291 (32) | $164,266 (142) | $-4,970 (24) | $64,519 (25) | $286,608 (77) | $286,073 (76) |
| $5,000 + $0/mo | legacy_50k | $327,614 (32) | $431,388 (52) | $419,615 (73) | $197,735 (27) | $450,387 (54) | $424,146 (56) | $99,155 (19) | $340,842 (51) | $425,511 (42) |
| $5,000 + $200/mo | legacy_25k | $375,547 (61) | $475,288 (102) | $468,445 (98) | $80,879 (33) | $407,532 (94) | $428,874 (83) | $64,519 (25) | $315,088 (70) | $314,685 (69) |
| $5,000 + $200/mo | legacy_50k | $336,985 (33) | $490,210 (55) | $485,825 (60) | $197,735 (27) | $466,438 (58) | $470,276 (60) | $99,155 (19) | $372,759 (47) | $441,830 (45) |

Cells show best total (accounts funded).

## Matched settings: share where 50K beats 25K

Same budget, purchasing, spares, withdrawal and headroom; settings where both lose are excluded.

| Purchasing | 50K ahead |
|---|---:|
| Monthly + replacements, 0 spares | 35% of 314 |
| Monthly + replacements, 5 spares | 49% of 324 |
| Monthly + replacements, 10 spares | 37% of 316 |
| Weekly, 0 spares | 98% of 293 |
| Weekly, 5 spares | 100% of 307 |
| Weekly, 10 spares | 100% of 301 |
| Monthly, 0 spares | 100% of 296 |
| Monthly, 5 spares | 95% of 303 |
| Monthly, 10 spares | 97% of 305 |

## Limits

In-sample best tested settings on one historical tape, not forecasts. Evaluations assume the worst point of each trade comes first, like the funded accounts; EODMAE shows the favourable-first bound 2–3 points lower. Evaluations and funded accounts both trade one position at a time. All other limits of the earlier studies apply.
