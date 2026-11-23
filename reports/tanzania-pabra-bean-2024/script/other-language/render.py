"""Render a maniva report folder to HTML and PDF, technical or annual type.

Python mirror of script/03-render.R, kept here because this report was rendered where R was not
available. It follows the same steps and reads the same report.yml, theme and stylesheet.
Use the R script when R is available.

Usage, from the repository root
    python3 reports/<folder>/script/other-language/render.py reports/<folder>
Needs the Python packages markdown and pyyaml, and Google Chrome or Chromium.
"""
import csv
import html
import os
import re
import shutil
import subprocess
import sys

import markdown
import yaml

report = os.path.abspath(sys.argv[1])
root = os.path.abspath(os.path.join(report, '..', '..'))
cfg = yaml.safe_load(open(os.path.join(report, 'report.yml'), encoding='utf-8'))
theme = yaml.safe_load(open(os.path.join(root, 'themes', cfg.get('theme', 'cgiar') + '.yml'), encoding='utf-8'))
esc = html.escape
annual = cfg.get('type') == 'annual'

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
m = re.search(r'<h2>(?:Section \d+: )?(?:Summary|Fact sheet and executive summary)</h2>(.*?)(?=<h2>|$)', body, flags=re.S)
if m:
    s = m.group(1)
    u = re.search(r'<ul>(.*?)</ul>', s, flags=re.S)
    if u and '<strong>' in u.group(1):
        cards = re.sub(r'<li>\s*(?:<p>)?(.*?)(?:</p>)?\s*</li>', r'<div class="card">\1</div>', u.group(1), flags=re.S)
        s2 = s.replace(u.group(0), f'<div class="cards">{cards}</div>', 1)
        body = body.replace(s, s2, 1)

# 5. layout markers written in the markdown as HTML comments -------------------
# <!-- class: factsheet --> before a table gives the table that class
body = re.sub(r'<!-- class: ([\w-]+) -->\s*<table>', r'<table class="\1">', body)
# <!-- split --> before a figure and a table sets them side by side
body = re.sub(r'<!-- split -->\s*(<figure>.*?</figure>)\s*(<table.*?</table>)', r'<div class="split">\1\2</div>', body, flags=re.S)
# status chips, only where the authors wrote them
for word in ('on track', 'delayed', 'off track'):
    body = body.replace(f'[{word}]', f'<span class="chip {word.replace(" ", "-")}">{word.capitalize()}</span>')

# 6. page breaks, numbered sections and wide tables ---------------------------
for h in cfg.get('page_break_before') or []:
    body = body.replace(f'<h2>{esc(h)}</h2>', f'<h2 class="newpage">{esc(h)}</h2>')
heads = []


def section(m):
    lab, nm = m.group(1), m.group(2)
    heads.append((lab, nm))
    if lab:
        return f'<h2 class="section"><span class="lab">{lab}:</span> {nm}</h2>'
    return f'<h2 class="unnumbered">{nm}</h2>' if annual else m.group(0)

body = re.sub(r'<h2>(?:(Section \d+): )?(.*?)</h2>', section, body)


def wide(m):
    return m.group(0).replace('<table>', '<table class="wide">', 1) if m.group(0).split('</thead>')[0].count('<th') >= 8 else m.group(0)

body = re.sub(r'<table>.*?</table>', wide, body, flags=re.S)

