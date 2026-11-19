"""Figures for the India 2025 tricot report. ColorBrewer palettes, Equal Earth map."""
import json, csv, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

os.makedirs('fig', exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#888888', 'axes.labelcolor': '#333333', 'xtick.color': '#555555',
                     'ytick.color': '#333333', 'axes.titlesize': 9.5, 'axes.titleweight': 'bold', 'figure.dpi': 200,
                     'savefig.bbox': 'tight', 'savefig.facecolor': 'white'})
GREEN, GREEN_L = '#238b45', '#a1d99b'          # Greens
TEAL, BROWN, GREY = '#01665e', '#8c510a', '#bdbdbd'  # BrBG ends
PL = pd.read_csv('out/pl_estimates.csv'); TR = pd.read_csv('out/trials.csv'); LOC = pd.read_csv('out/vs_local.csv')
TAUP = pd.read_csv('out/tau_pooled.csv'); RE = pd.read_csv('out/reasons.csv'); S = pd.read_csv('out/sites.csv')


def fmt_p(p):
    return 'p < 0.001' if p < 0.001 else f'p = {p:.3f}' if p < 0.1 else f'p = {p:.2f}'

# ------------------------------------------------------------------ Equal Earth map
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = np.sqrt(3) / 2


def eqearth(lon, lat):
    lon = np.radians(np.asarray(lon, float)); lat = np.radians(np.asarray(lat, float))
    th = np.arcsin(M * np.sin(lat)); t2 = th * th; t6 = t2 ** 3
    x = lon * np.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, y


