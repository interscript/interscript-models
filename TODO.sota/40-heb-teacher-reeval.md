# WO40 — v3 teacher TRUE in-domain PER (fixed-eval re-measurement)

## Why

run-061's gate reported `ivrit_dev_per 0.8722` — later proven
seed-independent EVAL BUG (asr_phones ignored the records' 32000 Hz
sample rate → 2× time-warped decode; training-path resampling was
correct, so the CHECKPOINT is fine, only the number is garbage).
Seed-variance runs (run-061/061b) confirmed both engines were stable
measurements of a broken eval.

The true in-domain PER is the decisive number for WO36's next lever:
- **ivrit_dev_per_true < 0.35** → labels are decent; the STUDENT is
  the bottleneck → e12 (+8 epochs) verdict decides; label-filter arm
  (confidence/SNR) optional.
- **≥ 0.35** → labels are noise-limited → teacher v4 on the 500h
  slice (run-063, WO36 stage 3, gate PER < 0.25) is MANDATORY before
  any further student spend.

## Arm

run-040-teacher-reeval — `eval_heb_teacher_hf.py` on run-061/best:
ivrit dev 400 (last len//20 shards, pointed-convention gold, FIXED
resample) + FLEURS dev 300 (comparability with 0.2069/0.2055).
Cheap (CTC forward only, l4x1, ~30 min). RUNNING.

## Status

- 2026-10-14: v3 script's eval branch patched in bucket
  (run-061-ivrit-teacher-v3/) and local repo; eval launched.
  Prior buggy report kept in the verdict JSON for the record.

## Verdict (2026-10-14)

ivrit_dev_per_true **0.1382** / FLEURS 0.2059 — LOW branch fires:
student-bottleneck confirmed. Teacher v4@500h demoted to last resort.
