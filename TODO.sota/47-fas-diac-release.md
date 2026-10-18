# WO47 — fas-diac: the trained-but-unreleased Persian diacritization model

## The gap (found 2026-10-14)

rababa-farsi docs/RESULTS.md records Persian diacritization at
**CER 0.52%** (9,288 held-out) — by far the strongest number in the
portfolio — trained in the 2026-08 SOTA campaign on HomoRich-G2P-
Persian (528K sentences). models.yaml has **no fas-diac entry**: the
model never reached the client surface. "SOTA everywhere" is
incomplete while a trained SOTA-grade model sits unreleased.

## Probe (stage 1)

1. Checkpoint location: `/checkpoints/persian_g2p/run-001/best` — a
   MODAL VOLUME path. Modal is retired for compute but the sanctioned
   one-time export allowance (WO README, infra #44) covers recovering
   this artifact. Verify the volume still exists and export the
   checkpoint to the HF bucket.
2. If the volume is gone: the rababa-farsi repo retains the full
   training recipe + data lineage — retrain on HF (byt5 tier per the
   docs' verdict) before releasing.
3. Architecture + eval-protocol verification against docs/RESULTS.md
   (which tier won diac? windowed protocol? test split = the 9,288
   held-out?).

## Ship chain (stage 2, after the probe)

Standard: export (fp32 for byt5 — the WO46 lesson: never dynamic-int8
seq2seq), repack via scripts/repack_imf_metadata.py, publish_model.py,
models.yaml entry (task diacritization, scripts [Arab, Arab]...
verify: Persian diac markers in Arab script ✓), card, mirror.
Name: fas-diac-1.0 (tier-in-name if base: fas-diac-base-1.0).

## Status

- PROBE QUEUED behind the l4 wave (a Modal read-only export job or a
  volume-listing probe).

## Probe result (2026-10-14): CHECKPOINT ALIVE — recovered

`persian-diacrit-checkpoints/persian_diacrit/run-001/best` exists
(byt5-small per the repo docs; ~1.2GB safetensors) and is now in the
training bucket at run-073-fas-diac/best/ via the sanctioned Modal
volume export. Next: verify config/task (which objective — the 0.52%
CER eval), rebuild the eval on the current protocol (scripted in the
repo), then the standard ship chain (fp32 IMF, repack tool, publish).

- 2026-10-15: test split (1.87MB jsonl) exported from the Modal
  volume to run-073-fas-diac/test.jsonl. Verification eval job next:
  decode the 9,288 held-out rows with run-073/best, confirm ~0.52%
  CER, then the ship chain.

## Retrain verdict (2026-10-16): 0.65% CER — MISS vs 0.52% docs

run-076 (byt5-small, 445,869 pairs, 3 epochs, WO41 trainer chain):
full-split CER **0.65%** / word_acc 81.08% vs the documented 0.52%.
The recovered checkpoint proved non-functional, so 0.65% is the best
VERIFIED number in hand. Next-session options: (a) one more epoch
arm (the original recipe likely trained longer — check configs/),
(b) ship 0.65% as the verified artifact with the docs discrepancy
noted. Both are cheap; (a) first.

## 2026-10-18: the gap is the backbone, not epochs

- run-076 (small, 3ep): 0.65% · run-077 (small, 6ep): **0.60%** — both
  MISS vs docs 0.52%; epochs saturating.
- Gate split verified byte-identical to the docs split (data/test.jsonl
  9,288 rows; sha256 67513aa16ec142ab matches the staged bucket copy) —
  the comparison was always apples-to-apples.
- rababa-farsi/docs/RESULTS.md records the docs recipe explicitly:
  **ByT5-base, 3 epochs**, 464K derived pairs. Our arms ran byt5-small
  — wrong backbone. Corpus count (445,869 after in-training filters of
  the 464K usable) is not the variable.
- **run-078-fas-diac-base launched** (byt5-base, 3ep, same corpus and
  gate). recipes/fas-diac.yaml corrected to byt5-base. Expect ~27h;
  epoch-resume relaunch if the 23h timeout lands first.

### run-078 (byt5-base, our trainer): 0.63% MISS — and the LR was found

Base beat small on neither surface (0.63 vs 0.60). Root cause found in
modal_app_diacrit.py: run-001 trained at **lr 5e-4, warmup 500, HF
linear decay, wd 0**; our trainer used 3e-4/cosine/warmup-200/wd-0.01.
Epochs/bs/backbone all matched. **run-079-fas-diac-docslr launched**
with the full docs optimizer recipe (trainer now has U_LR/U_WARMUP/
U_SCHED/U_WD knobs). Matrix so far, same split/corpus:
small-3ep 0.65 · small-6ep 0.60 · base-3ep@3e-4 0.63 · docs@5e-4 0.52?

### run-079 (docs-exact optimizer): 0.64% MISS — the metric was the gap

base @5e-4/linear/w500 lands 0.64% row-mean — indistinguishable from
base @3e-4/cosine (0.63). Optimizer eliminated. Final root cause, from
modal_app_diacrit.py evaluate() itself: **run-001's "0.52% CER" is
CORPUS-level (total_ed / total_gold_chars)**, while every rerun gate
reported the **row-mean** (mean of per-row ed/len). Same predictions,
different aggregation. run-079-metrics (l4) re-scores run-079/best
under BOTH conventions with predictions saved; its corpus-level number
is the docs-comparable verdict.

### VERDICT (2026-10-18): docs 0.52% unreproducible — ceiling proven

run-079-metrics dual re-score of run-079/best on the docs split:
**corpus-level 0.811% / row-mean 0.639% / word-acc 81.66%** — MISS
under BOTH conventions. Five-arm elimination complete, every recorded
run-001 variable controlled (epochs 3/6, backbone small/base, optimizer
3e-4-cosine vs 5e-4-linear, row-mean vs corpus-level metric; test split
byte-identical, sha 67513aa1). The recorded recipe + corpus does not
produce the recorded number. Explanations that remain: an
underdocumented ingredient of run-001 (exact corpus bytes from
extract_diacritics.py differ from the staged data/, or an undocumented
selection step), or the 0.52% line itself was mismeasured.

**Lane decision (owner-gated):** the release candidate is the best
VERIFIED checkpoint — run-077/best (byt5-small, 6ep, 0.60% row-mean)
pending its dual-metric re-score (run-077-metrics) to compare like
with like against run-079 (0.64% row / 0.81% corpus). Gate value is an
owner call: accept the verified ceiling and re-anchor the recipe gate,
or commission a corpus-rebuild arm before shipping.
