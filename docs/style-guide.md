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

## Theme

A theme is a YAML file with colours, fonts and chart colours. `themes/cgiar.yml` is the default. It takes its green and mint from the colour themes shown on cgiar.org and its dark green, amber and pale green from the deck of the India team that inspired the first report. It is the team's choice of colours, not an official brand template.

| Token | Role | cgiar theme |
|---|---|---|
| `primary` | Cover band, headings, table headers | `#06604B` |
| `primary_dark` | Tiles, bold text | `#0F533F` |
| `highlight` | Small accents on the cover | `#58FBD4` |
| `accent` | Numbers on tiles, bars above headings, caption rules | `#F6A93B` |
| `accent_dark` | Subheadings, status tag | `#B45F00` |
| `tint` | Even table rows, tinted cards | `#F3F8EE` |
| `ink` | Body text | `#22332A` |
| `muted` | Captions, footer | `#4A5A52` |
| `rule` | Table and divider lines | `#CFE1D8` |

To add a theme, copy `themes/cgiar.yml`, rename it, change the values and name it in `report.yml`. Check that white text on `primary` and `primary_dark`, and `accent` on `primary_dark`, keep a contrast ratio of at least 4.5 to 1.

## Logos

A report carries logos only when the authors supply the files and have the right to use them. Put them in the report folder and list them under `logos` in `report.yml`. They sit at the foot of the cover, in one row, at equal height. Never stretch, recolour or crop a logo.

## Charts

- ColorBrewer palettes that hold for colour-blind readers. Greens for one series or a sequence, BrBG for two opposed series such as most and least preferred, Paired for categories. Never a green and red scheme.
- One axis per chart. Two measures of different scale go in two panels.
- Thin marks, light grid, axis text in grey. Values that matter are labelled on the chart.
- Estimates carry their interval. Grey marks a trial where the entries do not differ.
- Entries on the vertical axis, ordered from most to least preferred, so names read without rotation.
- Text in charts is black or grey, never the series colour.
- Width of 16 cm for a full-width figure at 300 dpi. Panels side by side for trials of the same crop.

## Maps

Every map uses the Equal Earth projection (EPSG:8857). Coordinates stay in WGS84 for calculations and are projected only to draw. Site points come from coordinates rounded to two decimals, and a map says so when it matters.

Crop the map to the region of the trials. Boundaries shown on a map are indicative. Before a report is published in or for a country, check the boundaries against the official source of that country and replace the boundary file if needed. `report.yml` takes the path of a boundary file under `boundaries`.

## Typography

Inter for text and Inter Display for titles, with a system sans-serif as fallback. Both are open fonts. A theme can name other fonts that are installed on the machine that renders the report.
