# Fixed-R shared routing pools

Every exported trade receives R copies. Start once with K=5R accounts; reuse free seats and buy only a current shortfall. No monthly or weekly purchases. Account deaths can require replacements, so lifetime purchases can exceed initial K while live inventory stays within 20.

All cases use the inherited withdrawal settings, one MNQ per copy and the same rulebook. Each start/R group has identical signal-copy demand across withdrawals and allocations. The daily and monthly settings also have different retained balances: differences cannot be attributed to cadence alone.

This remains a capacity/economics experiment: funded seats are available immediately when needed, and external funding is supplied as required. The table measures that funding; it does not impose an affordability gate or Evaluation/activation delays. Five is the observed tape overlap, not a future guarantee. Trade extrema are applied at exit and working-order reservations are absent. 2023 is a start-date sensitivity, not independent out-of-sample policy selection.

Net cash subtracts all account costs and excludes contributions. Total includes one firm-permitted terminal request.

## Fresh start in 2020

| R / initial K | Withdrawal | Allocation | Bought / peak live | Deaths | Coverage | Ongoing net | Terminal receipt | Total net | Total owner funding needed |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 / 5 | minimum_daily_31900 | max_headroom | 8 / 5 | 3 | 100% | $25,400.00 | $1,733.54 | $27,133.54 | $1,600.00 |
| 1 / 5 | minimum_daily_31900 | round_robin | 17 / 5 | 13 | 100% | $21,600.00 | $13,014.62 | $34,614.62 | $2,200.00 |
| 1 / 5 | maximum_weekly_31600 | max_headroom | 8 / 5 | 3 | 100% | $28,290.15 | $5,037.10 | $33,327.25 | $1,600.00 |
| 1 / 5 | maximum_weekly_31600 | round_robin | 17 / 5 | 13 | 100% | $23,562.60 | $10,596.58 | $34,159.18 | $2,200.00 |
| 1 / 5 | minimum_calendar_month_30000 | max_headroom | 8 / 5 | 3 | 100% | $19,900.00 | $14,398.93 | $34,298.93 | $1,400.00 |
| 1 / 5 | minimum_calendar_month_30000 | round_robin | 17 / 5 | 13 | 100% | $24,100.00 | $8,498.28 | $32,598.28 | $2,200.00 |
| 2 / 10 | minimum_daily_31900 | max_headroom | 16 / 10 | 6 | 100% | $50,800.00 | $3,467.08 | $54,267.08 | $3,200.00 |
| 2 / 10 | minimum_daily_31900 | round_robin | 34 / 10 | 26 | 100% | $43,200.00 | $26,029.24 | $69,229.24 | $4,400.00 |
| 2 / 10 | maximum_weekly_31600 | max_headroom | 16 / 10 | 6 | 100% | $56,580.30 | $10,074.20 | $66,654.50 | $3,200.00 |
| 2 / 10 | maximum_weekly_31600 | round_robin | 34 / 10 | 26 | 100% | $47,125.20 | $21,193.16 | $68,318.36 | $4,400.00 |
| 2 / 10 | minimum_calendar_month_30000 | max_headroom | 16 / 10 | 6 | 100% | $39,800.00 | $28,797.86 | $68,597.86 | $2,800.00 |
| 2 / 10 | minimum_calendar_month_30000 | round_robin | 34 / 10 | 26 | 100% | $48,200.00 | $16,996.56 | $65,196.56 | $4,400.00 |
| 3 / 15 | minimum_daily_31900 | max_headroom | 24 / 15 | 9 | 100% | $76,200.00 | $5,200.62 | $81,400.62 | $4,800.00 |
| 3 / 15 | minimum_daily_31900 | round_robin | 51 / 15 | 39 | 100% | $64,800.00 | $39,043.86 | $103,843.86 | $6,600.00 |
| 3 / 15 | maximum_weekly_31600 | max_headroom | 24 / 15 | 9 | 100% | $84,870.45 | $15,111.30 | $99,981.75 | $4,800.00 |
| 3 / 15 | maximum_weekly_31600 | round_robin | 51 / 15 | 39 | 100% | $70,687.80 | $31,789.74 | $102,477.54 | $6,600.00 |
| 3 / 15 | minimum_calendar_month_30000 | max_headroom | 24 / 15 | 9 | 100% | $59,700.00 | $43,196.79 | $102,896.79 | $4,200.00 |
| 3 / 15 | minimum_calendar_month_30000 | round_robin | 51 / 15 | 39 | 100% | $72,300.00 | $25,494.84 | $97,794.84 | $6,600.00 |
| 4 / 20 | minimum_daily_31900 | max_headroom | 32 / 20 | 12 | 100% | $101,600.00 | $6,934.16 | $108,534.16 | $6,400.00 |
| 4 / 20 | minimum_daily_31900 | round_robin | 68 / 20 | 52 | 100% | $86,400.00 | $52,058.48 | $138,458.48 | $8,800.00 |
| 4 / 20 | maximum_weekly_31600 | max_headroom | 32 / 20 | 12 | 100% | $113,160.60 | $20,148.40 | $133,309.00 | $6,400.00 |
| 4 / 20 | maximum_weekly_31600 | round_robin | 68 / 20 | 52 | 100% | $94,250.40 | $42,386.32 | $136,636.72 | $8,800.00 |
| 4 / 20 | minimum_calendar_month_30000 | max_headroom | 32 / 20 | 12 | 100% | $79,600.00 | $57,595.72 | $137,195.72 | $5,600.00 |
| 4 / 20 | minimum_calendar_month_30000 | round_robin | 68 / 20 | 52 | 100% | $96,400.00 | $33,993.12 | $130,393.12 | $8,800.00 |

