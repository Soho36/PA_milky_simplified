"""Replay one pipeline_capacity winner folder with read-only taps.

Usage: replay_timeline.py <folder name> <dest json>
e.g.   replay_timeline.py legacy_25k__shared_seats__best_ongoing timeline.json

Nothing in the engine is changed: we wrap functions to *observe* state
(daily per-account equity, evaluation blow/pass/reset events) and then
assert the replay reproduces the saved report exactly.
"""
from pathlib import Path
from collections import defaultdict
import csv, json, sys

ROOT = Path(r'I:\PycharmProjects\PA_milky_simplified')
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))
FOLDER = sys.argv[1]
DEST = Path(sys.argv[2])
OUT_DIR = ROOT / 'results/comparisons/legacy_25k_vs_50k/pipeline_capacity' / FOLDER
product, mode, objective = FOLDER.split('__')
reserve_seats = {'shared_seats': True, 'evals_outside_cap': False}[mode]
objective = objective.removeprefix('best_')

import study_legacy_pipeline_capacity as cap
import pa_milky.simulator as simulator
from pa_milky.evaluation import Evaluation
from pa_milky.acquisition import AcquisitionLedger

cap.initialize()
study = json.loads((OUT_DIR.parent / 'study.json').read_text(encoding='utf-8'))
winner = [w for w in study['winners'] if w['product'] == product
          and w['reserve_seats'] == reserve_seats and w['objective'] == objective]
assert len(winner) == 1
job = tuple(winner[0]['job'])
print('job', job, flush=True)

# ---------------------------------------------------------------- taps
snaps = []            # (date, {account_id: equity_profit or None})
orig_decision = simulator.run_monthly_decision

def tap_decision(accounts, boundary, config, pending, **kw):
    out = orig_decision(accounts, boundary, config, pending, **kw)
    snaps.append((boundary, {a.account_id: (a.equity_profit_usd if a.alive else None) for a in accounts}))
    return out
simulator.run_monthly_decision = tap_decision

eval_events = []      # (eval_id, at, kind)
orig_apply = Evaluation.apply

def tap_apply(self, trade, spec, **kw):
    state = orig_apply(self, trade, spec, **kw)
    if state in ('blown', 'passed'):
        eval_events.append((self.eval_id, trade.exit_at, state))
    return state
Evaluation.apply = tap_apply

orig_run_evals = AcquisitionLedger.run_evaluations

def tap_run_evals(self, at, alive):
    before = {e.eval_id: (e.state, e.resets) for e in self.active}
    out = orig_run_evals(self, at, alive)
    for e in self.evaluations:
        if e.eval_id in before:
            st, rs = before[e.eval_id]
            if e.resets > rs:
                eval_events.append((e.eval_id, at, 'reset'))
            if e.state == 'cancelled' and st != 'cancelled':
                eval_events.append((e.eval_id, at, 'cancelled'))
    return out
AcquisitionLedger.run_evaluations = tap_run_evals

row, r = cap.evaluate(job, True)

# ---------------------------------------------------------------- reconcile with saved outputs
saved = json.loads((OUT_DIR / 'summary.json').read_text(encoding='utf-8'))
experiment = json.loads((OUT_DIR / 'experiment.json').read_text(encoding='utf-8'))
assert r.pocket_usd == saved['cash']['owner_cash_position_usd'], r.pocket_usd
assert len(r.accounts) == saved['book']['accounts_opened'] and r.alive_at_horizon == saved['book']['accounts_alive_at_end']
saved_daily = list(csv.DictReader((OUT_DIR / 'pipeline_daily.csv').open(encoding='utf-8')))
assert len(saved_daily) == len(r.acquisition.pipeline_daily) == len(snaps), (len(saved_daily), len(snaps))
for s, d in zip(saved_daily, r.acquisition.pipeline_daily):
    assert s['at'] == d['at'] and float(s['cash_usd']) == d['cash_usd'] and int(s['spares']) == d['spares']
    assert int(s['in_flight']) == d['in_flight'] and int(s['alive']) == d['alive']
assert sum(1 for *_, k in eval_events if k == 'reset') == saved['acquisition']['evaluation_resets']
print('replay reproduces saved report', flush=True)

# ---------------------------------------------------------------- daily frame
days = [b.date().isoformat() for b, _ in snaps]
day_index = {d: i for i, d in enumerate(days)}
n = len(days)

