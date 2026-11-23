# Lay out a report, from content/report.md to HTML and PDF
# Status: not executed yet (written 2026-11-19, annual type added 2026-11-23). The same steps
#   run in Python in reports/tanzania-pabra-bean-2024/script/other-language/render.py, which
#   produced the first annual PDF.
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
  annual = identical(cfg$type, "annual")
  sm = regexpr("<h2>(Section [0-9]+: )?(Summary|Fact sheet and executive summary)</h2>", body, perl = TRUE)
  s0 = as.integer(sm)
  if (s0 > 0) {
    rest = substr(body, s0 + attr(sm, "match.length"), nchar(body))
    s1 = regexpr("<h2>", rest, fixed = TRUE)
    s = if (s1 > 0) substr(rest, 1, s1 - 1) else rest
    new = sub("<p>", "<p class=\"lead\">", s, fixed = TRUE)
    ul = regmatches(new, regexpr("(?s)<ul>.*?</ul>", new, perl = TRUE))
    if (length(ul) == 1 && grepl("<strong>", ul, fixed = TRUE)) {
      cards = gsub("(?s)<li>\\s*(?:<p>)?(.*?)(?:</p>)?\\s*</li>", "<div class=\"card\">\\1</div>", ul, perl = TRUE)
      cards = sub("<ul>", "<div class=\"cards\">", cards, fixed = TRUE)
      cards = sub("</ul>", "</div>", cards, fixed = TRUE)
      new = sub(ul, cards, new, fixed = TRUE)
    }
    body = sub(s, new, body, fixed = TRUE)
  }

  # 5. layout markers written in the markdown as HTML comments
  body = gsub("<!-- class: ([A-Za-z0-9_-]+) -->\\s*<table>", "<table class=\"\\1\">", body, perl = TRUE)
  body = gsub("(?s)<!-- split -->\\s*(<figure>.*?</figure>)\\s*(<table.*?</table>)", "<div class=\"split\">\\1\\2</div>", body, perl = TRUE)
  for (word in c("on track", "delayed", "off track")) {
    chip = paste0("<span class=\"chip ", gsub(" ", "-", word), "\">", tools::toTitleCase(word), "</span>")
    body = gsub(paste0("[", word, "]"), chip, body, fixed = TRUE)
  }

  # 6. page breaks, numbered sections and wide tables
  hs = regmatches(body, gregexpr("<h2>(Section [0-9]+: )?[^<]*</h2>", body, perl = TRUE))[[1]]
  heads = data.frame(lab = sub("^<h2>(Section [0-9]+): .*$", "\\1", hs), nm = sub("^<h2>(Section [0-9]+: )?(.*)</h2>$", "\\2", hs))
  heads$lab[!grepl("^Section", heads$lab)] = ""
  for (i in seq_along(hs)) {
    new = if (nzchar(heads$lab[i])) paste0("<h2 class=\"section\"><span class=\"lab\">", heads$lab[i], ":</span> ", heads$nm[i], "</h2>")
          else if (annual) paste0("<h2 class=\"unnumbered\">", heads$nm[i], "</h2>") else hs[i]
    body = sub(hs[i], new, body, fixed = TRUE)
  }
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

  # 7. key result story, headline, standfirst, two columns and the side panel
  st = regmatches(body, regexpr("(?s)<h2 class=\"section\"><span class=\"lab\">Section [0-9]+:</span> Key result story</h2>.*?(?=<h2|$)", body, perl = TRUE))
  if (length(st) == 1) {
    h2 = sub("(?s)^(<h2.*?</h2>).*$", "\\1", st, perl = TRUE)
    inner = substr(st, nchar(h2) + 1, nchar(st))
    inner = sub("<h3>", "<h3 class=\"headline\">", inner, fixed = TRUE)
    inner = sub("(?s)(</h3>\\s*)<p>", "\\1<p class=\"standfirst\">", inner, perl = TRUE)
    sc = cfg$story
    item = function(title, v) {
      v = unlist(v); v = v[nzchar(v)]
      val = if (length(v) > 0) paste(esc(v), collapse = " &middot; ") else "<span class=\"empty\">To be set by the programme</span>"
      paste0("<div><h4>", title, "</h4>", val, "</div>")
    }
    panel = paste0("<aside class=\"panel\">", item("Primary Impact Area", sc$primary_impact_area),
                   item("Other Impact Areas", sc$other_impact_areas), item("Geographic scope", sc$geographic_scope),
                   item("Contributing programmes and funders", sc$contributing), item("Contributing centres", sc$centres),
                   item("Contributing partners", sc$partners), "</aside>")
    head_part = sub("(?s)^(.*?<p class=\"standfirst\">.*?</p>).*$", "\\1", inner, perl = TRUE)
    rest = substr(inner, nchar(head_part) + 1, nchar(inner))
    fig = regmatches(rest, regexpr("(?s)<figure>.*?</figure>", rest, perl = TRUE))
    if (length(fig) == 1) rest = sub(fig, "", rest, fixed = TRUE) else fig = ""
    inner = paste0(head_part, "<div class=\"storygrid\"><div><div class=\"storytext\">", rest, "</div>", fig, "</div>", panel, "</div>")
    body = sub(st, paste0("<section class=\"story\">", h2, inner, "</section>"), body, fixed = TRUE)
  }

  # 8. cover from report.yml
  tiles = paste(vapply(cfg$highlights, function(t) {
    paste0("<div class=\"tile\"><div class=\"n\">", esc(as.character(t$value)), "</div><div class=\"l\">", esc(t$label), "</div></div>")
  }, character(1)), collapse = "")
  au = unlist(cfg$authors)
  author_line = if (length(au) > 1) paste(paste(au[-length(au)], collapse = ", "), "and", au[length(au)]) else paste(au, collapse = "")
  inst = paste(esc(unlist(cfg$institutions)), collapse = " &middot; ")
  logos = paste(vapply(unlist(cfg$logos), function(p) paste0("<img src=\"", p, "\" alt=\"\">"), character(1)), collapse = "")
  kicker = if (is.null(cfg$kicker)) "Technical report" else cfg$kicker
  tiles_of = function(ts) paste(vapply(ts, function(t) {
    paste0("<div class=\"tile\"><div class=\"n\">", esc(as.character(t$value)), "</div><div class=\"l\">", esc(t$label), "</div></div>")
  }, character(1)), collapse = "")
  cover = paste0("<section class=\"cover\"><div class=\"top\"><div class=\"kicker\">", esc(kicker), "</div>",
                 "<h1>", esc(cfg$title), "</h1><div class=\"sub\">", esc(cfg$subtitle), "</div></div>",
                 "<div class=\"bottom\"><div class=\"tiles\">", tiles, "</div>",
                 "<div class=\"authors\">", esc(author_line), "</div><div class=\"inst\">", inst, "</div>",
                 if (nzchar(logos)) paste0("<div class=\"logos\">", logos, "</div>") else "",
                 "<div class=\"meta\"><div>", esc(as.character(cfg$date)), "</div>",
                 if (!is.null(cfg$status)) paste0("<div class=\"status\">", esc(cfg$status), "</div>") else "",
                 "</div></div></section>")
  if (identical(cfg$cover_style, "annual")) {
    per = vapply(cfg$highlights, function(t) if (is.null(t$period)) "" else t$period, character(1))
    groups = paste0("<div class=\"tilegroups\"><div class=\"tilegroup year\"><div class=\"gl\">In ", esc(as.character(cfg$reporting_year)),
                    "</div><div class=\"tiles\">", tiles_of(cfg$highlights[per == "year"]), "</div></div>",
                    "<div class=\"tilegroup cumulative\"><div class=\"gl\">Since the start, ", esc(as.character(cfg$period_label)),
                    "</div><div class=\"tiles\">", tiles_of(cfg$highlights[per == "cumulative"]), "</div></div></div>")
    pic = if (!is.null(cfg$cover_photo)) paste0("<img src=\"", esc(cfg$cover_photo$file), "\" alt=\"\"><div class=\"credit\">", esc(cfg$cover_photo$credit), "</div>")
          else "<div class=\"rings\"></div><div class=\"rings2\"></div>"
    cover = paste0("<section class=\"cover annual\"><div class=\"logobar\">", logos, "</div>",
                   "<div class=\"band\"><div class=\"programme\">", esc(cfg$programme_label), "</div><div class=\"kicker\">", esc(kicker), "</div>",
                   "<h1>", esc(cfg$title), "</h1><div class=\"sub\">", esc(cfg$subtitle), "</div></div>",
                   "<div class=\"photo\">", pic, "</div>",
                   "<div class=\"bottom\">", groups, "<div class=\"inst\">", inst, "</div>",
                   "<div class=\"meta\"><div>", esc(as.character(cfg$date)), "</div>",
                   if (!is.null(cfg$status)) paste0("<div class=\"status\">", esc(cfg$status), "</div>") else "",
                   "</div></div></section>")
  }

  # 9. colophon and contents, annual type only
  front = ""
  if (annual) {
    co = cfg$colophon
    ff = file.path(report, "output", "tables", "funders.csv")
    fund = if (file.exists(ff)) utils::read.csv(ff) else NULL
    fund_txt = if (is.null(fund)) "" else paste(paste0(esc(fund$funder), ", ", esc(fund$award), " (", esc(fund$number), ")"), collapse = "; ")
    handle = if (is.null(co$handle) || !nzchar(co$handle)) "<em>Handle to be issued by CGSpace</em>" else esc(co$handle)
    lic = if (is.null(co$licence)) "CC BY 4.0" else co$licence
    front = paste0("<section class=\"colophon\"><div class=\"cite\">",
                   "<p><strong>Author.</strong> ", esc(cfg$corporate_author), "</p>",
                   "<p><strong>Title.</strong> ", esc(if (is.null(co$title)) cfg$title else co$title), "</p>",
                   "<p><strong>Suggested citation.</strong> ", esc(co$citation), "</p><p>", handle, "</p>",
                   "<p>This publication is licensed under a Creative Commons Attribution 4.0 International License (", esc(lic),
                   "). The trial data it uses are released under CC0 1.0.</p></div>",
                   "<h4>Disclaimers</h4><p>This report presents evidence from the trial data it names. Views and interpretations are those of the authors and do not necessarily represent those of their institutions or funders.</p>",
                   "<p>Boundaries on the maps are indicative and do not imply any opinion on the legal status of any country, territory or area, or on the delimitation of its frontiers.</p>",
                   "<h4>Use of artificial intelligence</h4><p>", esc(co$ai_statement), "</p>",
                   "<div class=\"ack\"><h4>Acknowledgements</h4><p>We thank the farmers who tested the varieties on their own farms and shared their assessments. The trials were funded by ",
                   fund_txt, ".</p></div></section>")
    items = paste0("<li><span class=\"lab\">", heads$lab, "</span><span class=\"nm\">", heads$nm, "</span></li>", collapse = "")
    front = paste0(front, "<section class=\"contents\"><h2>Table of contents</h2><ol>", items, "</ol></section>")
  }

  # 10. theme variables and stylesheet
  co = theme$colours
  vars = paste0(" --", gsub("_", "-", names(co)), ": ", unlist(co), ";", collapse = "")
  if (!is.null(theme$status)) vars = paste0(vars, paste0(" --status-", gsub("_", "-", names(theme$status)), ": ", unlist(theme$status), ";", collapse = ""))
  footer = if (annual) paste0(kicker, ". ", cfg$title) else cfg$title
  vars = paste0(":root {", vars,
                " --font-body: \"", theme$fonts$body, "\"; --font-display: \"", theme$fonts$display,
                "\"; --font-mono: \"", theme$fonts$mono, "\"; --footer-title: \"", gsub("\"", "'", footer), "\"; }")
  css = paste(readLines(file.path("template", "report.css"), encoding = "UTF-8"), collapse = "\n")
  lang = if (is.null(cfg$language)) "en" else cfg$language
  doc = paste0("<!DOCTYPE html><html lang=\"", lang, "\"><head><meta charset=\"utf-8\"><title>", esc(cfg$title), ". ",
               esc(cfg$subtitle), "</title><style>", vars, "\n", css, "</style></head><body>\n", cover, "\n", front, "\n", body, "\n</body></html>")

  out_html = file.path(report, "report.html")
  writeLines(doc, out_html, useBytes = TRUE)

  # 11. PDF with headless Chrome
  name = if (is.null(cfg$output_name)) basename(normalizePath(report)) else cfg$output_name
  out_pdf = file.path(report, "output", paste0(name, ".pdf"))
  dir.create(dirname(out_pdf), showWarnings = FALSE, recursive = TRUE)
  pagedown::chrome_print(input = normalizePath(out_html), output = out_pdf,
                         options = list(printBackground = TRUE, preferCSSPageSize = TRUE),
                         extra_args = c("--no-pdf-header-footer"))

  # 12. Word version, for comments and edits, with the styles of template/reference.docx
  out_docx = render_docx(report, cfg, lines, sub("[.]pdf$", ".docx", out_pdf))

  c(out_pdf, out_docx)

}


