# Read trial files in the tricot-data format (release schema v3.0) for a report
# Status: not executed yet (written 2026-11-19, mirrors the Python draft of the India report)
#
# Intent
#   One reader for every report, so each section starts from the same objects.
#   The trial files are read from their source and never copied into the report
#   folder, because participant-level data stay with the data layer.


#' Read report.yml of a report folder
read_config = function(report) {

  cfg = yaml::read_yaml(file.path(report, "report.yml"))
  cfg$report = normalizePath(report)
  cfg

}


#' Read the theme named in report.yml
read_theme = function(cfg) {

  name = if (is.null(cfg$theme)) "cgiar" else cfg$theme
  yaml::read_yaml(file.path("themes", paste0(name, ".yml")))

}


#' Read the trials a report covers
#'
#' Trials are chosen by id, or by a filter on datasets.csv (country, start
#' year) and on the programme named in the metadata of each file.
#'
#' @param cfg the list returned by read_config()
#' @return a named list of trials, each a list with metadata, site_data and
#'   plot_data, plus label, crop and place
read_trials = function(cfg) {

  src = cfg$data$source
  idx = utils::read.csv(paste0(src, "datasets.csv"))

  ids = unlist(cfg$data$trial_ids)
  f = cfg$data$filter

  if (length(ids) > 0) {
    idx = idx[idx$trial_id %in% ids, ]
  } else {
    if (!is.null(f$country_iso3)) idx = idx[idx$country_iso3 %in% f$country_iso3, ]
    if (!is.null(f$crop_name)) idx = idx[idx$crop_name %in% f$crop_name, ]
    if (!is.null(f$start_year)) idx = idx[substr(idx$start_date, 1, 4) %in% as.character(f$start_year), ]
  }

  # the report standard covers farmer-managed tricot trials
  idx = idx[grepl("tricot", idx$management), ]

  trials = lapply(idx$path, function(p) {
    jsonlite::fromJSON(paste0(src, p), simplifyDataFrame = TRUE)
  })

  if (!is.null(f$program) && length(ids) == 0) {
    keep = vapply(trials, function(x) {
      identical(x$metadata$data_producer$program, f$program)
    }, logical(1))
    trials = trials[keep]
    idx = idx[keep, ]
  }

  if (length(trials) == 0) stop("no trial matches the data section of report.yml", call. = FALSE)

  for (i in seq_along(trials)) {
    s = trials[[i]]$site_data
    trials[[i]]$trial_id = idx$trial_id[i]
    trials[[i]]$crop = pretty_crop(idx$crop_name[i])
    trials[[i]]$place = first_place(s)
    trials[[i]]$label = paste(trials[[i]]$crop, trials[[i]]$place, sep = ", ")
    trials[[i]]$index = idx[i, ]
  }

  names(trials) = vapply(trials, function(x) x$label, character(1))

  if (any(duplicated(names(trials)))) {
    # two trials of one crop in one place, add the trial id to tell them apart
    d = names(trials) %in% names(trials)[duplicated(names(trials))]
    names(trials)[d] = paste0(names(trials)[d], " (", idx$trial_id[d], ")")
    for (i in which(d)) trials[[i]]$label = names(trials)[i]
  }

  trials[order(names(trials))]

}


#' Crop key to a readable name, "fingermillet" to "Finger millet"
pretty_crop = function(x) {

  known = c(fingermillet = "Finger millet", foxtailmillet = "Foxtail millet",
            littlemillet = "Little millet", horsegram = "Horse gram",
            commonbean = "Common bean", sweetpotato = "Sweetpotato",
            pearlmillet = "Pearl millet", kodomillet = "Kodo millet",
            breadwheat = "Bread wheat", durumwheat = "Durum wheat")

  if (x %in% names(known)) return(unname(known[x]))

  paste0(toupper(substr(x, 1, 1)), substr(x, 2, nchar(x)))

}


#' Most specific administrative unit shared by the sites of a trial
first_place = function(site) {

  for (v in c("adm3", "adm2", "adm1")) {
    if (v %in% names(site) && any(!is.na(site[[v]]))) {
      tb = sort(table(site[[v]]), decreasing = TRUE)
      # a trial spread over many units is named by the next level up
      if (tb[1] / sum(tb) >= 0.8) return(names(tb)[1])
    }
  }

  "all sites"

}


#' Rankings of one trait as a rankings object aligned to the sites of a trial
#'
#' Every trait of a trial gets the same rows (sites) and columns (entries), so
#' rankings of two traits can be compared row by row. A site without a valid
#' ranking for the trait is a row of zeros.
#'
#' @param trial one element of read_trials()
#' @param trait character, the standard trait name
#' @param decreasing FALSE when value holds positions (1 is best), TRUE when
#'   it holds a measurement to order from high to low
#' @return list with rankings, valid (logical per row) and n_ties
trait_rankings = function(trial, trait, value_type = "rank", decreasing = FALSE) {

  p = trial$plot_data
  p = p[p$trait == trait & p$value_type == value_type, ]

  # measured traits use the standard value when the file carries one
  v = p$value
  if (value_type == "numeric" && "value_standard" %in% names(p)) {
    v = ifelse(is.na(p$value_standard), p$value, p$value_standard)
  }
  p$v = suppressWarnings(as.numeric(v))
  p = p[!is.na(p$v), ]

  sites = trial$site_data$site_id
  items = sort(unique(trial$plot_data$genotype_name))

  m = matrix(0, nrow = length(sites), ncol = length(items), dimnames = list(sites, items))

  n_ties = 0

  for (s in unique(p$site_id)) {
    x = p[p$site_id == s, ]
    if (nrow(x) < 2 || any(duplicated(x$genotype_name))) next
    if (any(duplicated(x$v))) {
      n_ties = n_ties + 1
      next
    }
    m[s, x$genotype_name] = rank(if (decreasing) -x$v else x$v)
  }

  valid = rowSums(m > 0) >= 2

  list(rankings = PlackettLuce::as.rankings(m),
       valid = valid,
       n_valid = sum(valid),
       n_ties = n_ties,
       n_per_item = colSums(m[valid, , drop = FALSE] > 0))

}


#' Which ranked traits a trial holds
ranked_traits = function(trial) {

  p = trial$plot_data
  sort(unique(p$trait[p$value_type == "rank"]))

}
