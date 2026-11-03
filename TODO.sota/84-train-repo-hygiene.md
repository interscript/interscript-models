# WO84 — interscript-train: land the local uncommitted work

Status: PLANNED · hygiene (discovered 2026-10-22; durability lives only
on this laptop)

The local checkout of `training/wo31-wo36-campaign-scripts` carries
uncommitted improvements that production runs already depend on
(r8_noisy_student_hf.py's self-contained decode + sync_to_bucket
durability, C-Levenshtein eval path), plus untracked research docs and
utilities. One `/tmp`-style loss and the running campaign's durability
is unexplained by any commit.

Goal: `git status` clean on the campaign branch lineage; every behavior
a running job depends on exists in a pushed commit.

Method:
- Branch from `training/wo31-wo36-campaign-scripts`.
- Commit the five modified scripts with per-change messages (explicit
  paths only — never `git add -A`).
- Triage untracked: `TODO.research/*` docs, `conformance_runtime_check.py`,
  `classes.json` → commit if source; `dist/` → never (build output).
- PR into the campaign lineage; merge after green.

Acceptance: pushed branch + merged PR; running jobs' behavior matches
a commit; worktree clean.
