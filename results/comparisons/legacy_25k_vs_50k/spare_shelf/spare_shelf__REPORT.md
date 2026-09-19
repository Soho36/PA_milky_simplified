# Legacy 25K versus 50K under a limited supply of funded accounts

13,888 simulations. 1194 rows that must equal the unlimited-supply study reproduced it exactly. Both products are tested on exactly the same settings.

## The question

The unlimited-supply study let every purchase become a funded account at once. Its best 25K bundles bought 600+ accounts by replacing deaths immediately. Here funded accounts come from passed evaluations: at most **N passes per calendar month**, each paid in full ($200 / $250) when it passes. A pass not needed at once waits dormant on a shelf of up to K spares, and **spares count toward the 20-account cap**. Spares left at the end are sunk. See [ASSUMPTIONS.md](../../../../ASSUMPTIONS.md#supply-of-funded-accounts).

Replacement purchasing is tested with [0, 5, 10] spares and [1, 2, 3, 5, 10] passes a month. Weekly and monthly purchasing run without spares as comparators; more than five passes a month never binds them. Reserves are re-searched for every setting: coarse headrooms [0, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6500, 8000, 10000] above the frozen floor, then +/-$400 in $100 steps around each product's best bundle, applied to both products. This is coarser than the unlimited study, which slightly favours its numbers.

**The pass rate is fixed.** Real passes are lumpy and probably scarcest when the book is dying, so a fixed rate flatters replacement policies. Read each row as "an owner who can reliably pass N accounts a month".

## Files

- [All settings](all_settings.csv), [best by shelf](best_by_shelf.csv), [matched 50K-minus-25K differences](matched_deltas.csv), [contract and rows](study.json).
- Detailed ledgers for each product's best bundle at 3 passes a month.

## $1,000 initial; $0/month

Unlimited supply (earlier study): 25K $308,605 (61 bought) vs 50K $530,386 (38 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Weekly; minimum / calendar_month; reserve $27,700 | $326,333 | 64 / 17 | Monthly + replacements, 5 spares; maximum / weekly; reserve $58,100 | $431,643 | 35 / 20 | $105,310 |
| 2 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $28,300 | $464,523 | 58 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $52,700 | $509,467 | 43 / 20 | $44,943 |
| 3 | Monthly; minimum / daily; reserve $33,300 | $302,687 | 56 / 17 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,200 | $523,575 | 39 / 20 | $220,887 |
| 5 | Monthly; minimum / daily; reserve $33,300 | $302,687 | 56 / 17 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,200 | $530,386 | 38 / 20 | $227,698 |
| 10 | Monthly; minimum / daily; reserve $33,300 | $302,687 | 56 / 17 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $53,200 | $530,386 | 38 / 20 | $227,698 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $302,287 (58) | $302,287 (58) | $302,287 (58) | $418,322 (35) | $431,643 (35) | $431,643 (35) |
| 2 | $464,523 (58) | $-1,000 (5) | $-1,000 (5) | $491,182 (43) | $509,467 (43) | $509,467 (43) |
| 3 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $512,400 (42) | $523,575 (39) | $523,575 (39) |
| 5 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $524,599 (41) | $530,386 (38) | $530,386 (38) |
| 10 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $530,386 (38) | $530,386 (38) | $530,386 (38) |

Cells show best total (accounts bought).

## $1,000 initial; $200/month

Unlimited supply (earlier study): 25K $749,859 (611 bought) vs 50K $714,515 (368 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Weekly; maximum / daily; reserve $32,700 | $489,380 | 58 / 20 | Weekly; maximum / daily; reserve $57,800 | $523,219 | 48 / 20 | $33,839 |
| 2 | Weekly; minimum / calendar_month; reserve $28,100 | $591,603 | 63 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,000 | $582,310 | 54 / 20 | $-9,294 |
| 3 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $28,200 | $596,982 | 64 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,000 | $594,604 | 56 / 20 | $-2,378 |
| 5 | Monthly + replacements, 10 spares; minimum / calendar_month; reserve $27,900 | $575,712 | 74 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,000 | $603,404 | 56 / 20 | $27,693 |
| 10 | Monthly + replacements, 10 spares; minimum / calendar_month; reserve $26,800 | $579,008 | 102 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $53,000 | $606,499 | 55 / 20 | $27,491 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $464,312 (60) | $464,312 (60) | $464,312 (60) | $507,238 (49) | $507,238 (49) | $507,238 (49) |
| 2 | $573,438 (66) | $572,934 (69) | $572,934 (69) | $569,324 (60) | $582,310 (54) | $582,310 (54) |
| 3 | $596,982 (64) | $558,071 (69) | $558,071 (69) | $583,685 (56) | $594,604 (56) | $594,604 (56) |
| 5 | $567,043 (70) | $569,395 (70) | $575,712 (74) | $599,565 (56) | $603,404 (56) | $603,404 (56) |
| 10 | $575,712 (74) | $577,942 (89) | $579,008 (102) | $606,499 (55) | $606,323 (55) | $606,323 (55) |

Cells show best total (accounts bought).

## $5,000 initial; $0/month

Unlimited supply (earlier study): 25K $810,670 (674 bought) vs 50K $723,142 (371 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Weekly; minimum / daily; reserve $32,800 | $489,780 | 56 / 20 | Weekly; minimum / calendar_month; reserve $52,800 | $513,928 | 51 / 20 | $24,148 |
| 2 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $27,700 | $535,331 | 74 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,000 | $555,225 | 61 / 20 | $19,895 |
| 3 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $26,500 | $558,158 | 101 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $50,100 | $589,640 | 68 / 20 | $31,482 |
| 5 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,200 | $624,386 | 95 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $50,100 | $611,600 | 63 / 20 | $-12,786 |
| 10 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,000 | $646,429 | 82 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $50,100 | $600,795 | 65 / 20 | $-45,634 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $464,712 (58) | $464,712 (58) | $464,712 (58) | $500,171 (52) | $500,171 (52) | $500,171 (52) |
| 2 | $535,331 (74) | $510,704 (75) | $510,704 (75) | $554,730 (60) | $555,225 (61) | $555,225 (61) |
| 3 | $558,158 (101) | $536,484 (129) | $556,785 (69) | $569,365 (66) | $589,640 (68) | $584,881 (64) |
| 5 | $567,199 (74) | $624,386 (95) | $624,386 (95) | $611,600 (63) | $595,008 (52) | $595,008 (52) |
| 10 | $646,396 (83) | $646,429 (82) | $646,429 (82) | $600,795 (65) | $600,795 (65) | $600,795 (65) |

Cells show best total (accounts bought).

## $5,000 initial; $200/month

Unlimited supply (earlier study): 25K $810,670 (674 bought) vs 50K $734,754 (370 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Weekly; minimum / weekly; reserve $31,200 | $489,380 | 58 / 20 | Weekly; maximum / calendar_month; reserve $56,200 | $537,275 | 49 / 20 | $47,895 |
| 2 | Weekly; minimum / calendar_month; reserve $28,400 | $603,208 | 71 / 20 | Monthly + replacements, 10 spares; minimum / calendar_month; reserve $52,900 | $635,808 | 50 / 20 | $32,600 |
| 3 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $28,400 | $611,890 | 72 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $52,900 | $644,689 | 47 / 20 | $32,799 |
| 5 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,900 | $646,544 | 75 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $52,900 | $646,086 | 46 / 20 | $-457 |
| 10 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $27,900 | $650,990 | 73 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $52,900 | $645,870 | 46 / 20 | $-5,119 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $464,312 (60) | $464,312 (60) | $464,312 (60) | $523,535 (51) | $523,535 (51) | $523,535 (51) |
| 2 | $586,612 (64) | $594,041 (75) | $594,041 (75) | $610,704 (52) | $629,330 (52) | $635,808 (50) |
| 3 | $611,890 (72) | $608,092 (91) | $600,099 (96) | $636,453 (49) | $644,689 (47) | $644,511 (48) |
| 5 | $609,468 (92) | $646,544 (75) | $646,544 (75) | $644,816 (47) | $646,086 (46) | $646,086 (46) |
| 10 | $650,022 (73) | $650,990 (73) | $650,990 (73) | $645,870 (46) | $645,450 (47) | $645,450 (47) |

Cells show best total (accounts bought).

## Where 25K catches up

| Budget | Lowest tested pass rate at which the best 25K total beats the best 50K total |
|---|---|
| $1,000 + $0/mo | never, up to 10 |
| $1,000 + $200/mo | 2 passes a month |
| $5,000 + $0/mo | 5 passes a month |
| $5,000 + $200/mo | 5 passes a month |

## Matched settings: share where 50K beats 25K

Same budget, purchasing, shelf, withdrawal and headroom; settings where both lose are excluded.

| Passes / month | Monthly + replacements | Weekly |
|---:|---:|---:|
| 1 | 86% of 1020 | 87% of 338 |
| 2 | 98% of 916 | 68% of 252 |
| 3 | 98% of 912 | 87% of 243 |
| 5 | 89% of 952 | 90% of 249 |
| 10 | 78% of 912 | 90% of 249 |

## Limits

In-sample best tested settings on one historical tape, not forecasts. The pass rate is deterministic and uncorrelated with the book, which flatters replacement policies. Weekly and monthly purchasing are not given spares. Evaluations are not traded; their cost is the owner's measured average. All other model limits of the unlimited-supply study apply.
