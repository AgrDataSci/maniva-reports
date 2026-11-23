# Style guide

How a maniva report looks. The layout lives in `template/report.css` and the colours and fonts in a theme file under `themes/`. Change a theme, never the stylesheet, to give a report another look.

## Page

- A4 portrait. Margins of 21 mm top, 19 mm sides and 20 mm bottom.
- A footer on every page except the cover, with the report title on the left and the page number on the right.
- Body text at 9.6 pt with a line height of 1.5.

## Components

| Component | Use | Look |
|---|---|---|
| Cover | First page | Full-width band in the primary colour with a small label, the title and the subtitle. Below it the headline tiles, the authors, the institutions, the date and a status tag |
| Headline tiles | Three to five numbers on the cover | Dark tiles, the number in the accent colour, a short label below |
| Finding cards | The findings in the summary | Two columns of rounded cards, a bold sentence then the evidence. Outlined and tinted cards alternate |
| Section heading | Each section | Primary colour, with a short accent bar above |
| Subheading | Crop or topic within a section | Dark accent colour |
| Table | Exact values | Header in the primary colour with white text, tinted even rows, rounded outline. A table stays on one page |
| Figure | One message | Centred, with the caption below, a bold figure number and an accent rule at the left of the caption |
| Status tag | Draft, final | Small outlined label on the cover |
| Section label | Numbered sections of an annual report | "Section 1:" in a light weight, then the section name in bold, in the primary colour, with a thin rule under it |
| Colophon | Second page of an annual report | Citation block, licence, disclaimers and the statement on the use of AI in small type, then the acknowledgements in a tinted box |
| Fact sheet | Section 1 of an annual report | Two-column table without vertical rules, bold labels on the left |
| Year box | Year against cumulative numbers | Two columns side by side, the reporting year highlighted in the tint colour |
| Status chip | Outcome or trial-set rating given by the authors | Rounded label with a coloured dot and the word (on track, delayed, off track). Colour never carries the meaning alone |
| Definitions box | Beside any table that uses status chips | Three columns, one per status, in a tinted panel |
| Story page | Key result story | Headline across the page, standfirst in the accent colour, text in two columns, figure, and a side panel in the tint colour with the Impact Areas, scope, programmes and partners |
| Map with table | Where the trials were | Equal Earth map beside a small table of the districts with most participants |

## Theme

A theme is a YAML file with colours, fonts and chart colours. `themes/cgiar.yml` is the default. Every colour in it comes from the vector fills of two CGIAR reports the team supplied, the Portfolio Narrative 2025 (greens, mint, greys) and the RTB Breeding Annual Technical Report 2024 (yellow, status colours, chart palette). It is the team's choice of colours, not an official brand template.

| Token | Role | cgiar theme | From |
|---|---|---|---|
| `primary` | Headings, table headers, main series | `#065F4A` | Portfolio Narrative |
| `primary_dark` | Tiles, bold text | `#033529` | Portfolio Narrative |
| `deep` | Cover band | `#02211A` | Portfolio Narrative |
| `highlight` | Title on the cover band | `#17F1BD` | Portfolio Narrative |
| `accent` | Bars above headings, numbers on tiles, caption rules | `#FCC72E` | RTB |
| `accent_dark` | Subheadings, standfirst, status tag | `#494D5A` | RTB |
| `tint` | Even table rows, panels | `#F0F0F0` | RTB |
| `year_tint` | The reporting year in the year box | `#FEF1CB` | RTB |
| `ink` | Body text | `#010D09` | Portfolio Narrative |
| `muted` | Captions, footer | `#545454` | RTB |
| `rule` | Table lines and dividers | `#E2E0DF` | Portfolio Narrative |
| `status` (on_track, delayed, off_track) | Dots of the status chips | `#88C445`, `#F1D71B`, `#EA4636` | RTB |

To add a theme, copy `themes/cgiar.yml`, rename it, change the values and name it in `report.yml`. Check that white text on `primary` and `primary_dark`, and `accent` on `primary_dark`, keep a contrast ratio of at least 4.5 to 1.

## Cover styles

`cover_style` in `report.yml` sets the cover.

