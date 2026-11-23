# Result tables of the annual report type
# Status: reviewed-not-executed (written 2026-11-23). Mirrors the Python draft that produced
#   reports/tanzania-pabra-bean-2024 (script/other-language/analysis.py), where R was not available.
# Standard: docs/annual-report-standard.md. Decision records: ranking.md in tricot-analysis-workflows.
#
# Intent
#   An annual report shows the reporting year and the record since the programme started, side
#   by side. Each function returns one table for one display of the report. Worth comes from
#   worth() in analysis.R, so the methods stay those of the technical report.
#
# Limits
#   - The reporting year is the year a trial started, unless report.yml sets the trials by id.
#   - Entries are matched across trials by the name recorded in the data.
#   - Nothing here assigns a status, an Impact Area, a readiness level or a trainee count.


#' Year a trial started
trial_year = function(x) as.integer(substr(x$metadata$date$start, 1, 4))


#' Counts for a set of trials, used for the year and the cumulative columns
annual_block = function(trials) {

  s = do.call(rbind, lapply(trials, function(x) {
    d = x$site_data
    data.frame(site_id = d$site_id, district = if ("adm2" %in% names(d)) d$adm2 else NA)
  }))
  ents = unique(unlist(lapply(trials, function(x) x$plot_data$genotype_name)))
  pa = do.call(rbind, lapply(trials, function(x) as.data.frame(x$metadata$participants)))
  data.frame(trials = length(trials),
             participants = sum(pa$total),
             women = sum(pa$women, na.rm = TRUE),
             men = sum(pa$men, na.rm = TRUE),
             not_stated = sum(pa$not_stated, na.rm = TRUE),
             entries = length(stats::na.omit(ents)),
             districts = length(unique(stats::na.omit(tools::toTitleCase(tolower(trimws(s$district)))))))

}

#' Year against cumulative, for the cover, the fact sheet and section 4
annual_overview = function(trials, cfg) {

  yr = cfg$reporting_year
  y = vapply(trials, trial_year, integer(1))
  a = annual_block(trials[y == yr])
  b = annual_block(trials)
  data.frame(metric = names(b), reporting_year = unlist(a[1, ]), cumulative = unlist(b[1, ]), row.names = NULL)

}


#' One row per year, with the entries new to the programme that year
annual_by_year = function(trials) {

  y = vapply(trials, trial_year, integer(1))
  seen = character(0)
  out = lapply(sort(unique(y)), function(k) {
    tt = trials[y == k]
    b = annual_block(tt)
    e = unique(stats::na.omit(unlist(lapply(tt, function(x) x$plot_data$genotype_name))))
    b$new_entries = length(setdiff(e, seen))
    seen <<- union(seen, e)
    cbind(year = k, b)
  })
  do.call(rbind, out)

}


#' Participants per district, since the start and in the reporting year
annual_districts = function(trials, cfg) {

  s = do.call(rbind, lapply(trials, function(x) {
    d = x$site_data
    if (!"adm2" %in% names(d)) return(NULL)
    data.frame(trial_id = x$trial_id, year = trial_year(x),
               district = tools::toTitleCase(tolower(trimws(d$adm2))),
               lon = d$longitude, lat = d$latitude)
  }))
  s = s[!is.na(s$district), ]
  out = do.call(rbind, lapply(split(s, s$district), function(d) {
    data.frame(district = d$district[1], participants = nrow(d), trials = length(unique(d$trial_id)),
               lon = stats::median(d$lon, na.rm = TRUE), lat = stats::median(d$lat, na.rm = TRUE),
               participants_year = sum(d$year == cfg$reporting_year))
  }))
  out[order(-out$participants), ]

}


#' Share of plots rated better than the local variety, per year and overall
#'
#' The three plots of a farm are not independent, so the 95% interval comes from
#' a bootstrap over farms rather than from a binomial interval on plots.
annual_vs_local = function(trials, trait, nboot = 2000, seed = 2024) {

  f = do.call(rbind, lapply(trials, function(x) {
    p = x$plot_data
    p = p[p$trait == trait & p$value_type == "vs_local" & !is.na(p$value), ]
    if (nrow(p) == 0) return(NULL)
    b = tapply(p$value == "better", p$site_id, sum)
    n = tapply(p$value, p$site_id, length)
    data.frame(trial_id = x$trial_id, year = trial_year(x), better = as.integer(b), n = as.integer(n))
  }))
  if (is.null(f)) return(NULL)
  set.seed(seed)
  one = function(d, label) {
    bs = replicate(nboot, { i = sample.int(nrow(d), replace = TRUE); sum(d$better[i]) / sum(d$n[i]) })
    q = stats::quantile(bs, c(0.025, 0.975))
    data.frame(year = label, trials = length(unique(d$trial_id)), farms = nrow(d), plots = sum(d$n),
               better = sum(d$better), share = sum(d$better) / sum(d$n), lower = q[1], upper = q[2], row.names = NULL)
  }
  rbind(do.call(rbind, lapply(split(f, f$year), function(d) one(d, as.character(d$year[1])))), one(f, "all"))

}


