"""Figures for the annual report of the PABRA bean tricot trials in Tanzania.

Python draft mirroring script/02-figures.R, run where R was not available. Reads only the
aggregated tables in output/tables/. Colours from the theme, taken from the CGIAR reports the team supplied.
Country outlines from datasets/geo-countries (Natural Earth, public domain), indicative only.

Usage, from the repository root
    GEO_COUNTRIES=../geo-countries/data/countries.geojson python3 reports/tanzania-pabra-bean-2024/script/other-language/figs.py reports/tanzania-pabra-bean-2024
"""
import json, os, sys
import numpy as np, pandas as pd, yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

REPORT = os.path.abspath(sys.argv[1])
ROOT = os.path.abspath(os.path.join(REPORT, '..', '..'))
cfg = yaml.safe_load(open(os.path.join(REPORT, 'report.yml'), encoding='utf-8'))
theme = yaml.safe_load(open(os.path.join(ROOT, 'themes', cfg['theme'] + '.yml'), encoding='utf-8'))
CH = theme['charts']
YEAR = int(cfg['reporting_year'])
TAB = os.path.join(REPORT, 'output', 'tables')
FIG = os.path.join(REPORT, 'output', 'figures')
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({'font.family': 'Inter', 'font.size': 8.5, 'axes.edgecolor': '#9a9a9a', 'axes.linewidth': 0.6,
                     'axes.labelcolor': '#4a4a4a', 'xtick.color': '#4a4a4a', 'ytick.color': '#4a4a4a',
                     'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 300})
W = 16 / 2.54  # full-width figure, 16 cm


DAT = os.path.join(REPORT, 'output', 'figure-data')
os.makedirs(DAT, exist_ok=True)


def save(fig, name, data=None):
    """Save a figure and, beside it, the exact numbers it draws, for readers and reporting tools."""
    fig.savefig(os.path.join(FIG, name), bbox_inches='tight', facecolor='white')
    plt.close(fig)
    if data is not None:
        data.to_csv(os.path.join(DAT, name.replace('.png', '.csv')), index=False, float_format='%.3f')


def year_colours(years):
    """Reporting year in the primary green, earlier years in mint, as year against cumulative."""
    return {y: (CH['single'] if y == YEAR else CH['single_light']) for y in years}


# ---------------------------------------------------------------- 1. map, Equal Earth
def eqearth(lon, lat):
    """Equal Earth projection (Savric, Patterson and Jenny 2018), EPSG:8857, on the unit sphere."""
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    M = np.sqrt(3) / 2
    lam, phi = np.radians(lon), np.radians(lat)
    th = np.arcsin(M * np.sin(phi)); t2 = th * th; t6 = t2 ** 3
    x = lam * np.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y

pts = pd.read_csv(os.path.join(TAB, 'map-points.csv'))
# region of the trials, from the site points with a margin, or from report.yml map_bbox
bbox = tuple(cfg.get('map_bbox') or (pts.longitude.min() - 1.5, pts.longitude.max() + 1.5, pts.latitude.min() - 1.5, pts.latitude.max() + 1.5))
gj = json.load(open(os.environ.get('GEO_COUNTRIES', 'geo-countries/data/countries.geojson'), encoding='utf-8'))
fig, ax = plt.subplots(figsize=(W * 0.62, W * 0.62))
for f in gj['features']:
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    focus = f['properties'].get('ISO_A3', f['properties'].get('ISO3166-1-Alpha-3')) == 'TZA'
    for poly in polys:
        ring = np.asarray(poly[0])
        if ring[:, 0].max() < bbox[0] - 8 or ring[:, 0].min() > bbox[1] + 8 or ring[:, 1].max() < bbox[2] - 8 or ring[:, 1].min() > bbox[3] + 8:
            continue
        x, y = eqearth(ring[:, 0], ring[:, 1])
        ax.add_patch(Polygon(np.c_[x, y], closed=True, fc=CH['map_focus'] if focus else CH['map_fill'],
                             ec=CH['map_line'], lw=0.5 if focus else 0.35, zorder=1))
cols = year_colours(sorted(pts.year.unique()))
for y_ in sorted(pts.year.unique()):
    d = pts[pts.year == y_]
    x, yy = eqearth(d.longitude.values, d.latitude.values)
    ax.scatter(x, yy, s=6 + 2.2 * np.sqrt(d.participants), c=cols[y_], ec='#4a4a4a', lw=0.25, alpha=0.95,
               zorder=3 if y_ == YEAR else 2, label=str(y_))
x0, y0 = eqearth(bbox[0], bbox[2]); x1, y1 = eqearth(bbox[1], bbox[3])
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.axis('off')
ax.legend(title='Season start', frameon=False, loc='upper right', fontsize=7.5, title_fontsize=7.5, markerscale=1.4)
for nm, lo, la in (cfg.get('map_labels') or []):  # place names, from report.yml
    x, y = eqearth(lo, la); ax.text(x, y, nm, fontsize=7, color='#6b8fa3', style='italic', ha='center')
dist = pd.read_csv(os.path.join(TAB, 'districts.csv'))
save(fig, 'fig01-map.png', dist[['district', 'participants', 'participants_year', 'trials', 'lon', 'lat']]
     .rename(columns={'participants': 'participants_since_start', 'participants_year': 'participants_reporting_year',
                      'lon': 'longitude_median', 'lat': 'latitude_median'}))

# ---------------------------------------------------------------- 2. participants by year and gender
by = pd.read_csv(os.path.join(TAB, 'by-year.csv'))
fig, ax = plt.subplots(figsize=(W, W * 0.33))
ys = by.year.astype(str)[::-1]
left = np.zeros(len(by))
for col, lab, c in [('women', 'Women', CH['positive']), ('men', 'Men', CH['negative']), ('not_stated', 'Not stated', CH['missing'])]:
    v = by[col].values[::-1]
    ax.barh(ys, v, left=left, color=c, height=0.62, label=lab)
    for i, (l, w) in enumerate(zip(left, v)):
        if w >= 60:
            ax.text(l + w / 2, i, f'{w:,}', ha='center', va='center', fontsize=7.5,
                    color='white' if c == CH['positive'] else theme['colours']['ink'])
    left += v
for i, tot in enumerate(left):
    ax.text(tot + 12, i, f'{int(tot):,}', va='center', fontsize=7.5, color='#333')
ax.set_xlabel('Participants registered'); ax.set_xlim(0, left.max() * 1.1)
ax.legend(frameon=False, ncol=3, loc='lower right', bbox_to_anchor=(1, 1.0), fontsize=7.5)
ax.grid(axis='x', color='#eeeeee', lw=0.6); ax.set_axisbelow(True)
for t in ax.get_yticklabels():
    if t.get_text() == str(YEAR): t.set_fontweight('bold')
save(fig, 'fig02-participants.png', by[['year', 'women', 'men', 'not_stated', 'participants']])

# ---------------------------------------------------------------- 3. entries by year, new and repeated
fig, ax = plt.subplots(figsize=(W * 0.62, W * 0.3))
rep = by.entries - by.new_entries
ax.bar(by.year.astype(str), rep, color=CH['single_light'], width=0.6, label='Tested in an earlier season')
ax.bar(by.year.astype(str), by.new_entries, bottom=rep, color=CH['single'], width=0.6, label='New this season')
for i, (r, n) in enumerate(zip(rep, by.entries)):
    ax.text(i, n + 0.5, str(n), ha='center', fontsize=7.5)
ax.set_ylabel('Entries tested'); ax.set_ylim(0, by.entries.max() * 1.2)
ax.legend(frameon=False, fontsize=7, loc='upper left')
ax.grid(axis='y', color='#eeeeee', lw=0.6); ax.set_axisbelow(True)
save(fig, 'fig03-entries.png', by.assign(tested_before=by.entries - by.new_entries)[['year', 'entries', 'new_entries', 'tested_before']])

# ---------------------------------------------------------------- 4. log-worth, trials of the reporting year
PL = pd.read_csv(os.path.join(TAB, 'pl-estimates.csv'))
T = pd.read_csv(os.path.join(TAB, 'trials.csv'))
cur = PL[PL.year == YEAR]
codes = list(T[(T.year == YEAR) & T.indicator.notna()].code)
LAB = {'overall_performance': 'overall preference', 'plant_survival': 'plant survival', 'vigor': 'vigour',
       'disease_resistance': 'disease resistance'}
fig, axes = plt.subplots(1, len(codes), figsize=(W, W * 0.5), sharex=True)
for ax, code in zip(np.atleast_1d(axes), codes):
    d = cur[cur.code == code].sort_values('logworth')
    sig = d.p_value.iloc[0] < cfg['analysis']['alpha']
    c = CH['single'] if sig else CH['not_different']
    ax.errorbar(d.logworth, range(len(d)), xerr=1.96 * d.se, fmt='o', ms=3.2, color=c, ecolor=c, elinewidth=0.8, capsize=0)
    ax.axvline(0, color='#bbbbbb', lw=0.6, ls='--')
    ax.set_yticks(range(len(d))); ax.set_yticklabels(d.genotype, fontsize=6.6)
    t = T[T.code == code].iloc[0]
    ax.set_title(f'{code}\n{LAB.get(d.trait.iloc[0], d.trait.iloc[0]).capitalize()}\nn = {int(d.n_rankings.iloc[0])}, p = {d.p_value.iloc[0]:.2f}',
                 fontsize=7.2, loc='left', color='#333')
    ax.tick_params(axis='x', labelsize=7)
fig.supxlabel('Log-worth with 95% interval', fontsize=7.8)
fig.tight_layout(w_pad=0.6)
save(fig, 'fig04-year-results.png', cur.assign(lower=cur.logworth - 1.96 * cur.se, upper=cur.logworth + 1.96 * cur.se)
     [['code', 'trait', 'moment', 'genotype', 'logworth', 'se', 'lower', 'upper', 'n_tested', 'n_rankings', 'p_value']])

# ---------------------------------------------------------------- 5. better than the local variety, by year
vl = pd.read_csv(os.path.join(TAB, 'vs-local-year.csv'))
vl = vl[vl.year != 'all'].reset_index(drop=True); vl['year'] = vl.year.astype(int)
fig, ax = plt.subplots(figsize=(W * 0.62, W * 0.34))
cols = year_colours(list(vl.year))
ax.bar(vl.year.astype(str), vl.share * 100, color=[cols[y] for y in vl.year], width=0.6)
ax.errorbar(range(len(vl)), vl.share * 100, yerr=[(vl.share - vl.lower) * 100, (vl.upper - vl.share) * 100],
            fmt='none', ecolor='#333', elinewidth=0.8, capsize=2.5)
for i, r in vl.iterrows():
    ax.text(i, r.upper * 100 + 2.5, f'{r.share * 100:.0f}%', ha='center', fontsize=7.8, fontweight='bold')
    ax.text(i, 4, f'{int(r.plots):,} plots', ha='center', fontsize=6.6, color='white' if r.year == YEAR else theme['colours']['ink'])
ax.axhline(50, color='#888', lw=0.6, ls='--')
ax.set_ylim(0, 100); ax.set_ylabel('Plots rated better than\nthe local variety (%)')
ax.grid(axis='y', color='#eeeeee', lw=0.6); ax.set_axisbelow(True)
save(fig, 'fig05-vs-local.png', vl[['year', 'trials', 'farms', 'plots', 'better', 'share', 'lower', 'upper']])

# ---------------------------------------------------------------- 6. record of entries ranked in three or more trials
R = pd.read_csv(os.path.join(TAB, 'entries-record.csv'))
R = R[R.trials_ranked >= 3].sort_values(['share_top3', 'median_rank'], ascending=[True, False])
fig, ax = plt.subplots(figsize=(W * 0.75, W * 0.46))
ax.barh(R.genotype, R.share_top3 * 100, color=CH['single'], height=0.62)
for i, (_, r) in enumerate(R.iterrows()):
    ax.text(r.share_top3 * 100 + 1, i, f'{int(r.top3)} of {int(r.trials_ranked)} trials', va='center', fontsize=6.8, color='#333')
ax.set_xlim(0, 60); ax.set_xlabel('Trials where the entry ranked in the top three for overall preference (%)')
ax.tick_params(axis='y', labelsize=7)
ax.grid(axis='x', color='#eeeeee', lw=0.6); ax.set_axisbelow(True)
save(fig, 'fig06-entry-record.png', R[['genotype', 'trials_ranked', 'top3', 'share_top3', 'median_rank', 'years_tested']].iloc[::-1])
print('figures written to', FIG)
