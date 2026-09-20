# RR composition, group count and reserve ladders: findings

**Composition matters; adding RR groups is not a monotonic improvement. Reserve
ladders can genuinely spread recorded deaths over time, but did not improve
continuity under the primary daily-minimum policy.**

Completed 730 frozen historical runs: 600 primary isolation/operating cases,
100 March stress cases, and 30 primary operating intratrade-order sensitivities.
There are 36 homogeneous RR controls and 14 experimental arms. The core engine,
original study settings and earlier result files remain unchanged.

## 1. Width is insufficient to explain the original result

The requested 1.25/1.75/2.25/2.75 arm has a range of 1.50, half the original
0.50/1.50/2.50/3.50 range. We also tested 0.50/0.75/3.25/3.50, holding the
endpoints, mean, number of groups and equal weights fixed while changing the
interior constituents.

Primary operating results, daily minimum / $6,800 mean reserve:

| Portfolio | Starts with no empty-book episode, out of six | Important failure context |
|---|---:|---|
| Original 0.50/1.50/2.50/3.50 | 6 | None |
| Centered 1.25/1.75/2.25/2.75 | 4 | Startup books in 2020 and 2022; 56.06 total empty days across overlapping starts |
| Same-width 0.50/0.75/3.25/3.50 | 5 | 2023 episode; 47.23 empty days |
| Two endpoints 0.50/3.50 | 5 | 2023 episode; 48.09 empty days |
| Replace 0.50 with 0.75 in original | 4 | Startup books in 2020 and 2022; 20.18 total empty days |

The original mix remains the only one of all 50 tested portfolios without any
primary operating wipeout across all six starts. However, center4's 20-day
cluster never exceeds RR1's in the five 2021вЂ“2025 starts, whereas original wide4
is worse than RR1 in two. Continuity and clustered-loss severity are distinct
objectives; the original mix is not universally superior.

These contrasts rule out a simple explanation based only on range or group
count. They do not identify a universal optimal composition. Replacing 0.50
also shifts the mean and range; it is an ablation, not a pure width test.

## 2. Twenty groups does not mean one loss per portfolio signal

| Equal-weight RR grid | Starts with no empty-book episode | Primary same-signal peaks, 2020 / 2021 / 2022 / 2023 / 2024 / 2025 |
|---|---:|---|
| 2 groups | 5/6 | 7 / 6 / 5 / 3 / 2 / 1 |
| 4 groups, original wide | 6/6 | 3 / 4 / 3 / 4 / 2 / 1 |
| 5 groups | 5/6 | 3 / 3 / 2 / 2 / 2 / 1 |
| 10 groups | 4/6 | 3 / 4 / 1 / 2 / 1 / 1 |
| 20 groups | 4/6 | 4 / 3 / 2 / 2 / 2 / 2 |

Moving from ten to twenty groups increases the same-signal peak in four starts,
reduces it in one and ties in one. Its possible 20-day peak improves in two,
worsens in two and ties in two. There is no stable flattening point or monotonic
benefit in this grid. The fresh 2020 twenty-account isolation book loses six
different RR groups on one originating signal.

Twenty groups cap each group's size at one PA when twenty PAs are present;
they do not make the groups independent. In the operating model, evaluations
and spares share capacity, and the twenty-group 2023 book averages only 12.94
occupied groups on days with live accounts. Reversing initial assignment order
also changes operating results: from the 2022 start, the twenty-RR arm changes
from zero empty episodes to two, totaling 65.67 days. Both orders give identical
isolation outcomes. Startup composition and replacement supply matter.

## 3. Reserve ladders are a real alternative mechanism in the March replay

All following books enter March with twenty PAs. The historical stress policy
uses daily maximum withdrawals and a $5,700 mean reserve, with its original
evaluation pipeline. The ladders range from $4,200 to $7,200; the four-level
ladder uses $4,200/$5,200/$6,200/$7,200, and the twenty-level ladder is evenly
spaced. Figures below use MAE-first.

