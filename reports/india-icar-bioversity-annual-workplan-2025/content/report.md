# Farmer evaluation of crop varieties in India with the tricot approach. Results from the 2025 ICAR-Bioversity Annual Workplan trials

## Summary

In 2025, 646 farmers in four Indian states tested 109 varieties and landraces of eight crops on their own farms, using the tricot approach. The 13 trials ran under the ICAR-Bioversity Annual Workplan, with ICAR-NBPGR and the BAIF Development Research Foundation as partners. All data are public in tricot-data, the data layer of maniva.

- **Farmers found clear winners in eight of 13 trials.** Rankings separated the varieties in finger millet and little millet in Kaprada, foxtail millet and sorghum in Shahada, rice in Kaprada and Sambalpur, chickpea in Tumkur and horse gram in Sambalpur.
- **Entries with local names often led.** Diwali Bendri (finger millet), Raylo (foxtail millet), Mothi Safed Juwar (sorghum), Dhala Kuluth (horse gram) and Kalabathi (rice) each topped a trial. Released check varieties ranked last in both little millet trials and in sorghum.
- **Test entries beat the farmer's own variety in 70% of plots.** Farmers rated 1,128 of 1,617 test plots as better than what they currently grow. Kaprada is the exception, with 43 to 53%.
- **Yield drives preference.** Sixty percent of farmers gave yield as the reason for their best variety. Late maturity, disease and lodging explain rejections.
- **Rankings are site specific.** The same varieties ranked differently across sites, so recommendations hold per location.
- **Participation and design need attention.** Of the 646 registered farmers, 537 (83%) completed the final ranking and 28% were women. In trials with 16 entries and 50 farmers, each entry was ranked on only 3 to 10 farms.

## Background

India is where tricot started, and the 2025 trials are its third generation in the country. tricot stands for triadic comparison of technology options. Each farmer grows three varieties drawn at random from a larger set and ranks them for a few traits. Many small rankings combine into one robust ranking of all the varieties.

tricot-data holds 80 tricot trials from India, with about 22,450 farmer participations since 2012.

| Phase | Years | Crops | tricot trials | Farmers | Lead and funding |
|---|---|---|---:|---:|---|
| Seeds for Needs India | 2012 to 2016 | Bread wheat, rice | 45 | 21,237 | Prem Mathur. McKnight Foundation, BMZ, ICAR |
| UNEP-GEF Mainstreaming Agricultural Biodiversity | 2019 | 15 crops, mostly millets and pulses | 22 | 567 | Prem Mathur and Jai C Rana. GEF |
| ICAR-Bioversity Annual Workplan | 2025 | 8 crops | 13 | 646 | Jai C Rana. ICAR |

The first phase proved the method at scale in the wheat and rice belts of north India (van Etten et al. 2019). The second moved it to neglected crops. The Annual Workplan now uses tricot as its routine tool to evaluate elite germplasm lines, released varieties and farmers' landraces with tribal and smallholder communities in central and western India.

The trials sit inside a wider workplan led by ICAR-NBPGR and Bioversity International. Programme reporting for 2024 to 2026 lists seed multiplication of 268 varieties of 16 crops, mother trials, nutritional profiling, pre-breeding in sesame and chilli, four community seed banks and on-farm conservation of 173 landraces. This report covers the part with open, farmer-generated data, the 2025 tricot trials.

## Trials and methods

Thirteen trials ran at five locations between June 2025 and May 2026. BAIF field teams worked with farmers in Akole and Shahada (Maharashtra), Kaprada (Gujarat), Sambalpur (Odisha) and Tumkur (Karnataka).

![Map of central and southern India with the five trial locations](output/figures/fig01-map.png)

*Figure 1. Trial locations, farmers registered and crops tested in 2025. Equal Earth projection. State boundaries are indicative.*

