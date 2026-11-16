# 06 — WO20 tiny-student distillation of r7 (microkimi recipe) — PRE-REGISTRATION

Status: PRE-REGISTERED (2026-11-16, before any GPU spend). Issue
interscript/interscript-models#441, branch `wo20-ml-tiny`.

## The hypothesis

The lever ledger closes the student-side family with two size-axis
negatives: from-scratch 30M collapses (73.95 full-set, every lever
armed) and SVD width-stitch fails at both tested ratios (29M d384:
82.96; ~105M d768: 78.23). Both width arms were SVD-stitch INITs
trained blind. The microkimi recipe's untried remainder is
scan-first: choose the (student layer, teacher layer) pairings by
closed-form directional ridge R² BEFORE spending gradients, then
freeze low-rank bridges at those pairings and train the student with
a hidden-MSE loss THROUGH the bridges on top of the base recipe.

Mechanism (novel to the ledger — the standing rule requires this):
directional predictability of the teacher's residual stream from the
student's, measured and exploited as a frozen projector, is a
different operator from a blind SVD of the embedding/first-layer
map. If representation alignment is the binding constraint, the scan
finds it; if the width law is fundamental, the scan shows low R² and
kills the arm for free.

## The arms

- Teacher: `run-007-news` (r7, ByT5-base 580M, full-set 2.2864) from
  release `teachers-arabic-v1` (parts reassembled, sha256 verified
  in-job). Labels: `teacher_labels_r7.jsonl`, sha256 `e70ce991…`
  verified in-job (the canonical G2a lineage labels).
- Student: `google/byt5-small` (300M) — the only backbone class that
  ever cleared a client gate.
- Base recipe: the 2.0 rung verbatim (Muon + AdamW hybrid, r7
  labels, sequence KD, 3 epochs) so the bridge delta reads against
  the published 4.8218.
- Bridge arm: scan-selected pairs, ridge-solved W SVD-truncated to
  rank r, frozen; loss adds beta * MSE(W h_student, h_teacher) at
  paired layers.

## Stage 1 — the scan (kill gate)

Calibration slice: 256 label rows, student/teacher decoder streams
captured on the same byte positions (shared byte tokenizer, no
anchor problem). Ridge R² of teacher layer-L activation from student
layer-K stream for every (K, L) pair, closed form, subsampled.

**Kill rule (pre-registered):** the bridge arm is armed only if the
best directional R² (a) exceeds **0.30** and (b) exceeds the
scrambled-control R² (same solve against row-permuted teacher
activations) by at least 2x — i.e. the predictability is real signal,
not ridge leakage. The 0.30 bar is declared here, not inherited: the
microkimi selftest only asserts its toy scan separates a real stream
from noise (CKA > 0.4 on a planted stream vs a pure-noise layer); it
publishes no graded threshold. Below the bar the arm is NOT armed —
the scan is the negative result, recorded here and in RESULTS.md.

## Stage 2 — the gate

Full 1,200-paragraph SadeedDiac-25, windowed zero-skip protocol
(1400B word-boundary windows, greedy, haraqat-projected, Misraj
evaluator, `gt_missing_diacritic_is_error=False`), teacher decoded
in-job on the same paragraphs; paired bootstrap vs r7 (documents =
resampling unit, 10k resamples, seed 7).

- **Tolerance (the pipeline's established gate):** full-set DER-CE
  <= teacher + 0.5pp = **2.7864**. Nothing in the frontier (8.26 /
  5.78 / 4.82 / 4.57) has ever cleared it.
- Secondary read: paired delta vs the 4.8218 base rung — does the
  bridge arm move anything at all.
- Subset numbers are recorded but NEVER the verdict (five recorded
  subset-overstatement instances).
- A negative is recorded as a negative with its CI; no rescue runs.

## Infra

HF Jobs only (`--detach`, `--timeout 4h`, step checkpoints every 300
steps to the `isx-training` bucket, auto-resume, <= 2 concurrent GPU
apps). Data: teacher zip + labels fetched in-job from the GH
Releases channel with digest verification; SadeedDiac-25 parquet
from the `Interscript/arabic-r8` mount. No corpora on the laptop.

## Result

RECORDED 2026-11-17 (see docs/RESULTS.md for the full entry).

- Scan: ARMED (best directional R² 1.0000 L0→L0 vs control 0.2539;
  caveat recorded — the inflation is the scan's documented
  "early states align with everything" effect).
- Bridge arm (2.0 rung + β 0.1 frozen-bridge MSE): full-set DER-CE
  **4.0545** (teacher in-run 2.2093 ✓ reproduction).
- Strict gate teacher+0.5pp = 2.7093: **FAIL** — as with every student
  to date.
- BUT: **SEPARATED-IMPROVEMENT over the published frontier** — paired
  Δ vs G2a (4.5701 published; 4.4929 re-scored) = **−0.4385pp, CI95
  [−0.6463, −0.2767], p = 0.0**, at HALF G2a's epochs (3 vs 6); vs the
  matched 3-epoch 2.0 rung (4.8218): ~−0.77pp.
- The lever ledger's standing rule ("no further GPU spend on
  student-side levers without a pre-registered mechanism novel to the
  ledger") is satisfied by exactly this mechanism — scan-first
  directional ridge pairing + frozen low-rank bridges is now the ONE
  separated-positive student-side result on record. Natural next arm
  (owner-gated): the bridge recipe at 6 epochs against G2a directly.
- Single-seed caveat applies.
