# WO64 — B3: Arabic to external SOTA (DER < 2.0, WikiNews < 8)

**Stage-2 verdict (2026-10-23, FINAL — both checkpoints measured): NEGATIVE.**
The r8 noisy-student continuation finished all 36,321 steps (loss
0.001-0.003) but scores **DER-CE 7.13 (oepoch-1) / 6.96 (oepoch-0)**
on the SadeedDiac-25 protocol (1,200 paragraphs, interscript-ml-tools
scoring) — worse than the v1 lineage (teacher 2.29, rung-2.0 4.82,
rung-2.1 4.57) and far off the < 2.0 target. The two checkpoints
scoring the same kills the overfit hypothesis: the continuation
simply did not inherit the teacher's quality — the oracle-relabeled
targets are the bottleneck (same lesson as the Thai arm: low train
loss is not evidence when the targets are). The r8 student line ships
NOTHING; its durable infrastructure (self-contained decode, bucket
sync, chain dispatch) is the salvage. B3's SOTA path: the v1 lineage
numbers + VRR (both published) + a data-quality lever on the oracle
targets if the chain is ever revisited — the r6-morph knowledge-
injection template, not noisy-student relabeling.

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
