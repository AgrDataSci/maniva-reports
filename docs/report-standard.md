# Report standard

What a maniva technical report contains, what each section must show, and how it is worded. The standard comes from the first report built this way, on the 2025 tricot trials of the ICAR-Bioversity Annual Workplan in India (`reports/india-icar-bioversity-annual-workplan-2025/`).

Status: first version by Kauê de Sousa (Bioversity International), 2026-11-19. It records how the team writes reports. It is guidance, and authors adapt it to their reader.

## Who the report is for

A report serves the people who ran the trials and the people who fund or use them. Programme leaders, national partners, breeders, seed system actors and donors read it to decide what to test again, multiply or release. Write so that a reader outside statistics follows every section, and a statistician finds the n and the uncertainty behind every claim.

A report is also the visible return for a partner who shares data. It shows what open, well-documented trial data make possible.

## Sections

Keep this order. Leave a section out only when the data cannot support it, and say so in the limitations.

| Section | What it must show | Method and decision record |
|---|---|---|
| Cover | Title, subtitle, authors, institutions, date, status, and three to five headline numbers | Numbers from `output/overview.csv` |
| Summary | One opening paragraph and four to six findings, each a bold sentence followed by the evidence | Every finding repeats a result from a later section |
| Background | The programme, the question the trials answer, and earlier work in the country or crop | `datasets.csv` in tricot-data for earlier trials |
| Trials and methods | Where, when, which crops, how many entries and farmers, the collection moments, and the analysis in plain words. A map and one table of trials | Protocols in tricot-protocols |
| Participants | Who took part, by gender and other recorded variables, and how many completed the final ranking per trial | Coverage rule in `decisions/ranking.md` |
| Variety performance | Per trial, the entries participants preferred, with worth, n and a test of whether entries differ. One figure of log-worth per crop or crop group | `decisions/ranking.md`, use case `which-varieties-do-participants-prefer` |
| Comparison with the local variety | Share of test plots rated better than the participant's own variety, per trial, when the question was asked | Descriptive, with a 95% interval |
| Measured traits | Yield or other measurements, with units, flags and what they can be compared with | Caveats in the tricot-data skill |
| What drives preference | Agreement of each ranked trait with overall preference, and the reasons participants gave | `decisions/trait-associations.md`, use case `which-traits-drive-preference` |
| Groups | Whether women and men, or another designed group, prefer different entries | `decisions/socioeconomic-heterogeneity.md`, use case `do-user-groups-prefer-different-varieties`, part A |
| Limitations and next steps | What the results cannot support, what to change next season, and what the team will do with the results | Limits listed in each decision record |
| Data availability | Where the data are, the licence, the DOI and how to reach them through maniva | CITATION.cff of tricot-data |
| Contributors and acknowledgements | Names, affiliations and roles from the trial metadata, funders with grant numbers | `metadata$contributors` and `metadata$funder` of each trial |
| References | Only works cited in the text | |

Add a section on climate or environment when the report links trials with weather or soil data. Follow `decisions/climate-environment.md` and the environment-data layer for it.

## Method defaults

The decision records in tricot-analysis-workflows govern. These are the points a report most often gets wrong.

- **Overall preference.** Use the most recent overall-type question as overall preference and say which question, at which collection moment, with how many valid rows.
- **Worth.** Fit one Plackett-Luce model per trial and trait. Report log-worth with quasi-standard errors and the number of participants who ranked each entry. Give the probability of beating the check when the metadata name a check.
- **Do entries differ.** Report the likelihood-ratio test against equal worth. A trial that does not separate its entries is a result, and the report says so.
- **Few answers.** When an entry was ranked on few farms, name a group of top entries, give the bootstrap probability of a top-three place, and say that the order will change as more answers arrive.
- **Sites.** Fit trials separately before pooling. Report the rank correlation between sites for shared entries. Pool only when the entries and the question allow it.
- **Traits.** Report within-participant Kendall tau between each ranked trait and overall preference, with a bootstrap interval and the n of each pair. Do not assume yield is the main driver. A trait recorded after the overall ranking cannot explain it.
- **Groups.** Compare only groups with at least 20 valid answers each, and never the unlabelled ones. Check whether the group is confounded with site, and test within sites when it is. When the test is not significant, write that there are not yet enough answers to tell.
- **Gender ratio.** Report the share of women and say which population it reflects. An unequal ratio is not a flaw to correct.
- **Measured yield.** Use `value_standard` and `unit_standard` when they exist. State the protocol, the unit and the flags. When sites applied the protocol differently, compare within farms only.
- **Open answers.** Code the reasons participants gave into themes with a documented keyword list, kept in the report folder. Report the share of participants per theme and say that the coding is by keyword. Ask a native speaker to review it before publication.
- **Significance level.** 0.05, or 0.10 with a stated reason.

## Wording

- Lead each section with its finding. The heading names the topic and the first sentence states what the data show.
- One idea per paragraph, in two to four sentences.
- No em-dashes. No colons in running text. Assertive language.
- Write tricot and maniva in lowercase, always.
- Name entries exactly as in the data. Do not call an entry a landrace, an elite line or a check unless the metadata say so. When you read the type from a name, say that you did.
- Give counts with shares, for example "178 (28%) were women".
- Say "entries" for what was tested, "participants" or "farmers" for who tested, and "plots" for the three per farm.
- Write "preferred" for rankings. Do not write "better yielding" from a ranking.
- Name the institute that produced each trial.
- Use the legal name of each organisation as its people ask, for example Bioversity International.

## Figures and tables

- One message per figure. The caption says what the figure shows and how to read it. The text says what it means.
- Number figures in order of appearance and refer to none that is missing.
- A table for exact values, a figure for comparison. Six rows or fewer usually belong in a sentence or a small table.
- Show uncertainty wherever an estimate is drawn. Grey marks a trial where entries do not differ.
- Colours and layout follow `docs/style-guide.md`.

## Check before delivery

1. Every number in the text matches a file in `output/`.
2. Every estimate has its n and its uncertainty.
3. Totals add up across tables, text and cover.
4. No group smaller than 20 valid answers is compared.
5. Names of people, institutes, funders and grants come from the metadata or the authors.
6. The limitations section exists in `content/report.md`.
7. tricot and maniva are lowercase everywhere. No em-dashes and no colons in running text.
8. Every page of the PDF was looked at. No table row is cut, no label overlaps, no figure is unreadable in greyscale.
9. The cover says draft until the authors approve and the R scripts have run.
10. The data statement gives the DOI, the licence and the path to the files.
