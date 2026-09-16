"""Embed routing.json into the routing page template.

Usage: build_routing.py <scratch dir>
"""
from pathlib import Path
import sys

here = Path(sys.argv[1])
tpl = Path(__file__).resolve().parent / 'templates' / 'routing_template.html'
page = tpl.read_text(encoding='utf-8')
data = (here / 'routing.json').read_text(encoding='utf-8').replace('</', r'<\/')
assert page.count('__ROUTING_JSON__') == 1
out = here / 'routing_matched_exposure.html'
out.write_text(page.replace('__ROUTING_JSON__', data), encoding='utf-8')
print(f'wrote {out} {out.stat().st_size / 1024:,.0f} KB')
