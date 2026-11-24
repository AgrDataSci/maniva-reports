# maniva-reports 0.2.0 (2026-11-23)

- Page numbers in the contents of every report type. Chrome has no `target-counter()`, so the renderers print twice. The Python renderer reads the named destinations of the first print, the R renderer finds each heading in the page text with pdftools. Contents entries link to their sections. Headings with a page break before them are now listed too.
- Annual report type after the CGIAR annual technical report, in `docs/annual-report-standard.md`, with the CGIAR formats described in `docs/cgiar-reporting.md`. Seven numbered sections, colophon with a statement on the use of AI, fact sheet, year against cumulative, status chips, PRMS result candidates and a key result story page.
- Cover styles `band`, `annual` and `event`. Layout components in `template/report.css`, annual skeleton in `reports/_template/content/annual-report.md`.
- R workflow extended for the annual type (`script/helper/annual.R`, figures and renderer), not executed yet.
- Colours of the `cgiar` theme and of the charts taken from the CGIAR Portfolio Narrative 2025 and the RTB Breeding Annual Technical Report 2024.
- Logos of CGIAR, its centres, the Alliance of Bioversity International and CIAT and the Crop Trust in `logos/`, as SVG and PNG.
- Every report also comes as a Word file for comments and edits, styled by `template/reference.docx`.
- Annual cover after the Portfolio Narrative, with logos, a deep green band and the title in mint.
- Reporting fields of the CGIAR results framework, all printed, with Impact Areas, SDGs (always SDG 17) and readiness level suggested from the data by fixed rules (`reporting-fields.csv`).
- Machine-readable reports. The data of each figure in `output/figure-data/`, hidden in the PDF text layer and attached to the PDF with the result tables and `report-data.json`, and printed as an annex in the Word file.
- Core plus data modules (`docs/inputs.md`). Besides tricot trials, any programme can report from a list of results (`inputs/results.csv`) or form exports, with its context, and the analysis stays descriptive. Tag rules for text inputs are conservative and keep the matched words.
- Private reports live in `reports/private/`, ignored by git. Renderer scripts find the repository root at any depth.
- Colophon texts that depend on the data (data licence, evidence, acknowledgements, map note) can be set in `report.yml`. A story can carry its own tag suggestions. The cumulative tile group is dropped when a report has none.
- Preflight and delivery checks, after the feedback of a session with another assistant on 23 November 2026. `tests/preflight.py` sets the analysis level (`r-workflow`, `draft`, `descriptive`) from the installed tools, checks the trial fields the workflow reads and lists quality flags. `tests/check-report.py` checks the deliverables and lists the files to offer. The colophon states the analysis level, and a report not computed with the R workflow keeps a draft status on its cover. `script/01-analysis.R` records the level when it runs.
- Trial dates fall back to `datasets.csv` (day/month/year) and then to the plot moments, since 34 files of the November 2026 release have no `metadata.date`. Fixed the `start_year` filter of `read_trials()`, which read the day instead of the year. Python figure scripts set a writable matplotlib folder.
- Working paper type (`type: working_paper`, `cover_style: working_paper`) and the `cgiar-dta` theme, after the DTA working paper of October 2026. Inside cover with authors and roles, the unit text, citation and AI statement, contents with subsections, a patterned strip on every text page drawn in the page margin boxes, and a back cover with the CGIAR statement and contacts. Built in the Python renderer only. The synthetic example also renders as a working paper (`working-paper.yml`).
- The renderer takes another settings file as a second argument and another content file through `content` in the settings.
- India and Tanzania marked as worked examples of the standard on open data, not reports of the programmes, with the teams' agreement to keep them public.
- Synthetic example programme in `tests/fixtures/` with known answers, the synthetic annual report `reports/synthetic-example-annual/`, the checks `tests/check-synthetic.py` (passing on the Python draft) and `tests/test-synthetic.R`, and a manual GitHub workflow.
- Colophon states that the report was generated with AI through maniva, a CGIAR Digital Transformation Accelerator commons, and cites maniva (`template/colophon.yml`).
- The maniva router sends every report request to this repository (maniva PR #45). The colophon cites maniva with its current authors, including Mathieu Rouard and Valentin Guignon.
- Test annual report on the PABRA bean trials in Tanzania, 2024 with the record since 2021, from a Python run.

# maniva-reports 0.1.0 (2026-11-19)

First content, on branch `claude-kauedesousa`.

- Report standard and style guide in `docs/`.
- `cgiar` theme and page layout in `themes/` and `template/`.
- R workflow in `script/`, not executed yet.
- Report template in `reports/_template/`.
- First report, the 2025 tricot trials of the ICAR-Bioversity Annual Workplan in India, as a draft built from a Python run.
