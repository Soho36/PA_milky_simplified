"""Embed frontier.json into the frontier page template.

Usage: build_frontier.py <scratch dir>
"""
from pathlib import Path
import sys

here = Path(sys.argv[1])
page = (here / 'frontier_template.html').read_text(encoding='utf-8')
data = (here / 'frontier.json').read_text(encoding='utf-8').replace('</', '<\\/')
assert page.count('__FRONTIER_JSON__') == 1
out = here / 'legacy_reserve_frontier.html'
out.write_text(page.replace('__FRONTIER_JSON__', data), encoding='utf-8')
print('wrote', out, out.stat().st_size)
