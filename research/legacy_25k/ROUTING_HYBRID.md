# Hybrid routing: protect participation and vary replication

The hybrid can increase exposure while preserving every signal, but the first
experiment does not establish a consistently better policy. From the 2023
start, higher copy caps increase cash substantially. From 2020, those same
caps concentrate early losses and deplete the account pool. Reserving free
slots does not protect the accounts already exposed to a losing setup.

[Full tables and copy distributions](../../results/legacy_25k/routing_hybrid/routing_hybrid__REPORT.generated.md),
[comparison CSV](../../results/legacy_25k/routing_hybrid/comparison.csv),
[independent audit](../../results/legacy_25k/routing_hybrid/AUDIT.generated.json).

## Unchanged comparison rules

All arms start with 20 paid accounts ($4,000). There are no later purchases,
death replacements or owner contributions. Withdrawal policy, retained balance,
terminal request, contract size and account rules match within each case.
The main policy is daily minimum withdrawals retaining $31,900. Retain $30,000
and a fresh 2023 start are separate sensitivity checks, not retuned winners.
Every case ends at the same July 2026 dataset horizon.

Controls are unrestricted copying, blocked copying, fixed R=4 max-headroom
and fixed R=4 round-robin. Six hybrid settings combine minimum participation
of one or two copies with a maximum of four, eight or twelve copies. Every
hybrid selects free accounts by greatest current headroom, with account ID
breaking ties. The six settings were specified before running. The four cases
share data and are not independent validation samples.

## Entry decision

Let F be free live accounts, A be the number of distinct currently occupied
setups, m be minimum participation, c be the copy cap, and C=5 be the assumed
maximum overlapping setups.

```
reserve = m * max(0, C - A - 1)
target  = min(c, max(m, F - reserve))
filled  = min(F, target)
```

For example, m=1/c=8 allocates 8, 8, 2, 1, 1 copies to five consecutive
overlapping setups when starting with 20 free accounts. With m=2/c=8, the
corresponding allocation is 8, 6, 2, 2, 2. Isolated setups receive eight copies.

Only setups with actual open allocations count toward A. The router uses
current inventory, observed closures and current account headroom; future
holding time, outcome and extrema do not choose the allocation. Existing exits
at a timestamp release capacity before new entries. Instantaneous trades
enter then immediately exit. One account never carries overlapping positions.

If deaths make both the current minimum and future reservations impossible,
the router attempts the current minimum first. It records reservation deficits
and missing minimum copies. It does not reduce the declared minimum or hide
missed signals by setting its target to zero. The C=5 assumption comes from
historical overlap and does not guarantee future coverage or account survival.

## Main results: retain $31,900

All cash below is net of initial fees; total includes terminal receipts.

| Start | Arm | Copies | Signals traded | Deaths | Ongoing net | Total net |
|---|---|---:|---:|---:|---:|---:|
| 2020 | Blocked copying | 5,640 | 2.23% | 20 | -$4,000 | -$4,000 |
| 2020 | Fixed R=4 max-headroom | 49,168 | 97.11% | 12 | $104,000 | $110,891.16 |
| 2020 | Hybrid minimum 1 / cap 4 | 46,314 | 100% | 11 | $98,500 | $103,009.33 |
| 2020 | Hybrid minimum 1 / cap 8 | 15,228 | 99.66% | 17 | $25,000 | $26,661.44 |
| 2020 | Hybrid minimum 1 / cap 12 | 3,874 | 3.05% | 20 | -$4,000 | -$4,000 |
| 2023 | Blocked copying | 101,420 | 73.15% | 0 | $356,000 | $356,000 |
| 2023 | Fixed R=4 max-headroom | 27,728 | 100% | 0 | $68,000 | $68,000 |
| 2023 | Hybrid minimum 1 / cap 4 | 27,728 | 100% | 0 | $68,000 | $68,000 |
| 2023 | Hybrid minimum 1 / cap 8 | 53,083 | 100% | 3 | $144,500 | $144,500 |
| 2023 | Hybrid minimum 1 / cap 12 | 68,473 | 100% | 2 | $215,500 | $215,500 |

The 2023 cap-eight hybrid takes 1.91 times the fixed-R copies and produces
2.13 times the total cash. It takes eight copies on 6,392 of 6,932 signals;
the other signals receive one, two or six. It retains full signal coverage
while increasing replication, which is the intended mechanism. Blocked
copying still produces more cash, with more copies and lower signal coverage.

The 2020 cap-eight result is almost the opposite. It loses 17 accounts and
takes only one copy on 12,224 signals, with 43 signals missed entirely.
Thus 99.66% participation conceals a largely depleted book. Raising the cap
has reduced total lifetime copies because the book cannot sustain its early
replication. Both cap-twelve hybrids eventually lose all accounts in 2020.

Protecting two copies does not uniformly improve the outcome. In 2020, m=2/c=4
takes every signal but earns $54,367.68 total, versus $103,009.33 for m=1/c=4.
Its larger reservations hold replication at two on 8,779 signals. With m=2/c=8,
18 deaths leave only two accounts, and coverage falls to 76.79%.

## What survived the sensitivity checks

Minimum one / cap four is the only hybrid setting with 100% signal coverage
in all four tested cases. Its cash totals are:

| Start | Retained balance | Fixed R=4 max-headroom | Hybrid minimum 1 / cap 4 |
|---|---:|---:|---:|
| 2020 | $31,900 | $110,891.16 | $103,009.33 |
| 2020 | $30,000 | $118,000 | $112,450 |
| 2023 | $31,900 | $68,000 | $68,000 |
| 2023 | $30,000 | $78,000 | $77,000 |

This setting primarily repairs coverage after account losses; it does not
raise the four-copy ceiling. Its improved participation comes with slightly
lower cash in three cases and identical cash in the fourth.

With a 2023 start and retained balance $30,000, both cap-eight settings still
take every signal: total cash is $165,300.89 for minimum one and $168,672.58
for minimum two, versus $78,000 for fixed R=4. Both cap-twelve settings lose
all accounts and finish with about 91.5% signal coverage. Even within the
same starting period, the withdrawal setting changes survival materially.

The evidence supports keeping the reservation mechanism as a useful control.
It does not support choosing eight or twelve as a universally better cap.
A separate next hypothesis would make extra replication depend on account
health as well as free slots. That is not implemented or validated here:
headroom currently ranks account selection, while copy count depends on
capacity. Any such extension should retain these fixed-cap controls and
avoid selecting thresholds using the same periods used to claim improvement.

## Evidence and limitations

All 16 control arms reproduce their prior financial results and per-trade
account assignments. Earlier fixed-inventory files are hash-checked and
preserved. The independent audit validates 40 arms, 1,616,856 copies and
235,080 hybrid entry offers, including the reservation formula, minimum
shortfalls, copy histograms, initial-only purchases, cash and non-overlap.

Targeted tests cover the five-overlap examples, current-headroom selection,
future-outcome independence, reuse after exits, zero-duration trades,
depleted inventory and minimum preservation on a synthetic no-death tape.

Same resources do not imply equal exposure or risk. There is no signal-quality
model; earlier arrivals can receive more copies simply because slots are
free. As before, deaths use exported per-trade extrema at exit, and working
order reservations are absent. The unrestricted control does not aggregate
concurrent floating P&L. These remain historical simulations of the configured
account and withdrawal rules.

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/study_routing_hybrid.py
.\venv\Scripts\python.exe scripts/audit_routing_hybrid.py
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```
