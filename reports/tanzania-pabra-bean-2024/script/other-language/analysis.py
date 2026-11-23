"""Analysis for the annual report of the PABRA bean tricot trials in Tanzania, 2024 with the record since 2021.

Python draft, run where R was not available, following step 4 of SKILL.md. The Plackett-Luce
fit is the maximum-likelihood implementation with pseudo-rankings used for the first report
(reports/india-icar-bioversity-annual-workplan-2025), checked there on simulated rankings.
See ../../decisions/README.md for where this draft departs from the decision records.

Usage, from the repository root, with a local clone of tricot-data
    TRICOT_DATA=../tricot-data python3 reports/tanzania-pabra-bean-2024/script/other-language/analysis.py reports/tanzania-pabra-bean-2024
Writes aggregated tables to output/tables/. No participant-level row is written.
"""
import json, os, sys, subprocess, collections
import numpy as np, pandas as pd, yaml
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import chi2

REPORT = os.path.abspath(sys.argv[1])
REPO = os.environ.get('TRICOT_DATA', 'tricot-data')
cfg = yaml.safe_load(open(os.path.join(REPORT, 'report.yml'), encoding='utf-8'))
YEAR = int(cfg['reporting_year'])
OUT = os.path.join(REPORT, 'output', 'tables')
os.makedirs(OUT, exist_ok=True)
flt = cfg['data']['filter']
MIN_RANKINGS = cfg['analysis'].get('min_rankings', 15)


# ---------------------------------------------------------------- load
idx = pd.read_csv(os.path.join(REPO, 'datasets.csv'))
idx = idx[(idx.country_iso3 == flt['country_iso3']) & (idx.crop_name == flt['crop_name'])]
trials, sites, plots, meta = [], [], [], {}
for _, r in idx.iterrows():
    d = json.load(open(os.path.join(REPO, r.path), encoding='utf-8'))
    m = d['metadata']
    if m['data_producer'].get('program') != flt['program']:
        continue
    meta[r.trial_id] = m
    s = pd.DataFrame(d['site_data']); s['trial_id'] = r.trial_id
    p = pd.DataFrame(d['plot_data']); p['trial_id'] = r.trial_id
    sites.append(s); plots.append(p)
    trials.append(dict(trial_id=r.trial_id, code=m['study']['code'], title=m['study']['title'],
                       start=m['date']['start'], end=m['date']['end'], year=int(m['date']['start'][:4]),
                       pi=m['data_producer'].get('principal_investigator'), producer=m['data_producer']['name'],
                       partner=m['data_producer'].get('partner'), n_registered=len(s),
                       women=m['participants']['women'], men=m['participants']['men'],
                       not_stated=m['participants']['not_stated'], n_entries=len(m['genotypes'])))
T = pd.DataFrame(trials).sort_values('start').reset_index(drop=True)
S = pd.concat(sites, ignore_index=True)
P = pd.concat(plots, ignore_index=True)
T['period'] = np.where(T.year == YEAR, 'year', 'earlier')


# ---------------------------------------------------------------- Plackett-Luce
def nll_grad(theta, rankings, weights, k):
    th = np.append(theta, 0.0)
    nll = 0.0; g = np.zeros(k + 1)
    for r, w in zip(rankings, weights):
        for j in range(len(r) - 1):
            rest = r[j:]
            lse = logsumexp(th[rest])
            nll -= w * (th[r[j]] - lse)
            g[r[j]] -= w
            g[rest] += w * np.exp(th[rest] - lse)
    return nll, g[:k]


