# Legacy 25K versus 50K when funded accounts come from evaluations

6,328 simulations. With evaluations switched off, the engine still reproduces the 8 headline winners of the unlimited-supply study exactly.

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
- Fees and pass timing come from the tape instead of the $200 / $250 average. Funded accounts keep every earlier convention, including taking every overlapping signal.

## Check against EODMAE

One evaluation started on every weekday with a full 180-day horizon, renewed until it passes.

| Evaluation | Starts | Passed in 180 days | EODMAE, worst point first | Passed in the first month | EODMAE, resolved paths | Median days | EODMAE, resolved paths | Cost per activation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| legacy_25k × 3 MNQ | 1,575 | 97.1% | 97.3% | 39.5% | 38.4% | 35.3 | 35.6 | $202 |
| legacy_50k × 5 MNQ | 1,575 | 93.3% | 93.7% | 31.6% | 30.7% | 39.7 | 40.4 | $239 |

This project assumes the worst point of every trade comes first, so the comparable EODMAE pass rate is its worst-point-first bound. EODMAE resolves most trades from their exit instead, and its 30-day cycles leave a trade spanning a renewal unbooked, so small differences are expected.

## $1,000 initial; $0/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $308,605 (61 bought) vs 50K $530,386 (38 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $25,100 | $548,140 | 94 / 20 | 97 / 174 | $186 | 10 | 12 of 27 |
| legacy_50k | Monthly + replacements, 10 spares; minimum / calendar_month; reserve $53,400 | $517,937 | 36 / 20 | 40 / 79 | $213 | 8 | 25 of 29 |

50K minus 25K: $-30,203.

## $1,000 initial; $200/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $749,859 (611 bought) vs 50K $714,515 (368 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,100 | $590,701 | 65 / 20 | 65 / 144 | $198 | 8 | 9 of 23 |
| legacy_50k | Weekly, 5 spares; minimum / calendar_month; reserve $54,300 | $601,275 | 43 / 20 | 53 / 97 | $215 | 6 | 16 of 27 |

50K minus 25K: $10,574.

## $5,000 initial; $0/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $810,670 (674 bought) vs 50K $723,142 (371 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,100 | $586,881 | 67 / 20 | 67 / 143 | $195 | 8 | 10 of 24 |
| legacy_50k | Weekly, 5 spares; minimum / calendar_month; reserve $52,800 | $583,155 | 58 / 20 | 58 / 162 | $237 | 6 | 23 of 37 |

50K minus 25K: $-3,726.

## $5,000 initial; $200/month

Unlimited supply at $200 / $250 a seat (earlier study): 25K $810,670 (674 bought) vs 50K $734,754 (370 bought).

| Product | Best tested bundle | Total | Funded / alive | Evaluations / months paid | Cost per funded account | Most passes in a month | Short months without a pass |
|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | Monthly + replacements, 5 spares; maximum / daily; reserve $32,700 | $608,452 | 57 / 20 | 57 / 130 | $200 | 8 | 8 of 19 |
| legacy_50k | Monthly + replacements, 5 spares; maximum / daily; reserve $58,100 | $605,514 | 44 / 20 | 44 / 110 | $225 | 5 | 9 of 15 |

50K minus 25K: $-2,938.

## Best total by purchasing and spares

| Budget | Product | Monthly + replacements, 0 spares | Monthly + replacements, 5 spares | Monthly + replacements, 10 spares | Weekly, 0 spares | Weekly, 5 spares | Weekly, 10 spares | Monthly, 0 spares | Monthly, 5 spares | Monthly, 10 spares |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $1,000 + $0/mo | legacy_25k | $-968 (9) | $548,140 (94) | $535,483 (53) | $30,077 (33) | $-988 (5) | $-988 (5) | $-988 (5) | $302,559 (57) | $302,948 (56) |
| $1,000 + $0/mo | legacy_50k | $272,766 (29) | $488,717 (35) | $517,937 (36) | $-980 (4) | $486,999 (55) | $491,560 (60) | $150,348 (19) | $309,668 (40) | $419,582 (34) |
| $1,000 + $200/mo | legacy_25k | $443,013 (52) | $590,701 (65) | $583,861 (64) | $170,888 (33) | $539,443 (64) | $534,052 (66) | $136,876 (25) | $465,531 (58) | $464,666 (57) |
| $1,000 + $200/mo | legacy_50k | $376,922 (30) | $569,698 (51) | $569,167 (48) | $180,288 (27) | $601,275 (43) | $585,430 (46) | $156,841 (19) | $460,075 (44) | $487,799 (48) |
| $5,000 + $0/mo | legacy_25k | $443,013 (52) | $586,881 (67) | $583,528 (67) | $170,888 (33) | $-4,968 (25) | $-4,975 (20) | $136,876 (25) | $465,531 (58) | $465,239 (54) |
| $5,000 + $0/mo | legacy_50k | $376,922 (30) | $568,108 (49) | $505,788 (51) | $180,288 (27) | $583,155 (58) | $562,729 (61) | $156,841 (19) | $474,757 (41) | $477,221 (44) |
| $5,000 + $200/mo | legacy_25k | $443,013 (52) | $608,452 (57) | $591,568 (61) | $170,888 (33) | $525,497 (87) | $527,070 (80) | $136,876 (25) | $465,531 (58) | $464,831 (57) |
| $5,000 + $200/mo | legacy_50k | $376,922 (30) | $605,514 (44) | $580,575 (53) | $180,288 (27) | $589,404 (56) | $587,727 (57) | $156,841 (19) | $460,075 (44) | $505,210 (48) |

Cells show best total (accounts funded).

## Matched settings: share where 50K beats 25K

Same budget, purchasing, spares, withdrawal and headroom; settings where both lose are excluded.

| Purchasing | 50K ahead |
|---|---:|
| Monthly + replacements, 0 spares | 33% of 324 |
| Monthly + replacements, 5 spares | 27% of 332 |
| Monthly + replacements, 10 spares | 12% of 348 |
| Weekly, 0 spares | 84% of 262 |
| Weekly, 5 spares | 93% of 321 |
| Weekly, 10 spares | 93% of 321 |
| Monthly, 0 spares | 93% of 332 |
| Monthly, 5 spares | 46% of 376 |
| Monthly, 10 spares | 81% of 366 |

## Limits

In-sample best tested settings on one historical tape, not forecasts. Evaluations assume the worst point of each trade comes first, like the funded accounts; EODMAE shows the favourable-first bound 2–3 points lower. Evaluations trade one position at a time while funded accounts take every overlapping signal, as the owner trades them. All other limits of the earlier studies apply.
