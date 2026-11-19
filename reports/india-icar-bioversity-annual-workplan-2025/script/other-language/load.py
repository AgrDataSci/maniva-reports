"""Load the 13 India 2025 trials (ICAR-Bioversity Annual Workplan) from a local clone of tricot-data.

Set TRICOT_DATA to the path of the clone. Run at tricot-data commit 5d5999f (release schema v3.0).
"""
import csv, json, os
import numpy as np
import pandas as pd

REPO = os.environ.get('TRICOT_DATA', 'tricot-data')
PROGRAM = 'ICAR-Bioversity Annual Workplan India'
CROP_LABEL = {'chickpea': 'Chickpea', 'fingermillet': 'Finger millet', 'foxtailmillet': 'Foxtail millet',
              'horsegram': 'Horse gram', 'littlemillet': 'Little millet', 'maize': 'Maize', 'rice': 'Rice',
              'sorghum': 'Sorghum'}
RANK_TRAITS = ['overall_performance', 'maturity', 'disease_resistance', 'plant_height_rank', 'tillering',
               'pod_size', 'cob_size']
TRAIT_LABEL = {'overall_performance': 'Overall preference', 'maturity': 'Early maturity',
               'disease_resistance': 'Disease resistance', 'plant_height_rank': 'Plant height',
               'tillering': 'Tillering', 'pod_size': 'Pod size', 'cob_size': 'Cob or panicle size',
               'yield_rank': 'Yield (sampled plants)'}


def load():
    idx = [r for r in csv.DictReader(open(os.path.join(REPO, 'datasets.csv'))) if r['country_iso3'] == 'IND']
    trials, sites, plots = [], [], []
    for r in idx:
        d = json.load(open(os.path.join(REPO, r['path'])))
        m = d['metadata']
        if m['data_producer'].get('program') != PROGRAM:
            continue
        s = pd.DataFrame(d['site_data'])
        p = pd.DataFrame(d['plot_data'])
        place = s['adm2'].dropna().iloc[0] if 'adm2' in s and s['adm2'].notna().any() else s['adm3'].dropna().iloc[0]
        state = s['adm1'].iloc[0]
        label = f"{CROP_LABEL[r['crop_name']]}, {place}"
        t = dict(trial_id=r['trial_id'], crop=r['crop_name'], crop_label=CROP_LABEL[r['crop_name']], place=place,
                 state=state, label=label, start=m['date']['start'], end=m['date']['end'], code=m['study']['code'],
                 n_reg=len(s), women=m['participants']['women'], men=m['participants']['men'],
                 n_geno=len(m['genotypes']), title=m['study']['title'], taxon=m['crop']['taxon'])
        trials.append(t)
        s['label'] = label; p['trial_id'] = r['trial_id']; p['label'] = label
        sites.append(s); plots.append(p)
    T = pd.DataFrame(trials).sort_values(['crop_label', 'place']).reset_index(drop=True)
    S = pd.concat(sites, ignore_index=True)
    P = pd.concat(plots, ignore_index=True)
    return T, S, P


if __name__ == '__main__':
    T, S, P = load()
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    print(T.drop(columns=['title', 'taxon', 'trial_id']))
    print('farmers', len(S), 'women', T.women.sum(), 'men', T.men.sum())
    # completeness per trial and trait
    comp = P.groupby(['label', 'trait']).site_id.nunique().unstack().fillna(0).astype(int)
    print(comp.T)
    print(P.flag.value_counts(dropna=False))
    y = P[P.trait.isin(['yield_sampled_plants', 'plants_harvested', 'number_of_rows', 'row_length'])].copy()
    y['v'] = pd.to_numeric(y.value_standard.fillna(y.value), errors='coerce')
    print(y.groupby(['label', 'trait']).v.describe()[['count', 'min', '25%', '50%', '75%', 'max']].round(1).to_string())
    print(y.groupby(['trait', 'unit', 'unit_standard'], dropna=False).size())