def fit_pl(rankings, k, npseudo=0.5):
    """Plackett-Luce by maximum likelihood with pseudo-rankings against a ghost item, as in PlackettLuce."""
    rk = [np.asarray(r) for r in rankings]; w = [1.0] * len(rk)
    for i in range(k):
        rk += [np.array([i, k]), np.array([k, i])]; w += [npseudo, npseudo]
    f = lambda th: nll_grad(th, rk, w, k)
    th = minimize(f, np.zeros(k), jac=True, method='BFGS', options={'gtol': 1e-8, 'maxiter': 2000}).x
    eps = 1e-5; H = np.zeros((k, k))
    for i in range(k):
        e = np.zeros(k); e[i] = eps
        H[:, i] = (f(th + e)[1] - f(th - e)[1]) / (2 * eps)
    V = np.linalg.pinv((H + H.T) / 2)
    C = np.eye(k) - np.ones((k, k)) / k
    lw = C @ th
    se = np.sqrt(np.clip(np.diag(C @ V @ C.T), 0, None))
    obs = [np.asarray(r) for r in rankings]
    ll = -nll_grad(th, obs, [1.0] * len(obs), k)[0]
    ll0 = -nll_grad(np.zeros(k), obs, [1.0] * len(obs), k)[0]
    return dict(logworth=lw, se=se, ll=ll, ll0=ll0, n=len(obs))


def rankings_for(p, trait, moment, items):
    q = p[(p.trait == trait) & (p.collection_moment == moment) & (p.value_type == 'rank')].copy()
    q['v'] = pd.to_numeric(q.value, errors='coerce')
    out = {}
    for sid, g in q.groupby('site_id'):
        g = g.dropna(subset=['v'])
        if len(g) < 2 or g.v.duplicated().any() or g.genotype_name.duplicated().any():
            continue
        out[sid] = [items.index(x) for x in g.sort_values('v').genotype_name]
    return out


