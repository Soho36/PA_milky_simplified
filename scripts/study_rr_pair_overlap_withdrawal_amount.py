"""Monthly amount x cushion study for a fixed, alternating RR 0.50/2.50 book.

Uses the original policy grid, economics and terminal rules. Accounts accept
every eligible signal of their own variant, allowing overlap. Assignment is fixed by purchase index,
so withdrawal-induced deaths cannot alter later accounts' trading variants.
"""
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from functools import partial
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from pa_milky.account import money
from pa_milky.config import load_config, to_payload
from pa_milky.economics import Economics
from pa_milky.loader import load_trades
from pa_milky.policy import WithdrawalPolicy
from pa_milky.policy_study import annotate_against_benchmark, path_ceiling
from pa_milky.provenance import (engine_digest, git_revision, input_digest,
                                  sha256_file, tape_coverage)
from pa_milky.report import write_outputs
from pa_milky.routing import RoutingPolicy
from pa_milky.rr_diversification import RRRouter
from pa_milky.simulator import run_book
from rr_overlap_support import run_overlap_book
from pa_milky.study_config import load_study_profile, study_policies, profile_provenance
from report_names import write_study_report
import study_withdrawal_amount as original

OUT = ROOT / 'results/legacy_25k/rr_pair_overlap_monthly_amount_x_cushion'
PROFILE = ROOT / 'config/studies/legacy_25k.json'
CONFIG = TAPES = TRADES = TRADE_RR = None
ORDER = ('0.50', '2.50')


def initialize(order=ORDER):
    global CONFIG, TAPES, TRADES, TRADE_RR, ORDER
    ORDER = tuple(order)
    base = load_config(ROOT / 'config/scenarios/full_rulebook_monthly_500.json')
    CONFIG = replace(base, risk_reward='0.50/2.50', expected_trades=None,
                     scenario='rr_pair_overlap_monthly_amount_x_cushion',
                     brick_name='rr_pair_overlap_monthly_amount_x_cushion')
    if CONFIG.rulebook.processing_delay_days or CONFIG.max_accounts is not None:
        raise ValueError('Study requires zero processing delay and uncapped monthly purchases')
    TAPES = {rr: load_trades(CONFIG.sweeps_root, strategy='RR', risk_reward=rr) for rr in ORDER}
    TRADES = sorted([t for tape in TAPES.values() for t in tape],
                    key=lambda t: (t.exit_at, t.entry_at, t.window_order,
                                   t.source_row, t.ticket, t.trade_key))
    TRADE_RR = {t.trade_key: rr for rr, tape in TAPES.items() for t in tape}
    if len(TRADE_RR) != len(TRADES):
        raise ValueError('Variant trade keys are not distinct')


def simulate(policy, cushion):
    p = replace(policy, min_retained_balance_usd=cushion, terminal_withdrawal='firm_permitted')
    return run_overlap_book(TRADES, replace(CONFIG, policy=p), order=ORDER, trade_rr=TRADE_RR)


def audit_result(result):
    """Audit each accepted copy, including actual settled trade identities and activation."""
    accounts = {a.account_id: a for a in result.accounts}
    assigned = result.routing['account_rr']
    keys = {i: [] for i in accounts}
    for fill in result.routing_fills:
        entry = datetime.fromisoformat(fill['entry_at'])
        for i in fill['accounts']:
            assert assigned[i] == TRADE_RR[fill['trade_key']]
            assert assigned[i] == ORDER[(i-1) % len(ORDER)]
            assert accounts[i].activated_at <= entry
            keys[i].append(fill['trade_key'])
    for i, a in accounts.items():
        assert len(keys[i]) == a.trades_taken
        assert a.alive or keys[i][-1] == a.death_trade_key
    assert sum(map(len, keys.values())) == result.copies_filled
    return keys


