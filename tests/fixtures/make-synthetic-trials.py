"""Build the synthetic test fixture, tricot trials of an invented programme with known answers.

Everything here is invented. The programme, the crop ("examplebean", Fictus exemplaris), the
country (ISO code XXX), the districts, the entries and the people do not exist. Rankings are
drawn from a Plackett-Luce model with true worths written to expected.json, so a test can
check that an analysis recovers them.

The files follow release schema 3.0 of tricot-data closely enough for the maniva-reports
readers. Rerun only to change the fixture, and commit the output with expected.json.

Usage, from the repository root
    python3 tests/fixtures/make-synthetic-trials.py
"""
import json, os
import numpy as np
import pandas as pd

OUT = os.path.join('tests', 'fixtures', 'tricot-data')
rng = np.random.default_rng(20261123)
PROGRAM = 'Synthetic Example Programme'
PRODUCER = 'Synthetic Research Institute'
PARTNER = 'Synthetic National Partner'
DISTRICTS = {'Alpha District': (0.45, -1.10), 'Beta District': (1.10, -0.40), 'Gamma District': (1.70, -1.60),
             'Delta District': (0.80, -1.90)}  # in the open ocean on purpose, no real place
ENTRIES = ['SYN-01', 'SYN-02', 'SYN-03', 'SYN-04', 'SYN-05', 'SYN-06', 'SYN-07', 'SYN-08']
# true log-worth of overall preference, centred; SYN-01 is the clear favourite, SYN-08 the least
TRUE = dict(zip(ENTRIES, [1.2, 0.8, 0.5, 0.2, 0.0, -0.4, -0.9, -1.4]))
CHECK = 'SYN-05'
# true agreement of other traits with overall preference, via correlated worths
TRAITS = {'yield_rank': 0.9, 'marketability': 0.6, 'drought_tolerance': 0.3}
TRIALS = [  # id, code, start, end, entries, sites, share women, overall answers
    ('syn000000001', 'SYN23A', '2023-03-01', '2023-08-30', ENTRIES[:6], 90, 0.50, 0.80),
    ('syn000000002', 'SYN23B', '2023-09-15', '2024-02-20', ENTRIES[:6], 60, 0.45, 0.75),
    ('syn000000003', 'SYN24A', '2024-03-05', '2024-09-01', ENTRIES, 120, 0.55, 0.85),
    ('syn000000004', 'SYN24B', '2024-09-20', '2025-03-10', ENTRIES, 100, 0.40, 0.00),  # season not finished, no final ranking
]


def pl_order(items, logw):
    """One ranking of items drawn from a Plackett-Luce model, best first."""
    left = list(items); out = []
    while left:
        w = np.exp([logw[i] for i in left]); p = w / w.sum()
        j = rng.choice(len(left), p=p); out.append(left.pop(j))
    return out