def fig_map():
    # state boundaries from github.com/geohacker/india (2014), indicative only
    gj = json.load(open(os.environ.get('INDIA_STATES', 'india_telengana.geojson')))
    focus = {'Gujarat', 'Maharashtra', 'Karnataka', 'Orissa'}
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    lon0 = 82.0
    for f in gj['features']:
        g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        hl = f['properties']['NAME_1'] in focus
        for poly in polys:
            ring = np.asarray(poly[0])
            if len(ring) < 40: continue
            ring = ring[::max(1, len(ring) // 1500)]
            x, y = eqearth(ring[:, 0] - lon0, ring[:, 1])
            ax.fill(x, y, facecolor='#e5f5e0' if hl else '#f7f7f7', edgecolor='#9a9a9a', linewidth=0.4, zorder=1)
    for nm, (lo, la) in {'Gujarat': (70.9, 22.3), 'Maharashtra': (76.9, 19.3), 'Karnataka': (75.9, 15.2), 'Odisha': (84.6, 20.3)}.items():
        x, y = eqearth(lo - lon0, la); ax.text(x, y, nm, fontsize=8, color='#41784f', ha='center', style='italic', zorder=2)
    S['place'] = S['adm2'].fillna(S['adm3'])
    pts = S.groupby(['place', 'adm1']).agg(lon=('longitude', 'mean'), lat=('latitude', 'mean'), n=('site_id', 'size'),
                                           crops=('crop', lambda x: sorted(set(x)))).reset_index()
    lab = {'chickpea': 'chickpea', 'fingermillet': 'finger millet', 'foxtailmillet': 'foxtail millet', 'horsegram': 'horse gram',
           'littlemillet': 'little millet', 'maize': 'maize', 'rice': 'rice', 'sorghum': 'sorghum'}
    # label anchor (lon, lat) and alignment
    off = {'Akole': ((71.2, 16.2), 'right'), 'Kaprada': ((70.0, 19.5), 'right'), 'Shahada': ((75.6, 24.6), 'left'),
           'Sambalpur': ((86.9, 18.0), 'left'), 'Tumkur': ((79.4, 12.0), 'left')}
    for _, r in pts.iterrows():
        x, y = eqearth(r.lon - lon0, r.lat)
        ax.scatter(x, y, s=r.n * 1.1, color=GREEN, edgecolor='white', linewidth=1.2, zorder=4)
        (tlo, tla), ha = off[r.place]; tx, ty = eqearth(tlo - lon0, tla)
        ax.annotate(f"{r.place}\n{r.n} farmers\n" + ',\n'.join(lab[c] for c in r.crops),
                    (x, y), (tx, ty), fontsize=7.6, ha=ha, va='center', color='#222222', zorder=5,
                    arrowprops=dict(arrowstyle='-', color='#777777', lw=0.6, shrinkA=2, shrinkB=5))
    x0, y0 = eqearth(66.0 - lon0, 7.5); x1, y1 = eqearth(90.5 - lon0, 26.5)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_aspect('equal'); ax.axis('off')
    
    fig.savefig('fig/fig1_map.png'); plt.close(fig)

# ------------------------------------------------------------------ participation
def fig_participation():
    t = TR.sort_values(['crop', 'place'], ascending=[False, False]).reset_index(drop=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.4, 4.2), sharey=True, gridspec_kw={'width_ratios': [1.25, 1], 'wspace': 0.08})
    y = np.arange(len(t))
    a.barh(y, t.n_registered, color=GREEN_L, height=0.62, label='Registered')
    a.barh(y, t.n_ranked, color=GREEN, height=0.62, label='Completed the final ranking')
    for i, r in t.iterrows():
        a.text(r.n_registered + 1, i, f"{r.n_ranked} of {r.n_registered}", va='center', fontsize=7.5, color='#333333')
    a.set_yticks(y); a.set_yticklabels(t.label); a.set_xlim(0, 66); a.set_xlabel('Farmers')
    a.set_title('Farmers registered and completing', loc='left'); a.legend(frameon=False, fontsize=7.5, loc='lower right', bbox_to_anchor=(1.0, 1.06), ncol=2)
    sh = t.women / t.n_registered * 100
    b.barh(y, sh, color=TEAL, height=0.62)
    for i, v in enumerate(sh): b.text(v + 1, i, f"{v:.0f}%", va='center', fontsize=7.5, color='#333333')
    b.axvline(27.6, color='#888888', lw=0.8, ls=(0, (3, 3))); b.text(28.5, len(t) - 0.35, 'all trials 28%', fontsize=7, color='#666666')
    b.set_xlim(0, 60); b.set_xlabel('Women among registered farmers (%)'); b.set_title('Share of women', loc='left')
    b.tick_params(left=False)
    fig.savefig('fig/fig2_participation.png'); plt.close(fig)

# ------------------------------------------------------------------ forest plots
def forest(labels, fname, figsize):
    fig, axes = plt.subplots(1, len(labels), figsize=figsize, gridspec_kw={'wspace': 0.95 if len(labels) > 1 else 0})
    axes = np.atleast_1d(axes)
    for ax, lb in zip(axes, labels):
        d = PL[(PL.label == lb) & (PL.trait == 'overall_performance')].sort_values('logworth')
        tr = TR[TR.label == lb].iloc[0]
        y = np.arange(len(d)); sig = tr.p_value < 0.05
        ax.axvline(0, color='#999999', lw=0.8)
        ax.hlines(y, d.logworth - 1.96 * d.se, d.logworth + 1.96 * d.se, color=GREEN if sig else GREY, lw=1.6)
        ax.scatter(d.logworth, y, s=26, color=GREEN if sig else '#8a8a8a', zorder=3, edgecolor='white', linewidth=0.6)
        ax.set_yticks(y); ax.set_yticklabels(d.genotype, fontsize=7.6)
        ax.set_title(f"{lb}\n{tr.n_ranked} farmers, {fmt_p(tr.p_value)}", loc='left', fontsize=8.6)
        ax.set_xlabel('Log-worth (overall preference)', fontsize=8)
        ax.tick_params(axis='x', labelsize=7.5); ax.grid(axis='x', color='#eeeeee', lw=0.6); ax.set_axisbelow(True)
        m = max(abs(ax.get_xlim()[0]), abs(ax.get_xlim()[1])); ax.set_xlim(-m, m)
    fig.savefig(fname); plt.close(fig)

# ------------------------------------------------------------------ better than local
def fig_local():
    t = LOC.groupby('label').agg(n=('n', 'sum'), better=('better', 'sum')).reset_index()
    t['share'] = t.better / t.n * 100
    z = 1.96; p = t.better / t.n; d = 1 + z * z / t.n
    c = (p + z * z / (2 * t.n)) / d; h = z * np.sqrt(p * (1 - p) / t.n + z * z / (4 * t.n ** 2)) / d
    t['lo'] = (c - h) * 100; t['hi'] = (c + h) * 100
    t = t.sort_values('share').reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.6, 3.9)); y = np.arange(len(t))
    ax.axvline(50, color='#999999', lw=0.8, ls=(0, (3, 3)))
    ax.hlines(y, t.lo, t.hi, color=GREEN_L, lw=2.2); ax.scatter(t.share, y, s=34, color=GREEN, zorder=3, edgecolor='white', linewidth=0.7)
    for i, r in t.iterrows(): ax.text(103, i, f"{r.share:.0f}%  ({int(r.better)} of {int(r.n)})", va='center', fontsize=7.5, color='#333333')
    ax.set_yticks(y); ax.set_yticklabels(t.label); ax.set_xlim(0, 135); ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Test plots rated better than the farmer\'s own variety (%), with 95% interval')
    ax.spines['bottom'].set_bounds(0, 100)
    fig.savefig('fig/fig8_local.png'); plt.close(fig)

