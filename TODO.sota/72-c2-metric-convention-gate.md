# WO72 — C2: gates reject undeclared metric conventions

Status: PLANNED
Goal: quality gates refuse a metric that doesn't declare its convention
(row-mean vs corpus-level) and anchor.
Method: extend the gate registry (WO55 pattern): MetricDeclaration
required on every metrics file consumed by a gate; validate in
`isxml gate` and publish guard. Spec: real instances, no doubles.
Acceptance: gate tests proving rejection; all existing recipes updated
with declarations (they are, per WO53 — verify).
