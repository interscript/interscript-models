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


## Oracle-distill launch scoping (2026-10-29)

The WO39 chain is script-complete and ready to run: stage 1
`distill_oracle_hf.py` (300K QCRI rows, three arms, per-row oracle) and
stage 2 `continue_oracle_train_hf.py` (continue-train run-047/best 2 epochs,
SadeedDiac + WikiNews eval, gate first-alt WER < 3.5607, stretch <= 2.70).

Sole launch prerequisite: staging the three WO35 arm checkpoints
(run-047-large-strip/best — also the stage-2 init, run-040-strip-alt/best,
run-029-news-specialist/best) and the QCRI train_data mount onto HF storage.
Findings of the audit:

- The legacy Modal volumes (secryst-checkpoints et al.) list only
  thai/rababa-era artifacts — no run-047/040/029.
- rhtse/jobs-artifacts holds 78 timestamped job-sync dirs (r8 era) —
  candidate location, unverified.
- Recovery options if the checkpoints are gone: (a) the news specialist arm
  is SHIPPED (ara-diac-news-1.0/1.1) and the r7 canonical teacher is SHIPPED
  (ara-diac-2.0 lineage) — two of three arms restageable from pinned
  releases; (b) run-047-large-strip/best (the stage-2 init) may need a
  short re-derivation from its recorded recipe, or the stage-2 init moves
  to the closest recoverable ancestor — an owner-visible design decision
  recorded before any run.


### Archaeology CONCLUDED (2026-10-29): arms unrecoverable from buckets

The 78 timestamped job-sync dirs on rhtse/jobs-artifacts contain only script
copies (train_arabic_r8_hf.py et al.) — no checkpoints. The WO35 arm
checkpoints are unrecoverable from our storage. The launch decision is now
owner-visible, with two options:

- **Option A (restage + re-derive):** restage the two shipped arms
  (ara-diac-news-1.0/1.1, the r7 canonical lineage) from pinned releases;
  re-derive run-047-large-strip/best from its recorded recipe (a short
  continue-train of its own) — then run the WO39 chain as designed.
- **Option B (init substitution):** stage-2 continue-trains from the closest
  recoverable ancestor instead of run-047/best — cheaper but changes the
  gate lineage (the 3.5607 gate was measured ON run-047/best; a different
  init re-baselines the comparison).


### Option A scoping continued (2026-10-30)

With the owner unlock, Option A is the chosen path (faithful gate lineage).
Recipe audit: WO39 records run-047's CORPUS recipe exactly (MIX=qcri,
R8_GOLD=none, PSEUDO_CAP=900K, seed-7 article shuffle, WINDOW=600,
STRIP_ALT targets) — stage 1 is runnable once the arm checkpoints restage.
The large-strip TRAINING script itself is not in interscript-train (the
r-series scripts cover byt5/r3/r5/r6/r7/r8/r9/plane/raft); identifying or
reconstructing it is the remaining archaeology. The r7 lineage is fully
reproducible today (train_arabic_r7.py present). Execution order: (1)
restage p029 from the shipped ara-diac-news release; (2) re-derive
run-047-large-strip from the recovered recipe (the stage-2 init); (3)
re-derive or substitute p040; (4) run the WO39 chain. Steps 1-2 start next
session as the focused task.


### p047 recovery flickered; Option B is the executable path (2026-10-30)

A jobs-artifacts listing showed run-047-large-strip/export/ara-diac-news-1.2.zip
(821,320,781 B — exactly WO44's recorded size, dated 2026-10-12), but the
entry vanished from the listing minutes later and cp fails with not-found:
retention eviction or eventual consistency. One more listing probe is
worthwhile before declaring it gone.

**Option B concretized — fully executable from pinned releases, no
archaeology:** arms = {the shipped r7 lineage (ara-diac-2.0), the shipped
news specialist (ara-diac-news-1.0)}; init = the shipped r7 artifact. The
2-way oracle forfeits the p040/p047 complementarity and the gate
re-baselines (first-alt WER is measured against the r7 init's own
run), but every input is pinned and checksummed today. Recommend B, with
A opportunistically revisited if the bucket entry reappears.


### Storage verdict (2026-10-30): B3 is a re-train campaign

A full recursive dump of rhtse/jobs-artifacts (2,257 entries) contains ZERO
run-024 entries — the run-024-arabic-r8-* checkpoint dirs that appeared in
several listing greps earlier the same day have since vanished, as did the
p047 export. The bucket layer is lossy for the WO35/r8-era artifacts; no
launch can be built on restaging them.

**Definitive path (every input stable):** re-train the arms from the
recorded recipes against the staged corpus — `train_arabic_r7.py` is present
and the corpus is mounted from the Interscript/arabic-r8 dataset repo
(owner-approved license review 2026-10-18; also hosting SadeedDiac-25 and
the WikiNews-2024 multiref eval splits). Additionally documented corpus
options: qcri/advancing-arabic-diacritization (EMNLP 2025, CC BY-NC-SA —
refined datasets + the SadeedDiac-25 benchmark) and Misraj/Sadeed_Tashkeela
(gated, ~doubles the corpus). Cost: r7 re-train + 2-arm relabel +
continue-train ~= 2-3 GPU-days. The re-baselined gate (first-alt WER against
the re-trained init) is recorded before launch per the Option-B consequence.


### Option-B execution (2026-10-30): stage 1 built, parity-proven, smoke in flight

Stage 1 (`oracle_relabel_onnx.py`, interscript-train PR) decodes the two
surviving SHIPPED arms over run-047's exact corpus recipe (article shuffle
seed 7, row shuffle seed 42, WINDOW=600, slash-strip; full stripped corpus
= 290,575 rows, D_SUBSET covers it). Per-row oracle = arm pred with min
edit distance to corpus silver, ties -> r7.

Findings recorded:
- **Parity proof (local CPU, 3 equal-byte-length texts x 2 arms):** the
  length-bucketed zero-pad batched KV decode (ara-diac-2.0) matches the
  house runtime byte-exactly (6/6 after the plain fix). Plain-decoder
  exports (ara-diac-news-1.0) are BATCH=1-TRACED: batched plain decode
  silently corrupts (garbage logits/replacement chars) — this extends the
  WO51 finding from "padded batches corrupt unmasked encoders" to "plain
  decoder graphs are single-row exports; only the kv graph is batch-safe".
  The relabel plan therefore pins plain arms to single-row decode.
- **Batching payoff:** corpus byte-length distribution is tight (median
  38 B; ~91% batch occupancy at BS=48), so the KV arm batches ~48x.
- **Durability:** HfFileSystem API sync 401s from inside jobs (jobs token
  lacks bucket write scope); mount appends only flush reliably when files
  close. Per-arm raw preds therefore use rotating part files
  (parts-<arm>/part-NNN.jsonl every 2000 rows — the field-proven khm
  labeler pattern), resume by row-keyed dedup.
- **ORT-GPU pin:** latest onnxruntime-gpu (1.23) needs CUDA 13; the
  pytorch 2.5.1-cuda12.4-cudnn9 image gets onnxruntime-gpu==1.22.2.
- **Arms on record:** ara-diac-2.0 (r7 ByT5-base fp32 kv: DER 2.2864,
  WikiNews-2024 multiref WER 17.3794) vs ara-diac-news-1.0 (int8 plain:
  DER 5.5008, multiref WER 10.1262) — decorrelated exactly as Option B
  intended. Stage 2 trains a fresh google/byt5-base student on the oracle
  targets; gate re-baselined (RAW multiref WER < 17.3794; stretch <=
  10.1262; SadeedDiac DER within +0.1 of 2.2864).
