"""Account-count paths for the common Q3 2024 stress start."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

ROOT=Path(__file__).resolve().parents[1]/'results/legacy_25k/mature_rr_book'


def main():
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True,sharey=True)
    labels={'pair':'10 / 0 / 10 reference','middle10':'9 / 2 / 9 (10% RR 1.00)',
            'middle20':'8 / 4 / 8 (20% RR 1.00)'}
    colors=['#b44b35','#2272a6','#27835f']
    for ax,h in zip(axes,(6800,1500)):
        for (name,label),color in zip(labels.items(),colors):
            data=json.loads((ROOT/'cases'/f'{name}__h{h}__recovery__2024-07-01.json').read_text())
            events=Counter()
            for a in data['accounts']:
                events[datetime.fromisoformat(a['activated_at'])]+=1
                if not a['alive']:events[datetime.fromisoformat(a['died_at'])]-=1
            dates=[];values=[];live=0
            for at,delta in sorted(events.items()):
                live+=delta;dates.append(at);values.append(live)
            dates.append(datetime.fromisoformat(data['row']['end']));values.append(live)
            ax.step(dates,values,where='post',label=label,color=color,lw=2,
                    linestyle='--' if name=='middle10' else ':' if name=='middle20' else '-')
        ax.set_title(f'Initial headroom ${h:,} per account',loc='left',fontsize=12)
        ax.set_ylabel('Live PA accounts')
        ax.set_yticks([0,2,4,10,15,20]);ax.set_ylim(-.6,21)
        ax.grid(alpha=.18)
    axes[0].text(.02,.28,'All three remain at 20 accounts throughout this run.',transform=axes[0].transAxes)
    axes[1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    axes[1].legend(loc='upper right',fontsize=9)
    fig.suptitle('Fully populated books: Q3 2024 start with withdrawals and replacements',fontsize=14)
    fig.text(.07,.015,'Allocations are RR 0.50 / RR 1.00 / RR 2.50. Deaths use exported-exit timestamps. One historical start, not the aggregate result.',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,.95))
    fig.savefig(ROOT/'recovery_2024_q3.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':main()
