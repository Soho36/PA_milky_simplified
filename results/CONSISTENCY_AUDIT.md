# Saved-results consistency audit

This audit checks saved arithmetic, CSV/JSON agreement, current input hashes and identical candidate settings. It does not rerun every simulation or certify every sentence in reader-written notes.

## Checks

- economic identities: 988
- paired scores: 946
- csv rows: 946
- summary cash: 21
- matched candidates: 27
- funded shared controls: 12
- replacement shared controls: 24

Failures: 0.

## Comparability

| Family | Acquisition / capacity | Funding | Status |
|---|---|---|---|
| [study__full_rulebook__RR__account_purchases__cash_budgets](study__full_rulebook__RR__account_purchases__cash_budgets/REPORT.generated.md) | 11 policies; 20 live maximum | Four explicit budgets | Internally comparable within each budget |
| [study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores](study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/REPORT.md) | One monthly; no live cap | Purchases not cash-constrained | Historical uncapped experiment |
| [study__full_rulebook__RR__monthly_replacements__cap_20__cash_budgets](study__full_rulebook__RR__monthly_replacements__cap_20__cash_budgets/REPORT.generated.md) | 4 policies; 20 live maximum | Four explicit budgets | Internally comparable within each budget |
| [study__full_rulebook__RR__withdrawal_cadence__monthly_purchases](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases/REPORT.md) | One monthly; no live cap | Purchases not cash-constrained | Historical uncapped experiment |
| [study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets](study__full_rulebook__RR__withdrawal_cadence__monthly_purchases__cap_20__cash_budgets/REPORT.generated.md) | One monthly; 20 live maximum | Four explicit budgets | Internally comparable within each budget |

The amount and cadence studies agree on their overlapping settings. The purchase study changes both capacity and funding, so its monthly rows are not controls for the earlier uncapped studies. Its withdrawal settings were selected from those uncapped searches; they are not established capped optima.

Other scenario results and cushion sweeps are historical experiments with deliberately different rulebooks, terminal treatments, policies and (for GG) tapes. They must not be ranked as one common-policy study. Older sweep JSON files do not embed complete configurations or input/engine hashes, so their exact provenance cannot be verified from the saved files alone.

## Common 20-account comparison

The budget-matched cadence study adds 372 capped candidates and 12 explicit shared controls against the purchase study. Earlier amount/cushion and cadence results remain historical uncapped experiments answering their original questions. No wholesale rerun is required. The purchase shortlist is not automatically optimal over the wider capped cadence grid.

A binding live cap also changes the acquisition schedule when withdrawals change survival. Consequently, the existing fixed-cohort claim that hold bounds survival does not carry over automatically. A capped study must compare activation dates/trade identities and label its hold reference as a different portfolio when cohorts differ.

## Reader reports

REPORT.md and report_breakdown.txt are reader-maintained and are never overwritten by the study runners. Reruns write REPORT.generated.md; on a new directory only, REPORT.md is also initialized. Reader notes remain tied to their original results until reviewed. In particular, the cadence breakdown describes the uncapped 22-survivor experiment.
