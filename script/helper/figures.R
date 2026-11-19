# Figures for a report
# Status: not executed yet (written 2026-11-19, mirrors the Python draft of the India report)
#
# Intent
#   One function per figure of the report standard. Colours come from the
#   theme, so a figure follows the report it sits in. See docs/style-guide.md.

theme_report = function(base_size = 9) {

  ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(panel.grid.minor = ggplot2::element_blank(),
                   panel.grid.major.y = ggplot2::element_blank(),
                   panel.grid.major.x = ggplot2::element_line(colour = "#EEEEEE", linewidth = 0.3),
                   axis.text = ggplot2::element_text(colour = "#333333"),
                   axis.title = ggplot2::element_text(colour = "#333333", size = base_size - 1),
                   strip.text = ggplot2::element_text(face = "bold", hjust = 0),
                   plot.title = ggplot2::element_text(face = "bold", size = base_size + 0.5),
                   legend.position = "top")

}


save_figure = function(plot, file, width = 16, height = 10) {

  ggplot2::ggsave(file, plot, width = width, height = height, units = "cm", dpi = 300, bg = "white")

}


#' Map of the trial sites, Equal Earth projection, cropped to the trials
#'
#' Boundaries are indicative. Pass an official boundary file through
#' `boundaries` in report.yml when the report is published in or for a country.
figure_map = function(trials, cfg, theme) {

  ch = theme$charts

  pts = do.call(rbind, lapply(trials, function(x) {
    s = x$site_data
    data.frame(place = x$place, crop = x$crop, lon = s$longitude, lat = s$latitude)
  }))
  pts = pts[!is.na(pts$lon) & !is.na(pts$lat), ]

  agg = do.call(rbind, lapply(split(pts, pts$place), function(z) {
    data.frame(place = z$place[1], lon = mean(z$lon), lat = mean(z$lat), farmers = nrow(z),
               text = paste0(z$place[1], "\n", nrow(z), " farmers\n", paste(tolower(sort(unique(z$crop))), collapse = ",\n")))
  }))

  if (!is.null(cfg$boundaries)) {
    land = sf::st_read(file.path(cfg$report, cfg$boundaries), quiet = TRUE)
  } else {
    iso = unique(unlist(lapply(trials, function(x) x$site_data$country_iso3)))
    land = rnaturalearth::ne_states(returnclass = "sf")
    land = land[land$adm0_a3 %in% iso, ]
  }

  pad = 3
  xy = sf::st_as_sf(agg, coords = c("lon", "lat"), crs = 4326)

  ggplot2::ggplot() +
    ggplot2::geom_sf(data = land, fill = ch$map_fill, colour = ch$map_line, linewidth = 0.15) +
    ggplot2::geom_sf(data = xy, ggplot2::aes(size = farmers), colour = ch$single) +
    ggplot2::geom_sf_text(data = xy, ggplot2::aes(label = text), size = 2.6, nudge_y = 1.2, lineheight = 0.9) +
    ggplot2::scale_size_area(max_size = 5, guide = "none") +
    ggplot2::coord_sf(crs = sf::st_crs("EPSG:8857"), default_crs = sf::st_crs(4326),
                      xlim = range(agg$lon) + c(-pad, pad), ylim = range(agg$lat) + c(-pad, pad)) +
    ggplot2::theme_void()

}


#' Participants registered and completing per trial, and the share of women
figure_participation = function(ov, theme) {

  ch = theme$charts
  ov$label = factor(ov$label, levels = rev(sort(ov$label)))

  a = ggplot2::ggplot(ov, ggplot2::aes(y = label)) +
    ggplot2::geom_col(ggplot2::aes(x = registered), fill = ch$single_light, width = 0.62) +
    ggplot2::geom_col(ggplot2::aes(x = completed), fill = ch$single, width = 0.62) +
    ggplot2::geom_text(ggplot2::aes(x = registered, label = paste(completed, "of", registered)), hjust = -0.1, size = 2.6) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0, 0.3))) +
    ggplot2::labs(x = "Farmers, registered (light) and completing the final ranking (dark)", y = NULL) +
    theme_report()

  ov$women_share = 100 * ov$women / ov$registered

  b = ggplot2::ggplot(ov, ggplot2::aes(y = label, x = women_share)) +
    ggplot2::geom_col(fill = ch$positive, width = 0.62) +
    ggplot2::geom_text(ggplot2::aes(label = paste0(round(women_share), "%")), hjust = -0.2, size = 2.6) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0, 0.25))) +
    ggplot2::labs(x = "Women among registered farmers (%)", y = NULL) +
    theme_report() +
    ggplot2::theme(axis.text.y = ggplot2::element_blank())

  patchwork::wrap_plots(a, b, widths = c(1.4, 1))

}


