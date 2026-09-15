"""Standalone reserve research figure using ReportLab LinePlot, optional Sharp PNG."""
from pathlib import Path
import json
import subprocess
import sys

if len(sys.argv) > 1:
    sys.path.append(sys.argv[1])
from reportlab.graphics import renderSVG
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, Rect, String, Circle
from reportlab.lib import colors

OUT = Path(__file__).resolve().parents[1]/'results/comparisons/legacy_25k_vs_50k/reserve_frontier'


def main():
    rows = json.loads((OUT/'study.json').read_text())['rows']
    blue, orange, grey = [colors.HexColor(s) for s in ('#1b6287', '#c56c23', '#65717b')]
    d = Drawing(1100, 530)
    d.add(Rect(0, 0, 1100, 530, fillColor=colors.white, strokeColor=None))
    d.add(String(45, 492, 'More reserve preserves the book, but defers operating cash',
                 fontName='Helvetica-Bold', fontSize=21))
    d.add(String(45, 466, 'Fixed daily maximum withdrawals | Shared seat reservation | January 2020 to July 2026',
                 fontName='Helvetica', fontSize=12, fillColor=grey))
    for x, label, color in [(45, 'Total net, including closing withdrawal', blue),
                             (375, 'Ongoing net cash', orange), (605, 'Observed March survival threshold', grey)]:
        d.add(Line(x, 439, x+20, 439, strokeColor=color, strokeWidth=2))
        d.add(String(x+27, 435, label, fontName='Helvetica', fontSize=11))
    for i, product in enumerate(('legacy_25k', 'legacy_50k')):
        x, y, width, height = 80+i*540, 125, 410, 270
        family = sorted((r for r in rows if r['product'] == product and r['window'] == 'full'),
                        key=lambda r: r['headroom'])
        chart = LinePlot()
        chart.x, chart.y, chart.width, chart.height = x, y, width, height
        chart.data = [[(r['headroom']/1000, r[key]/1000) for r in family] for key in ('total', 'ongoing')]
        chart.xValueAxis.valueMin, chart.xValueAxis.valueMax = 0, 10
        chart.xValueAxis.valueStep = 1
        chart.xValueAxis.labelTextFormat = '$%dK'
        chart.yValueAxis.valueMin, chart.yValueAxis.valueMax, chart.yValueAxis.valueStep = 0, 700, 100
        chart.yValueAxis.labelTextFormat = '$%dK'
        chart.yValueAxis.visibleGrid = True
        chart.yValueAxis.gridStrokeColor = colors.HexColor('#e5e9ec')
        for axis in (chart.xValueAxis, chart.yValueAxis):
            axis.labels.fontSize = 10
            axis.strokeColor = grey
        for j, color in enumerate((blue, orange)):
            chart.lines[j].strokeColor = color
            chart.lines[j].strokeWidth = 2.5
        d.add(chart)
        boundary_x = x+width*6.78011/10
        d.add(Line(boundary_x, y, boundary_x, y+height, strokeColor=grey,
                   strokeWidth=1, strokeDashArray=[3, 4]))
        best = max(family, key=lambda r: r['ongoing'])
        bx, by = x+width*best['headroom']/10000, y+height*best['ongoing']/700000
        d.add(Circle(bx, by, 4, fillColor=orange, strokeColor=colors.white))
        d.add(String(x, 405, product.replace('legacy_', 'Legacy ').upper(), fontName='Helvetica-Bold', fontSize=15))
        d.add(String(x+width/2, 85, 'Reserve target above frozen failure floor',
                     fontName='Helvetica', fontSize=11, textAnchor='middle'))
        d.add(String(x+width/2, 66, 'Best tested ongoing cash at $5,700; the mature book fails in 2026.',
                     fontName='Helvetica', fontSize=10, textAnchor='middle', fillColor=grey))
    d.add(String(45, 30, 'Historical replay, not a survival guarantee. In 25K cold starts in 2024, the established-account boundary rises to $7,100.',
                 fontName='Helvetica', fontSize=10, fillColor=grey))
    renderSVG.drawToFile(d, str(OUT/'reserve_frontier.svg'))
    if len(sys.argv) > 3:
        js = 'const sharp=require(process.argv[3]); sharp(process.argv[1], {density:140}).png().toFile(process.argv[2]).catch(e=>{console.error(e);process.exit(1)});'
        subprocess.run([sys.argv[2], '-e', js, str(OUT/'reserve_frontier.svg'),
                        str(OUT/'reserve_frontier.png'), str(Path(sys.argv[3])/'sharp')], check=True)
    print(OUT/'reserve_frontier.svg')


if __name__ == '__main__':
    main()