rows_index, expected = [], dict(programme=PROGRAM, true_logworth_overall=TRUE, check=CHECK, trials={})
for tid, code, start, end, items, n, women, answer in TRIALS:
    k = len(items)
    sites, plots = [], []
    alloc = np.zeros(k, int)
    n_overall = 0
    for s in range(1, n + 1):
        sid = f'{tid}-{s}'
        dist = list(DISTRICTS)[s % len(DISTRICTS)]
        lat0, lon0 = DISTRICTS[dist]
        gender = 'woman' if rng.random() < women else 'man'
        if rng.random() < 0.03:
            gender = None
        sites.append(dict(site_id=sid, trial_id=tid, country_iso3='XXX', country='Synthetic country', crop='examplebean',
                          longitude=round(lon0 + rng.normal(0, 0.08), 2), latitude=round(lat0 + rng.normal(0, 0.08), 2),
                          geo_source='synthetic', geo_uncertainty=None, geo_flag=None, farmer_gender=gender,
                          age=int(rng.integers(20, 70)), adm1='Synthetic Region', adm2=dist, location=f'Village {s:03d}'))
        # a balanced incomplete block, three entries per farm, spread evenly
        pkg = list(np.array(items)[np.argsort(alloc + rng.random(k))[:3]])
        for g in pkg:
            alloc[items.index(g)] += 1
        plotlab = dict(zip(pkg, 'ABC'))
        # vegetative and reproductive rankings of other traits, for every farm
        for trait, rho in TRAITS.items():
            lw = {g: rho * TRUE[g] + np.sqrt(1 - rho ** 2) * rng.normal(0, 0.8) for g in pkg}
            order = pl_order(pkg, lw)
            moment = 'Post-harvest' if trait in ('yield_rank', 'marketability') else 'Reproductive'
            if moment == 'Post-harvest' and answer == 0:
                continue
            for r, g in enumerate(order, 1):
                plots.append(dict(site_id=sid, plot=plotlab[g], genotype_name=g, collection_moment=moment, moment_days=None,
                                  moment_date=None, trait=trait, trait_id=None, trait_original=trait, value=str(r),
                                  value_type='rank', unit=None, flag=None, value_standard=str(r), unit_standard=None))
        if rng.random() < answer:
            n_overall += 1
            order = pl_order(pkg, TRUE)
            for r, g in enumerate(order, 1):
                plots.append(dict(site_id=sid, plot=plotlab[g], genotype_name=g, collection_moment='Post-harvest', moment_days=None,
                                  moment_date=None, trait='overall_performance', trait_id=None, trait_original='overall_performance',
                                  value=str(r), value_type='rank', unit=None, flag=None, value_standard=str(r), unit_standard=None))
                # better than the local variety with a probability that rises with worth
                better = rng.random() < 1 / (1 + np.exp(-(TRUE[g] + 0.6)))
                plots.append(dict(site_id=sid, plot=plotlab[g], genotype_name=g, collection_moment='Post-harvest', moment_days=None,
                                  moment_date=None, trait='overall_performance_vs_local', trait_id=None,
                                  trait_original='overall_performance_vs_local', value='better' if better else 'worse',
                                  value_type='vs_local', unit=None, flag=None, value_standard=None, unit_standard=None))
                y = max(50.0, rng.normal(900 + 250 * TRUE[g], 180))
                plots.append(dict(site_id=sid, plot=plotlab[g], genotype_name=g, collection_moment='Post-harvest', moment_days=None,
                                  moment_date=None, trait='yield', trait_id=None, trait_original='yield', value=f'{y:.0f}',
                                  value_type='numeric', unit='kg/ha', flag=None, value_standard=f'{y:.0f}', unit_standard='kg/ha'))
        # germination for every farm, as in real trials
        for g in pkg:
            plots.append(dict(site_id=sid, plot=plotlab[g], genotype_name=g, collection_moment='Vegetative', moment_days=21,
                              moment_date=None, trait='plant_count', trait_id=None, trait_original='plant_count',
                              value=str(int(rng.integers(20, 60))), value_type='numeric', unit='count', flag=None,
                              value_standard=None, unit_standard='count'))
    S = pd.DataFrame(sites)
    wom = int((S.farmer_gender == 'woman').sum()); men = int((S.farmer_gender == 'man').sum())
    meta = dict(
        schema_version='3.0', identifier='synthetic-fixture-no-doi', license='CC0-1.0',
        study=dict(id=tid, code=code, title=f'Synthetic examplebean trial {code}', description='Synthetic test fixture. Not a real trial.',
                   type='on-farm', objective='variety evaluation', experimental_site='farm', unit_of_analysis='genotype',
                   country_iso2='XX', country_iso3='XXX', country_name='Synthetic country', source_platform='synthetic',
                   collection_moments=[dict(moment=m) for m in ('Vegetative', 'Reproductive', 'Post-harvest')]),
        date=dict(start=start, end=end), geo_location={}, location_privacy=dict(method='Synthetic coordinates in the open ocean'),
        data_producer=dict(name=PRODUCER, identifier=None, principal_investigator='Ada Example', email=None,
                           program=PROGRAM, partner=PARTNER),
        contributors=[dict(name='Ada Example', orcid=None, affiliation=PRODUCER, contributorType='ProjectLeader'),
                      dict(name='Ben Sample', orcid=None, affiliation=PARTNER, contributorType='ProjectMember'),
                      dict(name='Cleo Placeholder', orcid=None, affiliation=PRODUCER, contributorType='DataManager')],
        crop=dict(name='examplebean', taxon='Fictus exemplaris'),
        participants=dict(total=n, women=wom, men=men, not_stated=n - wom - men),
        genotypes=[dict(genotype_name=g, role='comparative check' if g == CHECK else 'release candidate') for g in items],
        funder=[dict(funderName='Synthetic Funder', funderIdentifier=None, awardTitle='Synthetic Award', awardNumber='SYN-0001')],
        variables=[], admin_levels=dict(adm1='region', adm2='district', adm3=None, adm4=None, adm5=None))
    path = f'data/examplebean/examplebean-XXX-{tid}.json'
    os.makedirs(os.path.join(OUT, 'data', 'examplebean'), exist_ok=True)
    json.dump(dict(metadata=meta, site_data=sites, plot_data=plots), open(os.path.join(OUT, path), 'w'), indent=1)
    P = pd.DataFrame(plots)
    rows_index.append(dict(trial_id=tid, crop_name='examplebean', taxon='Fictus exemplaris', country_iso3='XXX',
                           country_name='Synthetic country', data_producer=PRODUCER, start_date=start, end_date=end,
                           type='on-farm', management='farmer-managed (tricot)', objective='variety evaluation',
                           participants=n, n_sites=n, n_genotypes=k, n_plot_rows=len(P), n_genotype_rows=0, n_companions=0,
                           collection_moments='Vegetative; Reproductive; Post-harvest',
                           ranked_traits='; '.join(sorted(P[P.value_type == 'rank'].trait.unique())), path=path,
                           size_mb=round(os.path.getsize(os.path.join(OUT, path)) / 1e6, 2), license='CC0-1.0'))
    expected['trials'][tid] = dict(code=code, year=int(start[:4]), participants=n, women=wom, men=men,
                                   not_stated=n - wom - men, entries=k, overall_rankings=n_overall,
                                   true_order=sorted(items, key=lambda g: -TRUE[g]))
pd.DataFrame(rows_index).to_csv(os.path.join(OUT, 'datasets.csv'), index=False)
json.dump(expected, open(os.path.join('tests', 'fixtures', 'expected.json'), 'w'), indent=2)
print(pd.DataFrame(rows_index)[['trial_id', 'start_date', 'participants', 'n_genotypes', 'size_mb']])
print({t: v['overall_rankings'] for t, v in expected['trials'].items()})
