# Inputs for any programme

maniva-reports is a core plus data modules. The core is the same for every report. It holds the sections, the cover, the colophon, the reporting fields and their suggestion rules, the machine-readable output and the PDF and Word rendering. A data module turns one kind of input into the result tables of `output/tables/`. Any CGIAR team can use the core with its own data, its context and a link to maniva.

## Modules

| Module | Input | What it computes | Status |
|---|---|---|---|
| tricot | Trial files in the [tricot-data](https://github.com/AgrDataSci/tricot-data) format | Participants, entries, rankings with Plackett-Luce, comparison with the local check, entry record | R workflow in `script/`, Python draft in the worked examples |
| results | `inputs/results.csv`, one row per result, in the format below | Counts by type, centre, programme, country and stage, suggested tags per result | Python draft, first run on an internal pilot in November 2026 |
| forms | Microsoft Forms exports (docx), one file per submission | Converts the answers into `inputs/results.csv`, then runs the results module | Python draft, first run on an internal pilot in November 2026 |

A module never adds a method. Where the data hold no decision records, such as forms, lists of outputs or indicator tables, the analysis is descriptive. It counts what the teams reported and says so.

## What the team sends

1. **The data.** One of the inputs above. Any other table is converted to `inputs/results.csv` first.
2. **The context.** Programme name, reporting year, centres, partners, funders and outcomes, in `report.yml` or in a short `content/context.md`. Anything the team does not give stays empty in the report.
3. **The source documents**, when the results point to them (papers, slides, concept notes). They go to `inputs/source/` and are cited, never copied into the text.

## results.csv

One row per result. Separate several values in a cell with `;`. Leave a cell empty when it is unknown.

| Column | Content |
|---|---|
| result_id | Short identifier, unique in the file |
| title | Title of the result as the team writes it |
| type | PRMS result type if the team knows it (innovation development, knowledge product, capacity sharing, policy change, innovation use, other output, other outcome) |
| description | What was done and what came out, a few sentences |
| lead | Name of the lead person. Never an email |
| centre | CGIAR centre(s) |
| programme | Science Program(s) or Accelerator(s) |
| countries | Countries or regions |
| partners | Partner organisations |
| status | Not started, ongoing, completed |
| evidence_url | Link to the evidence (CGSpace handle, DOI, file) |
| year | Year of the result |
| readiness_level | Innovation readiness given by the team, 0 to 9 |
| impact_areas | Impact Areas given by the team |
| sdgs | SDGs given by the team |

The last three columns hold what the team states. When they are empty, the report shows a maniva suggestion beside them, labelled as such, with the rules of `docs/annual-report-standard.md`.

## Suggested tags for the results and forms modules

The tricot rules in `docs/annual-report-standard.md` read trial data. For text inputs the rules read the team's own words and stay conservative.

- **Impact Areas.** A keyword list per Impact Area, written in the analysis script and printed in the report method. A match suggests 1 (significant), never 2. The matched words are kept in `output/tables/suggested-tags.csv` so a reviewer sees why.
- **SDGs.** One SDG per suggested Impact Area (nutrition 2, poverty 1, gender 5, climate 13, environment 15), and SDG 17 always.
- **Readiness.** From the stated stage. Not started 2, under development 3, tested and worked as expected 4, used by its intended users on a partner platform 6. Never above 6 from forms alone. A study or evaluation gets no readiness level.
- **Result type.** Evaluation and impact studies are knowledge products once published. Tools and methods are innovation development.

## Private data

Most programme data are internal. A report on internal or unpublished data lives in `reports/private/<folder>/`, which `.gitignore` keeps out of this public repository. Its scripts find the repository root by walking up to the folder that holds `themes/`, so they run at any depth. Drop emails, phone numbers and other personal data at conversion. Names of leads may appear in a private report when the team agrees.