#' Word version of a report, for comments and edits
#'
#' Same text as the PDF. Figures and logos go in as PNG, layout markers become plain Word
#' content and status chips stay as their words. Needs pandoc, which comes with RStudio.
render_docx = function(report, cfg, lines, out_docx) {

  annual = identical(cfg$type, "annual")
  page = "\n```{=openxml}\n<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>\n```\n"
  md = paste(lines, collapse = "\n")
  split_figs = regmatches(md, gregexpr("<!-- split -->\\s*!\\[[^]]*\\]\\(([^)]+)\\)", md, perl = TRUE))[[1]]
  split_figs = sub(".*\\(([^)]+)\\)$", "\\1", split_figs)
  md = gsub("(?s)<!--.*?-->\\n?", "", md, perl = TRUE)

  # figures with their width, the caption paragraph kept as it is
  figs = regmatches(md, gregexpr("!\\[[^]]*\\]\\([^)]+\\)", md, perl = TRUE))[[1]]
  for (f in unique(figs)) {
    src = sub("^!\\[[^]]*\\]\\(([^)]+)\\)$", "\\1", f)
    w = if (src %in% split_figs) 60 else if (!is.null(cfg$figure_widths[[basename(src)]])) cfg$figure_widths[[basename(src)]] else 100
    md = gsub(f, paste0("![](", src, "){width=", round(w * 16.5 / 100, 1), "cm}"), md, fixed = TRUE)
  }

  if (annual) {
    md = gsub("(?m)^## (Section [0-9]+: )", paste0(gsub("\\\\", "\\\\\\\\", page), "# \\1"), md, perl = TRUE)
    md = gsub("(?m)^## ", "# ", md, perl = TRUE)
    md = gsub("(?m)^### ", "## ", md, perl = TRUE)
    sc = cfg$story
    val = function(v) { v = unlist(v); v = v[nzchar(v)]; if (length(v) > 0) paste(v, collapse = "; ") else "*To be set by the programme*" }
    panel = paste0("- **", c("Primary Impact Area", "Other Impact Areas", "Geographic scope", "Contributing programmes and funders",
                             "Contributing centres", "Contributing partners"), ".** ",
                   c(val(sc$primary_impact_area), val(sc$other_impact_areas), val(sc$geographic_scope), val(sc$contributing),
                     val(sc$centres), val(sc$partners)), collapse = "\n")
    md = sub("(?s)(# Section [0-9]+: Key result story\\n.*?)(?=\\n# |$)", paste0("\\1\n\n", gsub("\\\\", "\\\\\\\\", panel), "\n"), md, perl = TRUE)
  }

  styled = function(style, txt) if (is.null(txt) || !nzchar(txt)) "" else paste0("::: {custom-style=\"", style, "\"}\n", txt, "\n:::\n")
  hl = cfg$highlights
  rows = vapply(hl, function(t) {
    per = if (identical(t$period, "year")) paste("In", cfg$reporting_year) else if (identical(t$period, "cumulative")) cfg$period_label else ""
    paste0("| ", tools::toTitleCase(t$label), " | ", t$value, " | ", per, " |")
  }, character(1))
  logos = paste0("![](", sub("[.]svg$", ".png", unlist(cfg$logos)), "){height=1.4cm}", collapse = " ")
  byline = if (!is.null(cfg$corporate_author)) cfg$corporate_author else paste(unlist(cfg$authors), collapse = ", ")
  front = paste0(if (length(cfg$logos) > 0) logos else "", "\n\n**", cfg$kicker, "**\n\n",
                 styled("Title", cfg$title), styled("Subtitle", cfg$subtitle), styled("Author", byline),
                 styled("Date", as.character(cfg$date)), if (!is.null(cfg$status)) paste0("**", cfg$status, "**\n\n") else "",
                 "| Highlight | Value | Period |\n|---|---:|---|\n", paste(rows, collapse = "\n"), "\n\n",
                 paste(unlist(cfg$institutions), collapse = " · "), "\n")
  if (annual) {
    co = cfg$colophon
    front = paste0(front, page, "**Author.** ", cfg$corporate_author, "\n\n**Title.** ", co$title,
                   "\n\n**Suggested citation.** ", co$citation, "\n\n",
                   if (is.null(co$handle) || !nzchar(co$handle)) "*Handle to be issued by CGSpace*" else co$handle,
                   "\n\nThis publication is licensed under a Creative Commons Attribution 4.0 International License (",
                   if (is.null(co$licence)) "CC BY 4.0" else co$licence, "). The trial data it uses are released under CC0 1.0.\n\n",
                   "**Use of artificial intelligence.** ", co$ai_statement, "\n")
  }

  src = file.path(report, "report-docx.md")
  writeLines(paste0(front, if (annual) "" else page, md), src, useBytes = TRUE)
  on.exit(unlink(src))
  rmarkdown::pandoc_convert(normalizePath(src), to = "docx", output = normalizePath(out_docx, mustWork = FALSE), wd = normalizePath(report),
                            options = c("--reference-doc", normalizePath(file.path("template", "reference.docx")),
                                        "--resource-path", normalizePath(report)))
  out_docx

}
