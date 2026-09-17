# Fixed initial inventory: resources and exposure

All accounts are purchased before the first signal, at the first calendar boundary. **No later purchases or death replacements.** Initial K is fixed; live inventory may decline. Daily minimum withdrawal checks, retained balance, terminal withdrawal, contract size and all modeled rules are identical within each case. Retain $31,900 is the main policy; $30,000 and a fresh 2023 start are sensitivities.

Same resources compares 20 unrestricted accounts, 20 blocked copying accounts, and 20 routed accounts targeting R=4 throughout (max-headroom and round-robin). R is not reduced after deaths. Unrestricted accounts use the existing settlement-time model and ignore overlapping positions.

Same exposure freezes that reference model's realized copy count on every trade, then routes exactly those copies from a larger initial inventory. This is an ex-post counterfactual, not a live routing signal. It stops requesting trades when the reference model stops. Matching is verified per signal, not just in aggregate.

A separate **full_target** diagnostic requests 20 copies of every exported signal, including after the reference dies. Five overlapping setups imply 100 seats before deaths. We test this initial inventory and, if necessary, larger sizes in steps of 20. The first successful tested size is sufficient historically; it is not a global minimum unless it equals the weighted concurrency lower bound. It is also not matched realized reference exposure. Searches above 20 deliberately suspend the configured operating cap.

Initial fees are counted in ongoing and total net cash. Ongoing net excludes terminal receipts; total net includes them. No leftover nominal account balance is counted as cash. Account deaths follow per-trade extrema applied at exit; concurrent floating P&L is not aggregated in the unrestricted benchmark. Exported entry/exit intervals do not include pending-order reservation times. Same modeled copy exposure need not give the same booked P&L because failure truncation and commissions depend on account allocation.

## Start 2020; retained balance $31,900

### same_resources

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 20 | 20 | 7,520 | 2.97% | 0 | $-4,000.00 | $0.00 | $-4,000.00 |
| blocked_20 | 20 | 20 | 5,640 | 2.23% | 1,860 | $-4,000.00 | $0.00 | $-4,000.00 |
| routed_20_max_headroom | 20 | 12 | 49,168 | 97.11% | 1,464 | $104,000.00 | $6,891.16 | $110,891.16 |
| routed_20_round_robin | 20 | 8 | 50,392 | 99.53% | 240 | $84,000.00 | $37,938.52 | $121,938.52 |

### matched_reference

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_reference_60 | 60 | 0 | 7,520 | 2.97% | 0 | $-12,000.00 | $0.00 | $-12,000.00 |

### full_target

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_target_100 | 100 | 60 | 245,840 | 97.11% | 7,320 | $520,000.00 | $34,455.80 | $554,455.80 |
| full_target_140 | 140 | 40 | 253,160 | 100.00% | 0 | $542,000.00 | $34,447.80 | $576,447.80 |

- exact_reference_capacity: mechanical lower bound 60; first successful tested K 60; minimum proven: True.
- full_target_capacity: mechanical lower bound 100; first successful tested K 140; minimum proven: False.

## Start 2020; retained balance $30,000

### same_resources

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 20 | 20 | 7,520 | 2.97% | 0 | $-4,000.00 | $0.00 | $-4,000.00 |
| blocked_20 | 20 | 20 | 5,640 | 2.23% | 1,860 | $-4,000.00 | $0.00 | $-4,000.00 |
| routed_20_max_headroom | 20 | 16 | 48,848 | 96.48% | 1,784 | $118,000.00 | $0.00 | $118,000.00 |
| routed_20_round_robin | 20 | 12 | 50,292 | 99.33% | 340 | $108,000.00 | $0.00 | $108,000.00 |

### matched_reference

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_reference_60 | 60 | 0 | 7,520 | 2.97% | 0 | $-12,000.00 | $0.00 | $-12,000.00 |

### full_target

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_target_100 | 100 | 80 | 244,240 | 96.48% | 8,920 | $590,000.00 | $0.00 | $590,000.00 |
| full_target_180 | 180 | 60 | 253,160 | 100.00% | 0 | $574,000.00 | $0.00 | $574,000.00 |

- exact_reference_capacity: mechanical lower bound 60; first successful tested K 60; minimum proven: True.
- full_target_capacity: mechanical lower bound 100; first successful tested K 180; minimum proven: False.

## Start 2023; retained balance $31,900

### same_resources

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 20 | 0 | 138,640 | 100.00% | 0 | $406,000.00 | $102,679.00 | $508,679.00 |
| blocked_20 | 20 | 0 | 101,420 | 73.15% | 37,220 | $356,000.00 | $0.00 | $356,000.00 |
| routed_20_max_headroom | 20 | 0 | 27,728 | 100.00% | 0 | $68,000.00 | $0.00 | $68,000.00 |
| routed_20_round_robin | 20 | 8 | 27,616 | 99.60% | 112 | $44,000.00 | $24,284.96 | $68,284.96 |

### matched_reference

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_reference_100 | 100 | 0 | 138,640 | 100.00% | 0 | $340,000.00 | $0.00 | $340,000.00 |

### full_target

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_target_100 | 100 | 0 | 138,640 | 100.00% | 0 | $340,000.00 | $0.00 | $340,000.00 |

- exact_reference_capacity: mechanical lower bound 100; first successful tested K 100; minimum proven: True.
- full_target_capacity: mechanical lower bound 100; first successful tested K 100; minimum proven: True.

## Start 2023; retained balance $30,000

### same_resources

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unlimited_20 | 20 | 20 | 126,160 | 91.00% | 0 | $426,000.00 | $0.00 | $426,000.00 |
| blocked_20 | 20 | 20 | 92,460 | 66.69% | 33,940 | $366,000.00 | $0.00 | $366,000.00 |
| routed_20_max_headroom | 20 | 16 | 27,664 | 99.77% | 64 | $78,000.00 | $0.00 | $78,000.00 |
| routed_20_round_robin | 20 | 12 | 27,516 | 99.24% | 212 | $70,000.00 | $7,971.36 | $77,971.36 |

### matched_reference

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| matched_reference_100 | 100 | 0 | 126,160 | 91.00% | 0 | $350,000.00 | $0.00 | $350,000.00 |

### full_target

| Arm | Initial K | Deaths | Copies | Signals traded | Missed requested copies | Ongoing net | Terminal receipt | Total net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_target_100 | 100 | 80 | 138,320 | 99.77% | 320 | $390,000.00 | $0.00 | $390,000.00 |
| full_target_140 | 140 | 0 | 138,640 | 100.00% | 0 | $372,000.00 | $0.00 | $372,000.00 |

- exact_reference_capacity: mechanical lower bound 100; first successful tested K 100; minimum proven: True.
- full_target_capacity: mechanical lower bound 100; first successful tested K 140; minimum proven: False.