def score(result, cushion, stage):
    economics = Economics.measure(result)
    assert economics.residual_usd == 0
    keys = audit_result(result)
    terminal = money(sum(e.received_usd for e in result.terminal_payouts))
    p = result.config.policy
    material = [(a.account_id, result.routing['account_rr'][a.account_id],
                 keys[a.account_id], a.death_trade_key) for a in result.accounts]
    ceiling = path_ceiling(economics)
    return dict(policy=p.name, retained_balance_usd=cushion,
                headroom_usd=None if cushion is None else money(cushion-CONFIG.trailing_floor_balance_usd),
                ongoing_pocket_usd=money(result.pocket_usd-terminal),
                terminal_received_usd=terminal, combined_pocket_usd=result.pocket_usd,
                alive_before_terminal=result.alive_at_horizon,
                ongoing_payouts=len(result.payouts)-len(result.terminal_payouts),
                terminal_payouts=len(result.terminal_payouts),
                profit_before_terminal_usd=result.equity_at_horizon_usd,
                profit_after_terminal_usd=economics.retained_profit_usd,
                booked_net_trading_usd=economics.booked_net_trading_usd,
                firm_split_usd=economics.firm_split_usd, path_ceiling_usd=ceiling,
                unextracted_usd=money(ceiling-result.pocket_usd),
                path_fingerprint=hashlib.sha256(json.dumps(material).encode()).hexdigest(),
                economics=economics.to_payload(), policy_config=p.to_payload(), stage=stage,
                copies_checked=result.copies_filled,
                alive_rr050=sum(a.alive and result.routing['account_rr'][a.account_id]=='0.50' for a in result.accounts),
                alive_rr250=sum(a.alive and result.routing['account_rr'][a.account_id]=='2.50' for a in result.accounts))


def work(job):
    policy, level, stage = job
    return score(simulate(policy, level), level, stage)


