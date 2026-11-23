# Synthetic Example Programme. Annual report 2024, synthetic example

**Synthetic data. Not a real report.** The programme, crop (examplebean, *Fictus exemplaris*), country (ISO code XXX), districts, entries (SYN-01 to SYN-08) and people are invented. No number here describes a real trial.

## What it is for

- **Test fixture.** The trials in `tests/fixtures/tricot-data/` are drawn from a model with known answers, written to `tests/fixtures/expected.json`. `tests/check-synthetic.py` (Python) and `tests/test-synthetic.R` (R) compare the result tables with those answers. The GitHub workflow `check-synthetic` runs both on demand.
- **Layout without a real programme.** It shows every section of the annual report on data that speak for nobody.

To learn how a real report reads, with its gaps and judgement calls, use the worked examples on open data, `reports/india-icar-bioversity-annual-workplan-2025/` (technical) and `reports/tanzania-pabra-bean-2024/` (annual).

## Run it

```
python3 tests/fixtures/make-synthetic-trials.py   # only to change the fixture
TRICOT_DATA=tests/fixtures/tricot-data python3 reports/synthetic-example-annual/script/other-language/analysis.py reports/synthetic-example-annual
GEO_COUNTRIES=../geo-countries/data/countries.geojson python3 reports/synthetic-example-annual/script/other-language/figs.py reports/synthetic-example-annual
python3 reports/synthetic-example-annual/script/other-language/render.py reports/synthetic-example-annual
python3 tests/check-synthetic.py reports/synthetic-example-annual
```

In R, `Rscript script/01-analysis.R reports/synthetic-example-annual`, then `02-figures.R`, `03-render.R` and `Rscript tests/test-synthetic.R`.

## Status

The Python draft passes all 22 checks (23 November 2026). The R scripts have not run on it yet. The fixture is built so that SYN-01 is the true favourite and SYN-08 the least preferred, the 2024B trial has no final ranking, and about 3% of farmers have no recorded gender.
