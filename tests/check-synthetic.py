"""Check the result tables of the synthetic example against the true values of the fixture.

Run after the analysis of reports/synthetic-example-annual, in Python or R. It reads only the
result tables and tests/fixtures/expected.json, so it checks either implementation.

Usage, from the repository root
    python3 tests/check-synthetic.py reports/synthetic-example-annual
Exits with status 1 when a check fails.
"""
import json, os, sys
import pandas as pd
from scipy.stats import spearmanr

report = sys.argv[1] if len(sys.argv) > 1 else 'reports/synthetic-example-annual'
tab = os.path.join(report, 'output', 'tables')
exp = json.load(open(os.path.join('tests', 'fixtures', 'expected.json')))
T = exp['trials']
fails = []


def check(ok, msg):
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        fails.append(msg)

# 1. counts, year and cumulative, against the fixture
ov = pd.read_csv(os.path.join(tab, 'overview.csv')).set_index('metric')
yr = [t for t in T.values() if t['year'] == 2024]
for metric, key in [('participants', 'participants'), ('women', 'women'), ('men', 'men'), ('not_stated', 'not_stated')]:
    check(ov.loc[metric, 'cumulative'] == sum(t[key] for t in T.values()), f'cumulative {metric} = {sum(t[key] for t in T.values())}')
    check(ov.loc[metric, 'reporting_year'] == sum(t[key] for t in yr), f'reporting-year {metric} = {sum(t[key] for t in yr)}')
check(ov.loc['trials', 'cumulative'] == len(T), f'cumulative trials = {len(T)}')

# 2. overall preference, order recovered in the largest trial, and the favourite found
pl = pd.read_csv(os.path.join(tab, 'pl-estimates.csv'))
true = exp['true_logworth_overall']
for tid, t in T.items():
    d = pl[(pl.trial_id == tid) & (pl.trait == 'overall_performance')]
    if t['overall_rankings'] < 15:
        check(d.empty, f'{t["code"]} has no overall model, with {t["overall_rankings"]} rankings')
        continue
    rho = spearmanr(d.logworth, [true[g] for g in d.genotype]).correlation
    check(rho >= 0.6, f'{t["code"]} rank correlation with the true worths {rho:.2f} >= 0.6 (n = {t["overall_rankings"]})')
    check(int(d.n_rankings.iloc[0]) == t['overall_rankings'], f'{t["code"]} uses all {t["overall_rankings"]} overall rankings')
big = max(T, key=lambda k: T[k]['overall_rankings'])
d = pl[(pl.trial_id == big) & (pl.trait == 'overall_performance')]
check(d.sort_values('logworth').genotype.iloc[-1] == T[big]['true_order'][0], f'favourite of {T[big]["code"]} is {T[big]["true_order"][0]}')
check(d.p_value.iloc[0] < 0.05, f'{T[big]["code"]} separates its entries')

# 3. reporting fields, every field present and SDG 17 suggested
rf = pd.read_csv(os.path.join(tab, 'reporting-fields.csv'))
check(len(rf) >= 18, f'{len(rf)} reporting fields written')
check(rf[rf.group == 'SDGs'].suggested.str.contains('SDG 17').all(), 'SDG 17 suggested')
check(not (rf[rf.group == 'Impact Areas'].suggested.astype(str) == '2').any(), 'no principal score suggested')

# 4. figure data, one file per figure
fd = os.path.join(report, 'output', 'figure-data')
check(os.path.isdir(fd) and len(os.listdir(fd)) >= 5, 'figure data written')

print(f'\n{len(fails)} failed')
sys.exit(1 if fails else 0)
