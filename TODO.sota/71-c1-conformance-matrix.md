# WO71 — C1: model × runtime conformance matrix in CI

Status: PLANNED
Goal: every shipped model byte-exact in ruby/ts/py, CI-enforced, forever.
Method: fixtures already frozen in conformance/ (12 rows each; sidecar
on the release). Wire each runtime's CI to download the fixture set
from the models Releases (data channel law) and run the full matrix:
all shipped models, not just the ones curated per-repo. A red cell
blocks merge like any test.
Acceptance: matrix visible in CI summary (model × runtime grid, all
green); new model publication extends the matrix automatically.
