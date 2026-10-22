# WO64 — B3: Arabic to external SOTA (DER < 2.0, WikiNews < 8)

Status: IN_PROGRESS (r8 stage 2 training 2026-10-22, stage-3 SadeedDiac eval auto-chained; VRR closure = WO81)
Goal: SadeedDiac DER < 2.0 (canonical 2.29), WikiNews multiref WER < 8
(news specialist 8.85). VRR reported.
Method: r8 noisy-student chain — synthesize with the canonical r7
teacher over large unlabeled MSA, filter by VRR-licensed consistency,
retrain with morph features (r6-morph teacher); register closure on
the news specialist; decode policy unchanged (greedy, first-alternates).
HF Jobs, --detach, --timeout 23h, step ckpts; ≤2 GPU budget shared
with B7.
Acceptance: gates green + external protocol reconciliation (B9).
