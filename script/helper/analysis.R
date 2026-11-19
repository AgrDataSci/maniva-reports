# Result tables for a report
# Status: not executed yet (written 2026-11-19, mirrors the Python draft of the India report)
# Decision records: ranking.md, trait-associations.md, socioeconomic-heterogeneity.md
#   in tricot-analysis-workflows
#
# Intent
#   Each function returns one table that one section of the report reads.
#   Fitting and testing are done by the use-case functions loaded in
#   workflows.R. The code here only prepares their input and stacks their
#   output across trials.
#
# Limits
#   - One model per trial. Pooling trials is a separate decision, see the use
#     case can-heterogeneous-trials-be-combined.
#   - Worth is relative to the entries of a trial. It is not yield.


#' One row per trial, for the cover, the trial table and the participants section
overview = function(trials, cfg) {

  out = lapply(trials, function(x) {
    s = x$site_data
    R = trait_rankings(x, cfg$analysis$overall_trait)
    g = if ("farmer_gender" %in% names(s)) s$farmer_gender else rep(NA, nrow(s))
    data.frame(trial_id = x$trial_id,
               label = x$label,
               crop = x$crop,
               place = x$place,
               adm1 = if ("adm1" %in% names(s)) names(sort(table(s$adm1), decreasing = TRUE))[1] else NA,
               start = x$metadata$date$start,
               end = x$metadata$date$end,
               data_producer = x$metadata$data_producer$name,
               entries = length(unique(x$plot_data$genotype_name)),
               registered = nrow(s),
               women = sum(g == "woman", na.rm = TRUE),
               men = sum(g == "man", na.rm = TRUE),
               completed = R$n_valid,
               min_farms_per_entry = min(R$n_per_item),
               max_farms_per_entry = max(R$n_per_item))
  })

  do.call(rbind, out)

}


#' Worth of every entry in every trial, for overall preference or another trait
#'
#' Log-worth with quasi-standard errors, so any two entries can be compared.
#' Adds the bootstrap probability of a top-three place, which the report
#' standard asks for when entries were ranked on few farms, and the
#' probability of beating the check when the metadata name one.
worth = function(trials, trait, nboot = 200) {

  out = lapply(trials, function(x) {

    R = trait_rankings(x, trait)
    if (R$n_valid < 10) return(NULL)

    r = R$rankings[R$valid, ]

    connected = ranking$check_connectivity(r)

    mod = PlackettLuce::PlackettLuce(r)
    ad = ranking$model_adequacy(mod)

    qv = qvcalc::qvcalc(mod, ref = NULL)$qvframe

    res = data.frame(trial_id = x$trial_id,
                     label = x$label,
                     trait = trait,
                     entry = rownames(qv),
                     log_worth = qv$estimate,
                     quasi_se = qv$quasiSE,
                     lower = qv$estimate - stats::qnorm(0.975) * qv$quasiSE,
                     upper = qv$estimate + stats::qnorm(0.975) * qv$quasiSE,
                     worth = exp(qv$estimate) / sum(exp(qv$estimate)),
                     n_farms = as.integer(R$n_per_item[rownames(qv)]),
                     n_participants = R$n_valid,
                     connected = connected,
                     lr_deviance = ad$deviance,
                     lr_df = ad$df,
                     p_value = ad$p_value,
                     mcfadden_r2 = ad$mcfadden_r2,
                     row.names = NULL)

    tp = ranking$top_probability(r, k = 3, nboot = nboot)
    res$p_first = tp$p_first[match(res$entry, tp$item)]
    res$p_top3 = tp$p_top_k[match(res$entry, tp$item)]

    # probability of beating the check, only when the metadata name a check
    g = x$metadata$genotypes
    check = g$genotype_name[grepl("check", g$role, ignore.case = TRUE)]
    res$check = NA_character_
    res$p_beat_check = NA_real_
    if (length(check) == 1 && check %in% res$entry) {
      rel = gosset::reliability(mod, ref = check)
      res$check = check
      res$p_beat_check = rel$reliability[match(res$entry, rel$item)]
    }

    res[order(res$log_worth, decreasing = TRUE), ]

  })

  do.call(rbind, out)

}


#' Rank correlation of log-worth between trials of the same crop, on shared entries
site_agreement = function(w) {

  w$crop = sub(",.*$", "", w$label)
  out = list()

  for (cr in unique(w$crop)) {
    x = w[w$crop == cr, ]
    labs = unique(x$label)
    if (length(labs) < 2) next
    pairs = utils::combn(labs, 2)
    for (j in seq_len(ncol(pairs))) {
      a = x[x$label == pairs[1, j], ]
      b = x[x$label == pairs[2, j], ]
      shared = intersect(a$entry, b$entry)
      if (length(shared) < 4) next
      rho = stats::cor(a$log_worth[match(shared, a$entry)],
                       b$log_worth[match(shared, b$entry)], method = "spearman")
      out[[length(out) + 1]] = data.frame(crop = cr, trial_a = pairs[1, j], trial_b = pairs[2, j],
                                          shared_entries = length(shared), spearman = rho)
    }
  }

  do.call(rbind, out)

}


