"""Embed fixed_pool.json into the fixed-pool page template.

Usage: build_fixed_pool.py <scratch dir>
"""
from pathlib import Path
import sys

here = Path(sys.argv[1])
tpl = Path(__file__).resolve().parent / 'templates' / 'fixed_pool_template.html'
page = tpl.read_text(encoding='utf-8')
data = (here / 'fixed_pool.json').read_text(encoding='utf-8').replace('</', r'<\/')
assert page.count('__FIXED_POOL_JSON__') == 1
out = here / 'routing_fixed_pool.html'
out.write_text(page.replace('__FIXED_POOL_JSON__', data), encoding='utf-8')
print(f'wrote {out} {out.stat().st_size / 1024:,.0f} KB')