def wilson(x, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = x / n; d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d; h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# ---------------------------------------------------------------- per trial
MOMENT_ORDER = {'vegetative': 1, 'reproductive': 2, 'harvest': 3, 'post-harvest': 4}
pl_rows, ranked = [], {}
T['overall_n'] = 0; T['overall_moment'] = ''; T['lr'] = np.nan; T['p_value'] = np.nan
T['indicator'] = ''; T['vs_local_n'] = 0; T['yield_sites'] = 0
for i, t in T.iterrows():
    p = P[P.trial_id == t.trial_id]
    items = sorted(p.genotype_name.dropna().unique()); k = len(items)
    rk = p[p.value_type == 'rank']
    # overall preference, the most recent overall-type question (decisions/ranking.md)
    ov = rk[rk.trait == 'overall_performance']
    trait, moment = None, None
    if len(ov):
        moment = max(ov.collection_moment.unique(), key=lambda m: MOMENT_ORDER.get(m.lower(), 0))
        trait = 'overall_performance'
    r = rankings_for(p, trait, moment, items) if trait else {}
    T.loc[i, 'overall_n'] = len(r); T.loc[i, 'overall_moment'] = moment or ''
    if len(r) >= MIN_RANKINGS:
        m = fit_pl(list(r.values()), k)
        lr = 2 * (m['ll'] - m['ll0']); pv = chi2.sf(lr, k - 1)
        T.loc[i, 'lr'] = lr; T.loc[i, 'p_value'] = pv; T.loc[i, 'indicator'] = 'overall_performance'
        ntest = np.bincount(np.concatenate(list(r.values())), minlength=k)
        order = np.argsort(-m['logworth'])
        rank_of = {items[j]: int(np.where(order == j)[0][0]) + 1 for j in range(k)}
        role = {g['genotype_name']: g.get('role') for g in meta[t.trial_id]['genotypes']}
        for j, it in enumerate(items):
            pl_rows.append(dict(trial_id=t.trial_id, code=t.code, year=t.year, trait='overall_performance', moment=moment,
                                genotype=it, role=role.get(it), logworth=m['logworth'][j], se=m['se'][j],
                                n_tested=int(ntest[j]), rank=rank_of[it], k=k, n_rankings=m['n'], lr=lr, df=k - 1, p_value=pv))
    # interim indicator for trials of the reporting year without an overall ranking yet
    elif t.year == YEAR:
        latest = rk.assign(o=rk.collection_moment.str.lower().map(MOMENT_ORDER)).sort_values('o')
        latest = latest[latest.o == latest.o.max()]
        cand = latest[latest.trait.isin(cfg['analysis']['interim_traits'])].groupby('trait').site_id.nunique()
        if len(cand):
            trait = cand.idxmax(); moment = latest[latest.trait == trait].collection_moment.iloc[0]
            r = rankings_for(p, trait, moment, items)
            m = fit_pl(list(r.values()), k)
            lr = 2 * (m['ll'] - m['ll0']); pv = chi2.sf(lr, k - 1)
            T.loc[i, 'indicator'] = trait; T.loc[i, 'lr'] = lr; T.loc[i, 'p_value'] = pv
            ntest = np.bincount(np.concatenate(list(r.values())), minlength=k)
            order = np.argsort(-m['logworth'])
            role = {g['genotype_name']: g.get('role') for g in meta[t.trial_id]['genotypes']}
            for j, it in enumerate(items):
                pl_rows.append(dict(trial_id=t.trial_id, code=t.code, year=t.year, trait=trait, moment=moment,
                                    genotype=it, role=role.get(it), logworth=m['logworth'][j], se=m['se'][j],
                                    n_tested=int(ntest[j]), rank=int(np.where(order == j)[0][0]) + 1, k=k,
                                    n_rankings=m['n'], lr=lr, df=k - 1, p_value=pv))
            T.loc[i, 'interim_n'] = m['n']; T.loc[i, 'interim_moment'] = moment
    # comparison with the local variety, one answer per plot
    v = p[p.trait == 'overall_performance_vs_local']
    T.loc[i, 'vs_local_n'] = len(v); T.loc[i, 'vs_local_better'] = int((v.value == 'better').sum())
    y = p[(p.trait == 'yield') & (p.value_type == 'numeric')]
    T.loc[i, 'yield_sites'] = y.site_id.nunique()

PL = pd.DataFrame(pl_rows)
PL.to_csv(os.path.join(OUT, 'pl-estimates.csv'), index=False, float_format='%.4f')


# ---------------------------------------------------------------- overview, year and cumulative
def block(tt):
    ss = S[S.trial_id.isin(tt.trial_id)]
    ents = set(P[P.trial_id.isin(tt.trial_id)].genotype_name.dropna())
    return dict(trials=len(tt), participants=int(tt.n_registered.sum()), women=int(tt.women.sum()),
                men=int(tt.men.sum()), not_stated=int(tt.not_stated.sum()), entries=len(ents),
                districts=int(ss.adm2.dropna().str.strip().str.title().nunique()),
                vs_local_answers=int(T.loc[tt.index, 'vs_local_n'].sum()),
                vs_local_better=int(T.loc[tt.index, 'vs_local_better'].sum()))

yr, cum = block(T[T.year == YEAR]), block(T)
ov = pd.DataFrame({'metric': list(cum), 'reporting_year': [yr[k] for k in cum], 'cumulative': [cum[k] for k in cum]})
ov.to_csv(os.path.join(OUT, 'overview.csv'), index=False)

by_year = []
seen = set()
for y_, tt in T.groupby('year'):
    b = block(tt)
    ents = set(P[P.trial_id.isin(tt.trial_id)].genotype_name.dropna())
    b.update(year=y_, new_entries=len(ents - seen)); seen |= ents
    by_year.append(b)
pd.DataFrame(by_year)[['year', 'trials', 'participants', 'women', 'men', 'not_stated', 'entries', 'new_entries', 'districts']] \
    .to_csv(os.path.join(OUT, 'by-year.csv'), index=False)

# districts, participants registered, cumulative and reporting year
S['district'] = S.adm2.str.strip().str.title()
S['year'] = S.trial_id.map(T.set_index('trial_id').year)
dist = S.groupby('district').agg(participants=('site_id', 'size'), trials=('trial_id', 'nunique'),
                                 lon=('longitude', 'median'), lat=('latitude', 'median'))
dist['participants_year'] = S[S.year == YEAR].groupby('district').size().reindex(dist.index).fillna(0).astype(int)
dist.sort_values('participants', ascending=False).round(2).to_csv(os.path.join(OUT, 'districts.csv'))

# site points for the map, already rounded to two decimals in the published data, counted per point
pts = S.dropna(subset=['longitude', 'latitude']).groupby(['longitude', 'latitude', 'year']).size().rename('participants').reset_index()
pts.to_csv(os.path.join(OUT, 'map-points.csv'), index=False)

# comparison with the local variety per year
# plots of one farm are not independent, so the interval comes from a bootstrap over farms
VL = P[P.trait == 'overall_performance_vs_local'].assign(b=lambda d: (d.value == 'better').astype(int))
VL = VL.groupby(['trial_id', 'site_id']).b.agg(['sum', 'size']).reset_index()
VL['year'] = VL.trial_id.map(T.set_index('trial_id').year)
rng = np.random.default_rng(2024)
vl = []
for y_, tt in T.groupby('year'):
    n = int(tt.vs_local_n.sum()); x = int(tt.vs_local_better.sum())
    f = VL[VL.year == y_]
    bs = [f.iloc[i]['sum'].sum() / f.iloc[i]['size'].sum() for i in (rng.integers(0, len(f), len(f)) for _ in range(2000))]
    lo, hi = np.quantile(bs, [0.025, 0.975])
    vl.append(dict(year=y_, trials=int((tt.vs_local_n > 0).sum()), farms=len(f), plots=n, better=x, share=x / n if n else np.nan, lower=lo, upper=hi))
bs = [VL.iloc[i]['sum'].sum() / VL.iloc[i]['size'].sum() for i in (rng.integers(0, len(VL), len(VL)) for _ in range(2000))]
lo, hi = np.quantile(bs, [0.025, 0.975])
vl.append(dict(year='all', trials=int((T.vs_local_n > 0).sum()), farms=len(VL), plots=int(VL['size'].sum()), better=int(VL['sum'].sum()),
               share=VL['sum'].sum() / VL['size'].sum(), lower=lo, upper=hi))
pd.DataFrame(vl).to_csv(os.path.join(OUT, 'vs-local-year.csv'), index=False, float_format='%.3f')

# ---------------------------------------------------------------- entries across seasons
ovp = PL[PL.trait == 'overall_performance']
rec = []
for g, d in ovp.groupby('genotype'):
    yrs = sorted(T[T.trial_id.isin(P[P.genotype_name == g].trial_id.unique())].year.unique())
    rec.append(dict(genotype=g, role=d.role.dropna().mode().iloc[0] if d.role.notna().any() else None,
                    trials_ranked=len(d), seasons_ranked=d.year.nunique(), years_tested=';'.join(map(str, yrs)),
                    top3=int((d['rank'] <= 3).sum()), share_top3=(d['rank'] <= 3).mean(),
                    median_rank=d['rank'].median(), median_k=d.k.median(), median_logworth=d.logworth.median(),
                    participants_ranked=int(d.n_tested.sum())))
REC = pd.DataFrame(rec).sort_values(['share_top3', 'trials_ranked'], ascending=False)
REC.to_csv(os.path.join(OUT, 'entries-record.csv'), index=False, float_format='%.3f')

# ---------------------------------------------------------------- partnerships and linkages
inst = collections.defaultdict(lambda: dict(roles=set(), trials=set(), people=set()))
for tid, m in meta.items():
    dp = m['data_producer']
    inst[dp['name']]['roles'].add('data producer'); inst[dp['name']]['trials'].add(tid)
    if dp.get('partner'):
        inst[dp['partner']]['roles'].add('implementing partner'); inst[dp['partner']]['trials'].add(tid)
    for c in m['contributors']:
        inst[c['affiliation']]['trials'].add(tid); inst[c['affiliation']]['people'].add(c['name'])
        inst[c['affiliation']]['roles'].add('contributor')
pd.DataFrame([dict(institution=k, roles='; '.join(sorted(v['roles'])), trials=len(v['trials']), people=len(v['people']))
              for k, v in inst.items()]).sort_values('trials', ascending=False).to_csv(os.path.join(OUT, 'partners.csv'), index=False)

people = collections.defaultdict(lambda: dict(trials=set(), roles=set(), affiliation=None))
for tid, m in meta.items():
    for c in m['contributors']:
        people[c['name']]['trials'].add(tid); people[c['name']]['roles'].add(c['contributorType'])
        people[c['name']]['affiliation'] = c['affiliation']
pd.DataFrame([dict(name=k, affiliation=v['affiliation'], roles='; '.join(sorted(v['roles'])), trials=len(v['trials']))
              for k, v in people.items()]).sort_values(['trials', 'name'], ascending=[False, True]).to_csv(os.path.join(OUT, 'contributors.csv'), index=False)

fund = collections.Counter()
for tid, m in meta.items():
    for f in m['funder']:
        fund[(f['funderName'], f.get('awardTitle'), f.get('awardNumber'))] += 1
pd.DataFrame([dict(funder=a, award=b, number=c, trials=n) for (a, b, c), n in fund.items()]) \
    .to_csv(os.path.join(OUT, 'funders.csv'), index=False)

# ---------------------------------------------------------------- PRMS result candidates
doi = next(iter(meta.values()))['identifier']
prms = [dict(type='Knowledge product', title='Open trial data of the PABRA bean tricot trials in Tanzania, 2021 to %d' % YEAR,
             description='%d tricot trials with %d registered participants, published under CC0 1.0 in tricot-data' % (cum['trials'], cum['participants']),
             evidence='datasets.csv of tricot-data, programme %s' % flt['program'], countries='Tanzania', doi=doi,
             readiness_level='', impact_areas='')]
for _, e in REC[(REC.trials_ranked >= 3) & (REC.share_top3 >= 0.5)].iterrows():
    prms.append(dict(type='Innovation development', title='Bean entry %s, evaluated on-farm' % e.genotype,
                     description='Ranked in the top three for overall preference in %d of %d trials (seasons %s)'
                                 % (e.top3, e.trials_ranked, e.years_tested.replace(';', ', ')),
                     evidence='output/tables/entries-record.csv, output/tables/pl-estimates.csv', countries='Tanzania', doi=doi,
                     readiness_level='', impact_areas=''))
PRMS = pd.DataFrame(prms)
PRMS.to_csv(os.path.join(OUT, 'prms-results.csv'), index=False)

# overall preference, how many trials ranked and separated their entries
ovt = T[T.indicator == 'overall_performance']
pd.DataFrame([dict(period=per, trials=len(tt), trials_separated=int((tt.p_value < cfg['analysis']['alpha']).sum()),
                   rankings=int(tt.overall_n.sum()), trials_below_min=int(((T0.overall_n > 0) & (T0.overall_n < MIN_RANKINGS)).sum()),
                   trials_without=int((T0.overall_n == 0).sum()))
              for per, tt, T0 in [('reporting_year', ovt[ovt.year == YEAR], T[T.year == YEAR]), ('cumulative', ovt, T)]]) \
    .to_csv(os.path.join(OUT, 'overall-summary.csv'), index=False)

# ---------------------------------------------------------------- reporting fields and suggested tags
# docs/annual-report-standard.md, "Reporting fields". Suggestions follow fixed rules from the data and
# never set a principal (2) score. The programme confirms or changes every value.
rep = cfg.get('reporting') or {}
ranked = set(P[P.value_type == 'rank'].trait.unique())
roles = {str(g.get('role') or '').lower() for m in meta.values() for g in m['genotypes']}
g_known = cum['women'] + cum['men']; g_share = cum['women'] / g_known if g_known else 0
g_cover = g_known / cum['participants'] if cum['participants'] else 0
CLIMATE = {'drought_tolerance', 'flood_tolerance', 'heat_tolerance', 'maturity', 'waterlogging_tolerance'}
MARKET = {'marketability', 'yield_rank', 'grain_size', 'grain_color', 'taste', 'cooking_time'}
ia = [
    ('Nutrition, health and food security', 'nutrition', 1, 'Variety evaluation of a food crop with farmers',
     'crop %s, %d trials' % (flt['crop_name'], cum['trials'])),
    ('Poverty reduction, livelihoods and jobs', 'poverty', 1 if ranked & MARKET else 0, 'Market or yield traits ranked by farmers',
     ', '.join(sorted(ranked & MARKET)) or 'none ranked'),
    ('Gender equality, youth and social inclusion', 'gender', 1 if (g_share >= 0.3 and g_cover >= 0.8) else 0,
     'Gender recorded for at least 80% of participants and women at least 30% of them',
     'gender recorded for %.0f%%, women %.0f%%' % (100 * g_cover, 100 * g_share)),
    ('Climate adaptation and mitigation', 'climate', 1 if ranked & CLIMATE else 0, 'A climate-stress or earliness trait ranked by farmers',
     ', '.join(sorted(ranked & CLIMATE)) or 'none ranked'),
    ('Environmental health and biodiversity', 'environment', 1 if any(('landrace' in r) or ('accession' in r) for r in roles) else 0,
     'Landraces or genebank accessions among the entries', 'entry roles: ' + ', '.join(sorted(r for r in roles if r)))]
SDG = {'nutrition': 'SDG 2 Zero hunger', 'poverty': 'SDG 1 No poverty', 'gender': 'SDG 5 Gender equality',
       'climate': 'SDG 13 Climate action', 'environment': 'SDG 15 Life on land'}
given_ia = rep.get('impact_areas') or {}
rows = []
for name, key, sc, rule, ev in ia:
    rows.append(dict(group='Impact Areas', field=name, given=given_ia.get(key), suggested=sc, rule=rule, evidence=ev))
# SDG 17 always, because tricot trials and maniva work through partnerships of farmers, NARES and CGIAR
sdg_sug = '; '.join(sorted([SDG[k] for _, k, sc, _, _ in ia if sc > 0] + ['SDG 17 Partnerships for the goals'], key=lambda x: int(x.split()[1])))
rows.append(dict(group='SDGs', field='Sustainable Development Goals', given='; '.join(rep.get('sdgs') or []) or None,
                 suggested=sdg_sug, rule='One SDG per Impact Area scored 1 or 2, and SDG 17 always for tricot and maniva work',
                 evidence='Impact Areas above; trials run with farmers, national partners and CGIAR'))
rows.append(dict(group='Innovation', field='Innovation readiness level of the entries under evaluation', given=rep.get('readiness_level'),
                 suggested='8 Uncontrolled testing', rule='Entries tested by farmers on their own farms, under their own management. 9 needs evidence of validated impact, such as a release and its use',
                 evidence='%d entries in %d farmer-managed trials' % (cum['entries'], cum['trials'])))
rows.append(dict(group='Innovation', field='Innovation use', given=rep.get('innovation_use'), suggested=None,
                 rule='Set by the programme, for example a release or seed multiplication that used the trial evidence', evidence=None))
rows.append(dict(group='Policy', field='Policy change', given=rep.get('policy_change'), suggested=None, rule='Set by the programme', evidence=None))
cs = rep.get('capacity_sharing') or {}
for k, lab in [('short_term_women', 'Short-term trainees, women'), ('short_term_men', 'Short-term trainees, men'),
               ('long_term_women', 'Long-term trainees, women'), ('long_term_men', 'Long-term trainees, men'),
               ('degree_students', 'Students supervised for a degree')]:
    rows.append(dict(group='Capacity sharing for development', field=lab, given=cs.get(k), suggested=None,
                     rule='Recorded by the programme. Trial participants are not trainees', evidence=None))
bud = rep.get('budget') or {}
for k, lab in [('previous_year', 'Approved budget, previous year'), ('reporting_year', 'Approved budget, reporting year')]:
    rows.append(dict(group='Budget', field=lab, given=bud.get(k), suggested=None, rule='Set by the programme', evidence=None))
rows.append(dict(group='Outcomes', field='End-of-project outcomes and their status', given='; '.join(o.get('name', '') for o in rep.get('outcomes') or []) or None,
                 suggested=None, rule='Set by the programme, status on track, delayed or off track', evidence=None))
rows.append(dict(group='Linkages', field='CGIAR programmes and accelerators', given='; '.join(rep.get('linkages') or []) or None,
                 suggested=None, rule='Named by the programme', evidence=None))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'reporting-fields.csv'), index=False)

# trial table, aggregated
T.drop(columns=[]).to_csv(os.path.join(OUT, 'trials.csv'), index=False, float_format='%.4f')

# provenance
commit = subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%h'], capture_output=True, text=True).stdout.strip()
json.dump(dict(tricot_data_commit=commit, script='script/other-language/analysis.py', language='Python',
               trials=list(T.trial_id), reporting_year=YEAR), open(os.path.join(REPORT, 'metadata', 'provenance.json'), 'w'), indent=2)
print(ov.to_string()); print(pd.DataFrame(by_year).to_string()); print(T[['code', 'year', 'n_registered', 'overall_n', 'overall_moment', 'indicator', 'p_value', 'vs_local_n']].to_string())
print(REC.head(15).to_string())
