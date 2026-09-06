# Results index

Folder names show rulebook, withdrawal policy, retained balance, and closing action.
`terminal_request` is one firm-permitted request; `terminal_idealized` bypasses
payout restrictions for the closing profit withdrawal. `no_terminal` leaves
remaining account profit unwithdrawn. `retain_N` is nominal account balance,
not headroom above liquidation. Fixed monthly policies here accrue backlog.
All these runs buy one account monthly and use RR; sweep files identify their tape.

`full_rulebook` means the configured rulebook, with processing delay OFF.
`no_payout_rules` still enforces account drawdown mechanics.
`legacy_rules` enables only minimum balance and the historical safety net
(with its $100 encroachment allowance). Config IDs and sealed baselines retain their historical names. Each folder has
a `RUN.md` with its regeneration command.

| Result/report | Stable config path under config/ |
|---|---|
| [full_rulebook__monthly_500__no_cushion__no_terminal](full_rulebook__monthly_500__no_cushion__no_terminal/report.txt) | `scenarios/full_rulebook_monthly_500.json` |
| [full_rulebook__monthly_500__retain_30000__terminal_request](full_rulebook__monthly_500__retain_30000__terminal_request/report.txt) | `scenarios/monthly_500_cushion_liquidated.json` |
| [full_rulebook__monthly_maximum__no_cushion__no_terminal](full_rulebook__monthly_maximum__no_cushion__no_terminal/report.txt) | `scenarios/full_rulebook_monthly_maximum.json` |
| [full_rulebook__hold__terminal_request](full_rulebook__hold__terminal_request/report.txt) | `scenarios/hold_then_firm_permitted.json` |
| [no_payout_rules__hold__terminal_idealized](no_payout_rules__hold__terminal_idealized/report.txt) | `scenarios/hold_then_liquidate.json` |
| [no_payout_rules__hold__no_terminal](no_payout_rules__hold__no_terminal/report.txt) | `bricks/brick1_ideal_world.json` |
| [legacy_rules__monthly_100__no_cushion__no_terminal](legacy_rules__monthly_100__no_cushion__no_terminal/report.txt) | `bricks/brick2_monthly_100.json` |
| [no_payout_rules__monthly_500__retain_26100__no_terminal](no_payout_rules__monthly_500__retain_26100__no_terminal/report.txt) | `scenarios/no_rules_monthly_500_cushion.json` |
| [full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search](full_rulebook__monthly_500__no_cushion__no_terminal__adapted_search/report.txt) | `scenarios/full_rulebook_monthly_500.json` |

The `adapted_search` folder contains the same fixed-policy baseline plus the
cushion re-optimization experiment; its baseline cash is intentionally identical.
The other folders contain single-policy experiments and optional fixed ablations.

## Cushion searches

See `sweeps/`: filenames identify rulebook, tape, monthly withdrawal policy,
and whether the retained-balance grid is coarse or fine. These are historical
search outputs, not newly optimized policies. Terminal withdrawal is absent.

## Withdrawal amount x cushion study

[Compare monthly withdrawal policies and retained balances](study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/REPORT.md).
The study scores ongoing net cash and cash including one permitted terminal
request on each candidate's identical trading path. Account purchases remain
monthly. Every candidate also carries a trading-neutral flag and a ceiling
capture, both read against the hold benchmark's path. A withdrawal only lowers a
balance, so no candidate outlives that path, but it can out-earn it: trades an
early death avoids can be losing ones, and a capture above 100% would say so.
Neutrality is decided on a per-account fingerprint of the trades actually taken,
not on matching earnings totals, which two different paths can share.
`study.json` includes full provenance and `candidates.csv` contains
all tested settings. These are in-sample search results, not validated optima.

Reproduce: `venv/Scripts/python.exe scripts/study_withdrawal_amount.py`.
