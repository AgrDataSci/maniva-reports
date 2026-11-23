# maniva-reports 0.2.0 (2026-11-23)

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
