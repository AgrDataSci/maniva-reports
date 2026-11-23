"""Render a maniva report folder to HTML and PDF, technical or annual type.

Python mirror of script/03-render.R, kept here because this report was rendered where R was not
available. It follows the same steps and reads the same report.yml, theme and stylesheet.
Use the R script when R is available.

Usage, from the repository root
    python3 reports/<folder>/script/other-language/render.py reports/<folder> [settings.yml]
Needs the Python packages markdown and pyyaml, and Google Chrome or Chromium.
"""
import csv
import html
import json
import os
import re
import shutil
import subprocess
import sys

import markdown
import yaml

report = os.path.abspath(sys.argv[1])
root = report
while not os.path.isdir(os.path.join(root, 'themes')):  # repository root, however deep the report folder is
    root = os.path.dirname(root)
# an optional second argument names another settings file in the report folder, such as a
# working-paper version of the same content
cfg = yaml.safe_load(open(os.path.join(report, sys.argv[2] if len(sys.argv) > 2 else 'report.yml'), encoding='utf-8'))
theme = yaml.safe_load(open(os.path.join(root, 'themes', cfg.get('theme', 'cgiar') + '.yml'), encoding='utf-8'))
esc = html.escape
annual = cfg.get('type') == 'annual'
wp = cfg.get('type') == 'working_paper'  # working paper, after the DTA working paper of October 2026
# analysis level, from report.yml or from output/preflight.json written by tests/preflight.py
_pf = os.path.join(report, 'output', 'preflight.json')
level = cfg.get('analysis_level') or (json.load(open(_pf)).get('analysis_level') if os.path.exists(_pf) else 'draft')
_co = yaml.safe_load(open(os.path.join(root, 'template', 'colophon.yml'), encoding='utf-8'))
level_text = (_co.get('analysis_levels') or {}).get(level, '')
if level != 'r-workflow' and not cfg.get('status') and not cfg.get('synthetic'):
    cfg['status'] = _co['draft_status']  # a report the R workflow did not compute is never presented as final
# authors are names, or entries with name, role and institution
people = [a if isinstance(a, dict) else {'name': a} for a in (cfg.get('authors') or [])]

# 1. content, without the sections the authors hold back --------------------
text = open(os.path.join(report, cfg.get('content') or 'content/report.md'), encoding='utf-8').read()
exclude = set(cfg.get('exclude_sections') or [])
parts = re.split(r'(?m)^(?=## )', text)
parts = [p for p in parts if not (p.startswith('## ') and p.splitlines()[0][3:].strip() in exclude)]
text = ''.join(p for p in parts if not p.startswith('# '))  # the title comes from report.yml

# 1b. tables inserted from result files, so no number is typed by hand ---------
# <!-- insert: output/tables/<file>.csv --> becomes a markdown table. The reporting fields get
# their own layout, with the value the programme gave beside the one maniva suggests.
def md_cell(v):
    if v is None or (isinstance(v, float) and v != v) or str(v).strip() in ('', 'nan', 'None'):
        return ''
    v = str(v)
    return v[:-2] if v.endswith('.0') and v[:-2].isdigit() else v.replace('|', '/')


def insert_table(m):
    path = os.path.join(report, m.group(1))
    rows = list(csv.DictReader(open(path, encoding='utf-8')))
    if os.path.basename(path) == 'reporting-fields.csv':
        out = ['| Field | Given by the programme | Suggested by maniva | Basis of the suggestion |', '|---|---|---|---|']
        group = None
        for r in rows:
            if r['group'] != group:
                group = r['group']; out.append(f'| **{group}** | | | |')
            sug = md_cell(r['suggested'])
            if r['group'] == 'Impact Areas' and sug:
                sug = {'0': '0, not targeted', '1': '1, significant', '2': '2, principal'}.get(sug, sug)
            basis = md_cell(r['rule']) + ('. ' + md_cell(r['evidence']) if md_cell(r['evidence']) else '')
            out.append(f'| {r["field"]} | {md_cell(r["given"]) or "Empty"} | {sug or "None"} | {basis} |')
        return '\n'.join(out)
    cols = list(rows[0].keys())
    return '\n'.join(['| ' + ' | '.join(cols) + ' |', '|' + '---|' * len(cols)] +
                     ['| ' + ' | '.join(md_cell(r[c]) for c in cols) + ' |' for r in rows])