# 7. key result story, headline, standfirst, two columns and the side panel ---
st = re.search(r'(<h2 class="section"><span class="lab">Section \d+:</span> Key result story</h2>)(.*?)(?=<h2|$)', body, flags=re.S)
if st:
    inner = st.group(2)
    inner = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="headline">\1</h3>', inner, count=1)
    inner = re.sub(r'(</h3>\s*)<p>', r'\1<p class="standfirst">', inner, count=1)
    hm = re.search(r'^(.*?<p class="standfirst">.*?</p>)(.*)$', inner, flags=re.S)
    sc = cfg.get('story') or {}

    def item(title, v):
        v = [v] if isinstance(v, str) else (v or [])
        v = [x for x in v if x]
        val = ' &middot; '.join(esc(x) for x in v) if v else '<span class="empty">To be set by the programme</span>'
        return f'<div><h4>{title}</h4>{val}</div>'
    panel = ('<aside class="panel">' + item('Primary Impact Area', sc.get('primary_impact_area')) +
             item('Other Impact Areas', sc.get('other_impact_areas')) + item('Geographic scope', sc.get('geographic_scope')) +
             item('Contributing programmes and funders', sc.get('contributing')) + item('Contributing centres', sc.get('centres')) +
             item('Contributing partners', sc.get('partners')) + '</aside>')
    if hm:
        rest = hm.group(2)
        fig = re.search(r'<figure>.*?</figure>', rest, flags=re.S)
        figure_html = fig.group(0) if fig else ''
        rest = rest.replace(figure_html, '') if fig else rest
        inner = (hm.group(1) + f'<div class="storygrid"><div><div class="storytext">{rest}</div>{figure_html}</div>{panel}</div>')
    body = body.replace(st.group(0), f'<section class="story">{st.group(1)}{inner}</section>')

# 8. cover from report.yml ----------------------------------------------------
def tiles_html(ts):
    return ''.join(f'<div class="tile"><div class="n">{esc(str(t["value"]))}</div><div class="l">{esc(t["label"])}</div></div>' for t in ts)

authors = cfg.get('authors') or []
author_line = ', '.join(authors[:-1]) + (' and ' if len(authors) > 1 else '') + (authors[-1] if authors else '')
inst = ' &middot; '.join(esc(i) for i in cfg.get('institutions') or [])
logos = ''.join(f'<img src="{esc(p)}" alt="">' for p in cfg.get('logos') or [])
status = f'<div class="status">{esc(cfg["status"])}</div>' if cfg.get('status') else ''
hl = cfg.get('highlights') or []
if cfg.get('cover_style') == 'annual':
    yr = [t for t in hl if t.get('period') == 'year']; cu = [t for t in hl if t.get('period') == 'cumulative']
    groups = (f'<div class="tilegroups"><div class="tilegroup year"><div class="gl">In {esc(str(cfg.get("reporting_year", "")))}</div>'
              f'<div class="tiles">{tiles_html(yr)}</div></div><div class="tilegroup cumulative"><div class="gl">Since the start, '
              f'{esc(str(cfg.get("period_label", "")))}</div><div class="tiles">{tiles_html(cu)}</div></div></div>')
    photo = cfg.get('cover_photo')
    pic = (f'<img src="{esc(photo["file"])}" alt=""><div class="credit">{esc(photo.get("credit", ""))}</div>' if photo
           else '<div class="rings"></div><div class="rings2"></div>')
    cover = f'''<section class="cover annual"><div class="logobar">{logos}</div>
<div class="band"><div class="programme">{esc(cfg.get("programme_label", ""))}</div><div class="kicker">{esc(cfg.get("kicker", ""))}</div>
<h1>{esc(cfg["title"])}</h1><div class="sub">{esc(cfg.get("subtitle", ""))}</div></div>
<div class="photo">{pic}</div>
<div class="bottom">{groups}<div class="inst">{inst}</div>
<div class="meta"><div>{esc(str(cfg.get("date", "")))}</div>{status}</div></div></section>'''
else:
    cover = f'''<section class="cover"><div class="top"><div class="kicker">{esc(cfg.get("kicker", "Technical report"))}</div>
<h1>{esc(cfg["title"])}</h1><div class="sub">{esc(cfg.get("subtitle", ""))}</div></div>
<div class="bottom"><div class="tiles">{tiles_html(hl)}</div><div class="authors">{esc(author_line)}</div><div class="inst">{inst}</div>
{f'<div class="logos">{logos}</div>' if logos else ''}
<div class="meta"><div>{esc(str(cfg.get("date", "")))}</div>{status}</div></div></section>'''

