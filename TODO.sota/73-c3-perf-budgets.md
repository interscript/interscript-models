# WO73 — C3: performance budgets in CI

Status: PLANNED
Goal: decode latency + artifact size budgets enforced so regressions
block like test failures.
Method: measure current shipped baselines (single-row greedy, p50/p95
per model, mobile-typical CPU); encode budgets in models.yaml metadata
(perf: {latency_p50_ms, size_mb}); runtime CI asserts the budget on the
conformance fixture set; budget changes are owner-visible recipe edits.
Acceptance: budgets in the index; CI green under budget; a synthetic
regression fails CI (proven).
