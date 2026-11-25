# WO93 — urd direct-gold arm: ByT5-small on the data-diacrit gold pairs (no distillation, no teacher)

Status: IN_PROGRESS — loader PR urdu-dev#27 (merge-on-green), then launch.
Goal: the SOTA-2027 push. run-096 shipped as **urd-vocalized-2.0** at
full-split raw CER **0.03641** (beating the champion 3.74% and the
0.0377 gate). This arm tests the standing hypothesis: **human-verified
gold labels beat distilled (teacher-relabel) labels on the same
corpus** — the run-066 base tier already hit 0.0357 on this exact data,
so a small tier trained directly on gold should at least match the
distilled student's number, with the cleanest possible lineage.

## Arm

**run-097-urd-diac-gold** — ByT5-small (init `google/byt5-small`, the
urd-diac-1.0 / urd-vocalized tier) trained DIRECTLY on the gold src/tgt
pairs. No teacher, no relabel, no distillation step.

### Data (verified 2026-11-25, all pins re-checked from the bucket)

- Training corpus: `rhtse/jobs-artifacts/rababa-urdu-cc174b96/data-diacrit/train.jsonl`
  (bucket `rhtse/jobs-artifacts/rababa-urdu-cc174b96`, mounted ro at
  `/data-replay` by the standard launcher) — **573,130 rows**,
  sha256 `95736b0d19e57ada3ce435f28300b8a72a3fec6c761dfce34770ed9549331ee2`
  (36,589,714 B). This is the sha-pinned source the run-066 lineage
  trained on (corpora/urd-dia.yaml `split: train`; owner license
  review 2026-10-18, explicitly NOT CLE).
- Eval split (WO37 protocol, never trained on):
  `data-diacrit/test.jsonl` — **11,940 rows**, sha256
  `6d822ae70a383e5547ee82e841a65e83fac81ae47ff320999b8e6b101b1790bb`.
- Both hashes re-verified by streaming sha256 over the BUCKET copies on
  2026-11-25 — exact matches to the corpus registry pins.
- Row format verified from the bucket: `{"src", "tgt"}`; tgt carries
  diacritics; parsed src is not JSON (the run-093 invariant holds on
  gold by construction, asserted at load time anyway).
- Privacy lineage of the trained model: `google/byt5-small` (raw Google
  checkpoint — no interscript ancestry, no CLE) + public-lineage gold
  only. Single hop, no CLE anywhere. The zero-overlap discriminator
  (#477: data-diacrit ∩ CLE = 0 src shingles, 0 tgt shingles at
  GUARD_N 8) covers this corpus's content directly.

### Loader delta (urdu-dev#27 — merged before launch)

