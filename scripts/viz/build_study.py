"""Embed a study JSON into the explorer template.

Usage: build_study.py <scratch dir> <study_key.json> <out.html>
"""
from pathlib import Path
import json
import sys

here = Path(sys.argv[1])
data_name, out_name = sys.argv[2:4]
page = (here / 'study_template.html').read_text(encoding='utf-8')
data = (here / data_name).read_text(encoding='utf-8')
meta = json.loads(data)['meta']
for key, value in (('__TITLE__', meta['title']), ('__STUDY_JSON__', data.replace('</', '<\\/'))):
    assert page.count(key) == 1, key
    page = page.replace(key, value)
out = here / out_name
out.write_text(page, encoding='utf-8')
print(f"wrote {out} {out.stat().st_size / 1024:,.0f} KB")
