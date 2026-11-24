"""Preflight check of a report, run before any analysis.

Status: tested on the synthetic example and on the tricot-data release of November 2026.

Why
    A session with another AI assistant (feedback of 23 November 2026) ran a report where R was
    missing, guessed a metadata field and crashed, and then presented a descriptive Python draft as a
    maniva report. This script settles three things before the first line of analysis.
    1. Which analysis level the session can reach, from the tools that are installed.
    2. Whether the trial files carry the fields the workflow reads, and which fallbacks apply.
    3. Which quality flags the data carry, so the analysis excludes them on purpose.
    It writes output/preflight.json. The renderer prints the analysis level in the colophon and keeps
    the report a draft unless the level is r-workflow.

Usage, from the repository root
    python3 tests/preflight.py reports/<folder> [path/to/tricot-data/]

Analysis levels
    r-workflow   R and every package of the suite are installed. The R scripts in script/ can run.
    draft        No R, or packages missing. Analysis in another language in script/other-language/,
                 the report stays a draft, and methods with no faithful equivalent are left out.
    descriptive  The data hold no rankings (results, forms, indicators). Counts only, at any level.
"""
import json, os, shutil, subprocess, sys, tempfile
import yaml

report = os.path.abspath(sys.argv[1])
root = report
while not os.path.isdir(os.path.join(root, 'themes')):
    root = os.path.dirname(root)
cfg = yaml.safe_load(open(os.path.join(report, 'report.yml'), encoding='utf-8'))
out = dict(report=os.path.relpath(report, root), checks=[], warnings=[], errors=[])
ok = lambda m: out['checks'].append(m)
warn = lambda m: out['warnings'].append(m)
err = lambda m: out['errors'].append(m)

# ---------------------------------------------------------------- 1. tools
R_PACKAGES = ['PlackettLuce', 'gosset', 'qvcalc', 'ggplot2', 'patchwork', 'sf', 'jsonlite', 'yaml',
              'commonmark', 'pagedown', 'pdftools', 'rmarkdown']
rscript = shutil.which('Rscript')
missing = R_PACKAGES
if rscript:
    expr = 'cat(setdiff(c(%s), rownames(installed.packages())), sep = "\\n")' % ','.join(f'"{p}"' for p in R_PACKAGES)
    r = subprocess.run([rscript, '-e', expr], capture_output=True, text=True, timeout=120)
    missing = [x for x in r.stdout.split('\n') if x]
    ok(f'Rscript found at {rscript}') if not missing else warn('R packages missing: ' + ', '.join(missing))
else:
    warn('Rscript not found. The R workflow cannot run in this session.')
out['r'] = dict(rscript=rscript, missing_packages=missing)

for tool in ('pandoc', 'google-chrome', 'chromium', 'qpdf'):
    out.setdefault('tools', {})[tool] = shutil.which(tool)
if not (out['tools']['google-chrome'] or out['tools']['chromium']):
    warn('No headless Chrome. The PDF cannot be printed here, only the Word file.')
if not out['tools']['pandoc']:
    warn('No pandoc. The Word file cannot be built here.')

# matplotlib needs a writable configuration folder, which some sandboxes lack
mpl = os.environ.get('MPLCONFIGDIR') or os.path.join(os.path.expanduser('~'), '.config', 'matplotlib')
try:
    os.makedirs(mpl, exist_ok=True); tempfile.NamedTemporaryFile(dir=mpl).close()
except OSError:
    warn(f'{mpl} is not writable. Run the Python scripts with MPLCONFIGDIR set to a temporary folder.')