The distill trainer assumed relabel-shard layout (`shard-*.jsonl` +
`manifest.json`) and cannot see the gold single-file corpus. Minimal
change (PR urdu-dev#27, branch `wo93-run097-direct-gold`):

- `DATA_GLOB` env (default `shard-*.jsonl` — run-094/095/096 unchanged);
  run-097 sets `train.jsonl`, so the WO37 eval split can never enter
  training (different root, explicit file selection);
- `CORPUS_RUN` env fallback records provenance in meta.json + verdict
  when no manifest exists (`data-diacrit-gold-95736b0d`);
- `load_pairs()` asserts the run-093 lesson at load time: JSON-looking
  parsed text aborts; median len(tgt)/len(src) within [0.5, 3.0] and
  degenerate share (ratio < 0.35) under 1% — violations abort BEFORE
  any GPU spend (same thresholds as relabel_teacher_hf.py v2);
- 7 regression pins (glob selection, eval-split exclusion, both
  invariants, gold-shaped pass, degenerate/runaway aborts).
- Full-scale pre-check on the sha-verified corpus: **573,130 pairs
  load, ratio_median 1.7, degenerate_share 0.0**.

### Recipe (run-094/096 verbatim otherwise)

3 epochs, bs 16 × accum 2 (32 effective), lr 3e-4 cosine (200 warmup),
bf16 autocast, MAXLEN 256, CKPT_EVERY 1000, cross-job resumable,
EVAL_N=0 final full-split eval (11,940 rows, WO37 raw-char CER) vs the
pre-registered bars. Steps = ceil(573,130 / 32) × 3 = **53,733**;
ETA ≈ 3.3 h stepping at run-096's measured 4.48 it/s + ~15–25 min eval
≈ **3.5–3.8 h** total.

## Gates (pre-registered)

Three bars, one number:

| bar | value | meaning |
|---|---|---|
| quality gate | CER ≤ **0.0377** | shipped-champion floor (urd-diac-1.0, WO37) |
| champion | **3.74%** | urd-vocalized-1.0 recorded full-split (SOTA condition: land below it) |
| shipped distilled | **0.03641** | run-096 / urd-vocalized-2.0 — the number to beat |

Verdict matrix:

- **CER < 0.03641 (beats the shipped distilled student)** → proceed to
  the calibrated Clause 16(e) matched-split gate (plan below) → report
  AUC + verdict verbatim → on PASS, ship recommendation to owner on the
  candidate version.
- **0.03641 ≤ CER ≤ 0.0377** → gate + champion PASS but does not beat
  run-096: record the result, NO 16(e) spend, owner decides whether
  the direct-gold lineage justifies a ship consideration anyway.
- **CER > 0.0377** → quality MISS: record the negative with the same
  care as a positive, STOP. No 16(e) spend.

Kill criteria: the matrix above is exhaustive; no partial launches.
If the (launched) 16(e) gate is NOT near chance on the matched-split
instrument, that is genuine incremental memorization → STOP, report
verbatim, escalate (escalation clause preserved from WO92).

## Calibrated Clause 16(e) gate plan (only if CER < 0.03641)

Same machinery as run-096's PASSING gate (the amended methodology,
urdu-dev#23/#24/#25/#26):

- config `run-097-vocalized-calibrated-matchedsplit.json` on a gate
  branch: candidate `run-097-urd-diac-gold/<final-step>/model`,
  reference **`/ckpt/run-066-urd-diac-base/best`** via
  `GATE_REFERENCE_PATH` (domain-matched per the amendment; run-066 is
  verified CLE-clean per the #471 STEP-0 lineage trace), same_population
  split, holdout shards disjoint from held-in shards, length parity
  enforced (violations raise; the probe returns FAIL rather than run
  confounded).
- Pre-registered thresholds: reference self-control EXACTLY 0.5,
  calibrated AUC tolerance ±0.05, success-rate 0.6, verbatim floor
  25 words (Clause 18(d)), WordNet vocab scan, extraction 0 violations.
- Expected outcome: AUC near chance — a model whose entire lineage is
  google/byt5-small + zero-overlap public-lineage gold cannot carry
  CLE memorization beyond the domain-specialization residual the
  matched split corrects for.
- Records bucket `rhtse/urdu-16e-gate/urdu-16e-run-097-vocalized-
  calibrated-matchedsplit`, retention 2 years post-run.

## Version candidate (recorded delegation — not picked by the agent)

Candidate ship name: **`urd-vocalized-2.1`** (WO87 canonical form; the
vocalized target tag is decode-evidence-established for this task line;
major.minor increments from the shipped urd-vocalized-2.0). Recorded
per the standing delegation of record (verbatim, from the merged
urdu-dev#23 record, re-affirmed by the owner's work-order instruction
stating the candidate explicitly):

- "Fully approve all, use reasonable recommendations" (2026-11-21)
- "Continue all and make SOTA 2027... finally launch" (2026-11-22)

The actual ship remains gated on the full publish chain (quality →
16(e) matched-split PASS → parity ≥ 500 shipped-mode samples →
conformance fixtures → license strings → Schedule D → certificate →
owner-stated version at ship time). sha256/urls are never pre-staged.

## Jobs

HF Jobs only, one big-GPU job at a time (a100 lane verified free
2026-11-25 — the four running jobs are all a10g-large):

| job | purpose | config |
|---|---|---|
| `run-097-urd-diac-gold` (env `student-run097.env`) | ByT5-small direct-gold training + full-split eval | a100-large, `--detach`, 24 h timeout, `--attempts 2`, mounts = launcher defaults (`/ckpt` rw isx-training, `/data-replay` ro rababa-urdu-cc174b96) |

Launch (after urdu-dev#27 merges):
`training/teacher_distill/launch.sh train_student_distill_hf.py student-run097.env a100-large`.
First-checkpoint cadence: step-1000 at ~4.4 it/s ≈ 4 min after stepping
starts. Monitor: single 10-min-poll terminal monitor (until-loop);
progress via `hf jobs ps --all` — never interactive log tailing.
Aggregate-only logging (Clause 19): corpus text never printed.

## Compliance map

- Training data: public-lineage gold only (license review 2026-10-18,
  ship-with-dependency-note per corpora/urd-dia.yaml `license_review`);
  no CLE exposure anywhere in the lineage (init = raw Google ckpt,
  corpus = zero-overlap gold, verified above).
- No LLM anywhere near the labels (registry law) — labels are the
  human-verified corpus itself, never generated.
- Checkpoints land in the access-controlled training bucket
  (`Interscript/isx-training`, private) and are never a release
  channel; the release candidate is the exported artifact after the
  full ship gates.
- The weights-dependency note from the corpus license review carries
  into any ship record (Schedule D note + card), same as urd-vocalized-2.0.

## Cost

≈ 3.5–3.8 GPU-h on a100 (single job) + ~2 h l4x1 if the 16(e) gate runs.
