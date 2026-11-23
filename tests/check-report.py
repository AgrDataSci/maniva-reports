"""Check a rendered report before it is delivered.

Status: tested on the synthetic example, the worked examples and an internal pilot in November 2026.

Why
    The feedback of 23 November 2026 asked that an assistant verify every advertised file exists
    before it offers a link, and that checks tell descriptive screening from validated analysis.
    This script lists the files that exist, so the assistant links only those, and runs the
    mechanical part of the checklist in docs/report-standard.md. Looking at every page stays a
    human and assistant task.

Usage, from the repository root
    python3 tests/check-report.py reports/<folder> [settings.yml]

Exit status 1 when a check fails. Print the "Deliver" list to the user, nothing else.
"""
import glob, json, os, re, subprocess, sys
import yaml

report = os.path.abspath(sys.argv[1])
cfg = yaml.safe_load(open(os.path.join(report, sys.argv[2] if len(sys.argv) > 2 else 'report.yml'), encoding='utf-8'))
out = os.path.join(report, 'output')
name = cfg.get('output_name') or 'report'
fails, notes = [], []
fail = fails.append

# 1. the deliverables exist and are not empty
pdf, docx = os.path.join(out, name + '.pdf'), os.path.join(out, name + '.docx')
deliver = []
for f in (pdf, docx):
    if not os.path.exists(f) or os.path.getsize(f) < 5000:
        fail(f'Missing or empty {os.path.relpath(f, report)}. Do not offer it.')
    else:
        deliver.append(f)

# 2. analysis level and status agree
pf = os.path.join(out, 'preflight.json')
level = cfg.get('analysis_level') or (json.load(open(pf)).get('analysis_level') if os.path.exists(pf) else None)
if level is None:
    fail('No analysis level. Run tests/preflight.py first, or set analysis_level in report.yml.')
elif level != 'r-workflow' and cfg.get('approved'):
    fail(f'approved is true but the analysis level is {level}. Only a report computed with the R workflow leaves draft.')
notes.append(f'Analysis level {level}. Say it in one line when you deliver.')

# 3. every figure has its data, and every figure the text names exists
content = open(os.path.join(report, cfg.get('content') or 'content/report.md'), encoding='utf-8').read()
for fig in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content):
    if not os.path.exists(os.path.join(report, fig)):
        fail(f'Figure {fig} is named in the text but does not exist.')
    data = os.path.join(out, 'figure-data', os.path.basename(fig).rsplit('.', 1)[0] + '.csv')
    if not os.path.exists(data):
        fail(f'No figure data for {os.path.basename(fig)} in output/figure-data/.')
for tab in re.findall(r'<!-- insert: (\S+) -->', content):
    if not os.path.exists(os.path.join(report, tab)):
        fail(f'Table {tab} is inserted in the text but does not exist.')
if not os.path.exists(os.path.join(out, 'report-data.json')):
    fail('No output/report-data.json.')

# 4. prose rules on the text
if '—' in content:
    fail(f'{content.count(chr(0x2014))} em-dashes in the text.')
for bad in ('Maniva', 'Tricot'):
    hits = [m.start() for m in re.finditer(r'\b' + bad + r'\b', content)]
    if hits:
        fail(f'"{bad}" capitalised {len(hits)} times. Write it in lowercase.')
if not re.search(r'(?im)^## .*limitations', content) and 'Limitations' not in (cfg.get('exclude_sections') or []):
    fail('No section on limitations in the text.')

# 5. the PDF carries the machine-readable layer
if os.path.exists(pdf):
    try:
        att = subprocess.run(['qpdf', '--list-attachments', pdf], capture_output=True, text=True).stdout
        if 'report-data.json' not in att:
            fail('The PDF has no report-data.json attached.')
    except FileNotFoundError:
        notes.append('qpdf not installed, attachments not checked.')
    txt = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True).stdout
    for bad in ('nan', 'NaN', '{', '}'):
        n = len(re.findall(r'(?<![\w])' + re.escape(bad) + r'(?![\w])', txt))
        if n:
            fail(f'"{bad}" appears {n} times in the PDF text. A value or a template field did not resolve.')

print('Checks failed:' if fails else 'All checks passed.')
for m in fails: print('  FAIL ', m)
for m in notes: print('  note ', m)
print('Deliver')
for f in deliver: print('  ', os.path.relpath(f))
sys.exit(1 if fails else 0)