text = re.sub(r'<!-- insert: ([^ ]+) -->', insert_table, text)

# 2. markdown to HTML ---------------------------------------------------------
body = markdown.markdown(text, extensions=['tables'])

# 3. figures, an image paragraph followed by a caption paragraph --------------
widths = cfg.get('figure_widths') or {}


def figure_data(src):
    """The numbers a figure draws, from output/figure-data/, or None."""
    f = os.path.join(report, 'output', 'figure-data', os.path.basename(src).replace('.png', '.csv'))
    return (os.path.relpath(f, report), list(csv.reader(open(f, encoding='utf-8')))) if os.path.exists(f) else (None, None)


def figure(m):
    alt, src, num, cap = m.group(1), m.group(2), m.group(3), m.group(4)
    w = widths.get(os.path.basename(src), 100)
    path, rows = figure_data(src)
    hidden = ''
    if rows:
        # the table is in the text layer of the PDF, for reporting tools and screen readers, and not shown
        hidden = (f'<div class="machine-data" data-figure="{esc(num)}" data-source="{esc(path)}"><p>Data of {esc(num)}, {esc(path)}</p><table>' +
                  ''.join('<tr>' + ''.join(f'<td>{esc(c)}</td>' for c in r) + '</tr>' for r in rows) + '</table></div>')
    return (f'<figure><img src="{src}" alt="{alt}" style="width:{w}%">'
            f'<figcaption><span class="fignum">{num}</span> {cap}</figcaption>{hidden}</figure>')

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

if wp:
    # a working paper has unnumbered sections, and its contents list the subsections too
    def wp_head(m):
        lvl, nm = m.group(1), re.sub(r'^Section \d+: ', '', m.group(3))
        heads.append(('h' + lvl, nm))
        return f'<h{lvl}{m.group(2)}>{nm}</h{lvl}>'
    body = re.sub(r'<h([23])((?: class="[^"]*")?)>(.*?)</h\1>', wp_head, body)
