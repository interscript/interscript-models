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

## WO20u M1 — multi-seed confirmation — PRE-REGISTRATION

Status: PRE-REGISTERED (2026-11-17, before the seed-2/3 GPU spend).
Branch `wo20u-m1-m2` (interscript-models + interscript-train). The
single-seed caveat on the −0.4385pp separated-improvement is the
ledger's known blind axis (per arXiv 2608.27729, single-seed KD gains
below ~5pp are unresolvable); this run measures it.

### The judgment (fixed before launch)

**The bridge lever CONFIRMS iff ≥ 2 of 3 seeds show
separated-improvement vs G2a with non-overlapping CIs.** Operational:

- per seed: paired bootstrap delta (seed − G2a) on the full
  1,200-paragraph SadeedDiac-25, count-weighted, documents =
  resampling unit, 10k resamples, seed 7 — the identical math the
  seed-1 verdict used;
- a seed "shows separated-improvement" iff its CI95 upper bound is
  below zero (the interval excludes zero on the improvement side);
- "non-overlapping CIs" is the interval-vs-zero test above — the
  pre-registered bar; cross-seed interval agreement is reported
  alongside but is NOT the gate;
- 2-of-3 or 3-of-3 → CONFIRMED; 1-of-3 or 0-of-3 → NOT CONFIRMED
  (the single-seed result is downgraded to an unreplicated
  observation; recorded either way, no rescue runs).

### The arms (identical recipe, different draws)

- Same scan (`wo20-tiny-scan` bridges.npz + scan.json, ARMED,
  rank-256, pairs L0→L0 L1→L0 L2→L2 L3→L2 L4→L2), same bridge
  config (β 0.1 frozen MSE), same base recipe (the 2.0 rung
  verbatim: Muon 0.01 + AdamW 1e-4, sequence KD α 0.5 T 2.0, BS 8,
  3 epochs, canonical r7 labels sha `e70ce991…`, 10,995 steps),
  same eval epilogue + gate.
- Seed 2: `WO20_SEED=2`, run dir `wo20-tiny-g2w-s2`; Seed 3:
  `WO20_SEED=3`, run dir `wo20-tiny-g2w-s3` (explicit
  torch/numpy/python/DataLoader seeding — the trainer gained the
  `WO20_SEED` knob for this; seed 1 ran unseeded and is recorded as
  an uncontrolled draw, not re-run).
- Comparison baseline for every seed: G2a released predictions
  (`frontier-predictions-v1` / `run-007-r7-muon-6ep-final_preds.jsonl`,
  sha `f6f60619…` verified in-job), scored by the confirmation scorer
  (`wo20_seed_confirm.py`) under the identical evaluator, word-count
  mismatches skipped pairwise. Calibration: the scorer is first run
  on the seed-1 banked preds and must reproduce ≈ −0.4385pp
  CI [−0.6463, −0.2767] before the seed-2/3 numbers are read.

### Infra

HF Jobs only (`--detach`, `--timeout 4h`, 500-step labels.sha-pinned
checkpoints + auto-resume, retry loops, ≤ 2 concurrent big-GPU apps,
SadeedDiac-25 parquet from the `Interscript/arabic-r8` mount). No
corpora on the laptop. Verdict recorded in docs/RESULTS.md either way.

### Result

**CONFIRMED — 3 of 3 seeds (2026-11-18; full entry in
docs/RESULTS.md).** The scorer's seed-1 calibration reproduced the
published seed-1 verdict exactly (−0.4385pp CI [−0.6463, −0.2767]
p=0, aggregates 4.0545/4.493 to the fourth decimal), then:

- seed 2: Δ vs G2a **−0.3806pp, CI95 [−0.5876, −0.2168], p=0** —
  separated (full-set DER-CE 4.0882)
- seed 3: Δ vs G2a **−0.4140pp, CI95 [−0.6173, −0.2532], p=0** —
  separated (full-set DER-CE 4.0397)

Every seed's CI is entirely below zero and the three agree in
magnitude (−0.38 to −0.44pp) — the pre-registered ≥2-of-3 bar is met
by all three. Scan-first frozen bridges stand as the first
REPRODUCED separated-positive student-side lever on record (~−0.4pp
vs G2a at half its epochs). The strict teacher+0.5pp gate remains
FAILED for every seed (teacher reproductions 2.2231 / 2.2039),
unchanged. Provenance: `isx-training:/wo20u-m1/*.confirm.json` +
per-run final_eval.json; G2a preds sha `f6f60619…` verified in-job.
Infra lessons recorded with the ledger entry (epilogue pairwise-skip
fix, final_eval ×100 aggregate scale fix, wedged orchestrator
threads — both seeds crossed four 4h windows on checkpoint resume
exactly as designed).

## WO20u M1-6ep — the full-length bridge arm vs G2a — PRE-REGISTRATION

