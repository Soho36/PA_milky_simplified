# RR 0.50 / 2.50 with overlapping positions

Allowing overlap materially changes the mixture's result. Its best tested
headroom increases from **$4,500 to $6,100**, while best combined cash falls
from **$495,589 to $443,582** (10.5% lower). The large reserve reduction seen
in the while-flat run does not carry over to overlapping execution.

The new run tests 262 settings including hold. Both cash objectives select
**$1,500 monthly backlog or maximum excess monthly**, tied at a retained
balance of **$31,200** ($6,100 above the frozen $25,100 floor). Ongoing net
cash is $367,282 and the final permitted receipt is $76,300. There are 21
survivors from 79 purchases. These winners preserve the hold trading path;
the other 58 accounts also die without withdrawals.

## Compare the same policy family

For maximum excess monthly, choose each study's best combined-cash setting:

| Study | Retained balance | Headroom | Ongoing net cash | Including terminal | Survivors | Hold path preserved |
|---|---:|---:|---:|---:|---:|:-:|
| RR1 overlap | $31,600 | $6,500 | $354,140 | $456,486 | 22 | yes |
| Pair while flat | $29,600 | $4,500 | $415,319 | $495,589 | 27 | yes |
| Pair overlap | $31,200 | $6,100 | $367,282 | $443,582 | 21 | yes |

On this matched policy-family comparison, the overlapping pair's selected
reserve is only $400 below RR1's, rather than the $2,000 difference between
RR1 overlap and the pair while flat. These are local, in-sample optima, not
minimum reserves guaranteed to work in future. Without an RR1 while-flat
arm, this is not a complete strategy-by-execution interaction experiment.

## Compare identical policy and reserve settings

Maximum excess monthly at common tested balances:

| Retained balance | Study | Ongoing net cash | Including terminal | Survivors | Hold path preserved |
|---:|---|---:|---:|---:|:-:|
| $29,600 | RR1 overlap | $320,939 | $320,939 | 2 | no |
| $29,600 | Pair while flat | $415,319 | $495,589 | 27 | yes |
| $29,600 | Pair overlap | $258,534 | $291,520 | 15 | no |
| $31,100 | RR1 overlap | $362,771 | $445,869 | 20 | no |
| $31,100 | Pair while flat | $379,740 | $485,193 | 27 | yes |
| $31,100 | Pair overlap | $329,241 | $399,956 | 20 | no |
| $31,600 | RR1 overlap | $354,140 | $456,486 | 22 | yes |
| $31,600 | Pair while flat | $367,393 | $484,576 | 27 | yes |
| $31,600 | Pair overlap | $359,431 | $436,061 | 21 | yes |

All **185 common policy/reserve settings**, including hold, are retained in
[matched_comparison.csv](matched_comparison.csv). Each study's local refinement
also samples different extra points, so comparisons use the intersection of
tested settings, without interpolation.

## The hold controls explain part of the difference

| Study | Net booked trading earnings | Survivors without withdrawals |
|---|---:|---:|
| RR1 overlap | $462,022 | 22 |
| Pair while flat | $527,774 | 27 |
| Pair overlap | $470,886 | 21 |

The pair while flat ends with six more hold survivors than the overlapping
pair and more booked earnings. Thus the execution change affects the trading
paths before withdrawal policies are considered. Different r/r targets also
change holding times and concurrent exposure; this comparison does not
normalize that exposure or isolate a pure diversification effect.

Across all policy families, the original RR1 study's best combined cash is
$460,512 (minimum monthly at $30,000), versus $443,582 for the overlapping
pair. Those selected portfolios use different payout policies. The mixture
does not dominate the original study on cash extraction.

## Reserve sensitivity remains important

For the new leading policy, $31,100 produces $399,956 combined cash and 20
survivors; $31,200 produces $443,582 and 21 survivors. A $100 reserve change
preserves one account with substantial subsequent earnings. At $31,600,
21 survive and combined cash is $436,061, about 1.7% below the peak. This
does not establish $31,200 as a robust operating threshold.

## Scope and validation

Both mixture studies use the same inputs, dates, alternating monthly account
assignments (40 at 0.50, 39 at 2.50), fresh account states, commissions and
payout rules. Purchases remain uncapped and externally financed, with no
extra replacements. The surviving overlap winner contains 14 at 0.50 and
7 at 2.50; equal purchases do not maintain equal surviving allocations.

Overlap matches the original model: whole-trade MAE/MFE and P/L are applied
in exit order. It is not a reconstruction of combined open-position equity.
Later settlements are ignored once an account dies, even if those trades
were already open. One MNQ per trade can mean several concurrent contracts
per account. Results must be read within that historical model.

All 262 financial identities reconcile, with 31,382,198 booked-copy checks.
Hold and both leaders reproduce; an independent settlement selector checked
237 account paths and 432,984 booked copies. The original RR1 hold and both
leaders reproduce exactly, and the adapter matches the unchanged legacy
engine for those controls. All 14 targeted tests passed. Shared engine code
and earlier results were preserved.

- [Full overlap report](rr_pair_overlap_monthly_amount_x_cushion__REPORT.md)
- [All new candidates](candidates.csv)
- [Independent audit](audit.json)
- [Comparison input hashes](comparison.json)
- [Study design](../../../research/legacy_25k/RR_PAIR_OVERLAP_WITHDRAWAL_AMOUNT.md)

Rebuild this comparison with `venv/Scripts/python.exe scripts/compare_rr_pair_withdrawal_amount.py`.
