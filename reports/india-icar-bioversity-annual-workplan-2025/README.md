# Farmer evaluation of crop varieties in India with the tricot approach

*Results from the 2025 ICAR-Bioversity Annual Workplan trials*

The first report built with maniva-reports, and the worked example of the report standard.

**Status. Draft.** The numbers and figures come from a Python draft, run where R was not available and kept in `script/other-language/`. The R scripts of this repository have not been executed on these data yet. Do not publish before the R run and the authors' review.

## The question

Which entries of eight crops did farmers in four Indian states prefer in 2025, how sure are we, and what drove their choice.

## The data

Thirteen tricot trials with 646 farmers, published in [tricot-data](https://github.com/AgrDataSci/tricot-data) (https://doi.org/10.5281/zenodo.17112491, CC0 1.0), read at commit `5d5999f`, release schema v3.0. They carry the programme name "ICAR-Bioversity Annual Workplan India". Data producer is Bioversity International with ICAR-NBPGR and the BAIF Development Research Foundation. No trial data are copied here.

## What is in this folder

| Path | Content |
|---|---|
| `report.yml` | Title, authors, theme, trials, analysis settings and layout |
| `content/report.md` | The text of the report, including the limitations section |
| `content/reason-themes.yml` | Keyword list used to code farmers' reasons |
| `output/india-tricot-2025-technical-report.pdf` | The rendered report |
| `output/figures/` | The ten figures |
| `output/tables/` | Result tables behind the text, aggregated, with no participant-level rows |
| `script/other-language/` | The Python code that produced the outputs |
| `decisions/README.md` | Where the draft departs from the decision records |
| `metadata/provenance.json` | Which script and data version produced each output |

## Run it again

In R, from the repository root.

```
Rscript script/01-analysis.R reports/india-icar-bioversity-annual-workplan-2025
Rscript script/02-figures.R  reports/india-icar-bioversity-annual-workplan-2025
Rscript script/03-render.R   reports/india-icar-bioversity-annual-workplan-2025
```

The R run writes `overview.csv`, `worth.csv` and the other tables of the report standard to `output/`. Compare them with `output/tables/` and update `content/report.md` where numbers move, following `decisions/README.md`.

To rebuild only the PDF from the current text, with Python.

```
python3 reports/india-icar-bioversity-annual-workplan-2025/script/other-language/render.py reports/india-icar-bioversity-annual-workplan-2025
```

## What the results cannot support

- One season per site. Rankings changed across sites and will change across years.
- Rankings show preference among the entries tested. They do not show adoption or yield per hectare.
- Recorded yield is comparable within a farm only, because sites applied the sampling protocol differently.
- Entry types are read from names and wait for confirmation by the India team.
- Women and men were compared in five trials with at least 12 answers per group, below the 20 the decision record asks for.

## To confirm with the authors

Author order, names of BAIF staff and other national partners, funder wording, entry types, and official boundaries for the map.