#' Share of test plots rated better than the participant's own variety
#'
#' Descriptive. The interval is a Wilson 95% interval on plots, which treats
#' the three plots of a farm as independent and is therefore a little narrow.
vs_local = function(trials, trait) {

  out = lapply(trials, function(x) {
    p = x$plot_data
    p = p[p$trait == trait & p$value_type == "vs_local" & !is.na(p$value), ]
    if (nrow(p) == 0) return(NULL)
    better = tapply(p$value == "better", p$genotype_name, sum)
    n = tapply(p$value, p$genotype_name, length)
    a = data.frame(genotype_name = names(n), better = as.integer(better), n = as.integer(n))
    a = rbind(a, data.frame(genotype_name = "All entries", better = sum(a$better), n = sum(a$n)))
    ci = t(mapply(function(b, n) stats::prop.test(b, n, correct = FALSE)$conf.int, a$better, a$n))
    data.frame(trial_id = x$trial_id, label = x$label, entry = a$genotype_name,
               better = a$better, n = a$n, share = a$better / a$n, lower = ci[, 1], upper = ci[, 2])
  })

  do.call(rbind, out)

}


#' Agreement of each ranked trait, and of measured yield, with overall preference
#'
#' Within-participant Kendall tau, averaged with the number of entry pairs as
#' weight, with a bootstrap interval over participants. Marginal tau only,
#' because partial correlations need many more participants per pair than a
#' single trial usually has (decisions/trait-associations.md).
trait_agreement = function(trials, cfg, nboot = 500, seed = 1) {

  ref = cfg$analysis$overall_trait
  rows = list()

  for (x in trials) {

    R0 = trait_rankings(x, ref)
    others = setdiff(ranked_traits(x), ref)
    # a later overall-type question is never an explanatory trait
    others = others[!grepl("overall|generalappreciation|generalpreference|grownext", others)]

    cand = lapply(others, function(t) trait_rankings(x, t))
    names(cand) = others

    yt = cfg$analysis$yield_trait
    if (!is.null(yt) && yt %in% x$plot_data$trait) {
      cand[[paste0(yt, "_order")]] = trait_rankings(x, yt, value_type = "numeric", decreasing = TRUE)
    }

    for (t in names(cand)) {
      k = traits$row_kendall(R0$rankings, cand[[t]]$rankings)
      k = k[!is.na(k$tau) & k$pairs > 0, ]
      if (nrow(k) < 10) next
      rows[[length(rows) + 1]] = data.frame(label = x$label, trait = t, tau = k$tau, pairs = k$pairs)
    }

  }

  d = do.call(rbind, rows)

  wmean = function(z) sum(z$tau * z$pairs) / sum(z$pairs)

  boot = function(z) {
    set.seed(seed)
    b = vapply(seq_len(nboot), function(i) wmean(z[sample.int(nrow(z), nrow(z), replace = TRUE), ]), numeric(1))
    stats::quantile(b, c(0.025, 0.975))
  }

  summarise = function(z, label) {
    ci = boot(z)
    data.frame(label = label, trait = z$trait[1], tau = wmean(z), lower = ci[1], upper = ci[2],
               n_participants = nrow(z), n_trials = length(unique(z$label)), row.names = NULL)
  }

  per_trial = do.call(rbind, lapply(split(d, list(d$label, d$trait), drop = TRUE), function(z) summarise(z, z$label[1])))
  pooled = do.call(rbind, lapply(split(d, d$trait), function(z) summarise(z, "All trials")))

  rbind(pooled[order(pooled$tau, decreasing = TRUE), ], per_trial)

}


#' Do predefined groups, such as women and men, prefer different entries
#'
#' Follows part A of the use case do-user-groups-prefer-different-varieties.
#' A group needs at least min_group_n valid answers to be compared. Each trial
#' is one site here, so the test is within site by construction. When a trial
#' spans several sites, use groups$stratified_heterogeneity() instead.
group_differences = function(trials, cfg, nperm = 200) {

  gvar = cfg$analysis$group
  min_n = if (is.null(cfg$analysis$min_group_n)) 20 else cfg$analysis$min_group_n

  out = lapply(trials, function(x) {

    R = trait_rankings(x, cfg$analysis$overall_trait)
    g = x$site_data[[gvar]]
    if (is.null(g)) return(NULL)
    g = as.character(g)[R$valid]
    g[is.na(g)] = "Not specified"
    r = R$rankings[R$valid, ]

    el = groups$group_eligibility(g, min_n = min_n)

    res = data.frame(trial_id = x$trial_id, label = x$label, group_variable = gvar,
                     groups = paste(el$group, el$n, sep = " ", collapse = "; "),
                     compared = sum(el$eligible) >= 2,
                     deviance = NA_real_, df = NA_real_, p_chisq = NA_real_, p_permutation = NA_real_,
                     top_by_group = NA_character_)

    if (res$compared) {
      keep = g %in% el$group[el$eligible]
      h = groups$preference_heterogeneity(r[keep, ], g[keep], nperm = nperm)
      res$deviance = h$deviance
      res$df = h$df
      res$p_chisq = h$p_chisq
      res$p_permutation = h$p_permutation
      top = vapply(split(which(keep), g[keep]), function(i) {
        co = stats::coef(PlackettLuce::PlackettLuce(r[i, ]), log = TRUE)
        names(co)[which.max(co)]
      }, character(1))
      res$top_by_group = paste(names(top), top, sep = " ", collapse = "; ")
    }

    res

  })

  do.call(rbind, out)

}