Status: PRE-REGISTERED (2026-11-18, before any GPU spend of this arm).
Branch `wo20u-6ep` (interscript-models + interscript-train). The
confirmed-at-half-epochs lever (M1: −0.38..−0.44pp separated vs G2a,
3-of-3 seeds at 3 epochs vs G2a's 6) meets its full budget.

### Hypothesis (single variable: epochs 3 -> 6)

The bridge lever's separated improvement over G2a is not a
short-training artifact: with G2a's full budget under the identical
recipe + bridges, the student's frontier move holds or grows. If the
gain was carried by under-trained-baseline slack, it vanishes — that
is the drop verdict, recorded plainly.

### The arm

- Teacher r7 (`run-007-news`, release `teachers-arabic-v1`, per-part
  sha256 verified in-job); student `google/byt5-small`.
- The confirmed bridge arm verbatim (Muon 0.01 + AdamW 1e-4 hybrid,
  sequence KD α 0.5 T 2.0, BS 8, β 0.1 FROZEN rank-256 bridges at the
  `wo20-tiny-scan` pairs L0→L0 L1→L0 L2→L2 L3→L2 L4→L2, canonical r7
  labels sha `e70ce991…`) at **WO20_EPOCHS=6** (29,322 pairs → 21,990
  steps), `WO20_SEED=2` (explicit, recorded), run dir
  `wo20-tiny-g2w-6ep`. Same data plane (arabic-r8 mount + GH-release
  digests); the scan is NOT re-run (frozen provenance).

### Primary metric + gate (fixed before launch)

- Primary: full-set DER-CE (1,200-paragraph SadeedDiac-25, windowed
  zero-skip, identical evaluator, both surfaces in-job).
- **The arm CONFIRMS-AT-FULL-BUDGET iff paired Δ vs G2a
  (count-weighted bootstrap, documents = resampling unit, 10k,
  seed 7, word-count mismatches skipped pairwise) has CI95 entirely
  below zero** — the same separated-improvement bar as the 3-seed
  round, via the same validated scorer (`wo20_seed_confirm.py`;
  its calibration already reproduced the published seed-1 verdict to
  the fourth decimal, no recalibration required). Confirm marker:
  `isx-training:/wo20u-m1-6ep/wo20-tiny-g2w-6ep.confirm.json`.
- Secondary (explicit statement required in the report): the strict
  teacher+0.5pp gate (2.7864 vs the published teacher 2.2864; in-run
  reproduction expected ~2.2–2.3). Only a real crossing changes the
  SOTA claim; failure is recorded as the standing pattern.
- Negative = no separation → recorded plainly as the negative verdict
  and CLOSES the 6-epoch direction (drop) with an evidence-based
  answer.
- Trajectory: the per-checkpoint training-loss trajectory (500-step
  labels.sha-pinned saves) from the run logs, reported with the
  verdict. Any mid-checkpoint DER diagnostic is declared NON-GATED
  before it runs and never substitutes for the full-set verdict.

### Seed caveat

This is a single explicit seed (2). The multi-seed replication was
done at the 3-epoch rung; the full-budget read inherits the ledger's
single-seed caveat discipline and is labelled as such in the report.

### Infra

Smoke job FIRST (cpu: release + labels digest verification, bridges +
scan load, label-pair count — validates mounts/clone/data before GPU),
then a100-large `--detach` `--timeout 4h` `--attempts 3`, 500-step
labels.sha-pinned checkpoints + auto-resume, `hf jobs ps` before
launch, ≤ 2 concurrent big-GPU apps account-wide. No corpora on the
laptop. Verdict lands in docs/RESULTS.md either way.

### Result

**CONFIRMED AT FULL BUDGET — separated, effect ~doubled (2026-11-19;**
full entry in docs/RESULTS.md**).** Paired Δ vs G2a **−0.7440pp,
CI95 [−0.9448, −0.5884], p = 0.0** (n 1,170 scorable pairs, 32
pairwise skips; G2a re-scored 4.5156 on the shared set). Full-set
DER-CE **3.7260** (3ep arm: 4.0545–4.0882; G2a 4.5701 published /
4.4929 re-scored) — doubling the bridge arm's own budget took −0.35pp
and the G2a gap from −0.38pp (3ep, seed 2) to **−0.74pp**. The
pre-registered bar (CI95 entirely below zero) is met. The strict
teacher+0.5pp gate (2.7082 vs teacher in-run 2.2082, Δ +1.52pp
[1.39, 1.65] p=1.0) stays **FAILED** — no crossing; the r7
teacher-tier SOTA claim is untouched. Single explicit seed (2) as
labelled. Provenance:
`isx-training:/wo20u-m1-6ep/wo20-tiny-g2w-6ep.confirm.json`,
`wo20-tiny-g2w-6ep/final_eval.json` + banked preds; trajectory loss
0.341@8.5k → 0.289@21.95k across three 4h windows (resume-continuous
loss values).