# 9. colophon and contents, annual type only -----------------------------------
front = ''
if annual:
    co = cfg.get('colophon') or {}
    fund_path = os.path.join(report, 'output', 'tables', 'funders.csv')
    funders = list(csv.DictReader(open(fund_path, encoding='utf-8'))) if os.path.exists(fund_path) else []
    fund_txt = '; '.join(f'{esc(f["funder"])}, {esc(f["award"])} ({esc(f["number"])})' for f in funders)
    handle = esc(co.get('handle') or '') or '<em>Handle to be issued by CGSpace</em>'
    front = f'''<section class="colophon"><div class="cite">
<p><strong>Author.</strong> {esc(cfg.get("corporate_author", ""))}</p>
<p><strong>Title.</strong> {esc(co.get("title", cfg["title"]))}</p>
<p><strong>Suggested citation.</strong> {esc(co.get("citation", ""))}</p>
<p>{handle}</p>
<p>This publication is licensed under a Creative Commons Attribution 4.0 International License ({esc(co.get("licence", "CC BY 4.0"))}). The trial data it uses are released under CC0 1.0.</p></div>
<h4>Disclaimers</h4>
<p>This report presents evidence from the trial data it names. Views and interpretations are those of the authors and do not necessarily represent those of their institutions or funders.</p>
<p>Boundaries on the maps are indicative and do not imply any opinion on the legal status of any country, territory or area, or on the delimitation of its frontiers.</p>
<h4>Use of artificial intelligence</h4><p>{esc(co.get("ai_statement", ""))}</p>
<div class="ack"><h4>Acknowledgements</h4><p>We thank the farmers who tested the varieties on their own farms and shared their assessments.
The trials were funded by {fund_txt}.</p></div></section>'''
    items = ''.join(f'<li><span class="lab">{esc(l) if l else ""}</span><span class="nm">{nm}</span></li>' for l, nm in heads)
    front += f'<section class="contents"><h2>Table of contents</h2><ol>{items}</ol></section>'

# 10. theme variables and stylesheet -----------------------------------------
c, f = theme['colours'], theme['fonts']
st_cols = {f'status-{k.replace("_", "-")}': v for k, v in (theme.get('status') or {}).items()}
footer = (cfg.get('kicker', '') + '. ' + cfg['title']).replace('"', "'") if annual else cfg['title'].replace('"', "'")
variables = ':root {' + ''.join(f' --{k.replace("_", "-")}: {v};' for k, v in c.items()) + \
    ''.join(f' --{k}: {v};' for k, v in st_cols.items()) + \
    f' --font-body: "{f["body"]}"; --font-display: "{f["display"]}"; --font-mono: "{f["mono"]}"; --footer-title: "{footer}"; }}'
css = open(os.path.join(root, 'template', 'report.css'), encoding='utf-8').read()
doc = f'''<!DOCTYPE html><html lang="{cfg.get("language", "en")}"><head><meta charset="utf-8">
<title>{esc(cfg["title"])}. {esc(cfg.get("subtitle", ""))}</title><style>{variables}
{css}</style></head><body>
{cover}
{front}
{body}
</body></html>'''
out_html = os.path.join(report, 'report.html')
open(out_html, 'w', encoding='utf-8').write(doc)

# 11. PDF with headless Chrome ------------------------------------------------
chrome = next((c for c in ('google-chrome', 'chromium', 'chromium-browser', 'chrome') if shutil.which(c)), None)
out_pdf = os.path.join(report, 'output', (cfg.get('output_name') or os.path.basename(report)) + '.pdf')
os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={out_pdf}', 'file://' + out_html], check=True, capture_output=True, timeout=300)
print(out_pdf)