# ---------------------------------------------------------------- 2. data
src = (sys.argv[2] if len(sys.argv) > 2 else (cfg.get('data') or {}).get('source') or '')
has_rankings = False
if cfg.get('type') in ('annual', 'technical', 'story', None) and src and os.path.exists(os.path.join(src, 'datasets.csv')):
    import pandas as pd
    idx = pd.read_csv(os.path.join(src, 'datasets.csv'))
    d = cfg.get('data') or {}
    ids, flt = d.get('trial_ids') or [], d.get('filter') or {}
    if ids:
        idx = idx[idx.trial_id.isin(ids)]
    else:
        for k in ('country_iso3', 'crop_name'):
            if flt.get(k):
                v = flt[k] if isinstance(flt[k], list) else [flt[k]]
                idx = idx[idx[k].isin(v)]
    idx = idx[idx.management.fillna('').str.contains('tricot')]
    prog = None if ids else flt.get('program')
    trials = []
    for _, r in idx.iterrows():
        f = json.load(open(os.path.join(src, r.path), encoding='utf-8'))
        m = f.get('metadata') or {}
        if prog and (m.get('data_producer') or {}).get('program') != prog:
            continue
        t = dict(trial_id=r.trial_id, path=r.path)
        for k in ('identifier', 'crop', 'data_producer', 'genotypes', 'participants', 'study'):
            if not m.get(k):
                err(f'{r.trial_id} lacks metadata.{k}')
        # dates, from the metadata, else the index, else the moments recorded in plot_data
        dt = m.get('date') if isinstance(m.get('date'), dict) else None
        if dt and dt.get('start'):
            t['start'], t['date_source'] = dt['start'], 'metadata.date'
        elif isinstance(r.get('start_date'), str):
            dd, mm, yy = r.start_date.split('/')
            t['start'], t['date_source'] = f'{yy}-{mm}-{dd}', 'datasets.csv start_date (day/month/year)'
        else:
            md = sorted(x.get('moment_date') for x in f.get('plot_data') or [] if x.get('moment_date'))
            t['start'], t['date_source'] = (md[0], 'earliest plot_data moment_date') if md else (None, 'none')
        if t['date_source'] != 'metadata.date':
            warn(f'{r.trial_id} has no metadata.date. Start taken from {t["date_source"]}: {t["start"]}.' if t['start'] else
                 f'{r.trial_id} has no date anywhere. Leave its year empty, ask the data producer, and keep it out of yearly counts.')
        plots = f.get('plot_data') or []
        traits = {x.get('trait') for x in plots}
        t['rankings'] = any(str(x.get('value_type', '')).startswith('rank') or str(x.get('trait', '')).endswith('_pos')
                            or 'rank' in str(x.get('value_type', '')) for x in plots)
        has_rankings = has_rankings or t['rankings']
        # the flag column can hold several flags separated by ';'. derived alone is not a quality issue.
        # plot_area_assumed marks a yield from the protocol plot size (tricot-data README, Yield).
        flags = {}
        for x in plots:
            for fl in str(x.get('flag') or '').split(';'):
                if fl and fl != 'derived':
                    flags[fl] = flags.get(fl, 0) + 1
        t['flags'] = flags
        if flags:
            warn(f'{r.trial_id} carries quality flags {flags}. Drop flagged yields, or report them with the flag, and say which in the report.')
        t['traits'] = len(traits)
        trials.append(t)
    out['trials'] = trials
    ok(f'{len(trials)} tricot trials match the data section of report.yml')
    if not trials:
        err('No trial matches the data section of report.yml.')
    ok('Take field names from the tricot-data README and SKILL, never from a guess. Dates come from the rules above.')
elif cfg.get('type') in ('annual', 'technical', 'story', None):
    warn('No tricot-data folder found. Pass it as the second argument, or set data.source in report.yml.')

# ---------------------------------------------------------------- 3. level
if out['errors']:
    level = 'blocked'
elif not has_rankings and 'trials' not in out:
    level = 'descriptive'
elif rscript and not missing:
    level = 'r-workflow'
else:
    level = 'draft'
out['analysis_level'] = level
os.makedirs(os.path.join(report, 'output'), exist_ok=True)
json.dump(out, open(os.path.join(report, 'output', 'preflight.json'), 'w'), indent=1, default=str)

print(f'Analysis level: {level}')
for m in out['checks']: print('  ok    ', m)
for m in out['warnings']: print('  warn  ', m)
for m in out['errors']: print('  ERROR ', m)
sys.exit(1 if out['errors'] else 0)
