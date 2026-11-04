# Urdu WO65 — stage 1 + 2

## STAGE 1 COMPLETE (2026-11-03): oracle CER 2.62 vs arms 3.4 / 8.66

run-088-urd-oracle executed 2026-11-02/03. Arms: urd1 =
urd-diac-1.0-fp32.zip (sha c299ea44…, ~20 min at 183 rows/s) and urd2
= urd-diac-base-1.0-fp16.zip (sha 6818469c…, ~3h at 18 rows/s), over
data-diacrit/train.jsonl (573K rows; 486,444 usable after the ≥5-char
and ≤300-byte filters; subset 200,000, seed 42).

Consolidation (job 6ae91046c78863f9c6310f25): 137,270/200,000 rows
were exact ties under urd1 (arm2 skipped); urd2 decoded the remaining
62,730. relabel stats: `{"rows": 200000, "disagreement": 0.1045,
"arm_cer": {"urd1": 0.034, "urd2": 0.0866}, "arm_eval_rows": {"urd1":
200000, "urd2": 62730}, "oracle_cer": 0.0262, "picks": {"urd1":
183451, "urd2": 16549}}` — the oracle beats the better arm 3.4 → 2.62
(a 23% relative gain; urd2 contributes 16,549 picked rows).

Launch notes (durable): the `@revision` bucket-mount tag resolves
EMPTY — mount the plain directory path and point D_ROWS_JSONL at
rababa-urdu-cc174b96/data-diacrit/train.jsonl inside it. A
D_ARM_ONLY primary job exits without consolidating; run one final
consolidation-only job (no D_ARM_ONLY) after the second arm lands.

## STAGE 2 RUNNING (2026-11-03)

train_oracle_student_hf.py, O_RUN=run-088-urd-oracle, O_EPOCHS=3,
google/byt5-base (job 6ae933d7c78863f9c6312b44, a100, 24h). The
script gained an O_EVAL_JSONL epilogue (greedy CER on a {src,tgt}
jsonl) for non-Arabic oracle runs — train
PR interscript-train feat/urd-oracle-eval-jsonl; eval set =
data-diacrit/val.jsonl.

GATE: student CER < 3.57 (urd-vocalized-1.0 baseline); target < 3.
On gate green: export IMF artifact + parity (≥500 single-row greedy)
+ certify — the VERSION IS THE OWNER'S. Parts contract and publish
gates per README; never LLM teachers for the labels (the oracle is
the shipped arms).

STAGE 2 RESULT (2026-11-04): MISSED. run-088 student (google/byt5-base,
3 epochs, 37.5K steps, oracle-targets 200K x 300B): final-checkpoint
greedy CER 4.0765 on the 1200-row val subset (protocol: O_EVAL_JSONL,
row-mean, batch 32, bf16, window 600). Epoch sweep: oepoch-0 4.8905,
oepoch-1 4.2430, oepoch-2 4.0765 — monotonically improving, no
overfitting; the gate CER < 3.57 is met by NO checkpoint (target < 3
likewise). All three epoch checkpoints are durable in
rhtse/run-088-urd-oracle (uploaded in-job via the HF_TOKEN secret —
the run-1 failure mode was the read-only /ckpt repo mount, fixed by
mounting at /targets + a local writable ckpt dir).

OWNER OPTIONS (recorded, not pursued): (a) longer schedule — the
curve is still descending at 3 epochs; (b) ByT5-large backbone;
(c) data-side levers per the standing no-RL/no-LLM-teacher laws.
Infra note: stage-2 evals now have a standalone sweep harness
(interscript-train eval_oracle_student.py, E_CKPTS/E_EVAL_JSONL).
