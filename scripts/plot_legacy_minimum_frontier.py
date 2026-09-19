"""Research plots of paired reserve curves, using ReportLab and optional Sharp."""
from pathlib import Path
import json
import subprocess
import sys

if '--out' in sys.argv:
    # Chart another study folder, e.g. the blocked-copying twin; positional arguments are unchanged.
    at = sys.argv.index('--out'); FOLDER = sys.argv[at+1]; del sys.argv[at:at+2]
else:
    FOLDER = None
if len(sys.argv) > 1:
    sys.path.append(sys.argv[1])
from reportlab.graphics import renderSVG
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.lib import colors

OUT = Path(__file__).resolve().parents[1]/(FOLDER or 'results/comparisons/legacy_25k_vs_50k/reserve_frontier_minimum')


def main():
    rows = [r for r in json.loads((OUT/'study.json').read_text())['rows'] if r['window'] == 'full']
    blue, orange, grey = [colors.HexColor(c) for c in ('#196b91', '#bd6825', '#596972')]
    drawing = Drawing(1120, 880)
    drawing.add(Rect(0, 0, 1120, 880, fillColor=colors.white, strokeColor=None))
    drawing.add(String(45, 842, 'Daily minimum changes the cash and survival curves', fontName='Helvetica-Bold', fontSize=22))
    drawing.add(String(45, 815, 'Same reserve grid, funding and evaluation pipeline | Full historical replay: January 2020 to July 2026',
                       fontName='Helvetica', fontSize=11, fillColor=grey))
    for x, label, color in ((45, 'Daily minimum', blue), (250, 'Daily maximum', orange)):
        drawing.add(Line(x, 788, x+25, 788, strokeColor=color, strokeWidth=3))
        drawing.add(String(x+32, 784, label, fontName='Helvetica', fontSize=12))
    panels = [('ongoing', 'Ongoing net cash', 530, 700, 100),
              ('total', 'Net cash including closing withdrawal', 300, 700, 100),
              ('alive', 'Trading PAs alive at the horizon', 70, 20, 5)]
    for index, product in enumerate(('legacy_25k', 'legacy_50k')):
        x = 80+550*index
        drawing.add(String(x, 753, product.replace('legacy_', 'Legacy ').upper(), fontName='Helvetica-Bold', fontSize=15))
        for metric, title, y, ymax, step in panels:
            chart = LinePlot()
            chart.x, chart.y, chart.width, chart.height = x, y, 410, 175
            scale = 1 if metric == 'alive' else 1000
            chart.data = [[(r['headroom']/1000, r[metric]/scale) for r in
                sorted((r for r in rows if r['product'] == product and r['withdrawal'] == rule), key=lambda r: r['headroom'])]
                for rule in ('minimum', 'maximum')]
            chart.xValueAxis.valueMin, chart.xValueAxis.valueMax, chart.xValueAxis.valueStep = 0, 10, 1
            chart.xValueAxis.labelTextFormat = '$%dK'
            chart.yValueAxis.valueMin, chart.yValueAxis.valueMax, chart.yValueAxis.valueStep = 0, ymax, step
            chart.yValueAxis.labelTextFormat = '%d' if metric == 'alive' else '$%dK'
            chart.yValueAxis.visibleGrid = True
            chart.yValueAxis.gridStrokeColor = colors.HexColor('#e4e8eb')
            for axis in (chart.xValueAxis, chart.yValueAxis):
                axis.labels.fontSize = 9
                axis.strokeColor = grey
            for i, color in enumerate((blue, orange)):
                chart.lines[i].strokeColor, chart.lines[i].strokeWidth = color, 2.2
            drawing.add(chart)
            drawing.add(String(x, y+191, title, fontName='Helvetica', fontSize=12))
    drawing.add(String(560, 29, 'Horizontal axes: voluntary cushion above the frozen failure floor. Lines connect tested points; these are not forecasts.',
                       fontName='Helvetica', fontSize=10, textAnchor='middle', fillColor=grey))
    renderSVG.drawToFile(drawing, str(OUT/'paired_reserve_frontier.svg'))
    if len(sys.argv) > 3:
        js = 'const sharp=require(process.argv[3]); sharp(process.argv[1], {density:140}).png().toFile(process.argv[2]).catch(e=>{console.error(e);process.exit(1)});'
        subprocess.run([sys.argv[2], '-e', js, str(OUT/'paired_reserve_frontier.svg'),
            str(OUT/'paired_reserve_frontier.png'), str(Path(sys.argv[3])/'sharp')], check=True)
    print(OUT/'paired_reserve_frontier.svg')


if __name__ == '__main__':
    main()
