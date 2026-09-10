# Legacy 50K sources and study interpretation

Checked 2026-09-10. The existing 25K implementation came from the parent
project's supplied text, as explicitly documented in `src/pa_milky/firm.py`
and `tests/test_firm_rules.py`. Preserved copies and hashes:
[rule excerpt](../sources/parent_legacy/Payout_rules.txt),
[study contract](../sources/parent_legacy/25k_legacy_rules.txt),
[manifest](../sources/parent_legacy/manifest.json).
These local files do not establish when their web text was originally retrieved.

## Published Legacy parameters

[Apex Legacy payout parameters](https://apextraderfunding.com/help-center/legacy-payouts/legacy-pa-payout-parameters/)
specifies a $52,600 request gate, a $2,600 safety-net profit level for payouts
1-3 with $500 encroachment, a $500 minimum and $2,000 maximum for payouts 1-5.
Eligibility remains eight trading days including five $50-profit days.
Consistency is 30% through payout five. These thresholds do not all scale with DD.

That page's later-payout wording calls for the minimum balance to remain after
payout. Our inherited engine gates the balance before the request. A separately
labelled sensitivity applies a $52,600 retained floor from payout six (and
$26,600 for the 25K controls). The page also juxtaposes cumulative profit-split
wording with payout-count eligibility wording. Both products retain the
cumulative interpretation: first $25,000 paid at 100%, then 90%.

[Apex Legacy trailing drawdown](https://apextraderfunding.com/help-center/legacy-products/legacy-trailing-drawdown-rule/)
confirms $2,500 drawdown on 50K and a floor frozen at starting balance plus $100
once the peak reaches $52,600. The liquidation floor is $50,100, not $52,600.

## Explicit model choices

The user supplied the $250 50K seat fee in the product file; 25K uses $200.
Budgets are equal in dollars, not in affordable seat counts. Same tape, contracts,
commission, 20-live-account cap and no processing delay are retained. Tradability
through every historical purchase date is counterfactual. Evaluation costs,
contract-scaling enforcement, complete floating-equity aggregation and other
execution/compliance conditions remain outside this model. These reports must
not be labelled a complete implementation of current Apex requirements.

No 25K rule or result is overwritten. The strict later-payout sensitivity is an
optional parameter, off in the existing 25K configuration. It does not resolve
all textual ambiguities, and the main search is not re-optimized under that
sensitivity. Similar rule-effect rankings across sizes remain an untested hypothesis.
