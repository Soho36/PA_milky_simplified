"""Reproduce leaders and independently check their native entry selection."""
from collections import Counter
from datetime import timedelta
import json
from pathlib import Path

import study_rr_pair_withdrawal_amount as study
from pa_milky.policy import WithdrawalPolicy
from pa_milky.provenance import engine_digest, input_digest, sha256_file
from dataclasses import replace
from rr_curve_support import select_trades


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
            expected = select_trades(study.TAPES[rr], a.activated_at, result.tape_last_exit+timedelta(microseconds=1))
            expected_keys = [t.trade_key for t in expected]
            if a.alive:
                assert keys[a.account_id] == expected_keys
            else:
                assert keys[a.account_id] == expected_keys[:len(keys[a.account_id])]
            if hold_keys is not None:
                assert keys[a.account_id] == hold_keys[a.account_id][:len(keys[a.account_id])]
            checks['independent_account_entry_selections'] += 1
            checks['accepted_copies'] += len(keys[a.account_id])
        if row['stage']=='benchmark':
            hold_keys = keys
        checks['reproduced_paths'] += 1
    output = dict(status='passed', checks=dict(checks),
                  auditor_sha256=sha256_file(Path(__file__)),
                  study_sha256=sha256_file(study.OUT/'study.json'))
    (study.OUT/'audit.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
