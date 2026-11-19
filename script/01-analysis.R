# Result tables of a report
# Status: not executed yet (written 2026-11-19)
#
# Run from the repository root (open maniva-reports.Rproj) with
#   Rscript script/01-analysis.R reports/<folder>
# Reads the trials named in report.yml from their source and writes one table
# per section of the report standard to <folder>/output/.

library("jsonlite")
library("yaml")
library("PlackettLuce")
library("gosset")
library("qvcalc")

args = commandArgs(trailingOnly = TRUE)
report = if (length(args) > 0) args[1] else stop("give the report folder, for example reports/_template")

source("script/helper/read-trials.R")
source("script/helper/workflows.R")
source("script/helper/analysis.R")

cfg = read_config(report)
out = file.path(report, "output")
dir.create(out, showWarnings = FALSE, recursive = TRUE)

# 1. Read data ------------------------------------------------------------
trials = read_trials(cfg)

cat("Trials:", length(trials), "\n")

# 2. Overview and participants --------------------------------------------
ov = overview(trials, cfg)
write.csv(ov, file.path(out, "overview.csv"), row.names = FALSE)
write.csv(participants(trials), file.path(out, "participants.csv"), row.names = FALSE)

cat("Farmers registered:", sum(ov$registered), " completing:", sum(ov$completed), "\n")

# 3. Variety performance --------------------------------------------------
w = worth(trials, cfg$analysis$overall_trait)
write.csv(w, file.path(out, "worth.csv"), row.names = FALSE)

sa = site_agreement(w)
if (!is.null(sa)) write.csv(sa, file.path(out, "site-agreement.csv"), row.names = FALSE)

# 4. Comparison with the local variety ------------------------------------
if (!is.null(cfg$analysis$vs_local_trait)) {
  vl = vs_local(trials, cfg$analysis$vs_local_trait)
  if (!is.null(vl)) write.csv(vl, file.path(out, "vs-local.csv"), row.names = FALSE)
}

# 5. Measured yield -------------------------------------------------------
ys = yield_summary(trials, cfg)
if (!is.null(ys)) write.csv(ys, file.path(out, "yield.csv"), row.names = FALSE)

# 6. What drives preference -----------------------------------------------
ta = trait_agreement(trials, cfg)
write.csv(ta, file.path(out, "trait-agreement.csv"), row.names = FALSE)

rt = reason_themes(trials, cfg)
if (!is.null(rt)) write.csv(rt, file.path(out, "reasons.csv"), row.names = FALSE)

# 7. Groups ---------------------------------------------------------------
if (!is.null(cfg$analysis$group)) {
  gd = group_differences(trials, cfg)
  if (!is.null(gd)) write.csv(gd, file.path(out, "groups.csv"), row.names = FALSE)
}

# 8. Provenance -----------------------------------------------------------
prov = list(report = basename(normalizePath(report)),
            run = format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z"),
            data_source = cfg$data$source,
            trial_ids = unname(vapply(trials, function(x) x$trial_id, character(1))),
            schema_version = unique(unlist(lapply(trials, function(x) x$metadata$schema_version))),
            workflows_commit = workflows_commit,
            packages = vapply(c("PlackettLuce", "gosset", "qvcalc", "jsonlite"),
                              function(p) as.character(utils::packageVersion(p)), character(1)))
dir.create(file.path(report, "metadata"), showWarnings = FALSE)
write_json(prov, file.path(report, "metadata", "provenance.json"), pretty = TRUE, auto_unbox = TRUE)

dir.create(file.path(report, "script", "session-info"), showWarnings = FALSE, recursive = TRUE)
writeLines(capture.output(sessionInfo()), file.path(report, "script", "session-info", "01-analysis.txt"))
