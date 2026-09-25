"""Compare corresponding start dates without counting the two policies twice."""
from collections import defaultdict,Counter
import csv
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/legacy_25k/monthly_rr_pair_build'


def read(name):
    with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def main():
    rows=read('cases.csv');cases={r['case']:r for r in rows};groups=defaultdict(list)
    for a in read('accounts.csv'):groups[a['case']].append(a)
    matched=[]
    fields=('account_id','rr','activated_at','alive','died_at','death_trade_key','trades','trade_keys_sha256')
    for r in rows:
        if r['policy']!='minimum':continue
        other=cases[r['case'].replace('minimum','maximum')]
        same=[[a[k] for k in fields] for a in groups[r['case']]]==[[a[k] for k in fields] for a in groups[other['case']]]
        assert same
        matched.append(dict(start=r['start'],paths_identical=same,deaths=int(r['deaths']),
                            empty_episodes=int(r['empty_episodes']),empty_days=float(r['empty_days']),
                            purchased=int(r['purchased']),end_alive=int(r['end_alive']),
                            first20_at=r['first20_at'],minimum_net_cash=float(r['net_cash']),
                            maximum_net_cash=float(other['net_cash']),
                            extra_maximum_cash=round(float(other['net_cash'])-float(r['net_cash']),2)))
    episodes=[r for r in read('empty_episodes.csv') if r['case'].endswith('minimum')]
    checks=dict(starts=len(matched),identical_paths=sum(r['paths_identical'] for r in matched),
                maximum_cash_higher=sum(r['extra_maximum_cash']>0 for r in matched),
                maximum_cash_equal=sum(r['extra_maximum_cash']==0 for r in matched),
                maximum_cash_lower=sum(r['extra_maximum_cash']<0 for r in matched),
                mean_extra_maximum_cash=statistics.mean(r['extra_maximum_cash'] for r in matched),
                episode_counts_by_historical_peak=dict(Counter(int(r['historical_peak']) for r in episodes)))
    (OUT/'paired_comparison.json').write_text(json.dumps(dict(checks=checks,rows=matched,
            summarizer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            inputs_sha256={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ('cases.csv','accounts.csv','empty_episodes.csv')}),indent=2),encoding='utf-8')
    lines=['# Every monthly start: daily minimum versus maximum','',
           'Both policies retain $6,800 headroom. Purchases, accepted trades, death dates and account counts match exactly in each pair. '
           'Cash is ongoing receipts minus direct account fees, with no terminal payout. All starts end July 13, 2026; follow-up differs.','',
           '| Start | Bought | Deaths | Empty episodes | Empty days | End alive | First reached 20 | Minimum net cash | Maximum net cash |',
           '|---|---:|---:|---:|---:|---:|---|---:|---:|']
    for r in matched:
        lines.append(f"| {r['start'][:7]} | {r['purchased']} | {r['deaths']} | {r['empty_episodes']} | {r['empty_days']:.2f} | {r['end_alive']} | {r['first20_at'][:10] or 'not reached'} | ${r['minimum_net_cash']:,.2f} | ${r['maximum_net_cash']:,.2f} |")
    (OUT/'START_MONTHS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    text='''# Monthly RR pair build: findings

**Daily maximum extracted more cash without changing account mortality in
this experiment.** All 72 paired starts had identical account purchases,
accepted trades, death dates and death trades. Maximum paid more net cash in
70 starts and tied in two; it never paid less. This result is conditional on
the tested $6,800 withdrawal reserve, rulebook and historical paths, not a
general claim that larger payouts cannot increase risk.

| Through July 13, 2026 | Daily minimum | Daily maximum |
|---|---:|---:|
| Monthly starts | 72 | 72 |
| Mean account deaths per start | 23.46 | 23.46 |
| Starts with an empty-book episode | 31 | 31 |
| Empty episodes across starts | 42 | 42 |
| Mean days empty per start | 10.01 | 10.01 |
| Mean accounts alive at end | 15.94 | 15.94 |
| Starts reaching 20 live accounts | 39 | 39 |
| Mean ongoing net cash | $147,053 | $171,354 |

Maximum extracted an average $24,301 more. It did not improve survival;
it changed the timing and amount of cash extraction while the account paths
remained the same. Minimum leaves more profit retained in the accounts.

## Establishment is the vulnerable phase

Counting each start once, 38 of the 42 empty episodes happened before the
book had ever reached five live accounts. The remaining four happened after
a historical peak of exactly five. Twelve episodes occurred when the book
had never held more than one account.

An empty book restarts on the next month boundary because purchases are
externally funded. Empty episodes are therefore interruptions, not permanent
termination of the plan. The latest starts have less time to build inventory.

No book emptied after reaching six accounts in these paths. That observation
does **not** establish a safe six-account threshold: books reaching that size
are selected survivors and face different subsequent market histories.

All 36 starts in 2020–2022 eventually reached 20 and ended with 20. Only three
2023 starts reached 20; none of the 2024–2025 starts did before the endpoint.
Late starts have shorter follow-up; this is not a like-for-like year ranking.

## The first year needs external funding

For the 67 starts with twelve complete months:

| First twelve months | Daily minimum | Daily maximum |
|---|---:|---:|
| Mean deaths | 6.90 | 6.90 |
| Starts with an empty episode | 28 / 67 | 28 / 67 |
| Mean live accounts after twelve months | 5.10 | 5.10 |
| Mean net cash after purchase fees | -$1,303 | -$748 |

The $6,800 reserve is earned through trading. New PAs start with the original
$1,500 drawdown allowance, not an endowed $6,800 buffer. Many young accounts
die before accumulating that reserve or becoming eligible for a payout.
Long-history cash totals conceal this early financing requirement.

## What this supports

For this exact externally funded monthly-purchase plan, daily maximum at the
chosen reserve is the stronger historical cash-extraction policy, with no
observed penalty in deaths or downtime relative to daily minimum. Building
the book remains exposed to startup failures. The test does not establish
that the RR mixture is superior to a homogeneous RR book; that requires
matched constituent controls.

Both policies are subject to firm payout gates. Daily requests do not imply
daily approval. No evaluations, additional replacement purchases, terminal
liquidation or withdrawal-funded purchase restriction are included. Historical
starts overlap and are not independent trials or future probabilities.

All 144 cases passed independent checks covering 5,674 account entry paths,
6,765,432 accepted copies, 6,264 purchase boundaries and 474 checkpoint
ledgers. Three runs reproduced exactly; all 14 targeted tests passed.

- [Every start, policies side by side](START_MONTHS.md)
- [Full methods and yearly tables](monthly_rr_pair_build__REPORT.md)
- [Exact empty episodes](empty_episodes.csv)
- [Paired path and cash comparisons](paired_comparison.json)
- [Independent audit](audit.json)

Reproduce this readout: `venv/Scripts/python.exe scripts/summarize_monthly_rr_pair_build.py`.
'''
    (OUT/'FINDINGS.md').write_text(text,encoding='utf-8')
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
