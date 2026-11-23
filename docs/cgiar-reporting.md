# CGIAR reporting formats

What CGIAR annual reports look like, and how maniva-reports reproduces their structure from trial data. Read it before you write an annual report or a result story for CGIAR, PRMS or CGSpace.

Status: first version by Kauê de Sousa (Bioversity International), 2026-11-23. It records the layout and the ideas behind CGIAR reports, read from two CGIAR reports, published in 2025 and 2026, and the name tag of a 2026 workshop. No text, figure or photograph of those products is copied here. It is guidance, and the CGIAR Technical Reporting Arrangement of the reporting year governs.

## The CGIAR reporting family

CGIAR reports one year of work through a family of linked products. A programme, project or Science Group Project writes an annual report, the "Type 1" report, on its progress towards its end-of-project outcomes. Its results go into the CGIAR Results Dashboard through PRMS. The Portfolio Narrative synthesises all Type 1 reports and the dashboard into one view of the portfolio, and the CGIAR Annual Report and the Flagship Report draw on it.

A maniva report sits at the bottom of that chain. It gives a programme the evidence for its Type 1 report and for the results it submits to PRMS, from the trial data the programme already published. It never replaces the official template of the reporting year.

| Product | Written by | maniva-reports type |
|---|---|---|
| Annual technical report (Type 1) | Programme, project or Science Group Project | `annual` |
| Key result story | Programme, one per year, inside the Type 1 report | `story`, or the last section of `annual` |
| Results submitted to PRMS | Programme, one record per result | The result table of `annual`, `output/prms-results.csv` |
| Technical report on a set of trials | Programme or national partner, for CGSpace | `technical` (the default) |
| Portfolio Narrative, Annual Report, Flagship Report | CGIAR System Organization | Out of scope |

## Structure of an annual technical report

The 2024 Type 1 reports follow seven numbered sections after a front matter. maniva-reports keeps the order and the section names, so a programme can paste each section into the official template.

| Part | What it holds | What maniva data can feed |
|---|---|---|
| Cover | Programme name in large type, "Annual technical report" and the year, a full-bleed field photograph, the CGIAR wordmark | Title and year from `report.yml`. The photograph and logos only when the authors supply them |
| Colophon | Corporate author, title, suggested citation with the CGSpace handle, licence (CC BY 4.0), disclaimers, a statement on the use of AI, acknowledgements | Citation, licence and funders from the trial metadata. The handle stays empty until CGSpace issues it |
| Contents and context | Table of contents and a short page on where the report sits in CGIAR reporting | Generated |
| 1. Fact sheet, executive summary and budget | A two-column fact sheet (name, short name, lead with e-mail, Science Group, start and end date, geographic scope by region and country, web link), the executive summary, and a small table comparing the approved budget of the previous and the current year | Fact sheet from the trial metadata. The budget only when the authors supply it |
| 2. Progress towards end-of-project outcomes | A theory-of-change diagram (work packages in the sphere of control, outcomes in the sphere of influence, status chips), a one-page summary, and one infographic card per outcome with a short progress narrative | Status and narrative come from the authors. maniva adds the evidence line under each outcome |
| 3. Work package progress | One page per work package with its slice of the theory of change and a narrative, then a rating table with a status chip (on track, delayed, off track) and a rationale per work package, and a definitions box for the three ratings | maniva reports per trial set or season in place of work packages |
| 4. Quantitative overview of key results | Results per category (outputs and outcomes), contribution to the Sustainable Development Goals, innovations on the readiness scale, people trained by gender and year | Participants by gender and year, trials, entries tested, sites, a map, and the PRMS result candidates |
| 5. Partnerships | A network diagram of external partners by type, and the top partners by number of results | Institutions from `metadata$contributors` and `metadata$data_producer`, with their role and number of trials |
| 6. Portfolio linkages | A network diagram of links to other CGIAR initiatives and programmes | Funders and award numbers from `metadata$funder`, and links the authors name |
| 7. Key result story | One page with a headline, a one-sentence standfirst, a story of four to six paragraphs, a quote, a photograph, and a side panel with the primary Impact Area, other Impact Areas, geographic scope, contributing initiatives, centres and external partners | The result and its numbers from the analysis. Quote and photograph from the authors |
| Back cover | A full-bleed photograph with its credit | Optional |

## Ideas from the Portfolio Narrative