#' Log-worth with 95% intervals, one panel per trial
#'
#' Green marks trials where entries differ at the level in report.yml, grey
#' marks trials where they do not.
figure_worth = function(w, labels, theme, alpha = 0.05) {

  ch = theme$charts
  w = w[w$label %in% labels, ]
  w$differs = w$p_value < alpha
  w$panel = paste0(w$label, "\n", w$n_participants, " farmers, ",
                   ifelse(w$p_value < 0.001, "p < 0.001", paste("p =", signif(w$p_value, 2))))
  w$panel = factor(w$panel, levels = unique(w$panel[order(match(w$label, labels))]))
  # order entries within each panel, keeping one factor for the shared axis
  w$key = paste(w$entry, w$panel, sep = "___")
  w$key = factor(w$key, levels = w$key[order(w$panel, w$log_worth)])

  ggplot2::ggplot(w, ggplot2::aes(x = log_worth, y = key, colour = differs)) +
    ggplot2::geom_vline(xintercept = 0, colour = "#999999", linewidth = 0.3) +
    ggplot2::geom_linerange(ggplot2::aes(xmin = lower, xmax = upper), linewidth = 0.6) +
    ggplot2::geom_point(size = 1.6) +
    ggplot2::facet_wrap(~ panel, scales = "free", nrow = 1) +
    ggplot2::scale_y_discrete(labels = function(z) sub("___.*$", "", z)) +
    ggplot2::scale_colour_manual(values = c("TRUE" = ch$single, "FALSE" = ch$not_different), guide = "none") +
    ggplot2::labs(x = "Log-worth (overall preference)", y = NULL) +
    theme_report(8)

}


#' Share of test plots rated better than the participant's own variety, per trial
figure_vs_local = function(vl, theme) {

  ch = theme$charts
  d = vl[vl$entry == "All entries", ]
  d$label = stats::reorder(d$label, d$share)
  d$text = paste0(round(100 * d$share), "%  (", d$better, " of ", d$n, ")")

  ggplot2::ggplot(d, ggplot2::aes(y = label, x = 100 * share)) +
    ggplot2::geom_vline(xintercept = 50, colour = "#999999", linetype = "dashed", linewidth = 0.3) +
    ggplot2::geom_linerange(ggplot2::aes(xmin = 100 * lower, xmax = 100 * upper), colour = ch$single_light, linewidth = 1) +
    ggplot2::geom_point(colour = ch$single, size = 2) +
    ggplot2::geom_text(ggplot2::aes(x = 103, label = text), hjust = 0, size = 2.6) +
    ggplot2::scale_x_continuous(limits = c(0, 135), breaks = c(0, 25, 50, 75, 100)) +
    ggplot2::labs(x = "Test plots rated better than the farmer's own variety (%), with 95% interval", y = NULL) +
    theme_report()

}


#' Agreement of each trait with overall preference, pooled over trials
figure_trait_agreement = function(ta, theme, trait_labels = NULL) {

  ch = theme$charts
  d = ta[ta$label == "All trials", ]
  d$name = if (is.null(trait_labels)) gsub("_", " ", d$trait) else ifelse(d$trait %in% names(trait_labels), unlist(trait_labels[d$trait]), d$trait)
  d$name = stats::reorder(d$name, d$tau)
  d$text = paste0(sprintf("%.2f", d$tau), "   ", d$n_participants, " farmers, ", d$n_trials, " trials")

  ggplot2::ggplot(d, ggplot2::aes(y = name, x = tau)) +
    ggplot2::geom_vline(xintercept = 0, colour = "#999999", linewidth = 0.3) +
    ggplot2::geom_linerange(ggplot2::aes(xmin = lower, xmax = upper), colour = ch$single_light, linewidth = 1) +
    ggplot2::geom_point(colour = ch$single, size = 2) +
    ggplot2::geom_text(ggplot2::aes(x = max(d$upper) + 0.05, label = text), hjust = 0, size = 2.6) +
    ggplot2::scale_x_continuous(limits = c(min(-0.2, min(d$lower)), max(d$upper) + 0.6)) +
    ggplot2::labs(x = "Mean Kendall tau with overall preference, with 95% bootstrap interval", y = NULL) +
    theme_report()

}


#' Themes in the reasons for the most and least preferred entry
figure_reasons = function(rt, theme) {

  ch = theme$charts
  d = rt[rt$theme != "Other or general", ]
  ord = d$theme[d$kind == "most"][order(d$share[d$kind == "most"])]
  d$theme = factor(d$theme, levels = ord)
  n = tapply(d$answered, d$kind, max)
  d$series = ifelse(d$kind == "most",
                    paste0("Reason for the most preferred entry (", n["most"], " farmers)"),
                    paste0("Reason for the least preferred entry (", n["least"], " farmers)"))

  ggplot2::ggplot(d, ggplot2::aes(y = theme, x = 100 * share, fill = series)) +
    ggplot2::geom_col(position = ggplot2::position_dodge(width = 0.8), width = 0.72) +
    ggplot2::geom_text(ggplot2::aes(label = paste0(round(100 * share), "%")),
                       position = ggplot2::position_dodge(width = 0.8), hjust = -0.2, size = 2.5) +
    ggplot2::scale_fill_manual(values = stats::setNames(c(ch$positive, ch$negative), sort(unique(d$series), decreasing = TRUE)), name = NULL) +
    ggplot2::scale_x_continuous(expand = ggplot2::expansion(mult = c(0, 0.15))) +
    ggplot2::guides(fill = ggplot2::guide_legend(ncol = 1, reverse = TRUE)) +
    ggplot2::labs(x = "Farmers mentioning the theme (%)", y = NULL) +
    theme_report()

}
