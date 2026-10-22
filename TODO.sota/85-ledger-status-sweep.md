# WO85 — Ledger status sweep: headers must match verified reality

Status: DONE (2026-10-22 sweep in the same PR that adds WO81–86)

The `Status:` headers of WO57–78 lagged execution: C1/C2 recorded
PLANNED while all gates were green; A3/E1/E2 recorded PLANNED while
merged. A ledger that lies about state is worse than no ledger.

Goal: every WO header reflects the verified state at sweep time;
sweeps re-run whenever a plane milestone lands.

Method: sweep headers against evidence (merged PRs, CI, gates) —
never against intention. Dated.

Acceptance: this file records the sweep; headers current as of
2026-10-22.
