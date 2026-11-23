# Synthetic Example Programme

## Section 1: Fact sheet and executive summary

**This report is built on synthetic data.** The programme, crop, country, districts, entries and people are invented in `tests/fixtures/`. It exists to test the maniva-reports code and to show the layout without speaking for any real programme. No number here describes a real trial.

<!-- class: factsheet -->
| Field | Value |
|---|---|
| Programme | Synthetic Example Programme |
| Data producer | Synthetic Research Institute |
| Implementing partner | Synthetic National Partner |
| Project leader | Ada Example, Synthetic Research Institute |
| Reporting year | Trials that started in 2024, with the record since 2023 |
| Geographic scope | Synthetic country, 4 districts |
| Crop | examplebean (*Fictus exemplaris*), an invented crop |
| Funders | Synthetic Funder, Synthetic Award (SYN-0001) |
| Data | `tests/fixtures/tricot-data/`, synthetic, CC0 1.0 |

<!-- class: yearbox -->
| | 2024 | 2023 to 2024 |
|---|---:|---:|
| Trials | 2 | 4 |
| Participants registered | 220 | 370 |
| Women among participants | 94 (43%) | 175 (47%) |
| Entries tested | 8 | 8 |
| Plots rated better than the local variety | 68% of 294 | 70% of 615 |

The synthetic programme tested 8 entries of examplebean with 220 farmers in two trials that started in 2024, and 370 farmers in four trials since 2023.

Farmers clearly preferred SYN-01 and SYN-02 in the main 2024 trial, which separated its entries (98 farmers). SYN-08 came last. The fixture was built so that SYN-01 is the true favourite and SYN-08 the least preferred, and the analysis recovers that order.

The second 2024 trial has no final ranking yet, so the report shows drought tolerance at the reproductive stage for it, as an early signal.

## Section 2: Progress towards outcomes

The synthetic programme names no outcome. In a real report, each outcome the programme names goes here with the status it assigns, as [on track], [delayed] or [off track], and the evidence from the data.

| Outcome, as named by the programme | Status | Evidence from the trial data |
|---|---|---|
| Farmers evaluate new entries on their own farms | Empty | 370 participants in 4 trials since 2023, 220 in 2024 |

## Section 3: Results of the 2024 season

Two trials started in 2024. SYN24A reached a final ranking of overall preference. SYN24B holds rankings up to the reproductive stage only.

| Trial | Start | Entries | Registered | Indicator | Farmers ranking | Entries differ | Better than local |
|---|---|---:|---:|---|---:|---|---:|
| SYN24A | Mar 2024 | 8 | 120 | Overall preference, post-harvest | 98 | Yes (p < 0.001) | 68% of 294 |
| SYN24B | Sep 2024 | 8 | 100 | Drought tolerance, reproductive | 100 | No (p = 0.28) | Not asked yet |

![Log-worth of the entries in the 2024 trials](output/figures/fig04-year-results.png)

*Figure 1. Log-worth of each entry with its 95% interval, from one Plackett-Luce model per trial (Turner et al. 2020). Overall preference where farmers gave it, drought tolerance at the reproductive stage elsewhere. Grey marks a trial where the entries do not differ at the 5% level. Synthetic data.*

**Overall preference.** In SYN24A, SYN-01 had the highest log-worth (1.18, standard error 0.27, ranked on 37 farms), followed by SYN-02 (1.11, 0.27, 39 farms) and SYN-03 (0.80, 0.25, 40 farms). SYN-08 came last (-1.94, 0.38, 34 farms).

## Section 4: Quantitative overview of key results

![Participants by year and gender](output/figures/fig02-participants.png)

*Figure 2. Participants registered by the year the trial started, women, men and not stated. Synthetic data.*

<!-- split -->
![Map of trial sites](output/figures/fig01-map.png)

*Figure 3. Trial sites, sized by participants. The synthetic sites lie in the open ocean on purpose, so no real place is implied. Equal Earth projection.*

| District | Since 2023 | 2024 |
|---|---:|---:|
| Beta District | 93 | 55 |
| Gamma District | 93 | 55 |
| Alpha District | 92 | 55 |
| Delta District | 92 | 55 |

![Entries tested by year](output/figures/fig03-entries.png)

*Figure 4. Entries tested by year, new or tested in an earlier season. Synthetic data.*

![Record of entries across trials](output/figures/fig06-entry-record.png)

*Figure 5. Entries ranked for overall preference in three or more trials, by the share of those trials with a top-three place. Synthetic data.*

**Reporting fields and suggested tags.** Every field of the results framework, with the tags maniva suggests from the data.

<!-- insert: output/tables/reporting-fields.csv -->

## Section 5: Partnerships

| Institution | Role in the trials | Trials |
|---|---|---:|
| Synthetic Research Institute | Data producer | 4 |
| Synthetic National Partner | Implementing partner | 4 |

## Section 6: Portfolio linkages

| Funder | Award | Number | Trials |
|---|---|---|---:|
| Synthetic Funder | Synthetic Award | SYN-0001 | 4 |

## Section 7: Key result story

### Farmers find the true favourite in one season

In the synthetic trial SYN24A, 98 farmers ranked SYN-01 first among 8 entries, the entry the fixture was built to favour.

The fixture draws each farmer's ranking from a model with known worths, so the right answer is known. One Plackett-Luce model on the 98 rankings put the entries in the true order and separated them clearly.

The smaller trials of 2023, with 45 and 62 rankings of 6 entries, recovered the order less well. That is the point of the example. Fewer answers give a rougher order, and the report says so.

![Share of plots rated better than the local variety](output/figures/fig05-vs-local.png)

*Figure 6. Plots rated better than the local variety by year, with 95% intervals from a bootstrap over farms. Synthetic data.*

## Limitations and next steps

- Every number comes from synthetic data and describes no real trial.
- The fixture follows the tricot-data format closely enough for the readers of this repository. It is not a full release file.
- Run `tests/check-synthetic.py` after any change to the analysis code. It compares the result tables with the true values in `tests/fixtures/expected.json`.

## Data availability

The synthetic trials are in `tests/fixtures/tricot-data/`, built by `tests/fixtures/make-synthetic-trials.py` with a fixed seed. Real trial data are in tricot-data, https://doi.org/10.5281/zenodo.17112491.

## References

- Turner HL, van Etten J, Firth D, Kosmidis I. 2020. Modelling rankings in R. The PlackettLuce package. Computational Statistics 35, 1027 to 1060. https://doi.org/10.1007/s00180-020-00959-3
