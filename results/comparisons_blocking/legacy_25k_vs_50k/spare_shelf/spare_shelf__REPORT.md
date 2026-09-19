# Legacy 25K versus 50K under a limited supply of funded accounts — blocked copying

13,504 simulations. 1280 rows that must equal the unlimited-supply study reproduced it exactly, including per-trade account assignments. Both products are tested on exactly the same settings.

**Execution: blocked copying.** Each funded account holds at most one position; an account still in an earlier trade skips a new signal. The unlimited-supply reference is the [blocked reserve comparison](../reserve_by_policy/reserve_by_policy__REPORT.md). Everything else matches the [non-blocking spare-shelf study](../../../comparisons/legacy_25k_vs_50k/spare_shelf/spare_shelf__REPORT.md).

## The question

The unlimited-supply study let every purchase become a funded account at once. Its best 25K bundles bought 531–539 accounts by replacing deaths immediately. Here funded accounts come from passed evaluations: at most **N passes per calendar month**, each paid in full ($200 / $250) when it passes. A pass not needed at once waits dormant on a shelf of up to K spares, and **spares count toward the 20-account cap**. Spares left at the end are sunk. See [ASSUMPTIONS.md](../../../../ASSUMPTIONS.md#supply-of-funded-accounts).

Replacement purchasing is tested with [0, 5, 10] spares and [1, 2, 3, 5, 10] passes a month. Weekly and monthly purchasing run without spares as comparators; more than five passes a month never binds them. Reserves are re-searched for every setting: coarse headrooms [0, 500, 1000, 1500, 2000, 3000, 4000, 5000, 6500, 8000, 10000] above the frozen floor, then +/-$400 in $100 steps around each product's best bundle, applied to both products. This is coarser than the unlimited study, which slightly favours its numbers.

**The pass rate is fixed.** Real passes are lumpy and probably scarcest when the book is dying, so a fixed rate flatters replacement policies. Read each row as "an owner who can reliably pass N accounts a month".

## Files

- [All settings](all_settings.csv), [best by shelf](best_by_shelf.csv), [matched 50K-minus-25K differences](matched_deltas.csv), [contract and rows](study.json).
- Detailed ledgers for each product's best bundle at 3 passes a month.

## $1,000 initial; $0/month

Unlimited supply (earlier study): 25K $200,400 (68 bought) vs 50K $268,478 (56 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Monthly; minimum / weekly; reserve $27,000 | $200,400 | 68 / 3 | Weekly; maximum / weekly; reserve $52,100 | $281,490 | 55 / 1 | $81,090 |
| 2 | Monthly; minimum / weekly; reserve $27,000 | $200,400 | 68 / 3 | Monthly + replacements, 0 spares; maximum / weekly; reserve $52,100 | $270,533 | 78 / 2 | $70,133 |
| 3 | Monthly; minimum / weekly; reserve $27,000 | $200,400 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478 | 56 / 1 | $68,078 |
| 5 | Monthly; minimum / weekly; reserve $27,000 | $200,400 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478 | 56 / 1 | $68,078 |
| 10 | Monthly; minimum / weekly; reserve $27,000 | $200,400 | 68 / 3 | Monthly; maximum / weekly; reserve $52,100 | $268,478 | 56 / 1 | $68,078 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $157,313 (74) | $157,313 (74) | $157,313 (74) | $267,348 (58) | $265,470 (58) | $265,470 (58) |
| 2 | $-813 (12) | $-1,000 (5) | $-1,000 (5) | $270,533 (78) | $-759 (16) | $-759 (16) |
| 3 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $-759 (16) | $-857 (6) | $-857 (6) |
| 5 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $-857 (6) | $-857 (6) | $-857 (6) |
| 10 | $-1,000 (5) | $-1,000 (5) | $-1,000 (5) | $-857 (6) | $-857 (6) | $-857 (6) |

Cells show best total (accounts bought).

## $1,000 initial; $200/month

Unlimited supply (earlier study): 25K $665,421 (531 bought) vs 50K $585,935 (265 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Monthly; minimum / calendar_month; reserve $28,700 | $316,743 | 74 / 19 | Weekly; minimum / calendar_month; reserve $53,700 | $454,838 | 44 / 20 | $138,095 |
| 2 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $26,700 | $456,079 | 86 / 20 | Weekly; minimum / calendar_month; reserve $50,100 | $480,227 | 52 / 20 | $24,149 |
| 3 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $26,700 | $473,076 | 96 / 20 | Weekly; minimum / calendar_month; reserve $50,100 | $485,374 | 55 / 20 | $12,298 |
| 5 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $25,100 | $476,063 | 153 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $50,100 | $483,020 | 63 / 20 | $6,957 |
| 10 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $25,100 | $517,844 | 173 / 20 | Weekly; minimum / calendar_month; reserve $50,100 | $478,956 | 59 / 20 | $-38,888 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $316,543 (75) | $316,543 (75) | $316,543 (75) | $448,930 (50) | $448,930 (50) | $448,930 (50) |
| 2 | $449,539 (88) | $456,079 (86) | $456,079 (86) | $470,277 (54) | $470,277 (54) | $470,277 (54) |
| 3 | $473,076 (96) | $457,265 (75) | $457,265 (75) | $479,850 (58) | $479,850 (58) | $479,850 (58) |
| 5 | $476,063 (153) | $472,063 (163) | $468,163 (165) | $483,020 (63) | $470,824 (66) | $470,824 (66) |
| 10 | $517,844 (173) | $511,444 (175) | $511,444 (175) | $454,431 (67) | $454,431 (67) | $454,431 (67) |

Cells show best total (accounts bought).

## $5,000 initial; $0/month

Unlimited supply (earlier study): 25K $670,286 (539 bought) vs 50K $550,450 (236 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $26,900 | $285,659 | 79 / 17 | Weekly; minimum / calendar_month; reserve $50,100 | $454,773 | 45 / 20 | $169,115 |
| 2 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $26,800 | $447,739 | 77 / 20 | Monthly; minimum / calendar_month; reserve $50,100 | $449,930 | 46 / 20 | $2,190 |
| 3 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $28,500 | $470,469 | 66 / 20 | Monthly; minimum / calendar_month; reserve $50,100 | $449,930 | 46 / 20 | $-20,539 |
| 5 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $25,100 | $478,163 | 155 / 20 | Weekly; minimum / weekly; reserve $50,100 | $454,500 | 92 / 12 | $-23,663 |
| 10 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $25,100 | $525,044 | 172 / 20 | Weekly; minimum / weekly; reserve $50,100 | $454,500 | 92 / 12 | $-70,544 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $285,659 (79) | $285,659 (79) | $285,659 (79) | $449,930 (46) | $449,930 (46) | $449,930 (46) |
| 2 | $447,739 (77) | $395,865 (114) | $395,665 (115) | $418,000 (72) | $407,000 (76) | $406,000 (76) |
| 3 | $469,891 (93) | $470,469 (66) | $470,469 (66) | $423,750 (83) | $416,000 (86) | $415,500 (86) |
| 5 | $478,163 (155) | $475,263 (167) | $475,063 (168) | $431,000 (98) | $367,900 (174) | $367,900 (174) |
| 10 | $525,044 (172) | $523,644 (169) | $523,644 (169) | $428,692 (234) | $428,692 (234) | $428,692 (234) |

Cells show best total (accounts bought).

## $5,000 initial; $200/month

Unlimited supply (earlier study): 25K $670,286 (539 bought) vs 50K $603,596 (283 bought).

### Best tested bundle by pass rate (terminal-inclusive total)

| Passes / month | **25K — bundle** | **25K — total** | **25K — bought / alive** | **50K — bundle** | **50K — total** | **50K — bought / alive** | 50K minus 25K |
| ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| 1 | Monthly; minimum / calendar_month; reserve $28,700 | $316,743 | 74 / 19 | Weekly; maximum / weekly; reserve $56,300 | $460,667 | 47 / 20 | $143,924 |
| 2 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $26,700 | $456,279 | 95 / 20 | Weekly; minimum / calendar_month; reserve $50,100 | $482,227 | 66 / 20 | $25,949 |
| 3 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $26,700 | $475,876 | 102 / 20 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $53,800 | $496,665 | 55 / 20 | $20,789 |
| 5 | Monthly + replacements, 5 spares; minimum / calendar_month; reserve $26,700 | $500,612 | 133 / 20 | Weekly; minimum / calendar_month; reserve $50,100 | $501,090 | 70 / 20 | $478 |
| 10 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $25,100 | $525,044 | 172 / 20 | Monthly + replacements, 0 spares; minimum / calendar_month; reserve $50,100 | $521,830 | 81 / 20 | $-3,214 |

### Monthly + replacements: best total by spares held

| Passes / month | **25K — 0 spares** | **25K — 5 spares** | **25K — 10 spares** | **50K — 0 spares** | **50K — 5 spares** | **50K — 10 spares** |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | $316,543 (75) | $316,543 (75) | $316,543 (75) | $456,799 (48) | $456,799 (48) | $456,799 (48) |
| 2 | $449,539 (88) | $456,279 (95) | $456,079 (96) | $479,683 (61) | $479,183 (67) | $480,183 (67) |
| 3 | $475,876 (102) | $473,774 (88) | $473,774 (88) | $489,751 (66) | $496,665 (55) | $491,681 (56) |
| 5 | $499,012 (126) | $500,612 (133) | $500,612 (133) | $499,856 (73) | $498,606 (74) | $498,606 (74) |
| 10 | $525,044 (172) | $523,644 (169) | $523,644 (169) | $521,830 (81) | $521,830 (81) | $521,830 (81) |

Cells show best total (accounts bought).

## Where 25K catches up

| Budget | Lowest tested pass rate at which the best 25K total beats the best 50K total |
|---|---|
| $1,000 + $0/mo | never, up to 10 |
| $1,000 + $200/mo | 10 passes a month |
| $5,000 + $0/mo | 3 passes a month |
| $5,000 + $200/mo | 10 passes a month |

## Matched settings: share where 50K beats 25K

Same budget, purchasing, shelf, withdrawal and headroom; settings where both lose are excluded.

| Passes / month | Monthly + replacements | Weekly |
|---:|---:|---:|
| 1 | 93% of 921 | 91% of 311 |
| 2 | 95% of 686 | 95% of 222 |
| 3 | 80% of 743 | 95% of 222 |
| 5 | 71% of 740 | 97% of 253 |
| 10 | 40% of 699 | 97% of 253 |

## Limits

In-sample best tested settings on one historical tape, not forecasts. The pass rate is deterministic and uncorrelated with the book, which flatters replacement policies. Weekly and monthly purchasing are not given spares. Evaluations are not traded; their cost is the owner's measured average. All other model limits of the unlimited-supply study apply.