| Crop | Location | State | Season | Entries | Farmers registered | Completed final ranking |
|---|---|---|---|---:|---:|---:|
| Chickpea | Akole | Maharashtra | Dec 2025 to May 2026 | 8 | 50 | 50 |
| Chickpea | Tumkur | Karnataka | Nov 2025 to Apr 2026 | 8 | 50 | 37 |
| Finger millet | Akole | Maharashtra | Jul to Dec 2025 | 16 | 50 | 50 |
| Finger millet | Kaprada | Gujarat | Jul to Dec 2025 | 16 | 50 | 45 |
| Finger millet | Sambalpur | Odisha | Jul to Dec 2025 | 16 | 48 | 25 |
| Foxtail millet | Shahada | Maharashtra | Sep to Dec 2025 | 9 | 50 | 26 |
| Horse gram | Sambalpur | Odisha | Nov 2025 to Feb 2026 | 11 | 48 | 21 |
| Little millet | Akole | Maharashtra | Jul to Dec 2025 | 10 | 50 | 50 |
| Little millet | Kaprada | Gujarat | Jul to Nov 2025 | 9 | 50 | 46 |
| Maize | Shahada | Maharashtra | Jun to Oct 2025 | 10 | 50 | 50 |
| Rice | Kaprada | Gujarat | Jul to Dec 2025 | 16 | 50 | 48 |
| Rice | Sambalpur | Odisha | Aug to Dec 2025 | 16 | 50 | 43 |
| Sorghum | Shahada | Maharashtra | Jun to Nov 2025 | 10 | 50 | 46 |

**Design.** Each farmer received a package of three entries, labelled A, B and C, and grew them next to the usual crop under usual management. Entries combined released varieties, elite lines and local landraces.

**Data collection.** Field staff recorded data with ODK Collect in three moments, and the forms were stored in FormShare.

1. Registration. Farmer profile, farm size, seed source and management practices.
2. After the reproductive stage. Rankings for plant height, tillering or cob, panicle and pod size, and disease resistance.
3. Post-harvest. Rankings for maturity and overall preference, a comparison of each entry with the farmer's own variety, the grain weight of five sampled plants, and the reasons for the best and worst entry.

**Analysis.** We fitted a Plackett-Luce model to the rankings of each trial and trait (Turner et al. 2020). The model returns a log-worth per variety, where zero is the trial average and higher values mean farmers preferred the variety more often. A likelihood ratio test checks if the varieties differ at all. We measured agreement between traits with Kendall's tau within each farm. Free-text reasons, written in Marathi, Gujarati and English, were coded into eight themes by keyword.

The figures in this draft were computed in Python from the public trial files. The matching R scripts with PlackettLuce and gosset accompany the report, and the published version should run from those.

## Participants

The trials registered 646 farmers in 31 villages, of whom 178 (28%) were women. Women were 44 to 46% of participants in the Kaprada millet trials and the Sambalpur horse gram trial, and 10 to 18% in Shahada and Tumkur.

The typical participant is a smallholder who saves seed.

- Median age is 43 years, 40 for women and 45 for men.
- Median farm size is 1.0 ha, and 84% of farms are 2 ha or smaller.
- Among the 472 farmers who reported a seed source, 59% use their own seed, 33% buy in the local market and 6% get seed from neighbours or relatives. One farmer named a community seed bank.
- Seventy-three percent already grow the crop they tested. For the others the trial introduced a new crop.
- Only 39 farmers had joined a tricot trial the year before, so most were new to the method.

Farms are diverse and low-input. Rice is grown by 75% of participants, followed by pigeonpea (41%), black gram (34%), little millet (32%) and finger millet (30%). Almost all farmers apply cow dung (94%) and most add urea (88%). Twenty-nine percent farm without irrigation.

Eighty-three percent of registered farmers completed the final ranking. Completion reached 100% in four trials and fell to about half in three trials, finger millet and horse gram in Sambalpur and foxtail millet in Shahada.

![Bars of farmers registered and completing per trial, and share of women](output/figures/fig02-participation.png)

*Figure 2. Farmers registered and completing the final ranking, and share of women, per trial.*

## Variety performance

Farmers separated the varieties in eight of the 13 trials. The table gives the three entries farmers preferred most in each trial. Worth is the probability that an entry is ranked first among all entries of the trial. The p-value tests whether the entries differ in overall preference.

