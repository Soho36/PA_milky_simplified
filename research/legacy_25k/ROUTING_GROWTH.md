# Monthly growth: routing versus copying on the same budget

This comparison matches the operating policy and resources while allowing
routed exposure to grow with the account pool. It replaces the earlier
comparison of a fixed-R pool with a growing non-routing book.

The main result is that **non-routing copying still produces more total cash
in most tested cases, but it also takes substantially more trade copies**.
Routing captures more distinct signals and, in the main example, requires
many fewer replacement accounts. Neither approach wins on every measure.

[Full tables](../../results/legacy_25k/routing_funded_growth/REPORT.generated.md),
[comparison CSV](../../results/legacy_25k/routing_funded_growth/comparison.csv),
[independent audit](../../results/legacy_25k/routing_funded_growth/AUDIT.generated.json).

## Matched operating rules

Each case uses the same starting five paid accounts, initial owner cash and
monthly contributions, 20-live-account cap, and withdrawal settings in all arms.
The initial five replace the first ordinary monthly purchase. Starting in the
next month, the book tries to add one account each month and replace deaths
at daily checks. Replacements are separate from the monthly growth purchase.

Every purchase must be affordable from contributed cash and actual payout
receipts. There is no automatic additional funding and no entry-time rescue
purchase. An unaffordable monthly growth purchase is skipped; an unfilled
replacement remains pending. Outcomes therefore determine subsequent purchases:
the rules and funding match, but the realized purchase dates/counts need not.

All arms check for the minimum withdrawal daily. Retained balance is held
fixed within a case, at either $30,000 or $31,900. No policy is re-optimized.
Initial funding is $1,000 or $5,000, with $0 or $200/month; fresh starts are 2020
and 2023. There are 16 cases with four arms each.

| Arm | What happens to a setup |
|---|---|
| Unlimited reference | Every eligible account takes it, including overlapping trades. This preserves the existing idealized model as a benchmark. |
| Blocked copying | Every live account attempts to take it, but each must be flat. There is no reservation of capacity to distribute copies across later signals. |
| Adaptive max-headroom | Route R copies to free accounts with the most drawdown headroom. |
| Adaptive round-robin | Route the same R target by rotating through free accounts. |

For the routed arms, R is recalculated before every new entry:

| Live accounts K | New-trade copies R = floor(K/5) |
|---:|---:|
| 0–4 | 0 |
| 5–9 | 1 |
| 10–14 | 2 |
| 15–19 | 3 |
| 20 | 4 |

K includes busy accounts; only free accounts can receive the new trade. R rises
after growth and falls after deaths. Existing trades are unchanged. Accounts
between the thresholds are spare capacity. R=0 pauses new routed trading below
five, rather than assuming full coverage with insufficient inventory. Such
pauses are explicitly counted, separately from blocked requested copies.

## Main comparison

2020 start, five initial accounts, $5,000 owner cash initially plus $200/month,
monthly growth plus funded replacements, daily minimum withdrawal with a
$31,900 retained balance. All figures cover the full remaining dataset and
subtract account fees; total includes one firm-permitted terminal request.

| Arm | Copies taken | Distinct signals traded | Accounts bought / deaths | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|
| Unlimited reference | 206,943 | 99.97% | 76 / 56 | $524,300 | $99,514.56 | $623,814.56 |
| Blocked copying | 143,152 | 73.50% | 77 / 57 | $359,100 | $0 | $359,100 |
| Adaptive max-headroom | 45,921 | 100% | 28 / 8 | $94,400 | $5,306.52 | $99,706.52 |
| Adaptive round-robin | 45,854 | 100% | 54 / 34 | $29,200 | $45,571.97 | $74,771.97 |

All four finish with 20 live accounts. Max-headroom reaches 10 seats in June
2020, 15 in November 2020 and 20 in April 2021, so R rises from one to four.
Its lower total is not explained by leaving R fixed at one.

The copying model takes about 3.12 times as many copies as max-headroom routing
in this example. At the 20-account limit, copying can take 20 copies of an
accepted setup, while the conservative full-coverage routed target is four.
Copying concentrates exposure on fewer distinct setups; routing reserves enough
capacity to spread exposure across overlapping setups. Equal account resources
cannot simultaneously imply equal trade exposure under these policies.

With the same example's retained balance reduced to $30,000, total net is
$612,150 for unlimited, $387,400 for blocked copying, $108,400 for max-headroom
and $98,492.26 for round-robin. That is a separate fixed-reserve comparison,
not evidence of a universal optimal reserve.

## Across the tested cases

Blocked copying and the unlimited reference each beat max-headroom on total
net cash in 14 of 16 cases. Max-headroom beats both in the two 2020-start cases
with only $1,000 and no monthly contributions. In those two cases the copying
books lose the initial $1,000 and die; max-headroom ends at $500 total net after
the terminal request, but spends much of the period paused below five seats.
That is a materially different survival/cash path, not continuous full coverage.

Both adaptive arms filled every requested copy in all cases. This does **not**
mean all exported signals were traded in every case: zero-target periods are
excluded from requested-copy coverage. `signals_without_target` and
`signal_participation` make those pauses visible. The representative well-funded
case above has no such pauses and trades all signals.

The question answered is: **given identical owner funding and purchase/withdrawal
rules, how much cash and exposure does each execution policy produce?** It is
not a comparison at equal market exposure. Dividing profits by copy count would
not repair that difference because account failure, reserves and payout
thresholds are nonlinear.

The observed cash advantage also does not establish that copying is preferable
at equal risk. Concurrent floating P&L is still approximated in the unlimited
benchmark. Even the one-position arms only carry exported trade extrema, so
the study does not establish accurately synchronized intratrade portfolio
drawdown. Mortality, funding constraints, signal participation and copy volume
are reported alongside cash instead of equating more dollars with lower risk.

## Scope and next question

This is closer to the proposed operating comparison than `routing_fixed_pool`:
R now grows, monthly acquisitions are shared, and replacements must be funded.
It still assumes a purchased PA can activate at the daily decision immediately;
Evaluation lead time, processing delays where disabled in the inherited
rulebook, working entry-order reservations and live execution differences are
not newly modeled. The 2023 start is a sensitivity check, not independent
out-of-sample policy selection.

The remaining strategy choice is how strongly to prioritize full signal
coverage over copies per accepted setup. R=floor(K/5) deliberately uses a
conservative historical capacity rule. A higher R could increase exposure but
accept blocking. That would be a separate exposure/coverage policy comparison;
it has not been optimized in these results.

The common five-account start is new to this experiment. Do not splice these
columns into older one-account-start or unlimited-funding tables.

## Reproduce

```powershell
$env:PYTHONPATH = 'src'
.\venv\Scripts\python.exe scripts/study_routing_growth.py
.\venv\Scripts\python.exe scripts/audit_routing_growth.py
.\venv\Scripts\python.exe -m unittest discover -s tests -t .
```

The [profile](../../config/studies/legacy_25k_routing_growth.json) pins the design.
The audit independently verified matched contribution schedules, nonnegative
cash, purchases charged at daily checks, the live cap, entry-time dynamic R,
zero entry-time rescue buys, one-position occupancy in all executable arms,
and cash reconciliation across 4,216,572 trade copies.