else:
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
    rf_path = os.path.join(report, 'output', 'tables', 'reporting-fields.csv')
    rf = list(csv.DictReader(open(rf_path, encoding='utf-8'))) if os.path.exists(rf_path) else []
    sug_ia = [r['field'] for r in rf if r['group'] == 'Impact Areas' and r['suggested'] == '1']
    sug_sdg = next((r['suggested'] for r in rf if r['group'] == 'SDGs'), '')
    sug_rl = next((r['suggested'] for r in rf if r['field'].startswith('Innovation readiness')), '')
    # a story about one result can carry its own suggestions, when the portfolio values do not fit it
    sg = sc.get('suggested') or {}
    sug_ia = sg.get('impact_areas', sug_ia); sug_sdg = sg.get('sdgs', sug_sdg); sug_rl = sg.get('readiness_level', sug_rl)

    def item(title, v, suggestion=None):
        v = [v] if isinstance(v, str) else (v or [])
        v = [x for x in v if x]
        if v:
            val = ' &middot; '.join(esc(x) for x in v)
        elif suggestion:
            val = '<span class="empty">Suggested by maniva, to confirm</span><br>' + esc(suggestion)
        else:
            val = '<span class="empty">Empty, to be set by the programme</span>'
        return f'<div><h4>{title}</h4>{val}</div>'
    panel = ('<aside class="panel">' + item('Primary Impact Area', sc.get('primary_impact_area')) +
             item('Other Impact Areas', sc.get('other_impact_areas'), ', '.join(sug_ia) + ' (significant)' if sug_ia else None) +
             item('SDGs', sc.get('sdgs'), sug_sdg) + item('Innovation readiness', sc.get('readiness_level'), sug_rl) +
             item('Geographic scope', sc.get('geographic_scope')) +
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

authors = [a['name'] for a in people]
author_line = ', '.join(authors[:-1]) + (' and ' if len(authors) > 1 else '') + (authors[-1] if authors else '')
inst = ' &middot; '.join(esc(i) for i in cfg.get('institutions') or [])
logos = ''.join(f'<img src="{esc(p)}" alt="">' for p in cfg.get('logos') or [])
status = f'<div class="status">{esc(cfg["status"])}</div>' if cfg.get('status') else ''
hl = cfg.get('highlights') or []
if wp:
    photo = cfg.get('cover_photo')
    pic = f'<img src="{esc(photo["file"])}" alt="">' if photo else ''
    cover = f'''<section class="cover wp"><div class="head">{f'<img src="{esc(cfg["logos"][0])}" alt="">' if cfg.get("logos") else '<span></span>'}
<div class="label">{esc(cfg.get("kicker", "Working Paper"))}</div></div>
<div class="band"><h1>{esc(cfg["title"])}</h1>{f'<div class="sub">{esc(cfg["subtitle"])}</div>' if cfg.get("subtitle") else ""}
<div class="by">{esc(author_line or cfg.get("corporate_author", ""))}</div><div class="date">{esc(str(cfg.get("date", "")))}</div>{status}</div>
<div class="field">{pic}</div></section>'''
elif cfg.get('cover_style') == 'annual':
    yr = [t for t in hl if t.get('period') == 'year']; cu = [t for t in hl if t.get('period') == 'cumulative']
    groups = (f'<div class="tilegroups"><div class="tilegroup year"><div class="gl">In {esc(str(cfg.get("reporting_year", "")))}</div>'
              f'<div class="tiles">{tiles_html(yr)}</div></div>' + (f'<div class="tilegroup cumulative"><div class="gl">Since the start, '
              f'{esc(str(cfg.get("period_label", "")))}</div><div class="tiles">{tiles_html(cu)}</div></div>' if cu else '') + '</div>')
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
back = ''
shared = yaml.safe_load(open(os.path.join(root, 'template', 'colophon.yml'), encoding='utf-8'))
if wp:
    co = cfg.get('colophon') or {}
    unit = theme.get('unit') or {}
    who = ''.join(f'<p>{esc(a["name"])}' + ''.join(f', {esc(a[k])}' for k in ('role', 'institution') if a.get(k)) + '</p>' for a in people) \
        or f'<p>{esc(cfg.get("corporate_author", ""))}</p>'
    credits = ''.join(f'<p>{esc(t)}</p>' for t in [
        ('Cover photograph. ' + cfg['cover_photo']['credit']) if (cfg.get('cover_photo') or {}).get('credit') else '',
        ('Back cover. ' + cfg['back_figure']['credit']) if (cfg.get('back_figure') or {}).get('credit') else ''] if t)
    front = f'''<section class="inside"><h4>Authors</h4>{who}
<h4>Acknowledgements</h4><p>{esc(co.get("acknowledgements") or "")} {esc(shared["trust_fund"]) if co.get("trust_fund", True) else ""}</p>
{f'<h4>{esc(unit["name"])}</h4><p>{esc(unit["about"])}</p>' if unit else ""}
<h4>Citation</h4><p>{esc(co.get("citation", ""))}</p>
{f'<p>{esc(co["handle"])}</p>' if co.get("handle") else ""}
<h4>Use of artificial intelligence</h4><p>{esc(shared["generated_by"])} {esc(shared["reviewed"] if cfg.get("approved") else shared["not_reviewed"])} {esc(co.get("ai_statement") or "")} {esc(level_text)}</p>
<p>Cite maniva as {esc(shared["maniva_citation"])}</p>
{f'<h4>About this document</h4><p>{esc(shared["synthetic"] if cfg.get("synthetic") else shared["example"])}</p>' if (cfg.get("example") or cfg.get("synthetic")) else ""}
<h4>Machine-readable content</h4><p>{esc(shared["machine_readable"])}</p>
<p>This publication is licensed under a Creative Commons Attribution 4.0 International License ({esc(co.get("licence", "CC BY 4.0"))}).</p>
<div class="photo-credits">{credits}</div></section>'''
    items = ''.join(f'<li class="{l}"><span class="nm">{nm}</span></li>' for l, nm in heads)
    front += f'<section class="contents"><h2>Contents</h2><ol>{items}</ol></section>'
    bf = cfg.get('back_figure')
    contacts = ''.join(f'<p><strong>{esc(x["name"])}</strong>' + ''.join(f', {esc(x[k])}' for k in ('role', 'institution') if x.get(k)) +
                       (f'. <span class="link">{esc(x["email"])}</span>' if x.get('email') else '') + '</p>' for x in cfg.get('contacts') or [])
    lockup = unit.get('logo_lockup')
    back = f'''<section class="back"><div class="field">{f'<img src="{esc(bf["file"])}" alt="">' if bf else ""}</div>
<div class="band"><p>{esc(shared["cgiar_about"])}</p>{f'<h4>Contact</h4>{contacts}' if contacts else ""}</div>
<div class="foot">{f'<img src="{esc(os.path.relpath(os.path.join(root, lockup), report))}" alt="">' if lockup else ""}</div></section>'''
if annual:
    co = cfg.get('colophon') or {}
    fund_path = os.path.join(report, 'output', 'tables', 'funders.csv')
    funders = list(csv.DictReader(open(fund_path, encoding='utf-8'))) if os.path.exists(fund_path) else []
    fund_txt = '; '.join(f'{esc(f["funder"])}, {esc(f["award"])} ({esc(f["number"])})' for f in funders)
    handle = esc(co.get('handle') or '') or '<em>Handle to be issued by CGSpace</em>'
    # texts that depend on the data module, overridable in report.yml colophon
    data_licence = co.get('data_licence', 'The trial data it uses are released under CC0 1.0.')
    evidence = co.get('evidence', 'This report presents evidence from the trial data it names.')
    ack = co.get('acknowledgements') or ('No real farmer, trial or funder is behind this synthetic report.' if cfg.get('synthetic') else
          'We thank the farmers who tested the varieties on their own farms and shared their assessments. The trials were funded by ' + fund_txt + '.')
    maps_note = '' if co.get('no_maps') else '<p>Boundaries on the maps are indicative and do not imply any opinion on the legal status of any country, territory or area, or on the delimitation of its frontiers.</p>'
    front = f'''<section class="colophon"><div class="cite">
<p><strong>Author.</strong> {esc(cfg.get("corporate_author", ""))}</p>
<p><strong>Title.</strong> {esc(co.get("title", cfg["title"]))}</p>
<p><strong>Suggested citation.</strong> {esc(co.get("citation", ""))}</p>
<p>{handle}</p>
<p>This publication is licensed under a Creative Commons Attribution 4.0 International License ({esc(co.get("licence", "CC BY 4.0"))}). {esc(data_licence)}</p></div>
<h4>Disclaimers</h4>
<p>{esc(evidence)} Views and interpretations are those of the authors and do not necessarily represent those of their institutions or funders.</p>
{maps_note}
{f'<h4>About this document</h4><p>{esc(shared["synthetic"] if cfg.get("synthetic") else shared["example"])}</p>' if (cfg.get("example") or cfg.get("synthetic")) else ""}
<h4>Use of artificial intelligence</h4><p>{esc(shared["generated_by"])} {esc(shared["reviewed"] if cfg.get("approved") else shared["not_reviewed"])} {esc(co.get("ai_statement") or "")} {esc(level_text)}</p>
<p><strong>Cite maniva as</strong> {esc(shared["maniva_citation"])}</p>
<h4>Machine-readable content</h4><p>{esc(shared["machine_readable"])}</p>
<div class="ack"><h4>Acknowledgements</h4><p>{esc(ack)}</p></div></section>'''
    items = ''.join(f'<li><span class="lab">{esc(l) if l else ""}</span><span class="nm">{nm}</span></li>' for l, nm in heads)
    front += f'<section class="contents"><h2>Table of contents</h2><ol>{items}</ol></section>'

# 10. theme variables and stylesheet -----------------------------------------
c, f = theme['colours'], theme['fonts']
st_cols = {f'status-{k.replace("_", "-")}': v for k, v in (theme.get('status') or {}).items()}
footer = (cfg.get('kicker', '') + '. ' + cfg['title']).replace('"', "'") if annual else cfg['title'].replace('"', "'")
if wp:
    footer = ''


def pattern_svg(w, h, n, seed, ground, mark, stroke=2.2):
    """Pattern of short curved strokes in two theme colours, drawn here, not copied from any artwork."""
    import base64, math, random
    rnd = random.Random(seed); paths = []
    for _ in range(n):
        x, y, a = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.6, 1.2)
        dx, dy = 7 * math.cos(a), -7 * math.sin(a)
        paths.append(f'<path d="M{x:.1f} {y:.1f} q{dx * .6 - 2:.1f} {dy * .6:.1f} {dx:.1f} {dy:.1f}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{ground}"/>'
           f'<g fill="none" stroke="{mark}" stroke-width="{stroke}" stroke-linecap="round">{"".join(paths)}</g></svg>')
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'


