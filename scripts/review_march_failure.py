"""Forensic comparison of withdrawals and the March 2026 replacement episode.

Preserves prior results. Any factory pause below is an explicit counterfactual,
not a forecast or a random simulation of market outcomes.
"""
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import study_legacy_pipeline_capacity as prior
import pa_milky.simulator as simulator
from pa_milky.acquisition import AcquisitionLedger, AcquisitionPolicy
from pa_milky.evaluation import EvaluationSpec
from pa_milky.policy import WithdrawalPolicy
from pa_milky.pipeline_metrics import measure_pipeline, replacement_records
from pa_milky.economics import Economics
from pa_milky.provenance import engine_digest, input_digest, sha256_file

OUT = prior.ROOT/'march_failure_review'
EVENT = datetime(2026, 3, 30, 6)


class Snapshot:
    def __init__(self):
        self.rows = []

    def __call__(self, at, accounts, event, trade):
        wanted = (event == 'before_trade' and at == EVENT or
                  event == 'decision' and at.strftime('%Y-%m-%d') in
                  ('2026-03-01', '2026-03-31', '2026-04-30', '2026-05-31', '2026-06-30'))
        if not wanted:
            return
        live = [a for a in accounts if a.alive]
        balances = [a.equity_profit_usd for a in live]
        self.rows.append({'at': at.isoformat(), 'event': event, 'alive': len(live),
            'distinct_profit_balances': len(set(balances)), 'profit_min': min(balances, default=None),
            'profit_max': max(balances, default=None),
            'accounts': [{'id': a.account_id, 'profit': a.equity_profit_usd,
                          'cushion': a.headroom_usd} for a in live]})


def evaluate(label, job, first_check, pause_days=0, pause_start=EVENT):
    product, initial, monthly, rule, cadence, reserve, persistent, interval, concurrency, spares, seats = job
    base = prior.sim.C[product]
    policy = WithdrawalPolicy(name=f'{rule}_{cadence}_headroom_{reserve}', cadence=cadence,
        amount_rule=rule, quantize_to_amount=False, terminal_withdrawal='firm_permitted',
        min_retained_balance_usd=base.trailing_floor_balance_usd+reserve)
    acquisition = AcquisitionPolicy(prior.ACQ, initial, monthly, max_live_accounts=20,
        spare_capacity=spares, evaluation=EvaluationSpec(**prior.EVAL['evaluations'][product]),
        evaluations_at_once=concurrency, persistent_demand=persistent,
        evaluation_start_interval_days=interval, evaluations_reserve_seats=seats,
        activate_on_first_check=first_check)
    pause_end = pause_start+timedelta(days=pause_days)

    class PausedLedger(AcquisitionLedger):
        def settle(self, index, trade):
            # Skip complete evaluation positions whose entries fall in the
            # outage. Existing pre-outage positions settle normally. Fees,
            # renewals, PA trades, purchase demand and activation all continue.
            if pause_days and pause_start <= trade.entry_at < pause_end:
                self.settled = index+1
                for evaluation, generation in self.waiting.pop(index, ()):
                    if evaluation.state == 'running' and evaluation.generation == generation:
                        self.route(evaluation, trade.exit_at)
            else:
                super().settle(index, trade)

    observer = Snapshot()
    with patch.object(simulator, 'AcquisitionLedger', PausedLedger):
        result = simulator.run_book(prior.sim.T, replace(base, policy=policy),
                                    acquisition=acquisition, observer=observer)
    ledger = result.acquisition
    terminal = round(sum(p.received_usd for p in result.terminal_payouts), 2)
    assert Economics.measure(result).residual_usd == ledger.summary()['cash_identity_residual_usd'] == 0
    assert all(d['alive']+d['spares']+d['in_flight'] <= 20 for d in ledger.pipeline_daily)
    before = next(s for s in observer.rows if s['event'] == 'before_trade')
    deaths = Counter(a.died_at for a in result.dead)
    march_deaths = {str(k): v for k, v in sorted(deaths.items()) if k.year == 2026 and k.month == 3}
    waits = [w for w in replacement_records(result) if w['died_at'] == EVENT.isoformat()]
    day_30 = [w for w in waits if not w['censored'] and w['wait_days'] <= 30]
    recovers = [d['at'] for d in ledger.pipeline_daily if d['at'] > EVENT.isoformat() and d['alive'] == 20]
    row = {'label': label, 'product': product, 'rule': rule, 'reserve': reserve,
        'first_check': first_check, 'pause_days': pause_days, 'pause_start': pause_start.isoformat(),
        'ongoing': round(result.pocket_usd-terminal, 2), 'terminal': terminal, 'total': result.pocket_usd,
        'alive_at_end': result.alive_at_horizon, 'accounts': len(result.accounts),
        'evaluations': len(ledger.evaluations), 'pre_event_alive': before['alive'],
        'pre_event_distinct_balances': before['distinct_profit_balances'],
        'pre_event_min_profit': before['profit_min'], 'pre_event_max_profit': before['profit_max'],
        'deaths_on_event': deaths[EVENT], 'event_deaths_replaced_in_30_days': len(day_30),
        'event_deaths_still_unfilled': sum(w['censored'] for w in waits),
        'first_20_live_check_after_event': recovers[0] if recovers else None,
        'march_death_clusters': march_deaths,
        'operating_receipts_after_event': round(sum(p.received_usd for p in result.payouts
            if p.at > EVENT and p not in result.terminal_payouts), 2),
        'spend_after_event': round(-sum(e['amount_usd'] for e in ledger.cash_events
            if e['at'] > EVENT.isoformat() and e['amount_usd'] < 0), 2),
        **measure_pipeline(result), 'job': list(job)}
    return row, result, observer


