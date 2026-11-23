# Figures of a report
# Status: not executed yet (written 2026-11-19)
#
# Run after 01-analysis.R, from the repository root, with
#   Rscript script/02-figures.R reports/<folder>

library("jsonlite")
library("yaml")
library("ggplot2")
library("sf")
library("patchwork")

args = commandArgs(trailingOnly = TRUE)
report = if (length(args) > 0) args[1] else stop("give the report folder")

source("script/helper/read-trials.R")
source("script/helper/figures.R")

cfg = read_config(report)
theme = read_theme(cfg)
out = file.path(report, "output")
fig = file.path(out, "figures")
dir.create(fig, showWarnings = FALSE, recursive = TRUE)

read_out = function(f) if (file.exists(file.path(out, f))) read.csv(file.path(out, f)) else NULL

ov = read_out("overview.csv")
w = read_out("worth.csv")
vl = read_out("vs-local.csv")
ta = read_out("trait-agreement.csv")
rt = read_out("reasons.csv")

# the map needs the site coordinates, read from the source
trials = read_trials(cfg)

n = 1
name = function(x) sprintf("fig%02d-%s.png", n, x)

save_figure(figure_map(trials, cfg, theme), file.path(fig, name("map")), width = 14, height = 12)
n = n + 1

save_figure(figure_participation(ov, theme), file.path(fig, name("participation")), height = 0.6 * nrow(ov) + 3)
n = n + 1

# one log-worth figure per group of trials, or one per crop when no groups are given
groups_cfg = cfg$figure_groups
if (is.null(groups_cfg)) {
  crop = sub(",.*$", "", unique(w$label))
  groups_cfg = split(unique(w$label), tolower(gsub(" ", "-", crop)))
}

alpha = if (is.null(cfg$analysis$alpha)) 0.05 else cfg$analysis$alpha

for (g in names(groups_cfg)) {
  labs = unlist(groups_cfg[[g]])
  rows = max(table(w$label[w$label %in% labs]))
  save_figure(figure_worth(w, labs, theme, alpha), file.path(fig, name(g)),
              width = min(26, 9 * length(labs)), height = 0.42 * rows + 3.5)
  n = n + 1
}

if (!is.null(vl)) {
  save_figure(figure_vs_local(vl, theme), file.path(fig, name("local")), height = 0.55 * length(unique(vl$label)) + 2.5)
  n = n + 1
}

if (!is.null(ta)) {
  save_figure(figure_trait_agreement(ta, theme, cfg$analysis$trait_labels), file.path(fig, name("trait-agreement")), height = 7.5)
  n = n + 1
}

if (!is.null(rt)) {
  save_figure(figure_reasons(rt, theme), file.path(fig, name("reasons")), height = 9)
}

# Annual report, year against cumulative (docs/annual-report-standard.md)
if (identical(cfg$type, "annual")) {
  tab = file.path(report, "output", "tables")
  by = read.csv(file.path(tab, "by-year.csv"))
  save_figure(figure_participants_year(by, cfg, theme), file.path(fig, "annual-participants.png"), height = 5.5)
  save_figure(figure_entries_year(by, theme), file.path(fig, "annual-entries.png"), width = 10, height = 5)
  if (file.exists(file.path(tab, "vs-local-year.csv"))) {
    save_figure(figure_vs_local_year(read.csv(file.path(tab, "vs-local-year.csv"), colClasses = c(year = "character")), cfg, theme),
                file.path(fig, "annual-vs-local.png"), width = 10, height = 5.5)
  }
  save_figure(figure_entry_record(read.csv(file.path(tab, "entries-record.csv")), theme),
              file.path(fig, "annual-entry-record.png"), width = 12, height = 7.5)
}
