"""Read-only comparison of the three saved amount/cushion studies."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/legacy_25k/rr_pair_overlap_monthly_amount_x_cushion'
PATHS = {
    'RR1 overlap': ROOT/'results/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/study.json',
    'Pair while flat': ROOT/'results/legacy_25k/rr_pair_monthly_amount_x_cushion/study.json',
    'Pair overlap': OUT/'study.json',
}


def main():
    studies = {name:json.loads(path.read_text(encoding='utf-8')) for name,path in PATHS.items()}
    assert studies['Pair overlap']['inputs'] == studies['Pair while flat']['inputs']
    by_key = {name:{(r['policy'],r['retained_balance_usd']):r for r in p['rows']}
              for name,p in studies.items()}
    common = set.intersection(*(set(rows) for rows in by_key.values()))
    fields = ('headroom_usd','ongoing_pocket_usd','terminal_received_usd','combined_pocket_usd',
              'alive_before_terminal','trading_neutral','booked_net_trading_usd')
    rows = []
    for policy, balance in sorted(common,key=lambda k:(k[0],-1 if k[1] is None else k[1])):
        for name, source in by_key.items():
            r = source[policy,balance]
            rows.append(dict(study=name,policy=policy,retained_balance_usd=balance,
                             **{f:r[f] for f in fields}))
    with (OUT/'matched_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        w = csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    provenance = dict(sources={n:dict(path=p.relative_to(ROOT).as_posix(),
                      sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for n,p in PATHS.items()},
                      common_policy_reserve_settings=len(common),
                      pair_input_digests_and_coverage_identical=True,
                      comparison_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'comparison.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
    text = '''# RR 0.50 / 2.50 with overlapping positions

Allowing overlap materially changes the mixture's result. Its best tested
headroom increases from **$4,500 to $6,100**, while best combined cash falls
from **$495,589 to $443,582** (10.5% lower). The large reserve reduction seen
in the while-flat run does not carry over to overlapping execution.

The new run tests 262 settings including hold. Both cash objectives select
**$1,500 monthly backlog or maximum excess monthly**, tied at a retained
balance of **$31,200** ($6,100 above the frozen $25,100 floor). Ongoing net
cash is $367,282 and the final permitted receipt is $76,300. There are 21
survivors from 79 purchases. These winners preserve the hold trading path;
the other 58 accounts also die without withdrawals.

## Compare the same policy family

For maximum excess monthly, choose each study's best combined-cash setting:

| Study | Retained balance | Headroom | Ongoing net cash | Including terminal | Survivors | Hold path preserved |
|---|---:|---:|---:|---:|---:|:-:|
'''
    for name,p in studies.items():
        r = max((r for r in p['rows'] if r['policy']=='maximum_excess_monthly'),key=lambda r:r['combined_pocket_usd'])
        text += f"| {name} | ${r['retained_balance_usd']:,.0f} | ${r['headroom_usd']:,.0f} | ${r['ongoing_pocket_usd']:,.0f} | ${r['combined_pocket_usd']:,.0f} | {r['alive_before_terminal']} | {'yes' if r['trading_neutral'] else 'no'} |\n"
    text += '''
On this matched policy-family comparison, the overlapping pair's selected
reserve is only $400 below RR1's, rather than the $2,000 difference between
RR1 overlap and the pair while flat. These are local, in-sample optima, not
minimum reserves guaranteed to work in future. Without an RR1 while-flat
arm, this is not a complete strategy-by-execution interaction experiment.

## Compare identical policy and reserve settings

Maximum excess monthly at common tested balances:

| Retained balance | Study | Ongoing net cash | Including terminal | Survivors | Hold path preserved |
|---:|---|---:|---:|---:|:-:|
'''
    for balance in (29600,31100,31600):
        for name,source in by_key.items():
            r = source['maximum_excess_monthly',balance]
            text += f"| ${balance:,.0f} | {name} | ${r['ongoing_pocket_usd']:,.0f} | ${r['combined_pocket_usd']:,.0f} | {r['alive_before_terminal']} | {'yes' if r['trading_neutral'] else 'no'} |\n"
    text += f'''
All **{len(common)} common policy/reserve settings**, including hold, are retained in
[matched_comparison.csv](matched_comparison.csv). Each study's local refinement
also samples different extra points, so comparisons use the intersection of
tested settings, without interpolation.

## The hold controls explain part of the difference

| Study | Net booked trading earnings | Survivors without withdrawals |
|---|---:|---:|
'''
    for name,p in studies.items():
        r = next(r for r in p['rows'] if r['stage']=='benchmark')
        text += f"| {name} | ${r['booked_net_trading_usd']:,.0f} | {r['alive_before_terminal']} |\n"
    text += '''
The pair while flat ends with six more hold survivors than the overlapping
pair and more booked earnings. Thus the execution change affects the trading
paths before withdrawal policies are considered. Different r/r targets also
change holding times and concurrent exposure; this comparison does not
normalize that exposure or isolate a pure diversification effect.

Across all policy families, the original RR1 study's best combined cash is
$460,512 (minimum monthly at $30,000), versus $443,582 for the overlapping
pair. Those selected portfolios use different payout policies. The mixture
does not dominate the original study on cash extraction.

## Reserve sensitivity remains important

For the new leading policy, $31,100 produces $399,956 combined cash and 20
survivors; $31,200 produces $443,582 and 21 survivors. A $100 reserve change
preserves one account with substantial subsequent earnings. At $31,600,
21 survive and combined cash is $436,061, about 1.7% below the peak. This
does not establish $31,200 as a robust operating threshold.

## Scope and validation

Both mixture studies use the same inputs, dates, alternating monthly account
assignments (40 at 0.50, 39 at 2.50), fresh account states, commissions and
payout rules. Purchases remain uncapped and externally financed, with no
extra replacements. The surviving overlap winner contains 14 at 0.50 and
7 at 2.50; equal purchases do not maintain equal surviving allocations.

Overlap matches the original model: whole-trade MAE/MFE and P/L are applied
in exit order. It is not a reconstruction of combined open-position equity.
Later settlements are ignored once an account dies, even if those trades
were already open. One MNQ per trade can mean several concurrent contracts
per account. Results must be read within that historical model.

All 262 financial identities reconcile, with 31,382,198 booked-copy checks.
Hold and both leaders reproduce; an independent settlement selector checked
237 account paths and 432,984 booked copies. The original RR1 hold and both
leaders reproduce exactly, and the adapter matches the unchanged legacy
engine for those controls. All 14 targeted tests passed. Shared engine code
and earlier results were preserved.

- [Full overlap report](rr_pair_overlap_monthly_amount_x_cushion__REPORT.md)
- [All new candidates](candidates.csv)
- [Independent audit](audit.json)
- [Comparison input hashes](comparison.json)
- [Study design](../../../research/legacy_25k/RR_PAIR_OVERLAP_WITHDRAWAL_AMOUNT.md)

Rebuild this comparison with `venv/Scripts/python.exe scripts/compare_rr_pair_withdrawal_amount.py`.
'''
    (OUT/'FINDINGS.md').write_text(text,encoding='utf-8')
    print(json.dumps(provenance,indent=2))


if __name__ == '__main__':
    main()
