# Decisions for this report

The report follows the decision records of tricot-analysis-workflows at commit `44328b9`. This file records where the first draft departs from them, so the R run can close each gap.

| Topic | Decision record | What the draft did | To do in the R run |
|---|---|---|---|
| Overall preference | `ranking.md` | Used `overall_performance` at the post-harvest moment, the only overall-type question in these trials | None |
| Worth and intervals | `ranking.md` | Plackett-Luce fitted in Python by maximum likelihood with pseudo-rankings (0.5), intervals from standard errors relative to the trial mean | Replace with `PlackettLuce::PlackettLuce()` and quasi-standard errors from qvcalc |
| Do entries differ | `ranking.md` | Likelihood-ratio test of the real rankings at the fitted values against equal worth | Use `model_adequacy()` of the use case |
| Few answers | `ranking.md` | Named the first three entries per trial as a strict order | Add the bootstrap probability of a top-three place and name a top group where entries were ranked on fewer than ten farms |
| Check varieties | `ranking.md` | No probability of beating a check, because `metadata.genotypes.role` is empty in the 13 files | Fill the roles with the India team, then report reliability |
| Trait agreement | `trait-associations.md` | Kendall tau per farm on farms with all three entries ranked for both traits, simple mean, bootstrap interval | Use `row_kendall()` with pair weights. Small differences expected |
| Groups | `socioeconomic-heterogeneity.md` | Compared women and men where each had at least 12 valid answers, in five trials | The record asks for at least 20 per group. Rerun with 20 and add the permutation test. Fewer trials will qualify |
| Yield | tricot-data skill | Compared the recorded weight of the sampled plants within farms only | Agree a plot yield protocol with the India team for the next season |
| Reasons | Report standard | Keyword coding of answers in Marathi, Gujarati and English, list in `content/reason-themes.yml` | Review by a native speaker |
| Entry type | Report standard | Read from entry names (for example "MPKV" for a released variety) | Confirm with the India team |

The limitations section is kept in `content/report.md` and left out of the rendered PDF at the authors' request, through `exclude_sections` in `report.yml`.
