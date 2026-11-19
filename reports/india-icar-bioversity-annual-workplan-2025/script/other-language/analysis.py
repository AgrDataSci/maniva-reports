"""Analysis of the 13 India 2025 tricot trials. Writes results to out/ in the working directory.

Python draft that produced the numbers of the first version of the report, run where R was
not available. The Plackett-Luce fit is a maximum-likelihood implementation with pseudo-rankings,
checked on simulated rankings. See ../../decisions/README.md for where it departs from the
decision records. out/sites.csv and out/farmer_tau.csv hold participant-level rows and are not
committed.
"""
import json, os, re, itertools
import numpy as np, pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import chi2, kendalltau
from load import load, RANK_TRAITS, TRAIT_LABEL

os.makedirs('out', exist_ok=True)
T, S, P = load()
rng = np.random.default_rng(2025)

# ---------------------------------------------------------------- Plackett-Luce
def nll_grad(theta, rankings, weights, k):
    """theta has k free parameters; the pseudo item (index k) is fixed at 0."""
    th = np.append(theta, 0.0)
    nll = 0.0; g = np.zeros(k + 1)
    for r, w in zip(rankings, weights):
        for j in range(len(r) - 1):
            rest = r[j:]
            lse = logsumexp(th[rest])
            nll -= w * (th[r[j]] - lse)
            p = np.exp(th[rest] - lse)
            g[r[j]] -= w
            g[rest] += w * p
    return nll, g[:k]


def fit_pl(rankings, k, npseudo=0.5):
    """Plackett-Luce by maximum likelihood with pseudo-rankings against a ghost item (as in PlackettLuce)."""
    rk = [np.asarray(r) for r in rankings]
    w = [1.0] * len(rk)
    for i in range(k):
        rk += [np.array([i, k]), np.array([k, i])]; w += [npseudo, npseudo]
    f = lambda th: nll_grad(th, rk, w, k)
    res = minimize(f, np.zeros(k), jac=True, method='BFGS', options={'gtol': 1e-8, 'maxiter': 2000})
    th = res.x
    eps = 1e-5; H = np.zeros((k, k))
    for i in range(k):
        e = np.zeros(k); e[i] = eps
        H[:, i] = (f(th + e)[1] - f(th - e)[1]) / (2 * eps)
    H = (H + H.T) / 2
    V = np.linalg.pinv(H)
    C = np.eye(k) - np.ones((k, k)) / k
    logworth = C @ th
    se = np.sqrt(np.clip(np.diag(C @ V @ C.T), 0, None))
    ll_fit = -nll_grad(th, [np.asarray(r) for r in rankings], [1.0] * len(rankings), k)[0]
    ll_null = -nll_grad(np.zeros(k), [np.asarray(r) for r in rankings], [1.0] * len(rankings), k)[0]
    worth = np.exp(logworth - logsumexp(logworth))
    return dict(logworth=logworth, se=se, worth=worth, ll=ll_fit, ll0=ll_null, n=len(rankings))


def rankings_for(p, trait, items):
    """Ordered item indices (best first) per farmer for a ranked trait."""
    q = p[(p.trait == trait)].copy()
    q['v'] = pd.to_numeric(q.value, errors='coerce')
    out = {}
    for sid, g in q.groupby('site_id'):
        g = g.dropna(subset=['v'])
        if len(g) < 2 or g.v.duplicated().any() or g.genotype_name.duplicated().any():
            continue
        out[sid] = [items.index(x) for x in g.sort_values('v').genotype_name]
    return out


def yield_rankings(p, items):
    """Within-farm order of the recorded grain weight of the sampled plants (highest first). Ties dropped."""
    q = p[p.trait == 'yield_sampled_plants'].copy()
    q['v'] = pd.to_numeric(q.value_standard.fillna(q.value), errors='coerce')
    out = {}; ties = 0
    for sid, g in q.groupby('site_id'):
        g = g.dropna(subset=['v'])
        if len(g) < 2:
            continue
        if g.v.duplicated().any():
            ties += 1; continue
        out[sid] = [items.index(x) for x in g.sort_values('v', ascending=False).genotype_name]
    return out, ties


