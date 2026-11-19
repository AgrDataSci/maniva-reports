<!-- badges: start -->
[![ProjStatus](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Lifecycle](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/AgrDataSci/maniva-reports/blob/main/LICENSE)
<!-- badges: end -->

<a href="https://github.com/AgrDataSci/maniva"><img src="docs/maniva-logo.svg" alt="Part of maniva" height="64" align="right"></a>

# maniva-reports

*Technical reports from on-farm trial data in the maniva commons*

> Kauê de Sousa

A report standard, a page layout and an R workflow that turn trial data into a technical report people want to read. Trial files in the [tricot-data](https://github.com/AgrDataSci/tricot-data) format go in. A PDF with a cover, key findings, variety rankings, figures and a data statement comes out, ready for CGSpace or a donor report.

This repository belongs to the analysis layer of [maniva](https://github.com/AgrDataSci/maniva). The methods come from [tricot-analysis-workflows](https://github.com/AgrDataSci/tricot-analysis-workflows) and the data from [tricot-data](https://github.com/AgrDataSci/tricot-data). This repository adds how to tell the story and how to lay it out. [ClimMob-analysis](https://github.com/AgrDataSci/ClimMob-analysis) keeps producing the standard report of a ClimMob project. maniva-reports serves data that are already in the commons, across trials, seasons and programmes.

## Who it is for

| User | Decision it improves | Sign of use |
|---|---|---|
| National partners and programme teams who ran the trials, and the scientists and data managers who support them | Which entries to test again, multiply or release, and what to report to funders | Reports published on CGSpace and in PRMS that cite the data |
| Partners deciding whether to publish their trial data | Whether sharing data in maniva is worth the effort | New trial sets contributed to tricot-data |

## See it

The first report covers the 2025 tricot trials of the ICAR-Bioversity Annual Workplan in India, with 646 farmers, 13 trials and eight crops.

- [The PDF](reports/india-icar-bioversity-annual-workplan-2025/output/india-tricot-2025-technical-report.pdf)
- [The report folder](reports/india-icar-bioversity-annual-workplan-2025/), with the text, the settings, the result tables and the code

It is a draft. See its README for what is still to confirm.

## How it works

1. **Choose the trials.** By trial id, or by country, crop, year and programme, in `report.yml`.
2. **Run the analysis.** The R scripts read the trials from their source and write one result table per section, using the methods of tricot-analysis-workflows.
3. **Write the text.** A person or an AI assistant writes `content/report.md` from the result tables, following the report standard.
4. **Render.** The renderer adds the cover, the finding cards, the figures and the theme, and prints the PDF.

```
Rscript script/01-analysis.R reports/<folder>
Rscript script/02-figures.R  reports/<folder>
Rscript script/03-render.R   reports/<folder>
```

With an AI assistant, start from [maniva](https://github.com/AgrDataSci/maniva) and ask for a report of your trials. The assistant follows [SKILL.md](SKILL.md).

## What is in the repository

| Path | Content |
|---|---|
| [SKILL.md](SKILL.md) | Procedure for AI assistants |
| [AGENTS.md](AGENTS.md) | Rules for AI agents |
| [docs/report-standard.md](docs/report-standard.md) | Sections, what each must show, method defaults, wording and checks |
| [docs/style-guide.md](docs/style-guide.md) | Page layout, themes, charts and maps |
| [themes/](themes/) | Colours and fonts, one file per theme |
| [template/report.css](template/report.css) | The page layout |
| [script/](script/) | R workflow, three numbered scripts and their helpers |
| [reports/_template/](reports/_template/) | Start a new report from here |
| [reports/](reports/) | One folder per report |

Each report folder follows the layout of [template-repo-data-analysis](https://github.com/AgrDataSci/template-repo-data-analysis), with `content/`, `output/`, `decisions/` and `metadata/`.

## Status

Under construction.

- The report standard, the style guide, the theme and the layout are in use.
- The R scripts are written and **not executed yet**. They mirror the Python draft that produced the first report where R was not available. That code is kept in the report folder under `script/other-language/`.
- The first report is a draft until the R scripts have run and its authors approve it.

Planned next.

- Run and test the R scripts, with synthetic data and tests as in tricot-analysis-workflows.
- A GitHub Action that renders a report for a trial id, so partners get a report without installing R.
- A route from the maniva router to this repository.
- Themes for partner organisations, with logos supplied by them.
- Sections for climate and environment, with the environment-data layer.

## Standards

- Write maniva and tricot in lowercase, always. tricot stands for triadic comparison of technology options.
- R is the language of the suite, with `=` for assignment.
- Every map uses the Equal Earth projection (EPSG:8857).
- Charts use colour-blind-friendly ColorBrewer palettes.
- Trial data are read from their source and never copied into a report folder. Reports on unpublished data stay out of this public repository.

## Guidance, not prescription

The report standard records how the team writes reports. Authors adapt it to their reader and their data. A report presents evidence from the data it names. It does not establish adoption, market share or causal effects.

## Authors

- Kauê de Sousa, Bioversity International and University of Inland Norway

## Citation and license

Cite this repository using [CITATION.cff](CITATION.cff). Code and documentation are released under the [MIT License](LICENSE), copyright International Plant Genetic Resources Institute (Bioversity International). Each report belongs to its authors and states its own citation. The trial data keep their licence, CC0 1.0 for tricot-data.