| Trial | Farmers | First | Second | Third | Worth of first | Worth if all equal | p-value |
|---|---:|---|---|---|---:|---:|---:|
| Chickpea, Akole | 50 | Vijay | BGD-111-1 | Gavathi Pivla Harbhara | 0.21 | 0.13 | 0.21 |
| Chickpea, Tumkur | 37 | Virat | Kripa | PKV-2 | 0.29 | 0.13 | 0.050 |
| Finger millet, Akole | 50 | T-14 | Nagali Let | F-9 | 0.12 | 0.06 | 0.57 |
| Finger millet, Kaprada | 45 | Diwali Bendri | Dasarbendri | Safed Nagli | 0.65 | 0.06 | < 0.001 |
| Finger millet, Sambalpur | 25 | Dhawalperi | VL-929-Vegavathi | F-7 | 0.13 | 0.06 | 0.21 |
| Foxtail millet, Shahada | 26 | Raylo | Lahan Badhi | Moti badi | 0.50 | 0.11 | < 0.001 |
| Horse gram, Sambalpur | 21 | Dhala Kuluth | Gabra Hulga | VLG 14 | 0.47 | 0.09 | 0.035 |
| Little millet, Akole | 50 | Dhanori | Sakhali | Juni Varai | 0.18 | 0.10 | 0.71 |
| Little millet, Kaprada | 46 | Gari varai | Sakhali | Dudhamogara | 0.32 | 0.11 | 0.008 |
| Maize, Shahada | 50 | Kehari Lalyo dudo | Lahan Tapkiri Mukai | Kehari Mukai | 0.18 | 0.10 | 0.26 |
| Rice, Kaprada | 48 | Surati kolam | Gari kolapi | Indrayani (MPKV) | 0.18 | 0.06 | < 0.001 |
| Rice, Sambalpur | 43 | Kalabathi | Talmuri | Kusumkali | 0.24 | 0.06 | < 0.001 |
| Sorghum, Shahada | 46 | Mothi Safed Juwar | Dudh Mogara | Mothi Dudh Mogara | 0.62 | 0.10 | < 0.001 |

In the figures below, points are log-worth estimates and bars are 95% intervals. Green marks trials where the entries differ (p < 0.05). Grey marks trials where they do not.

### Finger millet

Kaprada farmers singled out three entries, Diwali Bendri, Dasarbendri and Safed Nagli. Diwali Bendri alone holds 65% of the worth among 16 entries. The released check Phule Nachani (MPKV) ranked 14th there, and only one of nine farmers rated it better than their own variety.

Akole and Sambalpur show no reliable differences. In Sambalpur only 25 farmers completed the ranking, so each entry was judged on three to eight farms.

![Log-worth of finger millet entries at three sites](output/figures/fig03-finger-millet.png)

*Figure 3. Overall preference for finger millet entries in Akole, Kaprada and Sambalpur.*

### Rice

Both rice trials separate the entries well. In Kaprada, Surati kolam and Gari kolapi lead, with the released Indrayani (MPKV) third. In Sambalpur, Kalabathi, Talmuri and Kusumkali lead, and all nine farmers who grew Kalabathi rated it better than their own rice.

The TC lines did poorly in Sambalpur, where TCDM-1, TCVM and Vikram TCR sit in the bottom four. In Kaprada TCDM-1 ranks 15th of 16, while Vikram TCR ranks sixth.

![Log-worth of rice entries at two sites](output/figures/fig04-rice.png)

*Figure 4. Overall preference for rice entries in Kaprada and Sambalpur.*

### Little millet and foxtail millet

Gari varai leads little millet in Kaprada, and Sakhali is second at both sites. Phule Ekadasi (MPKV) ranks last in Kaprada and in Akole. The Akole trial does not separate the entries.

In Shahada, Raylo takes half of the worth among nine foxtail millet entries, ahead of Lahan Badhi and Moti badi. The improved entries SiA-3088 and Krishnadevaraya rank eighth and ninth.

![Log-worth of little millet and foxtail millet entries](output/figures/fig05-small-millets.png)

*Figure 5. Overall preference for little millet entries in Akole and Kaprada, and foxtail millet entries in Shahada.*

### Maize and sorghum

Mothi Safed Juwar dominates the sorghum trial with 62% of the worth. Phule Anuradha/Godavari (MPKV) ranks last. The ten maize entries are not distinguishable, with Kehari Lalyo dudo and Lahan Tapkiri Mukai on top.

![Log-worth of maize and sorghum entries in Shahada](output/figures/fig06-maize-sorghum.png)

*Figure 6. Overall preference for maize and sorghum entries in Shahada.*

### Chickpea and horse gram

Tumkur farmers preferred Virat and Kripa, and Akole farmers put Vijay and BGD-111-1 first. The two chickpea rankings run in opposite directions, and only Tumkur shows differences at the 5% level.

