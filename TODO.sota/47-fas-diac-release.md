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
