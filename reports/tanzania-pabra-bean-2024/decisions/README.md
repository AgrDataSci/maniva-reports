# Decisions for this report

Where this draft departs from the decision records of tricot-analysis-workflows, and why.

- **Overall preference.** The most recent overall-type question of each trial, as `decisions/ranking.md` asks. Trials with fewer than 15 valid rankings are not modelled (`min_rankings` in `report.yml`), stricter than the 10 of the technical report, because an annual report compares entries across trials.
- **Interim indicator.** Three trials of 2024 have no overall ranking yet. The report shows plant survival at the reproductive stage for them, the ranked trait with most answers at their latest collection moment among vigour, plant survival and disease resistance. It is labelled as early agronomic performance, never as preference.
- **Plackett-Luce in Python.** Maximum likelihood with pseudo-rankings against a ghost item, as in the PlackettLuce package, with standard errors on centred log-worth instead of quasi-standard errors. The same code produced the India report.
- **Comparison with the local variety.** One answer per plot. The 95% interval comes from a bootstrap over farms (2,000 draws), because the three plots of one farm are not independent.
- **Record across trials.** An entry's place in each trial comes from its log-worth in that trial. The share of trials with a top-three place is descriptive. Trials were not pooled, as the decision record asks for separate fits first.
- **Not done.** Trait agreement, reasons and the comparison of women and men are left to the technical report of each season. Yield is not analysed.