| Portfolio | March deaths | March-end survivors | Distinct recorded death dates | Largest same-signal loss |
|---|---:|---:|---:|---:|
| Uniform RR1, uniform $5,700 | 20 | 0 | 1 | 20 |
| Original four-RR mix | 5 | 15 | 1 | 5 |
| Ten-RR grid | 4 | 16 | 1 | 2 |
| Twenty-RR grid | 7 | 13 | 4 | 2 |
| RR1, four reserve levels | 10 | 10 | 2 | 5 |
| RR1, twenty reserve levels | 12 | 8 | 6 | 2 |
| RR1, uniform $7,200 | 0 | 20 | 0 | 0 |

The twenty-level ladder's deaths are March 19 (2), 20 (1), 23 (4), 24 (2),
26 (2) and 27 (1). These involve different originating signals, rather than
different reported exits of one common signal. Its maximum daily loss is four;
do not confuse that with its maximum same-signal loss of two.

**Uniform RR1 and both forward reserve ladders enter March with exactly the
same $76,068 of total positive account equity.** Thus the ladder's protection
in this comparison cannot be explained by simply having more total equity at
that snapshot. The uniform $7,200 control holds $106,068 and survives, so its
better outcome comes with $30,000 more retained capital. Equal mean targets
do not generally equalize realized capital across other dates or assignment
orders; all snapshots and cash outcomes remain in the evidence.

March cohort-loss and month-end-survivor counts in this table are unchanged
under MFE-first. Exact death dates and pre-event balances are more sensitive.
The reverse twenty-reserve arm, for example, has the same twelve losses and
eight survivors but five recorded death dates under MAE-first.

This establishes that RR diversification is not the only mechanism available.
It also exposes its trade-offs: low-reserve accounts die earlier, and twenty
levels lose more accounts than four levels despite spreading their dates more.

## 4. That reserve benefit does not transfer to the primary policy

Under daily minimum withdrawals and the $6,800 mean target, ladder4 and
ladder20 use targets from $5,300 to $8,300. Both reproduce RR1's wipeout counts
and empty duration in every primary start: eight episodes and 101.52 total
empty days across the six overlapping histories. The reversed twenty-level
ladder does too. Their forward 20-day clusters are worse than RR1 in three
starts and equal in the other three.

In the 2023 isolation test, uniform RR1 loses no accounts, while ladder4 loses
ten and ladder20 seven. The uniform low-reserve control loses all twenty and
the uniform high-reserve control loses none. Balance dispersion can therefore
be created by making part of the book weaker. It is an explanatory measurement,
not a safety objective by itself.

## What this changes

The original wide mix remains a useful continuity benchmark under the frozen
operating assumptions. There is no evidence to replace it automatically with
twenty different RRs. The reserve ladder deserves recognition as a genuine
timing-diversification mechanism for the March policy, but these tests do not
support adopting it to improve continuity under the chosen daily-minimum policy.
Neither finding establishes future performance or a universal optimum.

The 2020 stress start is separated in the full report. All start-date samples
overlap; exact intratrade death times remain unknown. Native entry identities
differ by up to fifteen missing and one extra signal relative to RR1. Five
low-RR tapes have one common negative-outcome amount difference; details are
retained in source_alignment_details.json. No missing outcome was fabricated.

## Evidence and reproduction

- [Full comparisons](rr_followup__REPORT.generated.md), including homogeneous constituents, cash and sensitivities.
- [Frozen protocol](../../../research/legacy_25k/RR_FOLLOWUP.md) and [configuration](../../../config/studies/legacy_25k_rr_followup.json).
- comparison.csv, constituent_comparisons.csv, march_deaths.csv and wipeout_events.csv.
- Per-case assignments, death records and snapshots in cases/; source hashes in contract.json.
- 130 prior controls reproduced; 42,311,067 trade copies checked for assignment, overlap and accounting. Payouts respect each account's own reserve.
- Four new behavioral tests cover reserve requests, replacement assignment, simultaneous losses and exact uniform-policy replay.
- independent_audit.json reconciles all 22,448 deaths and reconstructs assignments, within/across-group losses, rolling/interval clusters, wipeout duration and March cohorts. All twelve isolation assignment-order pairs match.

```powershell
.\venv\Scripts\python.exe scripts/study_rr_followup.py --workers 4
.\venv\Scripts\python.exe scripts/audit_rr_followup.py
.\venv\Scripts\python.exe scripts/summarize_rr_followup.py
```
