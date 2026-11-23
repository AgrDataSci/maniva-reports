# Annual report standard

What a maniva annual report contains, for programmes that report a year of on-farm testing to CGIAR, PRMS and CGSpace. It follows the structure of the CGIAR annual technical report (`docs/cgiar-reporting.md`) and fills it with evidence from the trial data. Wording, method defaults and checks of `docs/report-standard.md` apply here too.

Status: first version by Kauê de Sousa (Bioversity International), 2026-11-23. Tested on the PABRA bean trials in Tanzania (`reports/tanzania-pabra-bean-2024/`). It is guidance, and authors adapt it to their reader.

## Who it is for

The programme leader who signs the annual report, the PRMS focal point who enters the results, and the funders and CGIAR reviewers who read them. Each section answers one question a reviewer asks. What did the programme do this year, how far did it get, with whom, and what is the evidence.

## Two time frames

An annual report presents the reporting year and the cumulative record of the programme, side by side. The reporting year is the year the trials started, unless the authors define it otherwise in `report.yml`. Every quantitative display gives both, for example participants in 2024 and participants since 2021. Say once, in the methods, which trials count for which year.

## Sections

Keep this order and these names, so each section maps to the official template. Leave a section out when the data and the authors cannot fill it, and list it in the limitations.

| Section | What it must show | Source |
|---|---|---|
| Cover | Programme name, "Annual technical report" and the year, status, and four headline numbers, two for the year and two cumulative | `report.yml` and `output/overview.csv` |
| Colophon | Corporate author, title, suggested citation, handle or DOI (empty until issued), licence, disclaimers, statement on the use of AI, acknowledgements | `report.yml` and `metadata$funder` |
| 1. Fact sheet and executive summary | The fact sheet table, a year-against-cumulative comparison box, and an executive summary of four to six paragraphs | `output/factsheet.csv`, `report.yml` |
| 2. Progress towards outcomes | One card per outcome the authors list, with the status they assign, their narrative and the evidence line from the data. Left out when the authors list no outcome, or kept in a draft as a marked placeholder with the evidence lines only | `report.yml` under `outcomes` |
| 3. Results of the year | Per trial set of the reporting year, what was tested, where, by how many participants, which entries they preferred with log-worth and n, comparison with the local variety, and measured yield where recorded. Close with a rating table when the authors rate the trial sets | Methods of `docs/report-standard.md` |
| 4. Quantitative overview | Participants by gender and year, trials and entries by year, a map of sites with a table of the districts with most participants, the record of entries across seasons, the PRMS result candidates, and the full table of reporting fields with suggested tags | `output/tables/` |
| 5. Partnerships | Institutions by role (data producer, partner, funder) with the number of trials, and the people credited, by institution | `metadata$contributors`, `metadata$data_producer` |
| 6. Portfolio linkages | Funders, awards and programmes the trials were run under, with award numbers, and links to CGIAR programmes the authors name | `metadata$funder`, `report.yml` under `linkages` |
| 7. Key result story | One page. A headline that states the result, a standfirst of one sentence, four to six short paragraphs, one figure, and the side panel. Quote and photograph only from the authors | One computed result, `report.yml` under `story` |
| Limitations | What the data cannot support, as in the technical report | |
| Data availability | DOI, licence, the trial ids and how to reach the data through maniva | CITATION.cff of tricot-data |
| References | Works cited in the text | |

## Key result story

Pick the result a reviewer outside the programme would remember. It is one finding with a number behind it, for example an entry that farmers ranked first in three seasons, or the share of plots rated better than the local variety. The headline states the finding in plain words. The standfirst gives the number and its n. The story says who tested, where, what they found and what the programme will do next. Name the people and institutes from the metadata. Do not invent a quote. Leave the quote out when the authors give none.

The side panel lists the primary Impact Area and other Impact Areas (from the authors, empty otherwise), the geographic scope (countries and districts from the data), the contributing programmes and funders (from the metadata), and the contributing centres and partners (from the metadata).

## Reporting fields and suggested tags