#' Themes in the reasons participants gave, coded with a documented keyword list
#'
#' The themes file is a YAML list of theme names with one regular expression
#' each. A reason can match several themes. Coding by keyword is a first pass
#' and a native speaker reviews it before publication.
reason_themes = function(trials, cfg) {

  rs = cfg$analysis$reasons
  if (is.null(rs$themes)) return(NULL)
  themes = yaml::read_yaml(file.path(cfg$report, rs$themes))$themes

  site = do.call(rbind, lapply(trials, function(x) {
    s = x$site_data
    data.frame(label = x$label,
               gender = if ("farmer_gender" %in% names(s)) s$farmer_gender else NA,
               most = if (rs$most %in% names(s)) s[[rs$most]] else NA,
               least = if (rs$least %in% names(s)) s[[rs$least]] else NA)
  }))

  out = list()

  for (kind in c("most", "least")) {
    txt = tolower(site[[kind]])
    answered = !is.na(txt) & nzchar(trimws(txt))
    hit = vapply(themes, function(t) grepl(t$pattern, paste0(txt, " "), perl = TRUE), logical(length(txt)))
    hit = matrix(hit, ncol = length(themes))
    other = answered & rowSums(hit) == 0
    counts = c(colSums(hit[answered, , drop = FALSE]), sum(other))
    out[[kind]] = data.frame(kind = kind,
                             theme = c(vapply(themes, function(t) t$name, character(1)), "Other or general"),
                             n = counts,
                             answered = sum(answered),
                             share = counts / sum(answered))
  }

  do.call(rbind, out)

}


#' Measured yield per trial, with what the protocol allows the reader to compare
#'
#' Returns the distribution of the recorded values and of the number of
#' plants harvested, so the report can say whether sites applied the same
#' protocol. No yield per hectare is derived here.
yield_summary = function(trials, cfg) {

  yt = cfg$analysis$yield_trait
  if (is.null(yt)) return(NULL)

  out = lapply(trials, function(x) {
    p = x$plot_data
    y = suppressWarnings(as.numeric(p$value[p$trait == yt & p$value_type == "numeric"]))
    y = y[!is.na(y)]
    if (length(y) == 0) return(NULL)
    ph = suppressWarnings(as.numeric(p$value[p$trait == "plants_harvested"]))
    data.frame(trial_id = x$trial_id, label = x$label, trait = yt,
               unit = paste(unique(stats::na.omit(p$unit[p$trait == yt])), collapse = "; "),
               n_plots = length(y), min = min(y), q1 = stats::quantile(y, 0.25), median = stats::median(y),
               q3 = stats::quantile(y, 0.75), max = max(y),
               plants_harvested_median = if (length(ph)) stats::median(ph, na.rm = TRUE) else NA,
               plants_harvested_max = if (length(ph)) max(ph, na.rm = TRUE) else NA,
               row.names = NULL)
  })

  do.call(rbind, out)

}


#' Who took part, pooled over trials, for the participants section
participants = function(trials) {

  s = do.call(rbind, lapply(trials, function(x) {
    v = c("farmer_gender", "age", "farm_size", "seed_source", "crop_usually_grown", "location")
    d = x$site_data
    for (m in setdiff(v, names(d))) d[[m]] = NA
    cbind(label = x$label, d[, v])
  }))

  share = function(x) {
    tb = sort(table(tolower(trimws(x))), decreasing = TRUE)
    paste(names(tb), paste0(round(100 * tb / sum(tb)), "%"), collapse = "; ")
  }

  data.frame(measure = c("participants", "villages", "women", "men", "median age", "median age women",
                         "median age men", "median farm size", "share of farms up to 2 ha",
                         "seed source", "crop usually grown"),
             value = c(nrow(s),
                       length(unique(stats::na.omit(s$location))),
                       sum(s$farmer_gender == "woman", na.rm = TRUE),
                       sum(s$farmer_gender == "man", na.rm = TRUE),
                       stats::median(as.numeric(s$age), na.rm = TRUE),
                       stats::median(as.numeric(s$age[s$farmer_gender == "woman"]), na.rm = TRUE),
                       stats::median(as.numeric(s$age[s$farmer_gender == "man"]), na.rm = TRUE),
                       stats::median(as.numeric(s$farm_size), na.rm = TRUE),
                       round(mean(as.numeric(s$farm_size) <= 2, na.rm = TRUE), 3),
                       share(s$seed_source),
                       share(s$crop_usually_grown)))

}