Dhala Kuluth and Gabra Hulga lead the horse gram trial in Sambalpur. Every farmer who grew them rated them better than the local variety. Only 21 of 48 farmers completed this trial, so the result needs a second season.

![Log-worth of chickpea and horse gram entries](output/figures/fig07-pulses.png)

*Figure 7. Overall preference for chickpea entries in Akole and Tumkur, and horse gram entries in Sambalpur.*

### Rankings change across sites

The same entries ranked differently from one site to the next. Rank correlations between sites range from -0.67 (chickpea, Akole and Tumkur) to 0.60 (little millet, Akole and Kaprada). Finger millet rankings in Kaprada are unrelated to those in Akole (-0.10) and Sambalpur (-0.12). Variety advice from these trials therefore applies to the site that produced it.

### Test entries against the farmer's own variety

Farmers rated 70% of test plots (1,128 of 1,617) as better than the variety they currently grow. The share is 64% or higher in ten trials. Kaprada stands apart, with 43% for little millet, 45% for finger millet and 53% for rice, which suggests that farmers there already hold well-adapted material.

Sorghum (138 of 138 plots) and maize (140 of 150) in Shahada sit at the other extreme. A score with no variation says little about the entries and points to a need to review how the question was asked there.

![Share of test plots rated better than the farmer's own variety, per trial](output/figures/fig08-local.png)

*Figure 8. Test plots rated better than the farmer's own variety, per trial.*

## Yield

Farmer preference follows the measured grain weight closely. On each farm we ordered the three entries by the grain weight of the sampled plants and compared that order with the farmer's overall ranking. Mean Kendall tau across 507 farms is 0.58, and on 59% of farms the two orders are identical.

Agreement varies by site. It is near complete in Akole (0.96 for finger millet, 0.87 for little millet) and in Sambalpur (0.69 to 0.89). It is weak in Kaprada (0.18 to 0.35), where farmers gave taste, maturity and disease as reasons more often.

The yield data support comparisons within a farm and do not support comparisons between trials or estimates per hectare. The form asked for the grain weight of five sampled plants, and sites applied it differently.

- In Sambalpur, staff recorded 36 to 247 plants harvested per plot in place of five.
- In the Tumkur chickpea trial, recorded weights range from 100 to 900 g with a median of 500 g. The Akole chickpea trial recorded 87 to 154 g. Tumkur is also the only trial where yield order and preference disagree (tau of -0.31).

A plot-level yield protocol with one unit and one sampling rule would turn these records into yield estimates that breeders and release committees accept.

## What drives farmer preference

Yield and the size of the cob or panicle track overall preference. The other ranked traits barely do. Cob or panicle size has a mean Kendall tau of 0.62 with overall preference and yield has 0.58. Disease resistance (0.20), pod size (0.16) and plant height (0.14) follow at a distance. Early maturity (0.04) and tillering (0.03) show no link.

![Kendall tau between each trait and overall preference](output/figures/fig09-trait-agreement.png)

*Figure 9. Agreement of each trait with overall preference within farms, pooled across trials.*

Farmers' own words confirm it. Of the 484 farmers who explained their best entry, 60% named yield or production. Plant type, meaning panicle, tillers, pods, height and grain size, follows with 16%, then taste and eating quality (10%) and market price and appearance (10%).

Reasons to reject an entry differ from reasons to choose one. Low yield still leads (57% of 451 farmers), and late maturity (18%), disease and pests (10%) and lodging (4%) matter far more for the worst entry than for the best. Taste and market value make a variety a favourite. Lateness, disease and lodging disqualify it.

![Themes farmers gave for their most and least preferred entry](output/figures/fig10-reasons.png)

*Figure 10. Reasons farmers gave for their most and least preferred entry, coded into themes. A farmer can mention several themes.*

Sites differ sharply. Outside Kaprada, 80% of farmers named yield for their best entry. In Kaprada 11% did. Taste led there (25%), and late maturity (45%) and disease (27%) drove rejections. Part of this contrast may come from how each field team asked and recorded the question.

### Women and men

Women and men mostly agree on the best varieties, with signs that they weigh traits differently. We compared rankings by gender in the five trials with at least 12 women and 12 men.

- In four trials the rankings of women and men do not differ. In Kaprada both groups put the same entry first, Diwali Bendri for finger millet and Gari varai for little millet.
- In the Akole chickpea trial they differ (p = 0.020). Women ranked Kripa first and men ranked Vijay first.
- Women mentioned plant type more often than men, both for the best entry (22% against 14%) and the worst (19% against 8%). They also cited disease (14% against 8%) and lodging (7% against 3%) more often as reasons to reject. Men cited yield more often (62% against 55% for the best entry).

These gender results are exploratory. Five trials allowed the comparison, and one significant result among five tests can arise by chance.

## Limitations and next steps

The trials deliver usable variety rankings in one season, and four changes would make the next round stronger.

1. **Match the number of entries to the number of farmers.** Trials with 16 entries and 50 farmers place each entry on six to ten farms, and fewer once farmers drop out. The chickpea, little millet and maize trials, with 8 to 10 entries, reach 13 to 19 farms per entry. Fewer entries per site, or 100 or more farmers, will give tighter rankings.
2. **Keep farmers to the end.** Three trials lost about half of their farmers before the final ranking. The disease ranking is also missing for many farms in Sambalpur and in both chickpea trials.
3. **Standardise yield measurement.** One protocol for plot yield, with fixed units and sampling, across all sites.
4. **Record the type of each entry.** The metadata do not yet say which entries are released varieties, elite lines, landraces or checks. This report reads entry type from names, and the India team should confirm it before publication.

Other points to keep in mind when reading the results.

- One season per site. Rankings changed across sites and will change across years.
- The comparison with the farmer's own variety shows no variation in the Shahada sorghum trial and little in maize.
- Reasons were coded by keyword from three languages. A native-speaker review will refine the themes.
- The Plackett-Luce estimates in this draft come from a Python implementation and need a final run with the PlackettLuce R package.

The 2026 season can build on this. Promising entries per site are ready for a second year of testing, seed multiplication through the community seed banks, and consumer testing for crops such as horse gram.

## Data availability

All data behind this report are open under CC0 1.0 in [tricot-data](https://github.com/AgrDataSci/tricot-data), archived on Zenodo at [doi.org/10.5281/zenodo.17112491](https://doi.org/10.5281/zenodo.17112491). The 13 trials carry the programme name ICAR-Bioversity Annual Workplan India in their metadata. Each trial is one JSON file, listed in `datasets.csv`.

tricot-data is the data layer of [maniva](https://github.com/AgrDataSci/maniva), an open commons of evidence, protocols, data and analysis for agricultural research. Anyone, including an AI assistant, can reach the protocols, the data and the analysis workflows from that single entry point. Site coordinates are rounded to two decimals to protect participants.

## Contributors

| Name | Affiliation | Role |
|---|---|---|
| Jai C Rana | Bioversity International | Project leader |
| Sarika Mittra | Bioversity International | Project manager |
| Rashmi Yadav | ICAR-National Bureau of Plant Genetic Resources | Project member |
| Harinder Vishwakarma | Bioversity International | Data manager |
| Kauê de Sousa | Bioversity International | Data manager, analysis |

Field implementation was led by the BAIF Development Research Foundation. Names of BAIF staff and other national partners are still to be added.

## Acknowledgements

We thank the 646 farmers who grew, observed and ranked the varieties. The trials were implemented under the ICAR-Bioversity Annual Workplan, funded by the Indian Council of Agricultural Research (ICAR). Data curation and publication were supported by the Gates Foundation (1000FARMS, INV-031561), the Kingdom of Norway through the Global Crop Diversity Trust (BOLD Work Package 7, CONT-1773) and the CGIAR Digital Transformation Accelerator.

## References

- de Sousa K, Laporte M-A, et al. Global multi-crop agricultural trial data supported by citizen science. Zenodo. https://doi.org/10.5281/zenodo.17112491
- de Sousa K, van Etten J, Manners R, et al. (2024). The tricot approach. An agile framework for decentralized on-farm testing supported by citizen science. A retrospective. Agronomy for Sustainable Development 44, 8. https://doi.org/10.1007/s13593-023-00937-1
- Turner HL, van Etten J, Firth D, Kosmidis I (2020). Modelling rankings in R. The PlackettLuce package. Computational Statistics 35, 1027-1057. https://doi.org/10.1007/s00180-020-00959-3
- van Etten J, de Sousa K, Aguilar A, et al. (2019). Crop variety management for climate adaptation supported by citizen science. PNAS 116, 4194-4199. https://doi.org/10.1073/pnas.1813720116