def strip_svg(ground, mark):
    """Thin wavy lines for the page strip."""
    import base64, math
    lines = ''.join(f'<path d="M{x} 0 ' + ' '.join(f'L{x + 2.2 * math.sin(y / 9 + x):.1f} {y}' for y in range(0, 300, 6)) + '"/>' for x in (6, 14, 22))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="30" height="300"><rect width="30" height="300" fill="{ground}"/>'
           f'<g fill="none" stroke="{mark}" stroke-width="0.7" opacity=".55">{lines}</g></svg>')
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'

extra = ''
page_css = ''
if wp and 'pattern' in c:
    # the strip down the right edge of every text page lives in the page margin boxes, the only place
    # Chrome prints outside the page area. The cover and back cover pages switch it off.
    strip = f'content: ""; background: {strip_svg(c["pattern"], c["pattern_mark"])} 0 0 / 9mm 90mm repeat-y;'
    boxes = ('right-top', 'right-middle', 'right-bottom', 'top-right-corner', 'bottom-right-corner')
    page_css = ('@page { margin: 21mm 9mm 20mm 19mm; ' + ' '.join(f'@{b} {{ {strip} }}' for b in boxes) + ' }\n' +
                '@page :first { ' + ' '.join(f'@{b} {{ content: none; background: none; }}' for b in boxes) + ' }\n' +
                '@page full { ' + ' '.join(f'@{b} {{ content: none; background: none; }}' for b in boxes) + ' }\n')
