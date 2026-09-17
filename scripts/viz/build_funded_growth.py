"""Embed funded_growth.json into the funded-growth page template.

Usage: build_funded_growth.py <scratch dir>
"""
from pathlib import Path
import sys

here = Path(sys.argv[1])
tpl = Path(__file__).resolve().parent / 'templates' / 'funded_growth_template.html'
page = tpl.read_text(encoding='utf-8')
data = (here / 'funded_growth.json').read_text(encoding='utf-8').replace('</', r'<\/')
assert page.count('__FUNDED_GROWTH_JSON__') == 1
out = here / 'routing_funded_growth.html'
out.write_text(page.replace('__FUNDED_GROWTH_JSON__', data), encoding='utf-8')
print(f'wrote {out} {out.stat().st_size / 1024:,.0f} KB')
