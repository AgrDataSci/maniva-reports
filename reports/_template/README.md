# Report template

Copy this folder to `reports/<country>-<programme>-<year>/`, all lowercase, then

1. fill `report.yml`
2. run `Rscript script/01-analysis.R reports/<folder>` and `Rscript script/02-figures.R reports/<folder>` from the repository root
3. write `content/report.md` from the tables in `output/`, following `docs/report-standard.md`
4. run `Rscript script/03-render.R reports/<folder>`
5. record in `decisions/README.md` any change to a default method and why
6. replace this README with the question, the data, the status and what the results cannot support

`metadata/provenance.json` and `script/session-info/` are written by the analysis script.
