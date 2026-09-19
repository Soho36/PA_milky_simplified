# Legacy 50K operating policies and matched 25K comparison

Same RR tape, contract exposure, owner budgets and 20-live-account cap. User-specified seat fees: 25K $200; 50K $250. This measures account specification, size-dependent payout parameters AND cost together. Legacy availability throughout the dataset is counterfactual. No evaluation phase is modelled.

36 saved 25K controls reproduced exactly. Coarse plus local reserve search: 296 settings; purchase shortlist: 60 settings. Local refinement is only around the coarse ongoing/total winners per budget, not an exhaustive joint search.

Main tables retain the inherited 25K payout interpretation for comparability. They are model outputs, not a claim of complete Apex compliance. The separate sensitivity enforces the published minimum-balance wording after payout six for BOTH products. See [sources and model limits](../../../research/legacy_50k/SOURCES.md).

## $1,000 initial; $0/month

### Matched daily minimum, equal $6,800 floor headroom

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | monthly_one | minimum / daily | $31,900 | 58 | 17 | $224,400.00 | $77,887.21 | $302,287.21 |
| legacy_25k | weekly_one | minimum / daily | $31,900 | 5 | 0 | $-1,000.00 | $0.00 | $-1,000.00 |
| legacy_25k | monthly_current_slot_replacements | minimum / daily | $31,900 | 5 | 0 | $-1,000.00 | $0.00 | $-1,000.00 |
| legacy_50k | monthly_one | minimum / daily | $56,900 | 38 | 20 | $313,000.00 | $98,697.22 | $411,697.22 |
| legacy_50k | weekly_one | minimum / daily | $56,900 | 4 | 0 | $-1,000.00 | $0.00 | $-1,000.00 |
| legacy_50k | monthly_current_slot_replacements | minimum / daily | $56,900 | 49 | 20 | $305,300.00 | $90,145.45 | $395,445.45 |

### Best tested 50K bundles by acquisition

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | minimum / weekly | $57,600 | 35 | 20 | $285,900.00 | $132,422.26 | $418,322.26 |
| legacy_50k | weekly_one | maximum / weekly | $56,600 | 4 | 0 | $-1,000.00 | $0.00 | $-1,000.00 |
| legacy_50k | monthly_current_slot_replacements | maximum / weekly | $56,600 | 36 | 20 | $399,197.64 | $92,180.62 | $491,378.26 |

### Same selected bundles with later-payout retained minimum

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | minimum / weekly | $57,600 | 35 | 20 | $285,900.00 | $83,242.90 | $369,142.90 |
| legacy_50k | weekly_one | maximum / weekly | $56,600 | 4 | 0 | $-1,000.00 | $0.00 | $-1,000.00 |
| legacy_50k | monthly_current_slot_replacements | maximum / weekly | $56,600 | 36 | 20 | $399,197.64 | $43,751.26 | $442,948.90 |

Ongoing leader: monthly_current_slot_replacements / minimum daily / reserve $54,100: $451,200.00. [Detailed ledger](budget_1000_0__best_ongoing/report.txt).

Total leader: monthly_current_slot_replacements / maximum weekly / reserve $56,600: $491,378.26. [Detailed ledger](budget_1000_0__best_total/report.txt).

## $1,000 initial; $200/month

### Matched daily minimum, equal $6,800 floor headroom

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | monthly_one | minimum / daily | $31,900 | 60 | 20 | $361,600.00 | $102,711.75 | $464,311.75 |
| legacy_25k | weekly_one | minimum / daily | $31,900 | 75 | 20 | $449,800.00 | $100,881.87 | $550,681.87 |
| legacy_25k | monthly_current_slot_replacements | minimum / daily | $31,900 | 69 | 20 | $458,800.00 | $101,196.24 | $559,996.24 |
| legacy_50k | monthly_one | minimum / daily | $56,900 | 51 | 20 | $403,650.00 | $97,213.44 | $500,863.44 |
| legacy_50k | weekly_one | minimum / daily | $56,900 | 55 | 20 | $463,250.00 | $99,248.68 | $562,498.68 |
| legacy_50k | monthly_current_slot_replacements | minimum / daily | $56,900 | 49 | 20 | $483,250.00 | $101,223.62 | $584,473.62 |

### Best tested 50K bundles by acquisition

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | maximum / daily | $57,600 | 49 | 20 | $387,877.26 | $119,361.23 | $507,238.49 |
| legacy_50k | weekly_one | maximum / daily | $57,600 | 53 | 20 | $446,350.68 | $116,648.02 | $562,998.70 |
| legacy_50k | monthly_current_slot_replacements | maximum / weekly | $56,600 | 51 | 20 | $501,396.01 | $86,727.18 | $588,123.19 |

### Same selected bundles with later-payout retained minimum

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | maximum / daily | $57,600 | 49 | 20 | $387,877.26 | $71,431.87 | $459,309.13 |
| legacy_50k | weekly_one | maximum / daily | $57,600 | 53 | 20 | $446,350.68 | $70,443.21 | $516,793.89 |
| legacy_50k | monthly_current_slot_replacements | maximum / weekly | $56,600 | 51 | 20 | $501,396.01 | $41,490.54 | $542,886.55 |

Ongoing leader: monthly_current_slot_replacements / minimum daily / reserve $53,700: $542,450.00. [Detailed ledger](budget_1000_200__best_ongoing/report.txt).

Total leader: monthly_current_slot_replacements / maximum weekly / reserve $56,600: $588,123.19. [Detailed ledger](budget_1000_200__best_total/report.txt).

## $5,000 initial; $0/month