## Fresh start in 2023

| R / initial K | Withdrawal | Allocation | Bought / peak live | Deaths | Coverage | Ongoing net | Terminal receipt | Total net | Total owner funding needed |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 / 5 | minimum_daily_31900 | max_headroom | 5 / 5 | 0 | 100% | $17,000.00 | $0.00 | $17,000.00 | $1,000.00 |
| 1 / 5 | minimum_daily_31900 | round_robin | 8 / 5 | 5 | 100% | $10,400.00 | $6,997.74 | $17,397.74 | $1,200.00 |
| 1 / 5 | maximum_weekly_31600 | max_headroom | 5 / 5 | 0 | 100% | $18,754.10 | $5,363.29 | $24,117.39 | $1,000.00 |
| 1 / 5 | maximum_weekly_31600 | round_robin | 8 / 5 | 5 | 100% | $10,690.40 | $13,456.78 | $24,147.18 | $1,200.00 |
| 1 / 5 | minimum_calendar_month_30000 | max_headroom | 5 / 5 | 0 | 100% | $12,000.00 | $11,197.69 | $23,197.69 | $1,000.00 |
| 1 / 5 | minimum_calendar_month_30000 | round_robin | 8 / 5 | 5 | 100% | $11,900.00 | $1,500.00 | $13,400.00 | $1,200.00 |
| 2 / 10 | minimum_daily_31900 | max_headroom | 10 / 10 | 0 | 100% | $34,000.00 | $0.00 | $34,000.00 | $2,000.00 |
| 2 / 10 | minimum_daily_31900 | round_robin | 16 / 10 | 10 | 100% | $20,800.00 | $13,995.48 | $34,795.48 | $2,400.00 |
| 2 / 10 | maximum_weekly_31600 | max_headroom | 10 / 10 | 0 | 100% | $37,508.20 | $10,726.58 | $48,234.78 | $2,000.00 |
| 2 / 10 | maximum_weekly_31600 | round_robin | 16 / 10 | 10 | 100% | $21,380.80 | $26,913.56 | $48,294.36 | $2,400.00 |
| 2 / 10 | minimum_calendar_month_30000 | max_headroom | 10 / 10 | 0 | 100% | $24,000.00 | $22,395.38 | $46,395.38 | $2,000.00 |
| 2 / 10 | minimum_calendar_month_30000 | round_robin | 16 / 10 | 10 | 100% | $23,800.00 | $3,000.00 | $26,800.00 | $2,400.00 |
| 3 / 15 | minimum_daily_31900 | max_headroom | 15 / 15 | 0 | 100% | $51,000.00 | $0.00 | $51,000.00 | $3,000.00 |
| 3 / 15 | minimum_daily_31900 | round_robin | 24 / 15 | 15 | 100% | $31,200.00 | $20,993.22 | $52,193.22 | $3,600.00 |
| 3 / 15 | maximum_weekly_31600 | max_headroom | 15 / 15 | 0 | 100% | $56,262.30 | $16,089.87 | $72,352.17 | $3,000.00 |
| 3 / 15 | maximum_weekly_31600 | round_robin | 24 / 15 | 15 | 100% | $32,071.20 | $40,370.34 | $72,441.54 | $3,600.00 |
| 3 / 15 | minimum_calendar_month_30000 | max_headroom | 15 / 15 | 0 | 100% | $36,000.00 | $33,593.07 | $69,593.07 | $3,000.00 |
| 3 / 15 | minimum_calendar_month_30000 | round_robin | 24 / 15 | 15 | 100% | $35,700.00 | $4,500.00 | $40,200.00 | $3,600.00 |
| 4 / 20 | minimum_daily_31900 | max_headroom | 20 / 20 | 0 | 100% | $68,000.00 | $0.00 | $68,000.00 | $4,000.00 |
| 4 / 20 | minimum_daily_31900 | round_robin | 32 / 20 | 20 | 100% | $41,600.00 | $27,990.96 | $69,590.96 | $4,800.00 |
| 4 / 20 | maximum_weekly_31600 | max_headroom | 20 / 20 | 0 | 100% | $75,016.40 | $21,453.16 | $96,469.56 | $4,000.00 |
| 4 / 20 | maximum_weekly_31600 | round_robin | 32 / 20 | 20 | 100% | $42,761.60 | $53,827.12 | $96,588.72 | $4,800.00 |
| 4 / 20 | minimum_calendar_month_30000 | max_headroom | 20 / 20 | 0 | 100% | $48,000.00 | $44,790.76 | $92,790.76 | $4,000.00 |
| 4 / 20 | minimum_calendar_month_30000 | round_robin | 32 / 20 | 20 | 100% | $47,600.00 | $6,000.00 | $53,600.00 | $4,800.00 |

