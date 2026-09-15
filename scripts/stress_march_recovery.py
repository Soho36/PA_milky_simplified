"""Small diagnostic evaluation-entry outages after the March 30 event."""
import json
from pathlib import Path
import review_march_failure as review


def main():
    review.prior.initialize()
    baselines = json.loads((review.OUT/'baselines.json').read_text())
    rows = []
    for base in baselines:
        if not base['first_check'] or not (base['label'].endswith('minimum_winner_first_check')
            or base['label'].endswith('maximum_6700') or base['label'].endswith('maximum_6800')):
            continue
        pauses = [30, 365] if base['rule'] == 'minimum' else [365]
        for days in pauses:
            row, result, observer = review.evaluate(base['label'], base['job'], True, pause_days=days)
            # All withdrawal receipts before the shock must be unchanged.
            before_net = round(base['ongoing']-base['operating_receipts_after_event']+base['spend_after_event'], 2)
            stressed_before_net = round(row['ongoing']-row['operating_receipts_after_event']+row['spend_after_event'], 2)
            assert before_net == stressed_before_net
            if base['label'].endswith('maximum_6800'):
                assert (row['ongoing'], row['total'], row['accounts']) == (
                    base['ongoing'], base['total'], base['accounts'])
            row.update(ongoing_change=round(row['ongoing']-base['ongoing'], 2),
                total_change=round(row['total']-base['total'], 2),
                baseline_total=base['total'], baseline_alive=base['alive_at_end'])
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('label', 'pause_days', 'ongoing', 'total',
                'ongoing_change', 'total_change', 'alive_at_end')}), flush=True)
    review.prior.csv_write(review.OUT/'recovery_stress.csv', rows)
    (review.OUT/'recovery_stress.json').write_text(json.dumps(rows, indent=2))
    (review.OUT/'STRESS_AUDIT.json').write_text(json.dumps({
        'runs': len(rows), 'start': review.EVENT.isoformat(),
        'intervention': 'No new evaluation trade entries for 30 or 365 calendar days. Pre-existing evaluation positions settle normally; subscriptions, fees, PA trades and demand continue. 365 days exceeds remaining tape.',
        'interpretation': 'Operational supply stress, not a probabilistic model of bad trading luck. Skipping losses can also help, and fewer activations save fees. No change to firm activation deadlines.',
        'pre_shock_net_cash_identical': True, 'unaffected_full_book_controls': 2,
        'runner_sha256': review.sha256_file(Path(__file__)),
        'simulation_helper_sha256': review.sha256_file(Path(review.__file__))}, indent=2))


if __name__ == '__main__':
    main()
