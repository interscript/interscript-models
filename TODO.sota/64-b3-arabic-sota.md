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
