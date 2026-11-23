<!-- badges: start -->
[![ProjStatus](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)
[![Lifecycle](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/AgrDataSci/maniva-reports/blob/main/LICENSE)
<!-- badges: end -->

<a href="https://github.com/AgrDataSci/maniva"><img src="docs/maniva-logo.svg" alt="Part of maniva" height="64" align="right"></a>

# maniva-reports

*Technical and annual reports from on-farm trial data in the maniva commons*

> Kauê de Sousa

A report standard, a page layout and an R workflow that turn trial data into a technical report people want to read. Trial files in the [tricot-data](https://github.com/AgrDataSci/tricot-data) format go in. A PDF with a cover, key findings, variety rankings, figures and a data statement comes out, ready for CGSpace, PRMS or a donor report, with a Word version of the same report for comments and edits.

This repository belongs to the analysis layer of [maniva](https://github.com/AgrDataSci/maniva). The methods come from [tricot-analysis-workflows](https://github.com/AgrDataSci/tricot-analysis-workflows) and the data from [tricot-data](https://github.com/AgrDataSci/tricot-data). This repository adds how to tell the story and how to lay it out. [ClimMob-analysis](https://github.com/AgrDataSci/ClimMob-analysis) keeps producing the standard report of a ClimMob project. maniva-reports serves data that are already in the commons, across trials, seasons and programmes.

## Who it is for

| User | Decision it improves | Sign of use |
|---|---|---|
| National partners and programme teams who ran the trials, and the scientists and data managers who support them | Which entries to test again, multiply or release, and what to report to funders | Reports published on CGSpace and in PRMS that cite the data |
| Partners deciding whether to publish their trial data | Whether sharing data in maniva is worth the effort | New trial sets contributed to tricot-data |

## Report types

| Type | For | Example |
|---|---|---|
| Technical report | Results of a set of trials, for partners and CGSpace | India 2025 |
| Annual report | One year of a programme and its record since the start, in the seven sections of the CGIAR annual technical report, with candidate results for PRMS and a key result story | PABRA bean Tanzania 2024, a test |
| Key result story | One result on one or two pages | Section 7 of the annual report |

How CGIAR reports are built, and which parts maniva fills from the data, is in [docs/cgiar-reporting.md](docs/cgiar-reporting.md).

## See it

Two worked examples show the standard on real, open data from tricot-data. They are examples of the standard, not reports of the programmes, and the teams that produced the data agreed that they stay public.

- **Technical report.** The 2025 tricot trials of the ICAR-Bioversity Annual Workplan in India, 646 farmers, 13 trials and eight crops. [PDF](reports/india-icar-bioversity-annual-workplan-2025/output/india-tricot-2025-technical-report.pdf), [folder](reports/india-icar-bioversity-annual-workplan-2025/).
- **Annual report.** The PABRA bean trials in Tanzania, 2024 with the record since 2021, 25 trials and 2,866 farmers. [PDF](reports/tanzania-pabra-bean-2024/output/tanzania-pabra-bean-annual-report-2024.pdf), [Word](reports/tanzania-pabra-bean-2024/output/tanzania-pabra-bean-annual-report-2024.docx), [folder](reports/tanzania-pabra-bean-2024/).

One synthetic example tests the code. It runs on an invented programme in `tests/fixtures/`, drawn from a model with known answers, and `tests/check-synthetic.py` and `tests/test-synthetic.R` compare its result tables with those answers. [PDF](reports/synthetic-example-annual/output/synthetic-example-annual-report-2024.pdf), [folder](reports/synthetic-example-annual/).

## How it works

1. **Choose the trials.** By trial id, or by country, crop, year and programme, in `report.yml`.
2. **Run the analysis.** The R scripts read the trials from their source and write one result table per section, using the methods of tricot-analysis-workflows.
3. **Write the text.** A person or an AI assistant writes `content/report.md` from the result tables, following the report standard.
4. **Render.** The renderer adds the cover, the finding cards, the figures and the theme, and writes a PDF to read and a Word file to comment on and edit.

```
Rscript script/01-analysis.R reports/<folder>
Rscript script/02-figures.R  reports/<folder>
Rscript script/03-render.R   reports/<folder>
```

With an AI assistant, start from [maniva](https://github.com/AgrDataSci/maniva) and ask for a report of your trials. The maniva router sends every report request here, and the assistant follows [SKILL.md](SKILL.md).

## What is in the repository

| Path | Content |
|---|---|
| [SKILL.md](SKILL.md) | Procedure for AI assistants |
| [AGENTS.md](AGENTS.md) | Rules for AI agents |
| [docs/report-standard.md](docs/report-standard.md) | Sections, what each must show, method defaults, wording and checks |
| [docs/annual-report-standard.md](docs/annual-report-standard.md) | Sections and checks of the annual report and the key result story |
| [docs/cgiar-reporting.md](docs/cgiar-reporting.md) | How CGIAR annual reports are built and what maniva fills from data |
| [docs/style-guide.md](docs/style-guide.md) | Page layout, themes, charts and maps |
| [themes/](themes/) | Colours and fonts, one file per theme |
| [logos/](logos/) | Logos of CGIAR, its centres and partners, with their sources and rules |
| [template/report.css](template/report.css) | The page layout of the PDF |
| [template/reference.docx](template/reference.docx) | The styles of the Word version |
| [script/](script/) | R workflow, three numbered scripts and their helpers |
| [reports/_template/](reports/_template/) | Start a new report from here |
| [reports/](reports/) | One folder per report, the worked examples and the synthetic example |
| [tests/](tests/) | Synthetic trials with known answers, and the checks that use them |
| [.github/workflows/check-synthetic.yml](.github/workflows/check-synthetic.yml) | Runs the checks on GitHub, on demand for now |

Each report folder follows the layout of [template-repo-data-analysis](https://github.com/AgrDataSci/template-repo-data-analysis), with `content/`, `output/`, `decisions/` and `metadata/`.

## Status

Under construction.

- The report standard, the style guide, the theme and the layout are in use.
- The R scripts are written and **not executed yet**. They mirror the Python drafts that produced the example reports where R was not available, kept in each report folder under `script/other-language/`.
- The Python draft passes every check on the synthetic example.

Planned next.

- Run the R scripts on the synthetic example until `tests/test-synthetic.R` passes, then switch the GitHub check on for every pull request.
- A GitHub Action that renders a report for a trial id, so partners get a report without installing R.
- Themes for partner organisations.
- Sections for climate and environment, with the environment-data layer.

## Standards

- Write maniva and tricot in lowercase, always. tricot stands for triadic comparison of technology options.
- R is the language of the suite, with `=` for assignment.
- Every map uses the Equal Earth projection (EPSG:8857).
- Colours come from CGIAR reports, in `themes/cgiar.yml`. Logos of CGIAR and its centres are in `logos/`.
- Trial data are read from their source and never copied into a report folder. Reports on unpublished data stay out of this public repository.

## Guidance, not prescription

The report standard records how the team writes reports. Authors adapt it to their reader and their data. A report presents evidence from the data it names. It does not establish adoption, market share or causal effects.

## Authors

- Kauê de Sousa, Bioversity International and University of Inland Norway

## Citation and license

Cite this repository using [CITATION.cff](CITATION.cff). Code and documentation are released under the [MIT License](LICENSE), copyright International Plant Genetic Resources Institute (Bioversity International). Each report belongs to its authors and states its own citation. The trial data keep their licence, CC0 1.0 for tricot-data.
