# WO36 — ivrit.ai scale: the ReNikud-class Hebrew g2p run

Owner approved the scale decision (2026-10-11). The $500 is NOT a
purchase: ivrit-ai/audio-v2 is free under its license (gated on
terms acceptance); the $500 is our own labeling compute at the WO09
measured rate ($0.28/audio-hour × ~1,700h ≈ $476), spent through
normal HF jobs credits.

## Access (OWNER, one click)

Visit https://huggingface.co/datasets/ivrit-ai/audio-v2 logged in as
rhtse (or the org account preferred for data licensing) and accept
the terms — gated=auto grants immediately. Corpus: ~64K files,
10K<n<100K category, license "other" (their terms), paper
arxiv:2307.08720. Companion: ivrit-ai/audio-transcripts if v2 ships
audio-only segments.

## Reality check after access (2026-10-11)

audio-v2 = **>20,000 hours** (not 1,700 — the corpus grew), raw
episode-length m4a/mp3 by source. Companions are SEPARATELY gated and
needed for pairing: audio-vad (segment boundaries), audio-transcripts,
crowd-transcribe-v5 (verified transcripts), audio-labeled (pre-paired
segments?) — OWNER: accept terms on each (one click per repo).
License: ivrit.ai v1 — broad research + commercial use; we ship only
derived models, never audio.

STANDING RULE (owner, 2026-10-11): the corpus NEVER downloads to the
laptop — everything mounts/streams in HF jobs with the gated token.

## Pipeline (every stage proven this week in WO31)

1. **Audit** (in-job, cpu): mount/stream the repos, count real
   hours, inspect schemas, 50-transcript QC — NO copying of audio;
   pair via the companions' segment indices.
2. **Point** (in-job): transcripts → nikud via our crown
   (heb-diac-plane-2.0, DER 8.18) — the WO31 convention fix; artifact
   zip fetched into the job, pointed text written to the bucket.
3. **Teacher at scale**: fine-tune the espeak-cv-ft CTC on
   pointed-espeak targets over a 300-500h slice first (gate: PER
   < 0.25, ~10 GPU-h); scale only if the gate demands it — data is no
   longer the constraint, compute budget is the dial (20K hours
   available).
4. **Label**: run the tuned teacher over all audio (audio-derived
   vowel-full labels; ~$0.28/audio-hour ≈ the $500).
5. **Student at scale**: byt5-BASE (the capacity verdict was for 3.2K
   pairs; at 50-100× data base is the right size) on text→IPA.
6. **Gate**: normalized CER < 0.2393 (rules layer) — ship decision;
   stretch ladder: Nakdimon 0.1102 · phonikud 0.0495 · ReNikud
   0.0244. Same normalized-CER discipline as WO31.

## Stage gates and abort points

- After (1): report actual hours + a 50-utterance spot-check of
  transcript quality before any GPU spend.
- After (3): teacher PER gate (< 0.25 expected; if not improved over
  0.319, stop and diagnose before labeling).
- After (5): if the gate misses at 10× data, the diagnosis is student
  capacity/data quality, not pipeline — one iteration, then park.

## Execution manifest (run-level, 2026-10-11)

- run-048 DONE: audit — v2 raw 1.21TB (>20K h); companions are
  self-contained pairs: crowd-transcribe-v5 ~165K rows, audio-labeled
  ~87K rows (schema: uuid + audio bytes + verified text).
- run-049 DONE/RUNNING: pointing — ~250K transcripts through the
  crown nikud model, 8-way in-job; output pairs-pointed.jsonl.
- run-050: **webdataset builder** — stream both pair-repos, decode
  embedded audio to 16-bit WAV (native sr, recorded), pair by uuid
  with pointed text, tar-shard ~500MB each into
  run-050-ivrit-wds/, CAP_HOURS slice (default 200h) with real
  decoded-duration stats; deterministic shard order (extend by
  raising the cap). Filter: 1s <= dur <= 30s.
- run-051: **teacher v2** — espeak-cv-ft CTC fine-tune on the slice
  (pointed-espeak targets, tokenizer he backend), gates: FLEURS dev
  PER < 0.25 AND ivrit-heldout PER reported. fp32 features, bf16
  autocast, step-ckpts, 12h timeout.
- run-052 (IMPLEMENTED + uploaded, combines 052+053): resumable
  labeler (teacher decodes the slice → labels.jsonl, LABEL_DONE
  checkpoint) + byt5-BASE student (byte-correct collate) + normalized
  CER gate in-job; ladder: Nakdimon 0.1102 · phonikud 0.0495 ·
  ReNikud 0.0244. Full chain now executable end-to-end.
- GPU budget: stages 3+4 ≈ 12-20 GPU-h total (teacher slice is the
  dial); well under the $500 envelope.

## Alternative noted

micsell/hebrew_speech_{campus,kan}_nikud — Hebrew speech with GOLD
nikud annotations (would upgrade stage 2 from model-pointed to gold-
pointed). Secondary; check availability while awaiting audio-v2
access.
