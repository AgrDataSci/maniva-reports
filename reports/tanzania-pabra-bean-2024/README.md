# Pan-Africa Bean Research Alliance in Tanzania. Annual technical report 2024

*Worked example of the annual report type, on the open data of the PABRA bean tricot trials*

**This is a worked example of the maniva-reports standard, not a report of the programme.** It shows agents and authors what an annual report looks like on real, open data, with its gaps and judgement calls. It does not speak for PABRA, CIAT or TARI. The team agreed on 23 November 2026 that it stays public as an example.

**Status.** The numbers and figures come from a Python run, kept in `script/other-language/`, done where R was not available. The R scripts of this repository have not been executed on these data. The programme has not given its outcomes, budget or training records, so those fields are empty, and the suggested tags wait for its confirmation.

To test code, use the synthetic example in `reports/synthetic-example-annual/`, whose true answers are known.

## The question

What did the PABRA bean programme test with farmers in Tanzania in 2024, how does it compare with the record since 2021, and which results can it report to PRMS.

## The data

25 tricot trials with 2,866 registered participants, 2021 to 2024, data producer International Center for Tropical Agriculture (CIAT) with the Tanzania Agricultural Research Institute (TARI), programme "Pan-Africa Bean Research Alliance (PABRA)" in the metadata. Published in [tricot-data](https://github.com/AgrDataSci/tricot-data) (https://doi.org/10.5281/zenodo.17112491, CC0 1.0), read at the commit in `metadata/provenance.json`. The One Acre Fund bean trial in Tanzania is not part of PABRA and is left out. No trial data are copied here.

## What is in this folder

| Path | Content |
|---|---|
| `report.yml` | Type, title, cover, colophon, trials, analysis settings and layout |
| `content/report.md` | The text, in the seven sections of the CGIAR annual technical report plus limitations, data and references |
| `output/tanzania-pabra-bean-annual-report-2024.pdf` | The rendered report |
| `output/tanzania-pabra-bean-annual-report-2024.docx` | The same report in Word, for comments and edits |
| `output/figures/` | Six figures |
| `output/tables/` | Aggregated result tables, with no participant-level rows |
| `script/other-language/` | The Python code that produced the outputs |
| `decisions/README.md` | Where the draft departs from the decision records |
| `metadata/provenance.json` | Data version and trials used |

## Run it again

With Python, from the repository root, with local clones of tricot-data and of datasets/geo-countries for the map outlines.

```
TRICOT_DATA=../tricot-data python3 reports/tanzania-pabra-bean-2024/script/other-language/analysis.py reports/tanzania-pabra-bean-2024
GEO_COUNTRIES=../geo-countries/data/countries.geojson python3 reports/tanzania-pabra-bean-2024/script/other-language/figs.py reports/tanzania-pabra-bean-2024
python3 reports/tanzania-pabra-bean-2024/script/other-language/render.py reports/tanzania-pabra-bean-2024
```

In R, once tested, `Rscript script/01-analysis.R`, `02-figures.R` and `03-render.R` with the folder as argument.

## What the results cannot support

- Three of the four 2024 trials have rankings up to the reproductive stage only.
- The comparison with the local variety pools different entries, districts and local varieties across years.
- Yield is recorded in part of the trials with unclear units at some sites, and is not analysed.
- Entries are matched across trials by name.
