# WO64 — B3: Arabic to external SOTA (DER < 2.0, WikiNews < 8)

**Stage-2 verdict (2026-10-22, INTERIM — oepoch-0 control pending):**
the r8 noisy-student continuation finished all 36,321 steps (loss
0.001-0.003) but scores **DER-CE 7.13** on the SadeedDiac-25 protocol
(1,200 paragraphs, interscript-ml-tools scoring) — worse than the v1
lineage (teacher 2.29, rung-2.0 4.82, rung-2.1 4.57) and far off the
< 2.0 target. Suspected cause: the continuation overfit the
oracle-relabeled targets (suspiciously low train loss + eval
regression). oepoch-0 (end of continuation-epoch 1) eval queued as the
control; the r8 student line ships NOTHING at this number.

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
