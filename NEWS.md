# maniva-reports 0.2.0 (2026-11-23)

- Annual report type after the CGIAR annual technical report, in `docs/annual-report-standard.md`, with the CGIAR formats described in `docs/cgiar-reporting.md`. Seven numbered sections, colophon with a statement on the use of AI, fact sheet, year against cumulative, status chips, PRMS result candidates and a key result story page.
- Cover styles `band`, `annual` and `event`. Layout components in `template/report.css`, annual skeleton in `reports/_template/content/annual-report.md`.
- R workflow extended for the annual type (`script/helper/annual.R`, figures and renderer), not executed yet.
- Chart palettes moved to YlGnBu, RdBu and Set1.
- Test annual report on the PABRA bean trials in Tanzania, 2024 with the record since 2021, from a Python run.

# maniva-reports 0.1.0 (2026-11-19)

First content, on branch `claude-kauedesousa`.

- Report standard and style guide in `docs/`.
- `cgiar` theme and page layout in `themes/` and `template/`.
- R workflow in `script/`, not executed yet.
- Report template in `reports/_template/`.
- First report, the 2025 tricot trials of the ICAR-Bioversity Annual Workplan in India, as a draft built from a Python run.
