# Additional MT5 experiment: no take-profit, session-close exit

Status: run brief prepared; no EA source, tester settings or session-close
exports were found in this repository. No MT5 run has been launched here.
The closing boundary still needs clarification: the existing per-window
forced close, or the final close of the trading day. The repository's modelled
01:00-23:59 session is descriptive and is not evidence of the EA's close rule.

## Experimental change

Disable the take-profit target explicitly if the EA supports it. Keep the
original protective stop-loss and its sizing. A surviving position exits at
the agreed session-close time; one that hits its stop exits earlier. This is
not a rule that holds losing positions regardless of their stop.

If disabling TP is impossible, use a sufficiently distant finite TP only as
an approximation and export evidence that no trade hits that TP anywhere in
the run. A large numeric RR alone does not establish equivalence. Do not
assume a value of zero disables TP unless the EA documents that behavior.

Keep instrument, historical interval, tick model, timezone/DST treatment,
entry rules, source window definitions, stop construction, position sizing,
cost assumptions and signal export behavior identical to the corrected RR
sweeps. Retain RR1.00 as a control export from the same tester setup to detect
unintended changes. Use ample starting balance to complete the entire history
without tester account failure; preserve fixed sizing rather than scaling
lots with that larger balance.

Run all 23 source windows (1-2 through 23-24) over the same historical interval
as the corrected sweeps. GG exports are not needed for this study. Longer
holding changes which later entries a single account can accept: retain
native entry/exit timestamps so the existing while-flat routing can make
that decision. Do not reuse finite-RR accepted trades with altered exit P&L.

## Deliverables and checks

Store this as a separate experimental arm, `session_close_no_tp`; do not
overwrite or relabel a finite-RR sweep. Save the tester configuration, EA
version/hash, tester log, requested history range, actual end-of-test status,
and exact closing rule with timezone and DST handling.

Preserve the existing trade-export content for every source window:
ticket, entry_time, exit_time, MAE, MFE, P&L and candle_range, with the same
units and timestamp format. Save corresponding statistics. Keep additional
exit-reason diagnostics in a separate file so the existing seven-column
schema is not silently changed. The current numeric-RR loader will need an
explicit adapter for this named arm after the export format is confirmed.

For each trade, export its exit reason (stop, session close, tester end or
other); if possible include the stop level and scheduled closing timestamp.
Check that winning trades without stops close at the intended boundary and
that trades hitting stops still close earlier. Investigate any other exit.
Distinguish final tester liquidation from the scheduled session-close rule.

Reconcile trade counts and P&L with statistics, check common signal/stop
construction against RR1.00, and verify coverage separately for every window.
The existing last-exit pins are a useful first check, but the tester log must
also demonstrate completion: a different exit rule can legitimately change
the last traded date. Do not weaken coverage pins to accept an incomplete run.

## Later comparison

After validation, add the new arm alone and paired with RR0.50, RR0.75 and
RR1.00 at 25/50/75% lower-RR allocation, retaining homogeneous controls.
Use the same common starts, normalized exposure and separate first-breach
markers as RR_PAIRS.md. Recompute native accepted trades; a later exit can
block an entry that a finite-RR arm would accept. Do not infer missing paths
from finite-RR MAE/MFE.