| Style | Use | Look |
|---|---|---|
| `band` | Technical reports. The default | Full-width band in the primary colour with the title, headline tiles below |
| `annual` | Annual reports | After the Portfolio Narrative. Logos on white at the top, then a deep green band with the programme label, "Annual technical report" and the year, and the title in mint. A photograph below when the authors supply one, headline tiles for the year and since the start at the foot |
| `working_paper` | Working papers, with the `cgiar-dta` theme for the Digital Transformation Accelerator | After the DTA working paper of October 2026. CGIAR logo and "Working Paper" on white with a patterned strip at the left, the title in a serif in mint on a deep green band with authors and date, and a patterned field below that holds the cover photograph. A patterned strip runs down the right edge of every text page. The back cover has the pattern, a deep green band with the CGIAR statement and the contacts, and the CGIAR and DTA logo lockup. The pattern is drawn by the renderer from the theme colours `pattern` and `pattern_mark`, never copied from the paper's artwork |
| `event` | Reports made for a workshop or event. Planned, not built yet | Dark green band with partner logos at top right, a two-tone title, a black-and-white photograph when supplied, date and place in bold |

A cover photograph comes only from the authors, with its credit, and the report states the credit in the caption or the colophon.

## Logos

The logos of CGIAR, its centres and close partners are in `logos/`, cut from publications the team supplied, with a README that gives the source and the rules. List them under `logos` in `report.yml` with paths relative to the report folder. Any other logo comes from the authors, who put it in the report folder. A report carries a logo only for an organisation that took part in the work. They sit in one row at equal height, at the foot of a `band` cover and at the top of an `annual` cover. Never stretch, recolour or crop a logo.

## Charts

- Colours from the theme, which takes them from the CGIAR reports. One series in `primary`. Two opposed series, such as women and men or most and least preferred, in `primary` green and `accent` yellow, which differ in lightness and hold for colour-blind readers. Not stated or no data in `missing` grey.
- A sequence, such as a map gradient, runs from light mint to deep green (`#A9FAE7`, `#67C4AA`, `#065F4A`, `#033529`), as in the Portfolio Narrative maps.
- Categories take the muted palette of the RTB charts (`#332288`, `#117733`, `#44AA99`, `#88CCEE`, `#DDCC77`, `#CC6677`, `#882255`), which is safe for colour-blind readers. Never a green and red pair for two opposed series.
- Year against cumulative. The reporting year in `primary`, earlier years in mint (`single_light`).
- One axis per chart. Two measures of different scale go in two panels.
- Thin marks, light grid, axis text in grey. Values that matter are labelled on the chart.
- Estimates carry their interval. Grey marks a trial where the entries do not differ.
- Entries on the vertical axis, ordered from most to least preferred, so names read without rotation.
- Text in charts is black or grey, never the series colour.
- Width of 16 cm for a full-width figure at 300 dpi. Panels side by side for trials of the same crop.

## Maps

Every map uses the Equal Earth projection (EPSG:8857). Coordinates stay in WGS84 for calculations and are projected only to draw. Site points come from coordinates rounded to two decimals, and a map says so when it matters.

Crop the map to the region of the trials. Boundaries shown on a map are indicative. Before a report is published in or for a country, check the boundaries against the official source of that country and replace the boundary file if needed. `report.yml` takes the path of a boundary file under `boundaries`.

## Word version

Every report comes as a PDF and as a Word file. The PDF shows the layout and carries the machine-readable data, hidden beside each figure and attached as files. The Word file is for comments and edits, ends with an annex of the data behind the figures, with tracked changes, by partners who do not use the repository. It holds the same text, tables and figures, takes its styles from `template/reference.docx` and uses Arial, so it opens the same everywhere. Layout that Word cannot hold, such as two columns or the story side panel, becomes plain text and lists. Rebuild `template/reference.docx` with `python3 template/make-reference-docx.py cgiar` after a change to the theme. Edits made in Word go back into `content/report.md` before the next render.

## Typography

Inter for text and Inter Display for titles, with a system sans-serif as fallback. Both are open fonts. A theme can name other fonts that are installed on the machine that renders the report.
