# WO64 — B3: Arabic to external SOTA (DER < 2.0, WikiNews < 8)

Status: IN_PROGRESS (stage 1 running 2026-10-21)
Stage 1 (synthesis): job rhtse/6ad82b055275124786e1feed — canonical
teacher (p047 = run-047 = ara-diac-2.0 lineage) decoding the run-047
corpus recipe, 290,575 stripped rows; script r8_noisy_student_hf.py on
the training/wo31-wo36-campaign-scripts branch (#135/#136, self-
contained durable decode). Stage 2: retrain on noisy-targets.jsonl.
Goal: SadeedDiac DER < 2.0 (canonical 2.29), WikiNews multiref WER < 8
(news specialist 8.85). VRR reported.
Method: r8 noisy-student chain — synthesize with the canonical r7
teacher over large unlabeled MSA, filter by VRR-licensed consistency,
retrain with morph features (r6-morph teacher); register closure on
the news specialist; decode policy unchanged (greedy, first-alternates).
HF Jobs, --detach, --timeout 23h, step ckpts; ≤2 GPU budget shared
with B7.
Acceptance: gates green + external protocol reconciliation (B9).
