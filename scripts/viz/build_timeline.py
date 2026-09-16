"""Embed a replay JSON into the page template.

Usage: build_timeline.py <scratch dir> <data.json> <out.html> <title> <headline>
"""
from pathlib import Path
import json
import sys

here = Path(sys.argv[1])
data_name, out_name, title, headline = sys.argv[2:6]
page = (here / 'timeline_template.html').read_text(encoding='utf-8')
data = (here / data_name).read_text(encoding='utf-8')
folder = json.loads(data)['meta']['folder']
# Text placeholders first, the JSON last, so nothing inside the data is ever substituted.
for key, value in (('__TITLE__', title), ('__FOLDER__', folder), ('__HEADLINE__', headline),
                   ('__TIMELINE_JSON__', data.replace('</', '<\\/'))):
    assert page.count(key) == 1, key
    page = page.replace(key, value)
out = here / out_name
out.write_text(page, encoding='utf-8')
print('wrote', out, out.stat().st_size)
