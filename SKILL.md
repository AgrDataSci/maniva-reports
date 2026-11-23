---
name: maniva-reports
description: Use whenever a user asks for a report for CGIAR, PRMS, CGSpace or a donor, such as a technical report, trial or season report, annual report (Type 1), PRMS results or key result story. Works on tricot trials in tricot-data and on any programme's own results, forms or output lists with its context. Covers the report types, structure, analysis per section, wording, page layout and colour themes.
---

# maniva-reports

A report standard, a page layout and an R workflow that turn trial data in the [maniva](https://github.com/AgrDataSci/maniva) commons into a technical report people want to read. One trial file, or a set of them, goes in. A PDF and a Word file with a cover, key findings, variety rankings, figures and a data statement comes out.

The [maniva router](https://raw.githubusercontent.com/AgrDataSci/maniva/main/SKILL.md) sends every request for a report here, whatever the report is called. The methods come from [tricot-analysis-workflows](https://github.com/AgrDataSci/tricot-analysis-workflows). The data format comes from [tricot-data](https://github.com/AgrDataSci/tricot-data). This skill adds how to tell the story and how to lay it out. It does not define methods of its own.

## Names

Write maniva and tricot in lowercase, always. That holds in headings, table cells, lists and at the start of a sentence, so never write "Maniva" or "Tricot". tricot stands for triadic comparison of technology options. Quote published titles exactly as printed.

## Use the live files

Once per conversation, before the first report, read the files you need from `https://raw.githubusercontent.com/AgrDataSci/maniva-reports/main/`. In Claude Code, where the skill is a git clone, run `git pull` instead. If you cannot reach the repository, say so in one short line and use the installed files.

| File | Read it when |
|---|---|
| [docs/report-standard.md](docs/report-standard.md) | Always. Sections, what each must show, wording rules, checks before delivery |
| [docs/style-guide.md](docs/style-guide.md) | You lay out the report or draw a figure |
| [docs/annual-report-standard.md](docs/annual-report-standard.md) | The report is an annual report, a key result story, or goes to CGIAR, PRMS or CGSpace |
| [docs/cgiar-reporting.md](docs/cgiar-reporting.md) | Same, to see which parts of the CGIAR formats maniva fills from data and which stay with the programme |
| [docs/inputs.md](docs/inputs.md) | The data are not tricot trials. Modules, the results.csv format, tag rules for text, private reports |
| [reports/_template/](reports/_template/) | You start a new report |
| [reports/india-icar-bioversity-annual-workplan-2025/](reports/india-icar-bioversity-annual-workplan-2025/) | You want a worked example of a technical report, on real open data |
| [reports/tanzania-pabra-bean-2024/](reports/tanzania-pabra-bean-2024/) | You want a worked example of an annual report, on real open data |
| [reports/synthetic-example-annual/](reports/synthetic-example-annual/) | You change or test the code. Synthetic data with known answers, checked by `tests/check-synthetic.py` and `tests/test-synthetic.R` |

## How to work

1. **Settle the scope in one question.** Which trials, who reads the report, and which type it is. A technical report for partners and CGSpace (`technical`), an annual report of a programme for CGIAR and PRMS (`annual`), or one key result (`story`). When the user names CGIAR, PRMS, Type 1, annual reporting or a funder report, the type is `annual`. Take the trials from `datasets.csv` in tricot-data, or from files the user gives in the tricot-data format. If the data are not trials, such as a list of results, probe or survey forms, or indicator tables, use the results or forms module of `docs/inputs.md` and ask for the context the data lack. That analysis is descriptive only.
2. **Copy `reports/_template/`** to `reports/<country>-<programme>-<year>/`, all lowercase, or to `reports/private/<programme>-<year>/` when the data are internal or unpublished, and fill `report.yml`. Never invent an author, affiliation, funder, DOI or ORCID. Leave the field empty and tell the user.
3. **Run the preflight.** `python3 tests/preflight.py reports/<folder> <path to tricot-data>` before any analysis. It says which analysis level this session can reach (`r-workflow`, `draft` or `descriptive`), checks that the trial files carry the fields the workflow reads, applies the documented fallbacks for missing dates, and lists the quality flags to handle. Take field names from the tricot-data README and SKILL, never from a guess. Tell the user the level in one line before you start. If you read this repository through a connector and cannot run the script, apply its rules by hand from the docstring of `tests/preflight.py`, and treat the level as `draft` unless you ran the R scripts.
4. **Read the decision records** in tricot-analysis-workflows that the report standard names for each section, before any analysis.
5. **Run the analysis in R.** `Rscript script/01-analysis.R reports/<folder>` writes the result tables to `output/`, and `script/02-figures.R` draws the figures. If you cannot run R, follow "Deliver a reproducible project", step 6, in the tricot-analysis-workflows skill. Run the analysis in a language you can execute, keep that code in `script/other-language/` of the report folder, mark the report as draft, and never approximate a method with no faithful equivalent.
6. **Write `content/report.md`** from the result tables, section by section, following the report standard. Every number in the text comes from a file in `output/`. Write for the reader named in step 1.
7. **Render.** `Rscript script/03-render.R reports/<folder>` builds the PDF and the Word file with the theme named in `report.yml`. The PDF shows the layout, and the Word file is for comments and edits.
8. **Check before delivery.** `python3 tests/check-report.py reports/<folder>` checks that the PDF and Word files exist, that every figure has its data, the prose rules and the machine-readable layer, and prints the files to deliver. Offer only the files it lists. Then run the rest of the checklist at the end of the report standard, and look at every page of the PDF.
9. **Deliver** the PDF, the Word file and the report folder, with the analysis level in one line. A `draft` report is a draft of a maniva report, never a maniva report, until the R scripts have run. When the authors send back edits in Word, carry them into `content/report.md` and render again. Say what was computed, with what, and what the authors still need to confirm.

## Boundaries

- A report presents evidence from the data it names. It does not establish adoption, market share, willingness to pay or causal effects of climate.
- Report a computed result only when the code ran in this conversation. Never show illustrative numbers as if they described the user's data.
- Every report has a section on limitations. The author may hold it back from one version, and the file keeps it.
- The data are read-only. When you find an error in a trial file, help the user report it to the data managers through an issue in tricot-data, and say how you handled it in the report.
- Data that are not public yet stay private. A report on them lives in `reports/private/`, which git ignores. Never push it to a public repository, and do not copy participant-level data into the report folder.
- Check the input for personal data such as names, phone numbers or exact GPS points before you write or map anything.
- Logos and brand colours belong to their organisations. Use the logos in `logos/`, or a file the user supplies, and only for organisations that took part in the work.
- Draw every map in the Equal Earth projection (EPSG:8857). Keep coordinates in WGS84 for calculations and project only to draw. Check national boundaries against the official source of the country before a report is published there.
- R is the language of the suite. Use `=` for assignment.
- The worked examples show how the standard reads on real data. They are not reports of those programmes, so never cite their numbers as results of the programme, and never copy their text into a new report. Take the structure, not the content.
- Never take a number from the synthetic example into a real report. It describes no real trial.
- Show every reporting field of the CGIAR results framework, filled or empty, from `output/tables/reporting-fields.csv`. Suggest the Impact Areas, SDGs and innovation readiness level with the fixed rules of `docs/annual-report-standard.md`, label them as suggestions, and never suggest a principal score. SDG 17 is always suggested for tricot and maniva work. Outcome status, budget, trainee counts, innovation use and policy change come only from the programme. Trial participants are not people trained.
- Make every report machine-readable. Each figure writes the numbers it draws to `output/figure-data/`. The PDF carries them as hidden text beside the figure and, with `output/report-data.json` and the result tables, as attached files. The Word file carries them as a visible annex.
- The colophon states that the report was generated with AI through maniva, an open commons developed under the CGIAR Digital Transformation Accelerator, and cites maniva. The text lives in `template/colophon.yml`.
- The colophon of an annual report states that an AI assistant drafted it and which steps it did.

## Credit

Cite this repository with `CITATION.cff`, the data with the concept DOI of tricot-data (https://doi.org/10.5281/zenodo.17112491) and the methods as tricot-analysis-workflows asks. Credit the data producer of each trial by name. The report belongs to its authors. This skill gives the structure and the layout, and it does not speak for them.
