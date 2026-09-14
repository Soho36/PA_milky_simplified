"""Standalone research chart using ReportLab's standard LinePlot charting.

Use the project venv. Optionally pass the bundled Python site-packages path
reported by Codex's workspace-dependency tool when ReportLab is not in the venv.
For PNG output, pass the bundled Node executable and Node node_modules path
as the second and third arguments; Sharp rasterizes the same SVG.
"""
from pathlib import Path
import json
import subprocess
import sys

if len(sys.argv)>1:sys.path.append(sys.argv[1])
from reportlab.graphics import renderSVG
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors

OUT=Path(__file__).resolve().parents[1]/'results/comparisons/legacy_25k_vs_50k/pipeline_capacity'


def main():
    study=json.loads((OUT/'study.json').read_text(encoding='utf-8'))
    rows=[json.loads(x) for x in (OUT/'checkpoint.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=[json.loads(x) for x in (OUT.parent/'reserve_by_policy/checkpoint.jsonl').read_text().splitlines()]
    budget=study['spec']['budget']
    caps=study['spec']['concurrency']
    palette=[colors.HexColor(c) for c in ('#135c86','#ce7623','#71629b','#777777')]
    d=Drawing(1000,530)
    d.add(Rect(0,0,1000,530,fillColor=colors.white,strokeColor=None))
    d.add(String(45,494,'More evaluation capacity helps, but withdrawal policy still matters',fontName='Helvetica-Bold',fontSize=19))
    d.add(String(45,470,'January 2020 – July 2026  |  $5,000 initial + $200/month  |  Net cash includes closing withdrawal',fontName='Helvetica',fontSize=11,fillColor=colors.HexColor('#555555')))
    legend=[('Retuned policy, shared seats',45),('Old aggressive, shared seats',290),('Old aggressive, evals outside cap',535),('Historical instant supply',810)]
    for i,(label,x) in enumerate(legend):
        d.add(Line(x,442,x+20,442,strokeColor=palette[i],strokeWidth=2,strokeDashArray=[3,3] if i==3 else None))
        d.add(String(x+25,438,label,fontName='Helvetica',fontSize=9))
    for index,prod in enumerate(study['spec']['products']):
        x=75+index*490
        d.add(String(x,402,prod.replace('legacy_','Legacy ').upper(),fontName='Helvetica-Bold',fontSize=15))
        anchor=tuple(study['anchors'][prod]['instant_aggressive'])
        fixed=[r for r in rows if r['product']==prod and [r['initial_cash'],r['monthly_funding']]==budget
               and (r['withdrawal'],r['cadence'],r['headroom'])==anchor]
        retuned=[r for r in study['frontier'] if r['product']==prod and r['reserve_seats'] and r['objective']=='total']
        benchmark=max(r['total'] for r in prior if r['product']==prod and [r['initial_cash'],r['monthly_funding']]==budget
                      and not r['strict_post_payout_balance'])
        data=[[(n,next(r['total'] for r in retuned if r['concurrency']==n)/1000) for n in caps]]
        for seats in (True,False):
            data.append([(n,max(r['total'] for r in fixed if r['reserve_seats']==seats and r['concurrency']==n)/1000) for n in caps])
        data.append([(min(caps),benchmark/1000),(max(caps),benchmark/1000)])
        chart=LinePlot()
        chart.x=x;chart.y=115;chart.width=370;chart.height=260
        chart.data=data
        chart.xValueAxis.valueMin=min(caps);chart.xValueAxis.valueMax=max(caps)
        chart.xValueAxis.valueSteps=caps
        chart.yValueAxis.valueMin=0;chart.yValueAxis.valueMax=900;chart.yValueAxis.valueStep=100
        chart.yValueAxis.labelTextFormat='$%dK'
        chart.xValueAxis.labels.fontSize=10;chart.yValueAxis.labels.fontSize=9
        chart.yValueAxis.visibleGrid=True
        chart.yValueAxis.gridStrokeColor=colors.HexColor('#e7eaed')
        chart.xValueAxis.strokeColor=colors.HexColor('#9ba4aa')
        chart.yValueAxis.strokeColor=colors.HexColor('#9ba4aa')
        for i,color in enumerate(palette):
            chart.lines[i].strokeColor=color
            chart.lines[i].strokeWidth=2.4 if i==0 else 1.8
        chart.lines[3].strokeDashArray=[4,4]
        d.add(chart)
        d.add(String(x+185,82,'Concurrent evaluation subscription limit',fontName='Helvetica',fontSize=11,textAnchor='middle'))
    d.add(String(45,46,'Each point selects the best tested pipeline at that cap. Retuned policies use a staged shortlist, not an exhaustive joint search.',fontName='Helvetica',fontSize=10,fillColor=colors.HexColor('#555555')))
    d.add(String(45,29,'Shared seats: live + spares + evaluations ≤ 20. Outside-cap evaluations are a modelling sensitivity. Lines connect tested limits.',fontName='Helvetica',fontSize=10,fillColor=colors.HexColor('#555555')))
    renderSVG.drawToFile(d,str(OUT/'capacity_frontier.svg'))
    print(OUT/'capacity_frontier.svg')
    if len(sys.argv)>3:
        js="const sharp=require(process.argv[3]); sharp(process.argv[1], {density:150}).png().toFile(process.argv[2]).catch(e=>{console.error(e);process.exit(1)});"
        subprocess.run([sys.argv[2],'-e',js,str(OUT/'capacity_frontier.svg'),
            str(OUT/'capacity_frontier.png'),str(Path(sys.argv[3])/'sharp')],check=True)
        print(OUT/'capacity_frontier.png')


if __name__=='__main__':main()
