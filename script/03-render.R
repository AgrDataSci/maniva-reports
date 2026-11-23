# Lay out a report as HTML and PDF
# Status: not executed yet (written 2026-11-19)
#
# Run from the repository root with
#   Rscript script/03-render.R reports/<folder>
# Needs Google Chrome or Chromium for the PDF, and pandoc for the Word version.

library("yaml")
library("commonmark")
library("pagedown")
library("rmarkdown")   # pandoc, for the Word version

args = commandArgs(trailingOnly = TRUE)
report = if (length(args) > 0) args[1] else stop("give the report folder")

source("script/helper/read-trials.R")
source("script/helper/render.R")

pdf = render_report(report)

cat("Report written to", paste(pdf, collapse = " and "), "\n")
