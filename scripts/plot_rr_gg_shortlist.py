"""Quarter losses and assignment-order continuity for the fixed shortlist."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results/legacy_25k/rr_gg_shortlist'
LABELS = {'RR:0.50':'RR 0.50', 'RR:1.00':'RR 1.00', 'RR:2.50':'RR 2.50', 'GG:1.25':'GG 1.25',
          'rr_pair':'RR 0.50 + RR 2.50', 'cross_pair':'RR 0.50 + GG 1.25',
          'rr_triple':'RR 0.50 + RR 2.50 + RR 1.00',
          'cross_triple':'RR 0.50 + GG 1.25 + RR 1.00'}


def read(name):
    with (ROOT / name).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def main():
    rows = read('isolation_quarters.csv')
    cases = sorted({r['case'] for r in rows})
    lookup = {(r['portfolio'],r['case']):float(r['failed_fraction']) for r in rows}
    values = np.array([[lookup[name,case] for case in cases] for name in LABELS])
    fig, ax = plt.subplots(figsize=(15, 5.5))
    im = ax.imshow(values, vmin=0, vmax=1, cmap='YlOrRd', aspect='auto')
    ax.set_yticks(range(len(LABELS)), LABELS.values())
    quarters = [f'{c[3:7]} Q{(int(c[8:10])-1)//3+1}' for c in cases]
    ax.set_xticks(range(len(cases)), quarters, rotation=60, ha='right')
    ax.set_title('Fraction of accounts failing in each fresh-start quarter', loc='left', pad=28, fontsize=15)
    ax.text(0, 1.015, 'Equal allocations; $1,500 fixed headroom per account. Full loss means by quarter end, not the same date.',
            transform=ax.transAxes, fontsize=9)
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            if value:
                ax.text(j, i, f'{value:.0%}', ha='center', va='center', fontsize=8,
                        color='white' if value > .75 else 'black')
    for i in range(1, len(cases)):
        if 'Q1' in quarters[i]:
            ax.axvline(i-.5, color='#777777', lw=.6)
    ax.axhline(3.5, color='#333333', lw=1)
    fig.colorbar(im, ax=ax, label='Fraction failed', shrink=.8)
    fig.tight_layout()
    fig.savefig(ROOT / 'quarter_failures.png', dpi=160)
    plt.close(fig)

    starts = read('operating_by_start.csv')
    mix = list(LABELS)[4:]
    lookup = {(r['portfolio'],int(r['start_year'])):r for r in starts}
    values = np.array([[int(lookup[name,year]['continuous_orders']) / int(lookup[name,year]['permutations'])
                        for year in range(2020,2026)] for name in mix])
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.imshow(values, vmin=0, vmax=1, cmap='YlGn', aspect='auto')
    ax.set_yticks(range(4), [LABELS[n] for n in mix])
    ax.set_xticks(range(6), range(2020,2026))
    ax.set_xlabel('Operating start year')
    ax.set_title('Assignment orders with uninterrupted operation after first activation',
                 loc='left', pad=28, fontsize=12)
    ax.text(0, 1.025, 'Count of continuous orders / all orders. Overlapping historical runs, not independent probabilities.',
            transform=ax.transAxes, fontsize=8)
    for i, name in enumerate(mix):
        for j, year in enumerate(range(2020,2026)):
            r = lookup[name,year]
            ax.text(j, i, f'{r["continuous_orders"]}/{r["permutations"]}', ha='center', va='center',
                    color='white' if values[i,j] > .8 else 'black', fontsize=12)
    fig.tight_layout()
    fig.savefig(ROOT / 'operating_continuity.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    main()
