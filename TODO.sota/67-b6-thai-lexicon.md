# WO67 — B6: Thai — lexicon-first, three layers (PER < 2)

Status: PLANNED · launchable now
Goal: published PER < 2; lexicon hit-rate reported; tone accuracy for
the TTS layer (RTGS / IPA / IPA+tone tracked separately).
Method: Royal Institute dictionary (or equivalent licensed lexicon) as
first-class lexicon layer with hit-rate metric; ByT5 fallback for novel
tokens (names); RTGS rule composite over the inferred layer (banked:
CTC cannot); tiny contract for the edge tier.
Acceptance: three-layer eval published; hit-rate + PER external-
protocol certified.