if 'pattern' in c:
    extra = f' --pattern: {pattern_svg(120, 120, 34, 7, c["pattern"], c["pattern_mark"])} 0 0 / 34mm 34mm; --strip: {strip_svg(c["pattern"], c["pattern_mark"])} 0 0 / 100% 100%;'
variables = ':root {' + ''.join(f' --{k.replace("_", "-")}: {v};' for k, v in c.items()) + \
    ''.join(f' --{k}: {v};' for k, v in st_cols.items()) + \
    f' --font-body: "{f["body"]}"; --font-display: "{f["display"]}"; --font-mono: "{f["mono"]}"; --footer-title: "{footer}";{extra} }}'
css = open(os.path.join(root, 'template', 'report.css'), encoding='utf-8').read()
doc = f'''<!DOCTYPE html><html lang="{cfg.get("language", "en")}"><head><meta charset="utf-8">
<title>{esc(cfg["title"])}. {esc(cfg.get("subtitle", ""))}</title><style>{variables}
{css}
{page_css}</style></head><body{' class="wp"' if wp else ''}>
{cover}
{front}
{body}
{back}
</body></html>'''
out_html = os.path.join(report, 'report.html')
open(out_html, 'w', encoding='utf-8').write(doc)

# 11. PDF with headless Chrome ------------------------------------------------
chrome = next((c for c in ('google-chrome', 'chromium', 'chromium-browser', 'chrome') if shutil.which(c)), None)
out_pdf = os.path.join(report, 'output', (cfg.get('output_name') or os.path.basename(report)) + '.pdf')
os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
subprocess.run([chrome, '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                f'--print-to-pdf={out_pdf}', 'file://' + out_html], check=True, capture_output=True, timeout=300)

# 11b. machine-readable summary and attachments -------------------------------
# output/report-data.json holds the reporting fields, the PRMS candidates and an index of the figure
# data. It and every aggregated result table are attached to the PDF, so a reporting tool can read
# them without parsing the layout. No participant-level table is attached.
def read_csv(p):
    return list(csv.DictReader(open(p, encoding='utf-8'))) if os.path.exists(p) else []

tab = os.path.join(report, 'output', 'tables'); figd = os.path.join(report, 'output', 'figure-data')
summary = dict(
    schema='maniva-reports/report-data/0.1', title=cfg['title'], subtitle=cfg.get('subtitle'), type=cfg.get('type', 'technical'),
    reporting_year=cfg.get('reporting_year'), period=cfg.get('period_label'), corporate_author=cfg.get('corporate_author'),
    authors=cfg.get('authors') or [], institutions=cfg.get('institutions') or [], status=cfg.get('status'),
    licence=(cfg.get('colophon') or {}).get('licence', 'CC BY 4.0'), handle=(cfg.get('colophon') or {}).get('handle') or None,
    data_source=cfg['data']['source'], generated_with='maniva-reports', maniva_citation=shared['maniva_citation'],
    overview=read_csv(os.path.join(tab, 'overview.csv')), reporting_fields=read_csv(os.path.join(tab, 'reporting-fields.csv')),
    prms_candidates=read_csv(os.path.join(tab, 'prms-results.csv')),
    figures=[dict(file='figures/' + f.replace('.csv', '.png'), data='figure-data/' + f) for f in sorted(os.listdir(figd))] if os.path.isdir(figd) else [])
json_path = os.path.join(report, 'output', 'report-data.json')
json.dump(summary, open(json_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
attach = [json_path] + [os.path.join(figd, f) for f in sorted(os.listdir(figd))] if os.path.isdir(figd) else [json_path]
attach += [os.path.join(tab, f) for f in sorted(os.listdir(tab)) if f.endswith('.csv') and f != 'map-points.csv'] if os.path.isdir(tab) else []
if shutil.which('qpdf'):
    cmd = ['qpdf', out_pdf, '--replace-input']
    for a in attach:
        key = os.path.relpath(a, os.path.join(report, 'output'))
        cmd += ['--add-attachment', a, '--key=' + key, '--filename=' + key, '--mimetype=' + ('application/json' if a.endswith('.json') else 'text/csv'), '--']
    subprocess.run(cmd, check=True)
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
    path, rows = figure_data(src)
    if rows:
        annex.append((cap.split('.')[0], path, rows))
    return f'![]({src}){{width={w:.1f}cm}}\n\n*{cap}*'

annex = []
md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)\s*\n\s*\n\*(Figure \d+\..*?)\*', docx_image, md, flags=re.S)
# the Word file carries the data behind the figures as a visible annex, one table per figure.
# The PDF carries the same data as hidden text and as attachments.
if annex:
    md += PAGE + '\n# Annex. Data behind the figures\n\nThe numbers each figure draws, as published with the report in `output/figure-data/`.\n'
    for num, path, rows in sorted(annex, key=lambda a: int(a[0].split()[1])):
        md += f'\n## {num}\n\nFile `{path}`.\n\n| ' + ' | '.join(rows[0]) + ' |\n|' + '---|' * len(rows[0]) + '\n' + \
              '\n'.join('| ' + ' | '.join(md_cell(c) for c in r) + ' |' for r in rows[1:]) + '\n'
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

byline = cfg.get('corporate_author') or ', '.join(a['name'] for a in people)
if wp:
    byline = ', '.join(a['name'] for a in people) or cfg.get('corporate_author', '')
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
if wp:
    unit = theme.get('unit') or {}
    front_md = f'''{logo_md}

**{cfg.get("kicker", "Working Paper")}**

{styled("Title", cfg["title"])}
{styled("Subtitle", cfg.get("subtitle", ""))}
{styled("Author", byline)}
{styled("Date", str(cfg.get("date", "")))}
{"**" + cfg["status"] + "**" if cfg.get("status") else ""}
''' + PAGE + '**Authors**\n\n' + '\n\n'.join(a['name'] + ''.join(', ' + a[k] for k in ('role', 'institution') if a.get(k)) for a in people) + \
        f'''

**Acknowledgements**

{co.get("acknowledgements") or ""} {shared["trust_fund"] if co.get("trust_fund", True) else ""}

{"**" + unit["name"] + "**" + chr(10) + chr(10) + unit["about"] if unit else ""}

**Citation**

{co.get("citation", "")}

**Use of artificial intelligence.** {shared["generated_by"]} {shared["reviewed"] if cfg.get("approved") else shared["not_reviewed"]} {co.get("ai_statement") or ""} {level_text}

**Cite maniva as** {shared["maniva_citation"]}

**Machine-readable content.** {shared["machine_readable"]} In this Word file the figure data are in the annex.
'''
    md = re.sub(r'(?m)^## Section \d+: ', '## ', md)
if annual:
    front_md += PAGE + f'''**Author.** {cfg.get("corporate_author", "")}

**Title.** {co.get("title", cfg["title"])}

**Suggested citation.** {co.get("citation", "")}

{co.get("handle") or "*Handle to be issued by CGSpace*"}

This publication is licensed under a Creative Commons Attribution 4.0 International License ({co.get("licence", "CC BY 4.0")}). {co.get("data_licence", "The trial data it uses are released under CC0 1.0.")}

{"**About this document.** " + (shared["synthetic"] if cfg.get("synthetic") else shared["example"]) + chr(10) + chr(10) if (cfg.get("example") or cfg.get("synthetic")) else ""}**Use of artificial intelligence.** {shared["generated_by"]} {shared["reviewed"] if cfg.get("approved") else shared["not_reviewed"]} {co.get("ai_statement") or ""} {level_text}

**Cite maniva as** {shared["maniva_citation"]}

**Machine-readable content.** {shared["machine_readable"]} In this Word file the figure data are in the annex.
'''
src_md = os.path.join(report, 'report-docx.md')
# numbered sections of the annual type open a new page themselves
open(src_md, 'w', encoding='utf-8').write(front_md + ('' if annual else PAGE) + md)
out_docx = out_pdf[:-4] + '.docx'
subprocess.run(['pandoc', src_md, '-f', 'markdown', '-o', out_docx, '--reference-doc', os.path.join(root, 'template', 'reference.docx'),
                '--resource-path', report], check=True)
os.remove(src_md)
print(out_docx)