The 2025 Portfolio Narrative synthesises results across the portfolio. Four display ideas carry over to a programme report.

- **Impact Area tagging.** Each result is tagged against the five Impact Areas (nutrition, health and food security; poverty reduction, livelihoods and jobs; gender equality, youth and social inclusion; climate adaptation and mitigation; environmental health and biodiversity) on a three-level score, 2 principal, 1 significant, 0 not targeted. The report shows the shares as one ring per Impact Area. The authors assign the tags. maniva never infers them.
- **Map with a top-ten table.** A choropleth of results per country with a gradient bar, set beside a table of the ten countries or districts with most results. In maniva the unit is the site, and the table lists the districts with most participants.
- **Horizontal bar charts with long labels.** Programmes, partners or regions on the vertical axis, ordered by value, value printed at the end of each bar, principal and significant shown as two shades.
- **Section openers.** A large heading, a short lead paragraph, one strong figure, and inline links to the evidence (dashboard records, CGSpace items, partner pages).

## Ideas from workshop and event material

Event material of Bioversity International, CIAT and their partners, such as the name tags of the 2026 Opportunity Crops India workshop of the Power of Diversity Funding Facility, uses a dark green band with partner logos at top right, a two-tone title (dark green over a lighter green), a black-and-white photograph that leaves colour to the text, and the date and place set in bold below. maniva-reports plans this as the cover of a report produced for a workshop or event (`cover_style: event`, not built yet).

## Layout features to keep

- A4 portrait, wide outer margins, two columns of text on narrative pages and one column on figure pages.
- Section labels in the form "Section 1:" in a light weight followed by the section name in bold, in the accent colour, with a thin rule under the heading.
- Running footer with the report title and the page number in a coloured tab at the outer edge.
- A fact sheet as a two-column table, labels in bold on the left and no vertical rules.
- Status chips as small rounded labels with a coloured dot, always with the word, never colour alone.
- Photograph captions in italics with a credit, placed on the photograph or under it.
- Every figure numbered, with a caption that states the source and the date the data were read.
- Data and evidence linked from the text, never pasted as a long list.

## What maniva-reports does not do

- It does not claim CGIAR branding. The `cgiar` theme is a set of colours the team chose. The CGIAR wordmark, centre logos and programme logos appear only when the authors supply the files and have the right to use them.
- It does not assign Impact Areas, SDG contributions, innovation readiness levels, outcome status or work package ratings. These are judgements the programme makes and signs. The report holds empty fields for them in `report.yml`, prints them when filled, and leaves the section out when empty.
- It does not count farmers who ranked varieties as people trained. Participation in a trial is not capacity sharing in the PRMS sense unless the programme ran a training and recorded it. The report counts participants and leaves the trainee count to the authors.
- It does not submit results to PRMS. It writes `output/prms-results.csv`, a list of candidate results with their evidence, for the programme's PRMS focal point to review.

## PRMS result candidates

PRMS records each result under one type. The candidates maniva can document from trial data are these.

| PRMS type | Candidate from trial data | Evidence maniva writes |
|---|---|---|
| Knowledge product | The published trial dataset, and the report itself once on CGSpace | DOI, licence, number of trials and participants |
| Innovation development | A variety or line evaluated on-farm, when the programme treats it as an innovation under development | Trials, seasons, participants who ranked it, its log-worth and its rank among entries |
| Capacity sharing for development | Training given to farmers, extension staff or students, only when the programme recorded it | Left to the authors |
| Innovation use, policy change, other outcome | A variety release or a seed system decision that used the trial evidence | The trials and figures the decision drew on. The decision itself comes from the authors |

The innovation readiness scale runs from 0 (idea) to 9 (proven innovation). A variety evaluated by farmers on their own farms is tested under uncontrolled conditions, but the level of an innovation is set by the programme for the whole innovation, not by one trial. maniva prints the level only when the authors give it.

## Sources read

- CGIAR Research Project on Roots, Tubers and Banana Breeding. 2025. Annual Technical Report 2024. CGIAR System Organization. https://hdl.handle.net/10568/175137
- CGIAR System Organization. 2026. Portfolio Narrative 2025. CGIAR Technical Reporting 2025.
- Power of Diversity Funding Facility. 2026. Name tag of the Opportunity Crops India Workshop, Pusa Campus, New Delhi, 16 to 19 November 2026.
