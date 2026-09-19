# Blocked copying with evaluation supply

This extends the [blocked-copying optimization](BLOCKED_OPTIMIZATION.md)
using the supply mechanics from the earlier
[pipeline-capacity study](../../results/comparisons/legacy_25k_vs_50k/pipeline_capacity/pipeline_capacity__FINDINGS.generated.md).
The primary budget stays at **$1,000 initially plus $200/month**.

**Result:** after 4,896 unique simulations, the best tested ongoing cash with
shared 20-seat supply is **$444,839**, using weekly minimum withdrawals and a
$26,900 retained balance. It funds 92 PAs and loses 87. Its pipeline allows
five concurrent evaluation subscriptions, batch starts and a ten-spare target,
with expiring monthly growth demand. The exact reserve is sensitive to the
historical path; $26,800 earns $349,477 and $27,000 earns $430,259 under the
same pipeline.

The old aggressive withdrawal policy earns $325,362.25 after optimizing its
shared-cap supply, versus $665,420.55 with instant supply. Retuning therefore
adds $119,476.75 of ongoing cash. The separate terminal-inclusive winner earns
$450,326.65, but $150,161.65 arrives only at closing. The ongoing winner gives
up just $5,487.65 of final total cash. Allowing evaluations outside the PA/spare
cap raises the retuned ongoing winner to $448,922 and the total winner to
$460,708.50.

All three historical headline controls reproduce. The existing 279 tests and
one new integration test pass. The independent audit reconciles 728,903 PA
assignments, all six detailed ledgers and the full declared search domain;
124 protected prior-result files are unchanged.

## Comparison

The primary product is Legacy25K. Funded accounts use one MNQ per accepted
setup and copy every signal while flat. Evaluations use the inherited
three-MNQ, one-position evaluation engine. No funded accounts are granted at
startup. Every PA requires a passed evaluation and paid activation.

The previous current-slot monthly-growth/replacement + maximum-weekly
withdrawal policy is a $665,420.55 instant-supply co-winner. Its retained
balance is $25,100. Carrying that withdrawal policy into evaluation supply
tests whether its account turnover remains economically useful when fresh
PAs take time to arrive.

The comparison changes procurement costs, initial inventory and lead time
together. It does not identify the isolated dollar cost of waiting. Persistent
growth-order demand is separately labeled because it also changes purchasing
behavior. The instant baseline starts one paid PA; the evaluation runs start
with none. No extra startup capital is supplied to compensate for that delay.

## Search protocol

- Four frozen withdrawal anchors: maximum weekly / $25,100; fixed $1,500
  monthly accrual with weekly checks / $25,100; minimum monthly / $27,900;
  minimum daily / $29,000. The latter two are former unrestricted-PA
  pipeline winners, transferred without retuning into the new budget.
- 192 pipeline combinations per anchor: 2/5/10/20 concurrent subscriptions;
  batch/daily/seven-day launch spacing; 0/2/5/10 desired spares; expiring or
  persistent monthly growth orders; shared or separate evaluation capacity.
- Main cap: live PAs + activated spares + in-flight evaluations <=20.
  Outside-cap sensitivity: live PAs + activated spares <=20, evaluations
  subject to their separate subscription limit.
- Both cash-objective leaders per concurrency and cap mode nominate
  pipelines. The original 5-evaluation/5-spare/batch/expiring/shared pipeline
  is always retained. Search minimum, maximum and fixed-$1,500 withdrawals
  across daily/weekly/monthly checks and the declared reserve grid on this
  union. Refine each withdrawal family by $100 within $400 of its coarse
  leader. The frozen screening settings remain eligible to win.
- Replay every frozen screen with unrestricted PA copying under identical
  supply. Replay final blocked winners with unrestricted copying too. These
  paired results isolate the PA allocation rule, though funding and subsequent
  procurement respond endogenously to its outcomes.
- Transfer the main shared-cap winners to other budgets and historical start
  dates without retuning. These overlap the selection tape and are not unseen
  out-of-sample evidence.

This is a staged best-tested search. It does not establish a global optimum
over all acquisition families, contract sizes, reserves, pipeline launch
phases, or dynamic policies. Evaluation renewals and activated spares are
charged, including inventory left unused at the end. Net cash excludes owner
contributions. Total cash includes one firm-permitted terminal withdrawal;
ongoing cash excludes it.

## Reproduce and inspect

Run from the project root with the project virtual environment:

```powershell
$env:PYTHONPATH='src'
.\venv\Scripts\python.exe scripts/study_blocked_pipeline.py
.\venv\Scripts\python.exe scripts/audit_blocked_pipeline.py
.\venv\Scripts\python.exe scripts/summarize_blocked_pipeline.py
```

The immutable contract hashes the profile, engine, inputs, runner, helpers
and historical control artifacts. Checkpoints resume only under the same
contract. Prior study files are preserved. The independent audit checks the
screen/search domains, winning scores, every exported cash event, evaluation
fees and paid activations, funded-seat provenance, seat limits, replacement
wait totals and all selected PA entry assignments.

[Generated report](../../results/legacy_25k/blocked_pipeline/blocked_pipeline__REPORT.generated.md),
[findings](../../results/legacy_25k/blocked_pipeline/blocked_pipeline__FINDINGS.generated.md),
[all settings](../../results/legacy_25k/blocked_pipeline/all_settings.csv),
[audit](../../results/legacy_25k/blocked_pipeline/AUDIT.generated.json).

The model inherits the reference study's evaluation rules and fees, rather
than verifying current firm terms. Passed evaluations may wait for activation;
activated spares have no modeled expiry or inactivity rule. Payout-processing
delay is disabled. Evaluations share the historical tape rather than receiving
independent pass-rate draws. Trade extrema settle at exported exits, and
pending-order reservation intervals are unavailable. These assumptions bound
what “realistic supply” means in this experiment.