#' Record of each entry across trials, from the worth table
#'
#' @param w the table returned by worth() for overall preference
#' @param min_rankings trials with fewer valid rankings are left out, as in report.yml
annual_entry_record = function(w, trials, min_rankings = 15) {

  w = w[w$n_participants >= min_rankings, ]
  y = vapply(trials, trial_year, integer(1))
  names(y) = vapply(trials, function(x) x$trial_id, character(1))
  w$year = y[w$trial_id]
  w = do.call(rbind, lapply(split(w, w$trial_id), function(d) {
    d$rank = rank(-d$log_worth, ties.method = "min"); d$k = nrow(d); d
  }))
  out = do.call(rbind, lapply(split(w, w$entry), function(d) {
    data.frame(genotype = d$entry[1], trials_ranked = nrow(d), seasons_ranked = length(unique(d$year)),
               years = paste(sort(unique(d$year)), collapse = ";"), top3 = sum(d$rank <= 3),
               share_top3 = mean(d$rank <= 3), median_rank = stats::median(d$rank),
               median_k = stats::median(d$k), median_logworth = stats::median(d$log_worth))
  }))
  out[order(-out$share_top3, -out$trials_ranked), ]

}


#' Institutions, people and funders from the trial metadata
annual_partners = function(trials) {

  rows = do.call(rbind, lapply(trials, function(x) {
    m = x$metadata
    c = m$contributors
    rbind(data.frame(institution = m$data_producer$name, role = "data producer", person = NA, trial_id = x$trial_id),
          if (!is.null(m$data_producer$partner)) data.frame(institution = m$data_producer$partner, role = "implementing partner",
                                                           person = NA, trial_id = x$trial_id),
          data.frame(institution = c$affiliation, role = "contributor", person = c$name, trial_id = x$trial_id))
  }))
  inst = do.call(rbind, lapply(split(rows, rows$institution), function(d) {
    data.frame(institution = d$institution[1], roles = paste(sort(unique(d$role)), collapse = "; "),
               trials = length(unique(d$trial_id)), people = length(unique(stats::na.omit(d$person))))
  }))
  people = rows[!is.na(rows$person), ]
  ppl = do.call(rbind, lapply(split(people, people$person), function(d) {
    data.frame(name = d$person[1], affiliation = d$institution[1], trials = length(unique(d$trial_id)))
  }))
  roles = do.call(rbind, lapply(trials, function(x) x$metadata$contributors[, c("name", "contributorType")]))
  ppl$roles = vapply(ppl$name, function(n) paste(sort(unique(roles$contributorType[roles$name == n])), collapse = "; "), character(1))
  fund = do.call(rbind, lapply(trials, function(x) cbind(x$metadata$funder, trial_id = x$trial_id)))
  fund = do.call(rbind, lapply(split(fund, paste(fund$funderName, fund$awardNumber)), function(d) {
    data.frame(funder = d$funderName[1], award = d$awardTitle[1], number = d$awardNumber[1], trials = length(unique(d$trial_id)))
  }))
  list(partners = inst[order(-inst$trials), ], contributors = ppl[order(-ppl$trials, ppl$name), ], funders = fund)

}


#' Candidate results for PRMS, reviewed by the programme's focal point before submission
#'
#' Readiness level and Impact Areas stay empty unless report.yml gives them.
annual_prms = function(trials, ov, record, cfg) {

  doi = trials[[1]]$metadata$identifier
  cum = stats::setNames(ov$cumulative, ov$metric)
  out = data.frame(type = "Knowledge product",
                   title = paste("Open trial data of the", cfg$title, "trials,", cfg$period_label),
                   description = paste(cum["trials"], "tricot trials with", cum["participants"], "registered participants, CC0 1.0"),
                   evidence = "datasets.csv of tricot-data", countries = paste(unique(vapply(trials, function(x) x$metadata$study$country_name, character(1))), collapse = "; "),
                   doi = doi, readiness_level = "", impact_areas = "")
  cand = record[record$trials_ranked >= 3 & record$share_top3 >= 0.5, ]
  if (nrow(cand) > 0) {
    out = rbind(out, data.frame(type = "Innovation development",
                                title = paste("Entry", cand$genotype, "evaluated on-farm"),
                                description = paste("Top three for overall preference in", cand$top3, "of", cand$trials_ranked, "trials"),
                                evidence = "entries-record.csv, worth.csv", countries = out$countries[1], doi = doi,
                                readiness_level = "", impact_areas = ""))
  }
  out

}
