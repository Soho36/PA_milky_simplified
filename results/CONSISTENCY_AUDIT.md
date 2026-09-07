# Saved-results consistency audit

This audit checks saved arithmetic, CSV/JSON agreement, current input hashes and identical candidate settings. It does not rerun every simulation or certify every sentence in reader-written notes.

## Checks

- economic identities: 544
- paired scores: 502
- csv rows: 502
- summary cash: 21
- matched candidates: 27

Failures: 0.

## Comparability

| Family | Acquisition / capacity | Funding | Status |
|---|---|---|---|
| [study__full_rulebook__RR__account_purchases__cash_budgets](study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.md) | Nine policies; 20 live maximum | Four explicit budgets | Internally comparable within each budget |
| [study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores](study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/REPORT.md) | One monthly; no live cap | Purchases not cash-constrained | Historical uncapped experiment |
| [study__full_rulebook__RR__withdrawal_cadence__monthly_purchases](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/REPORT.md) | One monthly; no live cap | Purchases not cash-constrained | Historical uncapped experiment |

The amount and cadence studies agree on their overlapping settings. The purchase study changes both capacity and funding, so its monthly rows are not controls for the earlier uncapped studies. Its withdrawal settings were selected from those uncapped searches; they are not established capped optima.

Other scenario results and cushion sweeps are historical experiments with deliberately different rulebooks, terminal treatments, policies and (for GG) tapes. They must not be ranked as one common-policy study. Older sweep JSON files do not embed complete configurations or input/engine hashes, so their exact provenance cannot be verified from the saved files alone.

## Required before a common 20-account comparison

Rerun amount/cushion and cadence candidates with a common live-account cap and an explicit funding convention; then reconsider the withdrawal shortlist used for purchase comparisons. Preserve the historical uncapped outputs. Do not simply set max_accounts=20: the legacy field limits monthly purchases, not simultaneous live accounts.

A binding live cap also changes the acquisition schedule when withdrawals change survival. Consequently, the existing fixed-cohort claim that hold bounds survival does not carry over automatically. A capped study must compare activation dates/trade identities and label its hold reference as a different portfolio when cohorts differ.

## Reader reports

REPORT.md and report_breakdown.txt are reader-maintained and are never overwritten by the three study runners. Reruns write REPORT.generated.md; on a new directory only, REPORT.md is also initialized. Reader notes remain tied to their original results until reviewed. In particular, the cadence breakdown describes the uncapped 22-survivor experiment.
