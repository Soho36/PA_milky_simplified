"""Audit overlapping mixture plus reproduce original RR1 reference scores."""
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path

import study_rr_pair_overlap_withdrawal_amount as study
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from pa_milky.loader import load_tape
from pa_milky.config import load_config
from pa_milky.policy_study import measure
from pa_milky.simulator import run_book
from rr_overlap_support import run_overlap_book

ORIGINAL = study.ROOT/'results/study__full_rulebook__RR__monthly_amount_x_cushion__dual_terminal_scores/study.json'


def main():
    study.initialize()
    saved = json.loads((study.OUT/'study.json').read_text(encoding='utf-8'))
    assert saved['engine'] == engine_digest()
    for name, digest in saved['scripts'].items():
        assert sha256_file(study.ROOT/'scripts'/name) == digest
    for rr, source in saved['inputs'].items():
        assert input_digest(replace(study.CONFIG, risk_reward=rr)) == source['digest']
    checks = Counter()
    rows = saved['rows']
    assert len({(r['policy'],r['retained_balance_usd']) for r in rows}) == len(rows)
    for row in rows:
        assert row['economics']['residual_usd'] == 0
        assert study.money(row['ongoing_pocket_usd']+row['terminal_received_usd']) == row['combined_pocket_usd']
        assert row['alive_rr050']+row['alive_rr250'] == row['alive_before_terminal']
        checks['candidate_identities'] += 1
    chosen = [next(r for r in rows if r['stage']=='benchmark')]
    chosen += [max(rows, key=lambda r:r[metric]) for metric in ('ongoing_pocket_usd','combined_pocket_usd')]
    hold_keys = None
    for row in chosen:
        result = study.simulate(WithdrawalPolicy.from_payload(row['policy_config']), row['retained_balance_usd'])
        actual = study.score(result, row['retained_balance_usd'], row['stage'])
        for key, value in actual.items():
            assert value == row[key], (row['policy'],key)
        keys = study.audit_result(result)
        for a in result.accounts:
            rr = result.routing['account_rr'][a.account_id]
            expected = [t.trade_key for t in study.TAPES[rr] if t.entry_at >= a.activated_at]
            if not a.alive:
                expected = expected[:expected.index(a.death_trade_key)+1]
            assert keys[a.account_id] == expected
            if hold_keys is not None:
                assert keys[a.account_id] == hold_keys[a.account_id][:len(keys[a.account_id])]
            checks['independent_account_settlement_selections'] += 1
            checks['booked_copies'] += len(keys[a.account_id])
        if row['stage']=='benchmark':
            hold_keys = keys
        checks['reproduced_paths'] += 1
    # Same single-variant inputs, policies and acquisition clock must reproduce
    # the historical report, not merely agree with a new mixed implementation.
    old = json.loads(ORIGINAL.read_text(encoding='utf-8'))
    baseline = load_config(study.ROOT/'config/scenarios/full_rulebook_monthly_500.json')
    tape = load_tape(baseline)
    controls = [next(r for r in old['rows'] if r['stage']=='benchmark')]
    controls += [max(old['rows'], key=lambda r:r[m]) for m in ('ongoing_pocket_usd','combined_pocket_usd')]
    for row in controls:
        policy = WithdrawalPolicy.from_payload(row['policy_config'])
        current = measure(tape, baseline, policy, row['retained_balance_usd'])
        for key, value in current.items():
            assert value == row[key], ('original RR1', row['policy'],key,value,row[key])
        cfg = replace(baseline, policy=policy)
        legacy = run_book(tape,cfg)
        adapted = run_overlap_book(tape,cfg,order=('1.00',),trade_rr={t.trade_key:'1.00' for t in tape})
        assert adapted.accounts == legacy.accounts
        assert adapted.payouts == legacy.payouts
        assert adapted.denials == legacy.denials
        assert adapted.copies_filled == legacy.copies_filled
        checks['historical_rr1_scores_and_adapter_equivalence'] += 1
    output = dict(status='passed', checks=dict(checks),
                  auditor_sha256=sha256_file(Path(__file__)),
                  original_rr1_sha256=sha256_file(ORIGINAL),
                  study_sha256=sha256_file(study.OUT/'study.json'))
    (study.OUT/'audit.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