# 12. Word version, for comments and edits ------------------------------------
# Same text as the PDF, with the styles of template/reference.docx. Figures and logos go in as
# PNG. Layout markers become plain Word content, and status chips stay as their words.
PAGE = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'
md = text
split_figs = set(re.findall(r'<!-- split -->\s*!\[[^\]]*\]\(([^)]+)\)', md))
md = re.sub(r'<!--.*?-->\n?', '', md, flags=re.S)


def docx_image(m):
    alt, src, cap = m.group(1), m.group(2), m.group(3)
    w = (60 if src in split_figs else widths.get(os.path.basename(src), 100)) * 16.5 / 100
    return f'![]({src}){{width={w:.1f}cm}}\n\n*{cap}*'

md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)\s*\n\s*\n\*(Figure \d+\..*?)\*', docx_image, md, flags=re.S)
if annual:
    md = re.sub(r'(?m)^## (Section \d+: )', PAGE + r'# \1', md)
    md = re.sub(r'(?m)^## ', '# ', md)
    md = re.sub(r'(?m)^### ', '## ', md)
    sc = cfg.get('story') or {}

    def val(v):
        v = [v] if isinstance(v, str) else (v or [])
        v = [x for x in v if x]
        return '; '.join(v) if v else '*To be set by the programme*'
    panel = '\n'.join(f'- **{t}.** {val(sc.get(k))}' for t, k in [
        ('Primary Impact Area', 'primary_impact_area'), ('Other Impact Areas', 'other_impact_areas'),
        ('Geographic scope', 'geographic_scope'), ('Contributing programmes and funders', 'contributing'),
        ('Contributing centres', 'centres'), ('Contributing partners', 'partners')])
    md = re.sub(r'(# Section \d+: Key result story\n.*?)(?=\n# |\Z)', lambda m: m.group(1).rstrip() + '\n\n' + panel + '\n', md, count=1, flags=re.S)

hl = cfg.get('highlights') or []
tile_rows = '\n'.join(f'| {t["label"].capitalize()} | {t["value"]} | {"In " + str(cfg.get("reporting_year")) if t.get("period") == "year" else (cfg.get("period_label") or "")} |'
                      for t in hl)
logo_md = ' '.join(f'![]({re.sub(r"[.]svg$", ".png", p)}){{height=1.4cm}}' for p in cfg.get('logos') or [])
co = cfg.get('colophon') or {}
def styled(style, txt):
    return f'::: {{custom-style="{style}"}}\n{txt}\n:::\n' if txt else ''

byline = cfg.get('corporate_author') or ', '.join(cfg.get('authors') or [])
front_md = f'''{logo_md}

**{cfg.get("kicker", "")}**

{styled("Title", cfg["title"])}
{styled("Subtitle", cfg.get("subtitle", ""))}
{styled("Author", byline)}
{styled("Date", str(cfg.get("date", "")))}
{"**" + cfg["status"] + "**" if cfg.get("status") else ""}

| Highlight | Value | Period |
|---|---:|---|
{tile_rows}

{" · ".join(cfg.get("institutions") or [])}
'''
if annual:
    front_md += PAGE + f'''**Author.** {cfg.get("corporate_author", "")}

**Title.** {co.get("title", cfg["title"])}

**Suggested citation.** {co.get("citation", "")}

{co.get("handle") or "*Handle to be issued by CGSpace*"}

This publication is licensed under a Creative Commons Attribution 4.0 International License ({co.get("licence", "CC BY 4.0")}). The trial data it uses are released under CC0 1.0.

**Use of artificial intelligence.** {co.get("ai_statement", "")}
'''
src_md = os.path.join(report, 'report-docx.md')
# numbered sections of the annual type open a new page themselves
open(src_md, 'w', encoding='utf-8').write(front_md + ('' if annual else PAGE) + md)
out_docx = out_pdf[:-4] + '.docx'
subprocess.run(['pandoc', src_md, '-f', 'markdown', '-o', out_docx, '--reference-doc', os.path.join(root, 'template', 'reference.docx'),
                '--resource-path', report], check=True)
os.remove(src_md)
print(out_docx)
