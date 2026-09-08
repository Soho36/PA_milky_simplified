# Legacy 50K — preparation only

No verified product parameters, rulebook or simulation results exist here yet.
The [study profile](../../config/studies/legacy_50k.json) is explicitly blocked
from running. The [product template](../../config/products/legacy_50k.template.json)
and [rulebook template](../../config/firm/legacy_50k.template.json) contain no
borrowed 25K values.

Before enabling it:

1. Record dated authoritative product and payout-rule sources; verify the exact
   Legacy product, fees, threshold mechanics, payout limits and split.
2. Create runnable product/rulebook files and a scenario binding them to the tape.
3. Define study grids, withdrawal shortlist, budgets and unique output paths.
   Choose explicitly whether contract exposure is held constant or varied.
4. Test account/rule boundaries and reject unsupported mechanics rather than
   silently approximating them.
5. Run shared controls, then publish an overview and study guide here.

A changed rulebook alone does not require duplicating the engine. We will assess
any unsupported mechanics when the verified specification is available. EOD
accounts are deferred and have no configuration or scaffold in this change.