def main():
    prior.initialize()
    OUT.mkdir(exist_ok=True)
    protected = {str(p): sha256_file(p) for p in (prior.PROJECT_ROOT/'results').rglob('*')
                 if p.is_file() and OUT not in p.parents}
    old = [r for r in prior.read_rows('pipeline_capacity') if r['reserve_seats']
           and r['initial_cash'] == 5000 and r['monthly_funding'] == 200]
    ranking = []
    cases = []
    for product in ('legacy_25k', 'legacy_50k'):
        family = [r for r in old if r['product'] == product]
        for score in ('ongoing', 'total'):
            winners = [max([r for r in family if r['withdrawal'] == rule and r['cadence'] == cadence],
                           key=lambda r: (r[score], r['ongoing']))
                       for rule in ('minimum', 'maximum') for cadence in ('daily', 'weekly', 'calendar_month')]
            ranking.extend(dict(objective=score, family_rank=i+1, **r)
                           for i, r in enumerate(sorted(winners, key=lambda r: r[score], reverse=True)))
        winner = max((r for r in family if r['withdrawal'] == 'minimum' and r['cadence'] == 'daily'),
                     key=lambda r: r['ongoing'])
        cases.append((product+'_minimum_winner_legacy', tuple(winner['job']), False))
        cases.append((product+'_minimum_winner_first_check', tuple(winner['job']), True))
        for rule, reserve in [('maximum', 5700), ('maximum', 6700), ('minimum', 6700),
                              ('maximum', 6800), ('minimum', 6800)]:
            cases.append((product+f'_{rule}_{reserve}',
                (product, 5000, 200, rule, 'daily', reserve, True,
                 7 if product == 'legacy_25k' else 1, 20, 2, True), True))
    prior.csv_write(OUT/'historical_policy_ranking.csv', ranking)
    summaries = []
    for label, job, first_check in cases:
        row, result, observer = evaluate(label, job, first_check)
        if not first_check:
            saved = next(r for r in old if r['job'] == list(job))
            assert (row['ongoing'], row['total'], row['accounts'], row['alive_at_end']) == (
                saved['ongoing'], saved['total'], saved['accounts'], saved['alive'])
        summaries.append(row)
        folder = OUT/label
        folder.mkdir(exist_ok=True)
        (folder/'snapshots.json').write_text(json.dumps(observer.rows, indent=2))
        prior.csv_write(folder/'pipeline_daily.csv', result.acquisition.pipeline_daily)
        prior.csv_write(folder/'replacement_waits.csv', replacement_records(result))
        prior.csv_write(folder/'march_deaths.csv', [{'account_id': a.account_id,
            'died_at': a.died_at, 'death_trade': a.death_trade_key, 'equity': a.death_equity_usd}
            for a in result.dead if a.died_at.year == 2026 and a.died_at.month == 3])
        prior.csv_write(folder/'passes_after_march.csv', [{'eval_id': e.eval_id,
            'started_at': e.started_at, 'passed_at': e.passed_at, 'funded_or_ended_at': e.ended_at,
            'state': e.state} for e in result.acquisition.evaluations
            if e.passed_at and e.passed_at >= datetime(2026, 3, 1)])
        # Show the last payout for each of the exact March 30 victims.
        victims = [a.account_id for a in result.dead if a.died_at == EVENT]
        payout_traces = []
        for aid in victims:
            payouts = [p for p in result.payouts if p.account_id == aid and p.at < EVENT]
            if payouts:
                p = max(payouts, key=lambda p: p.at)
                payout_traces.append({'account_id': aid, 'last_payout_at': p.at,
                    'profit_after_payout': round(p.balance_after_usd-result.config.starting_balance_usd, 2)})
        prior.csv_write(folder/'victim_last_payout.csv', payout_traces)
        print(json.dumps(row), flush=True)
    prior.csv_write(OUT/'baselines.csv', summaries)
    (OUT/'baselines.json').write_text(json.dumps(summaries, indent=2))
    assert all(sha256_file(Path(p)) == h for p, h in protected.items())
    (OUT/'AUDIT.json').write_text(json.dumps({'engine': engine_digest(),
        'inputs': input_digest(prior.sim.C['legacy_25k']), 'runner_sha256': sha256_file(Path(__file__)),
        'prior_files_unchanged': len(protected), 'baselines': len(summaries),
        'historical_minimum_winners_reproduced': 2}, indent=2))


if __name__ == '__main__':
    main()
