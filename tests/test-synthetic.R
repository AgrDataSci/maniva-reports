# Check the R workflow on the synthetic example against the true values of the fixture
# Status: reviewed-not-executed (written 2026-11-23). The same checks run in Python in
#   tests/check-synthetic.py, which passed on the Python draft of the analysis.
#
# Run from the repository root, after the R analysis of the synthetic example, with
#   Rscript script/01-analysis.R reports/synthetic-example-annual
#   Rscript tests/test-synthetic.R

library("testthat")
library("jsonlite")

report = "reports/synthetic-example-annual"
out = file.path(report, "output")
exp = fromJSON("tests/fixtures/expected.json", simplifyVector = FALSE)
trials = exp$trials
yr = Filter(function(t) t$year == 2024, trials)

test_that("counts match the fixture, year and cumulative", {
  ov = read.csv(file.path(out, "tables", "overview.csv"))
  get = function(m, col) ov[[col]][ov$metric == m]
  for (m in c("participants", "women", "men", "not_stated")) {
    expect_equal(get(m, "cumulative"), sum(vapply(trials, function(t) t[[m]], numeric(1))))
    expect_equal(get(m, "reporting_year"), sum(vapply(yr, function(t) t[[m]], numeric(1))))
  }
  expect_equal(get("trials", "cumulative"), length(trials))
})

test_that("overall preference recovers the true order", {
  w = read.csv(file.path(out, "worth.csv"))
  w = w[w$trait == "overall_performance", ]
  truth = unlist(exp$true_logworth_overall)
  for (id in names(trials)) {
    t = trials[[id]]
    d = w[w$trial_id == id, ]
    if (t$overall_rankings < 15) next
    rho = stats::cor(d$log_worth, truth[d$entry], method = "spearman")
    expect_gte(rho, 0.6, label = paste(t$code, "rank correlation"))
  }
  big = names(trials)[which.max(vapply(trials, function(t) t$overall_rankings, numeric(1)))]
  d = w[w$trial_id == big, ]
  expect_equal(d$entry[which.max(d$log_worth)], trials[[big]]$true_order[[1]])
})

test_that("every reporting field is written, with SDG 17 and no principal score", {
  rf = read.csv(file.path(out, "tables", "reporting-fields.csv"), colClasses = "character")
  expect_gte(nrow(rf), 18)
  expect_true(all(grepl("SDG 17", rf$suggested[rf$group == "SDGs"])))
  expect_false(any(rf$suggested[rf$group == "Impact Areas"] == "2"))
})

test_that("figure data are written", {
  expect_gte(length(list.files(file.path(out, "figure-data"), pattern = "[.]csv$")), 4)
})