Every annual report prints the full set of fields of the CGIAR results framework, filled or empty, so the programme sees what it still has to give and reporting tools find every field in the same place. `output/tables/reporting-fields.csv` holds one row per field, with the value the programme gave under `reporting` in `report.yml`, the value maniva suggests, and the rule and evidence behind the suggestion. Insert it in the text with `<!-- insert: output/tables/reporting-fields.csv -->`.

maniva suggests three kinds of tag from the data, with fixed rules. It never suggests a principal score (2), which only the programme sets. A value the programme gives replaces the suggestion.

| Field | Suggested value | Rule |
|---|---|---|
| Nutrition, health and food security | 1, significant | Variety evaluation of a food crop with farmers |
| Poverty reduction, livelihoods and jobs | 1, significant | Market or yield traits ranked by farmers (marketability, yield, grain size or colour, taste, cooking time) |
| Gender equality, youth and social inclusion | 1, significant | Gender recorded for at least 80% of participants and women at least 30% of them |
| Climate adaptation and mitigation | 1, significant | A climate-stress or earliness trait ranked (drought, flood, heat or waterlogging tolerance, maturity) |
| Environmental health and biodiversity | 1, significant | Landraces or genebank accessions among the entries |
| SDGs | One per Impact Area scored 1 or 2, and SDG 17 always | Nutrition SDG 2, poverty SDG 1, gender SDG 5, climate SDG 13, environment SDG 15. SDG 17 Partnerships for the goals for all tricot and maniva work |
| Innovation readiness of the entries | 8, uncontrolled testing | Entries tested by farmers on their own farms. Level 9, proven innovation, needs evidence of validated impact such as a release and its use, from the programme |

The other fields have no suggestion. Capacity sharing (short- and long-term trainees by gender, degree students), innovation use, policy change, budget, outcomes and their status, and CGIAR linkages come only from the programme. Trial participants are never counted as trainees.

The CGIAR innovation readiness scale runs 0 Idea, 1 Basic research, 2 Formulation, 3 Proof of concept, 4 Controlled testing, 5 Model or early prototype, 6 Semi-controlled testing, 7 Prototype, 8 Uncontrolled testing, 9 Proven innovation.

## Machine-readable report

CGIAR reporting tools pick up what they can read. Every figure writes the numbers it draws to `output/figure-data/<figure>.csv`. The PDF carries them as hidden text in the text layer next to each figure, and attaches them as files together with every aggregated result table and `output/report-data.json`, a summary of the report, its reporting fields, its PRMS candidates and an index of the figure data. The Word file prints the same data in an annex, "Data behind the figures". No participant-level table is embedded or attached.

## Rating outcomes and trial sets

A status is the programme's judgement. Use three levels with the CGIAR wording, on track, delayed and off track, and print the definitions box beside any table that uses them. Draw a status as a chip with the word and a dot. Never rate on behalf of the authors, and never derive a status from a statistical test.

## PRMS result candidates

Write `output/prms-results.csv` with one row per candidate result and the columns `type`, `title`, `description`, `evidence`, `countries`, `doi`, `readiness_level`, `impact_areas`. Fill `type`, `title`, `description`, `evidence`, `countries` and `doi` from the data. Fill `readiness_level` and `impact_areas` with the suggestions of the reporting fields, marked as suggested, unless the authors give them in `report.yml`. Print the table in section 4 and say that the PRMS focal point reviews it before submission.

## Check before delivery

Run the checklist of `docs/report-standard.md`, and also these.

1. Every number shows whether it is for the reporting year or cumulative.
2. The year and cumulative totals on the cover, the fact sheet and section 4 agree.
3. Every reporting field is printed. Suggested tags are labelled as suggestions and follow the rules above. No status, budget, trainee count, innovation use or policy change appears unless the authors gave it.
4. The colophon carries the statement of `template/colophon.yml` with the maniva citation, and says whether the authors reviewed the report.
7. Every figure has its data in `output/figure-data/`, the PDF lists them as attachments (`qpdf --list-attachments`), and the Word file has the annex.
5. The suggested citation names the corporate author and leaves the handle empty until CGSpace issues one.
6. The PDF and the Word file were both rendered and opened. The Word file holds every table and figure of the PDF.
