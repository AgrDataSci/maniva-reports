# Lay out a report, from content/report.md to HTML and PDF
# Status: not executed yet (written 2026-11-19). The same steps run in Python in
#   reports/india-icar-bioversity-annual-workplan-2025/script/other-language/render.py,
#   which produced the first PDF.
#
# Intent
#   The authors write plain markdown. The renderer adds the cover from
#   report.yml, turns the summary into finding cards, sets figures with their
#   captions and applies the theme. Nothing in the text depends on the layout.

render_report = function(report) {

  cfg = read_config(report)
  theme = read_theme(cfg)
  esc = function(x) {
    x = gsub("&", "&amp;", x, fixed = TRUE)
    x = gsub("<", "&lt;", x, fixed = TRUE)
    gsub(">", "&gt;", x, fixed = TRUE)
  }

  # 1. content, without the sections the authors hold back
  lines = readLines(file.path(report, "content", "report.md"), encoding = "UTF-8")
  section = cumsum(grepl("^## ", lines))
  heads = sub("^## ", "", lines[grepl("^## ", lines)])
  drop = which(trimws(heads) %in% unlist(cfg$exclude_sections))
  lines = lines[!(section %in% drop)]
  lines = lines[!grepl("^# ", lines)]  # the title comes from report.yml

  # 2. markdown to HTML
  body = commonmark::markdown_html(paste(lines, collapse = "\n"), extensions = TRUE)

  # 3. figures, an image paragraph followed by a caption paragraph
  pat = "<p><img src=\"([^\"]*)\" alt=\"([^\"]*)\" ?/?></p>\\s*<p><em>(Figure [0-9]+)\\. (.*?)</em></p>"
  m = gregexpr(pat, body, perl = TRUE)
  hits = regmatches(body, m)[[1]]
  for (h in hits) {
    src = sub(pat, "\\1", h, perl = TRUE)
    alt = sub(pat, "\\2", h, perl = TRUE)
    num = sub(pat, "\\3", h, perl = TRUE)
    cap = sub(pat, "\\4", h, perl = TRUE)
    w = cfg$figure_widths[[basename(src)]]
    if (is.null(w)) w = 100
    fig = paste0("<figure><img src=\"", src, "\" alt=\"", alt, "\" style=\"width:", w, "%\">",
                 "<figcaption><span class=\"fignum\">", num, "</span> ", cap, "</figcaption></figure>")
    body = sub(h, fig, body, fixed = TRUE)
  }

  # 4. summary, a lead paragraph and finding cards
  s0 = regexpr("<h2>Summary</h2>", body, fixed = TRUE)
  if (s0 > 0) {
    rest = substr(body, s0 + nchar("<h2>Summary</h2>"), nchar(body))
    s1 = regexpr("<h2>", rest, fixed = TRUE)
    s = if (s1 > 0) substr(rest, 1, s1 - 1) else rest
    new = sub("<p>", "<p class=\"lead\">", s, fixed = TRUE)
    ul = regmatches(new, regexpr("(?s)<ul>.*?</ul>", new, perl = TRUE))
    if (length(ul) == 1) {
      cards = gsub("(?s)<li>\\s*(?:<p>)?(.*?)(?:</p>)?\\s*</li>", "<div class=\"card\">\\1</div>", ul, perl = TRUE)
      cards = sub("<ul>", "<div class=\"cards\">", cards, fixed = TRUE)
      cards = sub("</ul>", "</div>", cards, fixed = TRUE)
      new = sub(ul, cards, new, fixed = TRUE)
    }
    body = sub(s, new, body, fixed = TRUE)
  }

  # 5. page breaks and wide tables
  for (h in unlist(cfg$page_break_before)) {
    body = sub(paste0("<h2>", esc(h), "</h2>"), paste0("<h2 class=\"newpage\">", esc(h), "</h2>"), body, fixed = TRUE)
  }
  tabs = regmatches(body, gregexpr("(?s)<table>.*?</table>", body, perl = TRUE))[[1]]
  for (tb in tabs) {
    head = strsplit(tb, "</thead>", fixed = TRUE)[[1]][1]
    if (lengths(regmatches(head, gregexpr("<th", head, fixed = TRUE))) >= 8) {
      body = sub(tb, sub("<table>", "<table class=\"wide\">", tb, fixed = TRUE), body, fixed = TRUE)
    }
  }

  # 6. cover from report.yml
  tiles = paste(vapply(cfg$highlights, function(t) {
    paste0("<div class=\"tile\"><div class=\"n\">", esc(as.character(t$value)), "</div><div class=\"l\">", esc(t$label), "</div></div>")
  }, character(1)), collapse = "")
  au = unlist(cfg$authors)
  author_line = if (length(au) > 1) paste(paste(au[-length(au)], collapse = ", "), "and", au[length(au)]) else paste(au, collapse = "")
  inst = paste(esc(unlist(cfg$institutions)), collapse = " &middot; ")
  logos = paste(vapply(unlist(cfg$logos), function(p) paste0("<img src=\"", p, "\" alt=\"\">"), character(1)), collapse = "")
  kicker = if (is.null(cfg$kicker)) "Technical report" else cfg$kicker
  cover = paste0("<section class=\"cover\"><div class=\"top\"><div class=\"kicker\">", esc(kicker), "</div>",
                 "<h1>", esc(cfg$title), "</h1><div class=\"sub\">", esc(cfg$subtitle), "</div></div>",
                 "<div class=\"bottom\"><div class=\"tiles\">", tiles, "</div>",
                 "<div class=\"authors\">", esc(author_line), "</div><div class=\"inst\">", inst, "</div>",
                 if (nzchar(logos)) paste0("<div class=\"logos\">", logos, "</div>") else "",
                 "<div class=\"meta\"><div>", esc(as.character(cfg$date)), "</div>",
                 if (!is.null(cfg$status)) paste0("<div class=\"status\">", esc(cfg$status), "</div>") else "",
                 "</div></div></section>")

  # 7. theme variables and stylesheet
  co = theme$colours
  vars = paste0(" --", gsub("_", "-", names(co)), ": ", unlist(co), ";", collapse = "")
  vars = paste0(":root {", vars,
                " --font-body: \"", theme$fonts$body, "\"; --font-display: \"", theme$fonts$display,
                "\"; --font-mono: \"", theme$fonts$mono, "\"; --footer-title: \"", gsub("\"", "'", cfg$title), "\"; }")
  css = paste(readLines(file.path("template", "report.css"), encoding = "UTF-8"), collapse = "\n")
  lang = if (is.null(cfg$language)) "en" else cfg$language
  doc = paste0("<!DOCTYPE html><html lang=\"", lang, "\"><head><meta charset=\"utf-8\"><title>", esc(cfg$title), ". ",
               esc(cfg$subtitle), "</title><style>", vars, "\n", css, "</style></head><body>\n", cover, "\n", body, "\n</body></html>")

  out_html = file.path(report, "report.html")
  writeLines(doc, out_html, useBytes = TRUE)

  # 8. PDF with headless Chrome
  name = if (is.null(cfg$output_name)) basename(normalizePath(report)) else cfg$output_name
  out_pdf = file.path(report, "output", paste0(name, ".pdf"))
  dir.create(dirname(out_pdf), showWarnings = FALSE, recursive = TRUE)
  pagedown::chrome_print(input = normalizePath(out_html), output = out_pdf,
                         options = list(printBackground = TRUE, preferCSSPageSize = TRUE),
                         extra_args = c("--no-pdf-header-footer"))

  out_pdf

}