cash_kinds = defaultdict(lambda: [0.0] * n)
for ev in r.acquisition.cash_events:
    d = ev['at'][:10]
    if d in day_index:
        cash_kinds[ev['kind']][day_index[d]] += ev['amount_usd']

def cumulative(xs):
    out, t = [], 0.0
    for x in xs:
        t += x; out.append(round(t, 2))
    return out

contrib = cumulative(cash_kinds['owner_contribution'])
received = cumulative(cash_kinds['payout_received'])
eval_fees = cumulative([-x for x in cash_kinds['evaluation_fee']])
act_fees = cumulative([-x for x in cash_kinds['activation_fee']])

pd = r.acquisition.pipeline_daily
live_profit = [round(sum(v for v in m.values() if v is not None), 2) for _, m in snaps]

# ---------------------------------------------------------------- account path groups (identical clones collapsed)
accounts = {a.account_id: a for a in r.accounts}
series = defaultdict(lambda: [None] * n)
for i, (_, m) in enumerate(snaps):
    for aid, v in m.items():
        series[aid][i] = v
received_by = defaultdict(float)
payouts_by = defaultdict(int)
for p in r.payouts:
    received_by[p.account_id] += p.received_usd
    payouts_by[p.account_id] += 1

groups = {}
for aid, a in accounts.items():
    s = series[aid]
    key = (a.activated_at, a.died_at, a.death_equity_usd, a.equity_profit_usd, tuple(s))
    g = groups.setdefault(key, {'ids': [], 'activated': a.activated_at.isoformat(), 'cohort': a.cohort_month,
        'died': a.died_at.isoformat() if a.died_at else None, 'death_equity': a.death_equity_usd,
        'death_reason': a.death_reason, 'alive': a.alive, 'trades': a.trades_taken,
        'payouts': payouts_by[aid], 'received': round(received_by[aid], 2),
        'end_profit': a.equity_profit_usd if a.alive else None})
    g['ids'].append(aid)
    first = next((i for i, v in enumerate(s) if v is not None), None)
    last = max((i for i, v in enumerate(s) if v is not None), default=None)
    g['start'] = first
    g['values'] = [round(v) for v in s[first:last + 1]] if first is not None else []
group_list = sorted(groups.values(), key=lambda g: (g['activated'], g['ids'][0]))
print('accounts', len(accounts), 'unique paths', len(group_list), flush=True)

# ---------------------------------------------------------------- evaluations
evals = []
by_eval = defaultdict(list)
for eid, at, kind in eval_events:
    by_eval[eid].append({'at': at.isoformat(), 'kind': kind})
for e in r.acquisition.evaluations:
    evals.append({'id': e.eval_id, 'started': e.started_at.isoformat(), 'state': e.state,
        'months_paid': e.months_paid, 'resets': e.resets,
        'passed': e.passed_at.isoformat() if e.passed_at else None,
        'ended': e.ended_at.isoformat() if e.ended_at else None,
        'events': sorted(by_eval[e.eval_id], key=lambda x: x['at'])})

payload = {
    'meta': {'folder': FOLDER, 'objective': objective, 'job': list(job), 'pocket_usd': r.pocket_usd,
             'accounts': len(accounts), 'alive_at_end': r.alive_at_horizon,
             'tape_first': r.tape_first_entry.isoformat(), 'tape_last': r.tape_last_exit.isoformat(),
             'summary': saved, 'run_config': experiment['run_config']},
    'days': days,
    'daily': {
        'cash': [d['cash_usd'] for d in pd],
        'alive': [d['alive'] for d in pd],
        'spares': [d['spares'] for d in pd],
        'subscriptions': [d['subscriptions'] for d in pd],
        'awaiting': [d['awaiting_activation'] for d in pd],
        'in_flight': [d['in_flight'] for d in pd],
        'shortfall': [d['shortfall'] for d in pd],
        'pending': [d['pending_replacements'] for d in pd],
        'live_profit': live_profit,
        'contrib': contrib, 'received': received, 'eval_fees': eval_fees, 'act_fees': act_fees,
    },
    'groups': group_list,
    'evaluations': evals,
}
DEST.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')
print('wrote', DEST, DEST.stat().st_size, flush=True)