# ------------------------------------------------------------------ trait agreement
def fig_tau():
    t = TAUP.sort_values('mean').reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.4, 3.0)); y = np.arange(len(t))
    ax.axvline(0, color='#999999', lw=0.8)
    ax.hlines(y, t.lo, t.hi, color=GREEN_L, lw=2.2); ax.scatter(t['mean'], y, s=34, color=GREEN, zorder=3, edgecolor='white', linewidth=0.7)
    for i, r in t.iterrows(): ax.text(0.80, i, f"{r['mean']:.2f}   {int(r.n)} farmers, {int(r.n_trials)} trials", va='center', fontsize=7.5, color='#333333')
    ax.set_yticks(y); ax.set_yticklabels(t.label_trait); ax.set_xlim(-0.2, 1.32); ax.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xlabel('Mean Kendall tau with overall preference, with 95% bootstrap interval'); ax.spines['bottom'].set_bounds(-0.2, 0.8)
    fig.savefig('fig/fig9_tau.png'); plt.close(fig)

# ------------------------------------------------------------------ reasons
def fig_reasons():
    t = RE[RE.theme != 'Other or general'].copy()
    t['short'] = t.theme.str.replace(r' \(.*\)', '', regex=True)
    t = t.sort_values('most_share').reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(6.8, 3.6)); y = np.arange(len(t)); h = 0.36
    ax.barh(y + h / 2 + 0.02, t.most_share * 100, height=h, color=TEAL, label='Reason for the most preferred variety (484 farmers)')
    ax.barh(y - h / 2 - 0.02, t.least_share * 100, height=h, color=BROWN, label='Reason for the least preferred variety (451 farmers)')
    for i, r in t.iterrows():
        ax.text(r.most_share * 100 + 0.8, i + h / 2 + 0.02, f"{r.most_share * 100:.0f}%", va='center', fontsize=7.3, color='#333333')
        ax.text(r.least_share * 100 + 0.8, i - h / 2 - 0.02, f"{r.least_share * 100:.0f}%", va='center', fontsize=7.3, color='#333333')
    ax.set_yticks(y); ax.set_yticklabels(t.short); ax.set_xlim(0, 68); ax.set_xlabel('Farmers mentioning the theme (%)')
    ax.legend(frameon=False, fontsize=7.6, loc='lower right')
    fig.savefig('fig/fig10_reasons.png'); plt.close(fig)


fig_map(); fig_participation()
forest(['Finger millet, Akole', 'Finger millet, Kaprada', 'Finger millet, Sambalpur'], 'fig/fig3_fingermillet.png', (10.2, 4.6))
forest(['Rice, Kaprada', 'Rice, Sambalpur'], 'fig/fig4_rice.png', (8.2, 4.6))
forest(['Little millet, Akole', 'Little millet, Kaprada', 'Foxtail millet, Shahada'], 'fig/fig5_smallmillets.png', (10.2, 3.5))
forest(['Maize, Shahada', 'Sorghum, Shahada'], 'fig/fig6_maize_sorghum.png', (9.2, 3.5))
forest(['Chickpea, Akole', 'Chickpea, Tumkur', 'Horse gram, Sambalpur'], 'fig/fig7_pulses.png', (10.2, 3.5))
fig_local(); fig_tau(); fig_reasons()
print('done')
