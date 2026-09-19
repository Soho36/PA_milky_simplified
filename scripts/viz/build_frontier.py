"""Embed frontier.json into the frontier page template.

Usage: build_frontier.py <scratch dir> [label, e.g. 'blocked copying']
"""
from pathlib import Path
import sys

here = Path(sys.argv[1])
page = (here / 'frontier_template.html').read_text(encoding='utf-8')
data = (here / 'frontier.json').read_text(encoding='utf-8').replace('</', '<\\/')
assert page.count('__FRONTIER_JSON__') == 1
out = here / 'legacy_reserve_frontier.html'
page = page.replace('__FRONTIER_JSON__', data)
if len(sys.argv) > 2:
    # Say which execution tree the page shows, in the tab and the heading.
    for tag in ('</title>', '</h1>'):
        assert page.count(tag) == 1, tag
        page = page.replace(tag, f' — {sys.argv[2]}{tag}')
out.write_text(page, encoding='utf-8')
print('wrote', out, out.stat().st_size)
