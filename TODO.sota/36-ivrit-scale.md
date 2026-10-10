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

## Pipeline (every stage proven this week in WO31)

1. **Ingest**: download audio-v2 + transcripts to the HF dataset
   repo `Interscript/ivrit-v2` (resumable, sample-audio verified,
   total-hours counted).
2. **Point**: transcripts → nikud via our crown (heb-diac-plane-2.0,
   DER 8.18) — the WO31 convention fix. Local/batch, free.
3. **Teacher at scale**: fine-tune the espeak-cv-ft CTC on the
   pointed-espeak targets over the FULL corpus (FLEURS 10h gave PER
   0.319; ~1,700h should drive it far lower). a100, ~10-20 GPU-h.
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

## Alternative noted

micsell/hebrew_speech_{campus,kan}_nikud — Hebrew speech with GOLD
nikud annotations (would upgrade stage 2 from model-pointed to gold-
pointed). Secondary; check availability while awaiting audio-v2
access.
