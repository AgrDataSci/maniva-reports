"""Render a maniva report folder to HTML and PDF.

Python mirror of script/03-render.R, kept here because the first report was
rendered where R was not available. It follows the same steps and reads the same
report.yml, theme and stylesheet. Use the R script when R is available.

Usage, from the repository root
    python3 reports/<folder>/script/other-language/render.py reports/<folder>
Needs the Python packages markdown and pyyaml, and Google Chrome or Chromium.
"""
import html
import os
import re
import shutil
import subprocess
import sys

import markdown
import yaml

report = os.path.abspath(sys.argv[1])
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
cfg = yaml.safe_load(open(os.path.join(report, 'report.yml'), encoding='utf-8'))
theme = yaml.safe_load(open(os.path.join(root, 'themes', cfg.get('theme', 'cgiar') + '.yml'), encoding='utf-8'))
esc = html.escape

# 1. content, without the sections the authors hold back --------------------
text = open(os.path.join(report, 'content', 'report.md'), encoding='utf-8').read()
exclude = set(cfg.get('exclude_sections') or [])
parts = re.split(r'(?m)^(?=## )', text)
parts = [p for p in parts if not (p.startswith('## ') and p.splitlines()[0][3:].strip() in exclude)]
text = ''.join(p for p in parts if not p.startswith('# '))  # the title comes from report.yml

# 2. markdown to HTML ---------------------------------------------------------
body = markdown.markdown(text, extensions=['tables'])

# 3. figures, an image paragraph followed by a caption paragraph --------------
widths = cfg.get('figure_widths') or {}


def figure(m):
    alt, src, num, cap = m.group(1), m.group(2), m.group(3), m.group(4)
    w = widths.get(os.path.basename(src), 100)
    return (f'<figure><img src="{src}" alt="{alt}" style="width:{w}%">'
            f'<figcaption><span class="fignum">{num}</span> {cap}</figcaption></figure>')

body = re.sub(r'<p><img alt="([^"]*)" src="([^"]*)" ?/?></p>\s*<p><em>(Figure \d+)\. (.*?)</em></p>', figure, body, flags=re.S)

# 4. summary, a lead paragraph and finding cards ------------------------------
m = re.search(r'<h2>Summary</h2>(.*?)(?=<h2>|$)', body, flags=re.S)
if m:
    s = m.group(1)
    s = s.replace('<p>', '<p class="lead">', 1)
    u = re.search(r'<ul>(.*?)</ul>', s, flags=re.S)
    if u:
        cards = re.sub(r'<li>\s*(?:<p>)?(.*?)(?:</p>)?\s*</li>', r'<div class="card">\1</div>', u.group(1), flags=re.S)
        s = s.replace(u.group(0), f'<div class="cards">{cards}</div>', 1)
    body = body.replace(m.group(1), s, 1)

# 5. page breaks and wide tables ----------------------------------------------
for h in cfg.get('page_break_before') or []:
    body = body.replace(f'<h2>{esc(h)}</h2>', f'<h2 class="newpage">{esc(h)}</h2>')


def wide(m):
    return m.group(0).replace('<table>', '<table class="wide">', 1) if m.group(0).split('</thead>')[0].count('<th') >= 8 else m.group(0)

body = re.sub(r'<table>.*?</table>', wide, body, flags=re.S)

# 6. cover from report.yml ----------------------------------------------------
tiles = ''.join(f'<div class="tile"><div class="n">{esc(str(t["value"]))}</div><div class="l">{esc(t["label"])}</div></div>'
                for t in cfg.get('highlights') or [])
authors = cfg.get('authors') or []
author_line = ', '.join(authors[:-1]) + (' and ' if len(authors) > 1 else '') + (authors[-1] if authors else '')
inst = ' &middot; '.join(esc(i) for i in cfg.get('institutions') or [])
logos = ''.join(f'<img src="{esc(p)}" alt="">' for p in cfg.get('logos') or [])
status = f'<div class="status">{esc(cfg["status"])}</div>' if cfg.get('status') else ''
cover = f'''<section class="cover"><div class="top"><div class="kicker">{esc(cfg.get("kicker", "Technical report"))}</div>
<h1>{esc(cfg["title"])}</h1><div class="sub">{esc(cfg.get("subtitle", ""))}</div></div>
<div class="bottom"><div class="tiles">{tiles}</div><div class="authors">{esc(author_line)}</div><div class="inst">{inst}</div>
{f'<div class="logos">{logos}</div>' if logos else ''}
<div class="meta"><div>{esc(str(cfg.get("date", "")))}</div>{status}</div></div></section>'''

# 7. theme variables and stylesheet -------------------------------------------
c, f = theme['colours'], theme['fonts']
footer = cfg['title'].replace('"', "'")
variables = ':root {' + ''.join(f' --{k.replace("_", "-")}: {v};' for k, v in c.items()) + \
    f' --font-body: "{f["body"]}"; --font-display: "{f["display"]}"; --font-mono: "{f["mono"]}"; --footer-title: "{footer}"; }}'
css = open(os.path.join(root, 'template', 'report.css'), encoding='utf-8').read()
doc = f'''<!DOCTYPE html><html lang="{cfg.get("language", "en")}"><head><meta charset="utf-8">
<title>{esc(cfg["title"])}. {esc(cfg.get("subtitle", ""))}</title><style>{variables}
{css}</style></head><body>
{cover}
{body}
</body></html>'''
out_html = os.path.join(report, 'report.html')
open(out_html, 'w', encoding='utf-8').write(doc)

# 8. PDF with headless Chrome -------------------------------------------------
chrome = next((c for c in ('google-chrome', 'chromium', 'chromium-browser', 'chrome') if shutil.which(c)), None)
out_pdf = os.path.join(report, 'output', cfg.get('output_name', os.path.basename(report)) + '.pdf')
os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={out_pdf}', 'file://' + out_html], check=True, capture_output=True, timeout=300)
print(out_pdf)
