# Load the methods from tricot-analysis-workflows
# Status: not executed yet (written 2026-11-19)
#
# Intent
#   Reports never define a method of their own. The functions that fit and
#   test come from the use cases of tricot-analysis-workflows, read at a pinned
#   commit so a report can say exactly which version of the methods it used.
#   Update the commit on purpose, after reading what changed in the use cases.

workflows_commit = "44328b96052685e5256df3a2bb4d343de53ba72f"

workflows_base = paste0("https://raw.githubusercontent.com/AgrDataSci/tricot-analysis-workflows/",
                        workflows_commit, "/use-cases/")

# each use case defines helpers with the same names (build_rankings,
# check_connectivity), so each is sourced into its own environment
ranking = new.env()
traits = new.env()
groups = new.env()

source(paste0(workflows_base, "which-varieties-do-participants-prefer/script/helper/functions.R"), local = ranking)
source(paste0(workflows_base, "which-traits-drive-preference/script/helper/functions.R"), local = traits)
source(paste0(workflows_base, "do-user-groups-prefer-different-varieties/script/helper/functions.R"), local = groups)