def wilson(x, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = x / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h

# ---------------------------------------------------------------- per trial models
pl_rows, trial_rows, local_rows, tau_rows, gender_rows, design_rows = [], [], [], [], [], []
farm_tau = []
for _, t in T.iterrows():
    p = P[P.trial_id == t.trial_id]
    s = S[S.trial_id == t.trial_id].set_index('site_id')
    items = sorted(p.genotype_name.dropna().unique())
    k = len(items)
    allr = {}
    for tr in RANK_TRAITS:
        r = rankings_for(p, tr, items)
        if len(r) >= 10:
            allr[tr] = r
    yr, ties = yield_rankings(p, items)
    if len(yr) >= 10:
        allr['yield_rank'] = yr
    for tr, r in allr.items():
        m = fit_pl(list(r.values()), k)
        lr = 2 * (m['ll'] - m['ll0']); pv = chi2.sf(lr, k - 1)
        ntest = np.bincount(np.concatenate(list(r.values())), minlength=k)
        for i, it in enumerate(items):
            pl_rows.append(dict(trial_id=t.trial_id, label=t.label, crop=t.crop_label, place=t.place, trait=tr,
                                genotype=it, logworth=m['logworth'][i], se=m['se'][i], worth=m['worth'][i],
                                n_farmers=m['n'], n_tested=int(ntest[i]), lr=lr, df=k - 1, p_value=pv))
        if tr == 'overall_performance':
            top = np.argsort(-m['logworth'])
            trial_rows.append(dict(trial_id=t.trial_id, label=t.label, crop=t.crop_label, place=t.place, state=t.state,
                                   code=t.code, start=t.start, end=t.end, n_registered=t.n_reg, women=t.women, men=t.men,
                                   n_ranked=m['n'], response=m['n'] / t.n_reg, n_genotypes=k, lr=lr, df=k - 1, p_value=pv,
                                   top1=items[top[0]], top2=items[top[1]], top3=items[top[2]], bottom=items[top[-1]],
                                   worth_top1=m['worth'][top[0]], worth_equal=1 / k, yield_ties=ties))
            # gender heterogeneity
            g = s.farmer_gender.reindex(list(r.keys()))
            rw = [r[i] for i in r if g.get(i) == 'woman']; rm = [r[i] for i in r if g.get(i) == 'man']
            row = dict(label=t.label, n_women=len(rw), n_men=len(rm))
            if len(rw) >= 12 and len(rm) >= 12:
                mw, mm = fit_pl(rw, k), fit_pl(rm, k)
                st = 2 * (mw['ll'] + mm['ll'] - m['ll'])
                row.update(lr=st, df=k - 1, p_value=chi2.sf(st, k - 1),
                           top_women=items[int(np.argmax(mw['logworth']))], top_men=items[int(np.argmax(mm['logworth']))],
                           rho=float(pd.Series(mw['logworth']).corr(pd.Series(mm['logworth']), method='spearman')))
            gender_rows.append(row)
    # design: how many farmers received each genotype (registration packages = any plot row)
    alloc = p.drop_duplicates(['site_id', 'genotype_name']).genotype_name.value_counts()
    design_rows.append(dict(label=t.label, n_genotypes=k, min_alloc=int(alloc.min()), max_alloc=int(alloc.max()),
                            median_alloc=float(alloc.median())))
    # comparison with local
    q = p[p.trait == 'overall_performance_vs_local']
    for it, g in q.groupby('genotype_name'):
        n = len(g); x = int((g.value == 'better').sum()); lo, hi = wilson(x, n)
        local_rows.append(dict(trial_id=t.trial_id, label=t.label, crop=t.crop_label, genotype=it, n=n, better=x,
                               share=x / n, lo=lo, hi=hi))
    # farmer-level Kendall tau of each trait with overall preference
    if 'overall_performance' in allr:
        ov = allr['overall_performance']
        for tr, r in allr.items():
            if tr == 'overall_performance': continue
            for sid in set(ov) & set(r):
                a, b = ov[sid], r[sid]
                if set(a) != set(b) or len(a) < 3: continue
                ra = [a.index(i) for i in sorted(a)]; rb = [b.index(i) for i in sorted(a)]
                tau = kendalltau(ra, rb).statistic
                farm_tau.append(dict(label=t.label, crop=t.crop_label, trait=tr, site_id=sid, tau=tau,
                                     gender=s.farmer_gender.get(sid)))

PL = pd.DataFrame(pl_rows); TR = pd.DataFrame(trial_rows); LOC = pd.DataFrame(local_rows)
FT = pd.DataFrame(farm_tau); GD = pd.DataFrame(gender_rows); DS = pd.DataFrame(design_rows)


def boot_ci(x, n=2000):
    x = np.asarray(x); m = [rng.choice(x, len(x)).mean() for _ in range(n)]
    return np.percentile(m, [2.5, 97.5])

tau_t = FT.groupby(['label', 'trait']).tau.agg(['mean', 'count']).reset_index()
tau_p = []
for tr, g in FT.groupby('trait'):
    lo, hi = boot_ci(g.tau.values)
    tau_p.append(dict(trait=tr, label_trait=TRAIT_LABEL[tr], mean=g.tau.mean(), lo=lo, hi=hi, n=len(g),
                      n_trials=g.label.nunique(), agree_top=float((g.tau == 1).mean())))
TAUP = pd.DataFrame(tau_p).sort_values('mean', ascending=False)
tau_g = FT.groupby(['trait', 'gender']).tau.agg(['mean', 'count']).reset_index()

# ---------------------------------------------------------------- participants
part = {}
part['n'] = len(S)
part['gender'] = S.farmer_gender.value_counts(dropna=False).to_dict()
part['age'] = S.age.describe().round(1).to_dict()
part['age_by_gender'] = S.groupby('farmer_gender').age.median().to_dict()
part['farm_size'] = pd.to_numeric(S.farm_size, errors='coerce').describe().round(2).to_dict()
part['crop_usually_grown'] = S.crop_usually_grown.value_counts(dropna=False).to_dict()
part['tricot_previous_year'] = S.tricot_previous_year.value_counts(dropna=False).to_dict()
part['seed_source'] = S.seed_source.str.lower().str.strip().value_counts(dropna=False).head(12).to_dict()


def multi(col):
    x = S[col].dropna().str.lower().str.split(';').explode().str.strip()
    return (x.value_counts() / S[col].notna().sum()).round(3).head(10).to_dict(), int(S[col].notna().sum())
for c in ['fertilizer_types', 'irrigation_method', 'tillage_practice', 'water_conservation', 'soil_conservation', 'crops_grown']:
    part[c] = multi(c)
part['by_state'] = S.groupby('adm1').agg(n=('site_id', 'size'), women=('farmer_gender', lambda x: (x == 'woman').sum())).reset_index().to_dict('records')
part['villages'] = int(S.location.nunique())
part['by_gender_trial'] = S.groupby(['label', 'farmer_gender']).size().unstack(fill_value=0).reset_index().to_dict('records')

# ---------------------------------------------------------------- farmer reasons (keyword coding)
THEMES = {
    'Yield and production': r'yield|yeild|production|cultivation|उत्पन्न|उत्पादन|ઉત્પાદન|more grain|less grain|loosing|પાક સારો|paak saro|saro paak|સારો પાકેલ|સારી રીતે પાકે',
    'Maturity time': r'early|late|મોડી|મોડે|mode |વહેલ|વેહલી|સમય|ગરવી|garvi|divas|samay',
    'Taste and eating quality': r'ખાવા|चवदार|गोड|સુગંધ|રોટલી|sugar free',
    'Disease and pests': r'disease|pest|રોગ|જીવાત|મરેલ|મરી|mari |mare |marti|કોહવાઈ|કોવાઈ|કાળું|કાળી|ચકલા',
    'Lodging': r'નીચે પડ|પડી જાય|fall|પડતી નથી',
    'Water and local adaptation': r'water|પાણી|વરસાદ|pani|suitable|suit|land',
    'Plant type (panicle, tillers, pods, height, grain size)': r'tillar|tiller|panicle|pinnacle|finger|કંઠી|કટી|kanthi|ફૂટ|pod|density|height|hight|ઊંચાઈ|ઉંચાઈ|uchai|size|कणीस|દાણા|small grain|long grain|weight of grain|straw|beared',
    'Market price and appearance': r'market|બજાર|માર્કેટ|માકેટ|बाजार|बाजरी भाव|colour|colou|દેખાવ|દેખાય|attractive|good to see|white|red|black',
}


def code_reason(txt):
    x = str(txt).lower() + ' '
    hits = [k for k, pat in THEMES.items() if re.search(pat, x)]
    # dead or rotten panicles are a disease reason, not a plant type reason
    if 'Disease and pests' in hits and re.search(r'મરેલ|મરી|mari |mare |marti|કોહવાઈ|કાળી', x) and not re.search(r'મોટી|નાની|height|hight', x):
        hits = [h for h in hits if not h.startswith('Plant type')]
    return hits or ['Other or general']

rs = []
for col, kind in [('reason_most_preferred', 'most'), ('reason_least_preferred', 'least')]:
    for _, r in S.dropna(subset=[col]).iterrows():
        for h in code_reason(r[col]):
            rs.append(dict(kind=kind, theme=h, gender=r.farmer_gender, label=r.label, site_id=r.site_id))
RS = pd.DataFrame(rs)
n_most = S.reason_most_preferred.notna().sum(); n_least = S.reason_least_preferred.notna().sum()
reason_tab = RS.groupby(['kind', 'theme']).site_id.nunique().unstack(0).fillna(0).astype(int)
reason_tab['most_share'] = reason_tab['most'] / n_most; reason_tab['least_share'] = reason_tab['least'] / n_least
reason_tab = reason_tab.sort_values('most', ascending=False)
ng = {k: {g: int(S[S.farmer_gender == g][c].notna().sum()) for g in ['woman', 'man']} for k, c in [('most', 'reason_most_preferred'), ('least', 'reason_least_preferred')]}
reason_gender = RS[RS.gender.isin(['woman', 'man'])].groupby(['kind', 'theme', 'gender']).site_id.nunique().unstack(fill_value=0).reset_index()
reason_gender['woman_share'] = reason_gender.apply(lambda r: r.woman / ng[r.kind]['woman'], axis=1)
reason_gender['man_share'] = reason_gender.apply(lambda r: r.man / ng[r.kind]['man'], axis=1)

# ---------------------------------------------------------------- yield (five sampled plants)
Y = P[P.trait.isin(['yield_sampled_plants', 'plants_harvested'])].copy()
Y['v'] = pd.to_numeric(Y.value_standard.fillna(Y.value), errors='coerce')
Yw = Y.pivot_table(index=['label', 'trial_id', 'site_id', 'genotype_name'], columns='trait', values='v', aggfunc='first').reset_index()
ysum = Yw.groupby('label').agg(n_plots=('yield_sampled_plants', 'count'), median_g=('yield_sampled_plants', 'median'),
                               q1=('yield_sampled_plants', lambda x: x.quantile(.25)), q3=('yield_sampled_plants', lambda x: x.quantile(.75)),
                               mn=('yield_sampled_plants', 'min'), mx=('yield_sampled_plants', 'max'),
                               plants_median=('plants_harvested', 'median'), plants_max=('plants_harvested', 'max'),
                               share_5_plants=('plants_harvested', lambda x: (x == 5).mean())).reset_index()
ygen = Yw.groupby(['label', 'genotype_name']).yield_sampled_plants.agg(['median', 'mean', 'count']).reset_index()

# ---------------------------------------------------------------- save
PL.to_csv('out/pl_estimates.csv', index=False); TR.to_csv('out/trials.csv', index=False)
LOC.to_csv('out/vs_local.csv', index=False); FT.to_csv('out/farmer_tau.csv', index=False)
TAUP.to_csv('out/tau_pooled.csv', index=False); tau_t.to_csv('out/tau_trial.csv', index=False)
GD.to_csv('out/gender.csv', index=False); DS.to_csv('out/design.csv', index=False)
reason_tab.to_csv('out/reasons.csv'); reason_gender.to_csv('out/reasons_gender.csv', index=False)
ysum.to_csv('out/yield_trial.csv', index=False); ygen.to_csv('out/yield_genotype.csv', index=False)
S.to_csv('out/sites.csv', index=False)
json.dump(part, open('out/participants.json', 'w'), indent=1, default=str)

pd.set_option('display.width', 260); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
print(TR[['label', 'n_registered', 'n_ranked', 'response', 'n_genotypes', 'lr', 'p_value', 'top1', 'top2', 'top3', 'bottom', 'worth_top1', 'worth_equal', 'yield_ties']].round(3).to_string())
print('ranked total', TR.n_ranked.sum(), 'of', TR.n_registered.sum())
print(DS.to_string())
print(GD.round(3).to_string())
print(TAUP.round(3).to_string()); print(tau_g.round(3).to_string())
print(tau_t.pivot(index='label', columns='trait', values='mean').round(2).to_string())
lt = LOC.groupby('label').agg(n=('n', 'sum'), better=('better', 'sum')); lt['share'] = lt.better / lt.n
print(lt.round(3).to_string()); print('overall better', LOC.better.sum(), LOC.n.sum(), LOC.better.sum() / LOC.n.sum())
print(reason_tab.round(3).to_string()); print(n_most, n_least, ng)
print(reason_gender.round(3).to_string())
print(ysum.round(1).to_string())
print(json.dumps(part, indent=0, default=str, ensure_ascii=False)[:5000])
