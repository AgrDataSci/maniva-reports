# Instructions for AI agents

This repository holds the report standard, the page layout and the R workflow that the maniva suite uses to turn trial data into technical reports. Use it to produce a report the way the team would. `SKILL.md` has the procedure. This file has the rules.

## How to work with this repository

1. Read `SKILL.md`, then `docs/report-standard.md`. For an annual report, a key result story or anything meant for CGIAR, PRMS or CGSpace, also read `docs/annual-report-standard.md` and `docs/cgiar-reporting.md`. Read `docs/style-guide.md` before you lay out a page or draw a figure.
2. Take methods from [tricot-analysis-workflows](https://github.com/AgrDataSci/tricot-analysis-workflows). Read the decision record a section names before you analyse anything for it. This repository never defines a method of its own.
3. Take data from [tricot-data](https://github.com/AgrDataSci/tricot-data), or from files the user supplies in the same format. The data are read-only.
4. Work in one folder per report under `reports/`, copied from `reports/_template/`.
5. Write maniva and tricot in lowercase, always, including headings, table cells and the start of a sentence. Never write "Maniva" or "Tricot". tricot stands for triadic comparison of technology options. Quote published titles exactly as printed.

## Rules

- Deliver every report as a PDF and a Word file. The PDF shows the layout, and the Word file takes comments and edits.
- Every number in a report comes from a file in the report's `output/` folder, written by a script in the report folder or in `script/`. No number is typed from memory.
- Report a computed result only when the code ran. If you cannot run R, follow step 4 of `SKILL.md`, and mark the report as draft until the R scripts have run.
- Never show illustrative or hypothetical numbers as if they described the user's data.
- Never invent an author, affiliation, funder, grant number, DOI or ORCID. Leave it empty and tell the user.
- State the n behind each estimate and its uncertainty, in the text or in the table beside it.
- Separate what the data show from what the authors conclude and from what you infer.
- Keep the section on limitations in `content/report.md`. An author can leave it out of one rendered version through `exclude_sections` in `report.yml`.
- Do not push a report on unpublished data to a public repository. Do not copy participant-level data into a report folder. Read the trial files from their source.
- Use logos only from `logos/` of this repository, or from files the user supplies. Do not download logos, and never redraw or recolour one.
- Do not present a theme as the official brand of an organisation. A theme is a set of colours and fonts the team chose.
- Never assign an outcome status, Impact Area, SDG, innovation readiness level, budget or trainee count. Print them only when the authors give them in `report.yml`.
- Never count trial participants as people trained.
- State in the colophon of every annual report that it was drafted with an AI assistant and reviewed by the authors.

## Conventions for new code

- R is the language of the suite. Use `=` for assignment.
- Use sf and ggplot2 for maps and figures.
- Draw every map in the Equal Earth projection (EPSG:8857, `+proj=eqearth`). Keep coordinates in WGS84 (EPSG:4326) for storage and calculations, and project only to draw, with `coord_sf(crs = sf::st_crs("EPSG:8857"), default_crs = sf::st_crs(4326))`.
- Charts take their colours from the theme, which follows the CGIAR reports the team supplied. Never a green and red pair for two opposed series.
- Paths are relative to the repository root. A script takes the report folder as its first argument.
- Comments explain intent, choices and limits, not only the mechanics.
- Mark each script with a status label from tricot-analysis-workflows (historical, reviewed-not-executed, tested-on-synthetic-data, validated-against-original-results).

## Prose in reports

No em-dashes. No colons in running text. Assertive language and short paragraphs. Lead each section with its finding. Plain words for readers outside statistics, with the technical term given once.

## Related resources

- Entry point of the suite, [maniva](https://github.com/AgrDataSci/maniva)
- Methods in [tricot-analysis-workflows](https://github.com/AgrDataSci/tricot-analysis-workflows)
- Trial data in [tricot-data](https://github.com/AgrDataSci/tricot-data)
- Evidence in [tricot-knowledge-base](https://github.com/AgrDataSci/tricot-knowledge-base)
- Protocols in [tricot-protocols](https://github.com/AgrDataSci/tricot-protocols)
- ClimMob project reports in [ClimMob-analysis](https://github.com/AgrDataSci/ClimMob-analysis)
- FAIR project layout in [template-repo-data-analysis](https://github.com/AgrDataSci/template-repo-data-analysis)