def write_csv(path, rows):
    fields = [k for k in rows[0] if k not in ('economics', 'policy_config')]
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k:r[k] for k in fields} for r in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('workers must be positive')
    study = load_study_profile(PROFILE)
    initialize()
    original.CONFIG = CONFIG
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    floor = CONFIG.trailing_floor_balance_usd
    levels = [None] + [floor+x for x in study['amount']['headroom_grid']]
    choices = study_policies(study)
    jobs = [(p, level, 'coarse') for p in choices for level in levels]
    jobs.append((WithdrawalPolicy(name='hold'), None, 'benchmark'))
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize) as pool:
        for i, row in enumerate(pool.map(work, jobs), 1):
            rows.append(row)
            if i % 20 == 0 or i == len(jobs):
                print(f'Coarse: {i}/{len(jobs)}', flush=True)
        seen = {(r['policy'], r['retained_balance_usd']) for r in rows}
        refined = []
        for p in choices:
            family = [r for r in rows if r['policy']==p.name]
            for metric in ('ongoing_pocket_usd', 'combined_pocket_usd'):
                center = max(family, key=lambda r:r[metric])['retained_balance_usd']
                if center is None:
                    continue
                for offset in range(-study['amount']['refinement_radius'],
                                    study['amount']['refinement_radius']+1,
                                    study['amount']['refinement_step']):
                    level = center+offset
                    key = (p.name, level)
                    if level >= floor and key not in seen:
                        seen.add(key)
                        refined.append((p, level, 'local_refinement'))
        for i, row in enumerate(pool.map(work, refined), 1):
            rows.append(row)
            if i % 20 == 0 or i == len(refined):
                print(f'Refinement: {i}/{len(refined)}', flush=True)
    benchmark = next(r for r in rows if r['stage']=='benchmark')
    annotate_against_benchmark(rows, benchmark)
    rows.sort(key=lambda r:(r['policy'], -1 if r['retained_balance_usd'] is None else r['retained_balance_usd']))
    winners = {metric: sorted([max([r for r in rows if r['policy']==p.name], key=lambda r:r[metric])
                               for p in choices], key=lambda r:r[metric], reverse=True)
               for metric in ('ongoing_pocket_usd', 'combined_pocket_usd')}
    payload = dict(schema='pa_milky.rr_pair_amount_cushion.v1',
                   generated_utc=datetime.now(timezone.utc).isoformat(),
                   study_profile=profile_provenance(study), config=to_payload(CONFIG),
                   engine=engine_digest(), git_revision=git_revision(),
                   scripts={p.name:sha256_file(p) for p in (Path(__file__), ROOT/'scripts/study_withdrawal_amount.py', ROOT/'scripts/report_names.py', ROOT/'scripts/rr_overlap_support.py')},
                   inputs={rr:dict(digest=input_digest(replace(CONFIG, risk_reward=rr)),
                                   coverage=tape_coverage(tape)) for rr,tape in TAPES.items()},
                   coverage_pin_sha256=sha256_file(ROOT/'config/tape_coverage.json'),
                   design=dict(assignment='alternate monthly purchase index; fixed for life', order=ORDER,
                               target='50/50 purchases; live allocation may drift',
                               execution='unlimited overlapping own-variant trades; legacy per-trade settlement; one MNQ per trade',
                               acquisition='one funded PA monthly, uncapped, externally financed, no extra replacements',
                               coarse_retained_balances=levels,
                               refinement_radius=study['amount']['refinement_radius'],
                               refinement_step=study['amount']['refinement_step'],
                               terminal='one firm-permitted request; voluntary cushion released',
                               neutrality='exact per-account accepted trade keys and killing trade',
                               selection='in-sample local search'), rows=rows)
    (out/'study.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    write_csv(out/'candidates.csv', rows)
    for metric, label in (('ongoing_pocket_usd','best_ongoing'), ('combined_pocket_usd','best_terminal')):
        best = max(rows, key=lambda r:r[metric])
        result = simulate(WithdrawalPolicy.from_payload(best['policy_config']), best['retained_balance_usd'])
        assert score(result, best['retained_balance_usd'], best['stage'])['path_fingerprint'] == best['path_fingerprint']
        assert result.pocket_usd == best['combined_pocket_usd']
        write_outputs(result, out/label)
        assignments = [dict(account_id=a.account_id, rr=result.routing['account_rr'][a.account_id],
                            activated_at=a.activated_at.isoformat(), alive=a.alive,
                            died_at=a.died_at.isoformat() if a.died_at else '') for a in result.accounts]
        write_csv(out/label/'assignments.csv', assignments)
    report = '# RR 0.50 / RR 2.50 with overlap: monthly withdrawal amount x cushion\n\n'
    report += (f'{len(rows)} candidates including hold. Same eight payout families, coarse grid and local refinement as the original study. '
               'Full historical payout rulebook, processing delay off, one MNQ per trade, $200 purchase fee.\n\n'
               '**Allocation:** new monthly purchases alternate 0.50, 2.50, starting with 0.50. Each account keeps its variant for life. '
               'The 50/50 target applies to purchases, not surviving accounts; deaths can skew the live allocation. '
               'The schedule is fixed across policies so withdrawals cannot change future variant assignments.\n\n'
               '**Execution:** each account takes every eligible signal from its assigned variant, allowing unlimited overlapping positions. '
               'This reproduces the original whole-trade MAE/MFE/P&L settlement at exit, without aggregate open-position mark-to-market. A death stops subsequent settlements, including trades already open. '
               'The same uncapped, externally financed monthly purchases are retained: no 20-seat cap, evaluation queue, funding budget or additional replacements. '
               'This is a policy sweep, not the fully built 20-seat experiment.\n\n')
    report += original.ceiling_section(rows, benchmark).replace('per-account fingerprint of trade counts, booked results and killing trade', 'per-account fingerprint of exact booked trade keys, assignment and killing trade')
    report += ('\nThe neutrality check here hashes every accepted trade key per account, including assignment and killing trade. '
               'The ceiling is a fixed no-withdrawal reference, not an achievable payout policy.\n')
    report += '\n## Best tested cushion per policy: ongoing cash\n\n'+original.table(winners['ongoing_pocket_usd'])
    report += '\n\n## Best tested cushion per policy: including terminal request\n\n'+original.table(winners['combined_pocket_usd'])
    report += '\n\n## Hold reference\n\n'+original.table([benchmark])
    report += ('\n\nRetained balance = $25,100 frozen floor + headroom. Initial accounts still start at $25,000 with $1,500 trailing drawdown; '
               'a retained-balance setting is a withdrawal threshold, not starting capital. '
               'Minimum monthly asks $500 without backlog. Fixed targets accrue backlog; legacy rounds to $500 blocks. '
               'Maximum asks all permitted excess. Net cash deducts purchase fees and firm split. '
               'Terminal cash is one permitted request per surviving account, not liquidation.\n')
    detail = original.findings(rows)
    seen_lines = set()
    lines = []
    for line in detail.splitlines():
        if line.startswith('| ') and line in seen_lines:
            continue
        seen_lines.add(line)
        lines.append(line)
    report += '\n'.join(lines)+'\n' 
    report += ('\n## Validation and reproduction\n\n'
               f'All {len(rows)} economic ledgers reconcile. Audited {sum(r["copies_checked"] for r in rows):,} accepted copies '
               'for variant membership, activation, booked settlement counts and killing trades. Both winning runs were reproduced with account and payout ledgers. '
               'The loader checks trade/stats reconciliation and per-window coverage; hashes and actual spans for both variants are in study.json.\n\n'
               'Reproduce: `venv/Scripts/python.exe scripts/study_rr_pair_overlap_withdrawal_amount.py --workers 4`. '
               'Use this runner: the normal single-tape CLI does not encode the mixed allocation. '
               'See candidates.csv, study.json, best_ongoing/ and best_terminal/. '
               'Thresholds are in-sample, the refinement is local, and the allocation order is fixed rather than permutation-tested.\n')
    write_study_report(out, report)
    print(report, flush=True)


if __name__ == '__main__':
    main()