### Matched daily minimum, equal $6,800 floor headroom

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | monthly_one | minimum / daily | $31,900 | 59 | 20 | $361,800.00 | $102,711.75 | $464,511.75 |
| legacy_25k | weekly_one | minimum / daily | $31,900 | 75 | 20 | $443,000.00 | $101,526.53 | $544,526.53 |
| legacy_25k | monthly_current_slot_replacements | minimum / daily | $31,900 | 94 | 20 | $476,400.00 | $100,943.23 | $577,343.23 |
| legacy_50k | monthly_one | minimum / daily | $56,900 | 52 | 20 | $353,900.00 | $98,127.93 | $452,027.93 |
| legacy_50k | weekly_one | minimum / daily | $56,900 | 57 | 20 | $454,250.00 | $100,302.20 | $554,552.20 |
| legacy_50k | monthly_current_slot_replacements | minimum / daily | $56,900 | 73 | 20 | $444,900.00 | $102,694.55 | $547,594.55 |

### Best tested 50K bundles by acquisition

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | minimum / calendar_month | $52,900 | 52 | 20 | $318,000.00 | $182,170.67 | $500,170.67 |
| legacy_50k | weekly_one | minimum / calendar_month | $52,900 | 70 | 20 | $386,850.00 | $190,993.42 | $577,843.42 |
| legacy_50k | monthly_current_slot_replacements | minimum / calendar_month | $52,900 | 63 | 20 | $409,250.00 | $187,629.32 | $596,879.32 |

### Same selected bundles with later-payout retained minimum

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | minimum / calendar_month | $52,900 | 52 | 20 | $318,000.00 | $133,991.28 | $451,991.28 |
| legacy_50k | weekly_one | minimum / calendar_month | $52,900 | 70 | 20 | $386,850.00 | $144,538.56 | $531,388.56 |
| legacy_50k | monthly_current_slot_replacements | minimum / calendar_month | $52,900 | 63 | 20 | $409,250.00 | $142,629.41 | $551,879.41 |

Ongoing leader: monthly_current_slot_replacements / minimum daily / reserve $53,700: $533,650.00. [Detailed ledger](budget_5000_0__best_ongoing/report.txt).

Total leader: monthly_current_slot_replacements / minimum calendar_month / reserve $52,900: $596,879.32. [Detailed ledger](budget_5000_0__best_total/report.txt).

## $5,000 initial; $200/month

### Matched daily minimum, equal $6,800 floor headroom

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_25k | monthly_one | minimum / daily | $31,900 | 60 | 20 | $361,600.00 | $102,711.75 | $464,311.75 |
| legacy_25k | weekly_one | minimum / daily | $31,900 | 83 | 20 | $490,700.00 | $98,640.13 | $589,340.13 |
| legacy_25k | monthly_current_slot_replacements | minimum / daily | $31,900 | 91 | 20 | $503,600.00 | $99,993.42 | $603,593.42 |
| legacy_50k | monthly_one | minimum / daily | $56,900 | 52 | 20 | $415,550.00 | $97,152.00 | $512,702.00 |
| legacy_50k | weekly_one | minimum / daily | $56,900 | 62 | 20 | $502,000.00 | $97,121.07 | $599,121.07 |
| legacy_50k | monthly_current_slot_replacements | minimum / daily | $56,900 | 59 | 20 | $513,100.00 | $99,313.28 | $612,413.28 |

### Best tested 50K bundles by acquisition

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | maximum / daily | $56,900 | 51 | 20 | $413,627.82 | $105,199.27 | $518,827.09 |
| legacy_50k | weekly_one | maximum / daily | $56,900 | 62 | 20 | $498,169.49 | $100,951.66 | $599,121.15 |
| legacy_50k | monthly_current_slot_replacements | maximum / daily | $56,900 | 59 | 20 | $512,603.03 | $99,810.36 | $612,413.39 |

### Same selected bundles with later-payout retained minimum

| Product | Acquisition | Withdrawal / checks | Reserve | Accounts | Alive | Ongoing | Terminal | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| legacy_50k | monthly_one | maximum / daily | $56,900 | 51 | 20 | $413,627.82 | $57,519.91 | $471,147.73 |
| legacy_50k | weekly_one | maximum / daily | $56,900 | 62 | 20 | $498,169.49 | $55,735.77 | $553,905.26 |
| legacy_50k | monthly_current_slot_replacements | maximum / daily | $56,900 | 59 | 20 | $512,603.03 | $54,810.55 | $567,413.58 |

Ongoing leader: monthly_current_slot_replacements / minimum daily / reserve $54,100: $559,600.00. [Detailed ledger](budget_5000_200__best_ongoing/report.txt).

Total leader: monthly_current_slot_replacements / maximum daily / reserve $56,900: $612,413.39. [Detailed ledger](budget_5000_200__best_total/report.txt).

## Interpretation

Matched tables hold dollar headroom above the frozen floor fixed, not headroom as a multiple of drawdown. With the same tape/exposure, a larger account does not double per-trade earnings: it changes survival, extraction gates and acquisition affordability. Fresh search winners compare adapted bundles, not the isolated effect of the account size. Purchase shortlist reserves were selected with monthly-one; other acquisitions were not independently exhaustively optimized.

Both scored objectives use the same path, with one endpoint request releasing the voluntary reserve. Results can depend strongly on that receipt. The strict sensitivity can alter subsequent cohorts as well as terminal cash; it is not merely an arithmetic haircut. All profiles retain the cumulative first-$25,000 split interpretation and the inherited concurrency approximation. Historical 25K reports are unchanged.
