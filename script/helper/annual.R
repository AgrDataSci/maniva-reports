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


#' Reporting fields of the CGIAR results framework, with suggested tags
#'
#' Every field is returned, empty or not, so the report shows the full set. Impact Areas,
#' SDGs and the readiness level are suggested from the data with fixed rules
#' (docs/annual-report-standard.md). A suggestion never sets a principal score (2). The
#' value the programme gives under `reporting` in report.yml goes in `given`.
annual_reporting_fields = function(trials, ov, cfg) {

  rep = cfg$reporting
  cum = stats::setNames(ov$cumulative, ov$metric)
  p = do.call(rbind, lapply(trials, function(x) x$plot_data[, c("trait", "value_type")]))
  ranked = unique(p$trait[p$value_type == "rank"])
  roles = tolower(unique(unlist(lapply(trials, function(x) x$metadata$genotypes$role))))
  known = cum["women"] + cum["men"]
  g_share = if (known > 0) cum["women"] / known else 0
  g_cover = if (cum["participants"] > 0) known / cum["participants"] else 0
  climate = intersect(ranked, c("drought_tolerance", "flood_tolerance", "heat_tolerance", "maturity", "waterlogging_tolerance"))
  market = intersect(ranked, c("marketability", "yield_rank", "grain_size", "grain_color", "taste", "cooking_time"))
  biod = any(grepl("landrace|accession", roles))
  given = function(x) if (is.null(x) || length(unlist(x)) == 0) NA_character_ else paste(unlist(x), collapse = "; ")
  row = function(group, field, g, s, rule, ev) data.frame(group = group, field = field, given = given(g),
                                                          suggested = if (is.null(s)) NA else as.character(s), rule = rule,
                                                          evidence = if (is.null(ev)) NA else ev)
  ia = rep$impact_areas
  out = rbind(
    row("Impact Areas", "Nutrition, health and food security", ia$nutrition, 1, "Variety evaluation of a food crop with farmers",
        paste(cum["trials"], "trials")),
    row("Impact Areas", "Poverty reduction, livelihoods and jobs", ia$poverty, as.integer(length(market) > 0),
        "Market or yield traits ranked by farmers", if (length(market) > 0) paste(sort(market), collapse = ", ") else "none ranked"),
    row("Impact Areas", "Gender equality, youth and social inclusion", ia$gender, as.integer(g_share >= 0.3 && g_cover >= 0.8),
        "Gender recorded for at least 80% of participants and women at least 30% of them",
        sprintf("gender recorded for %.0f%%, women %.0f%%", 100 * g_cover, 100 * g_share)),
    row("Impact Areas", "Climate adaptation and mitigation", ia$climate, as.integer(length(climate) > 0),
        "A climate-stress or earliness trait ranked by farmers", if (length(climate) > 0) paste(sort(climate), collapse = ", ") else "none ranked"),
    row("Impact Areas", "Environmental health and biodiversity", ia$environment, as.integer(biod),
        "Landraces or genebank accessions among the entries", paste("entry roles:", paste(sort(roles[nzchar(roles)]), collapse = ", "))))
  sdg = c(Nutrition = "SDG 2 Zero hunger", Poverty = "SDG 1 No poverty", Gender = "SDG 5 Gender equality",
          Climate = "SDG 13 Climate action", Environmental = "SDG 15 Life on land")
  on = c(sdg[sub(" .*|,.*", "", out$field)[as.integer(out$suggested) > 0]], "SDG 17 Partnerships for the goals")
  on = on[order(as.integer(sub("SDG ([0-9]+).*", "\\1", on)))]
  cs = rep$capacity_sharing
  bud = rep$budget
  out = rbind(out,
    row("SDGs", "Sustainable Development Goals", rep$sdgs, paste(on, collapse = "; "),
        "One SDG per Impact Area scored 1 or 2, and SDG 17 always for tricot and maniva work",
        "Impact Areas above; trials run with farmers, national partners and CGIAR"),
    row("Innovation", "Innovation readiness level of the entries under evaluation", rep$readiness_level, "8 Uncontrolled testing",
        "Entries tested by farmers on their own farms, under their own management. 9 needs evidence of validated impact, such as a release and its use",
        paste(cum["entries"], "entries in", cum["trials"], "farmer-managed trials")),
    row("Innovation", "Innovation use", rep$innovation_use, NULL, "Set by the programme, for example a release or seed multiplication that used the trial evidence", NULL),
    row("Policy", "Policy change", rep$policy_change, NULL, "Set by the programme", NULL),
    row("Capacity sharing for development", "Short-term trainees, women", cs$short_term_women, NULL, "Recorded by the programme. Trial participants are not trainees", NULL),
    row("Capacity sharing for development", "Short-term trainees, men", cs$short_term_men, NULL, "Recorded by the programme. Trial participants are not trainees", NULL),
    row("Capacity sharing for development", "Long-term trainees, women", cs$long_term_women, NULL, "Recorded by the programme. Trial participants are not trainees", NULL),
    row("Capacity sharing for development", "Long-term trainees, men", cs$long_term_men, NULL, "Recorded by the programme. Trial participants are not trainees", NULL),
    row("Capacity sharing for development", "Students supervised for a degree", cs$degree_students, NULL, "Recorded by the programme. Trial participants are not trainees", NULL),
    row("Budget", "Approved budget, previous year", bud$previous_year, NULL, "Set by the programme", NULL),
    row("Budget", "Approved budget, reporting year", bud$reporting_year, NULL, "Set by the programme", NULL),
    row("Outcomes", "End-of-project outcomes and their status", vapply(rep$outcomes, function(o) o$name, character(1)), NULL,
        "Set by the programme, status on track, delayed or off track", NULL),
    row("Linkages", "CGIAR programmes and accelerators", rep$linkages, NULL, "Named by the programme", NULL))
  rownames(out) = NULL
  out

}
