# WO67 — B6: Thai — lexicon-first, three layers (PER < 2)

Status: IN_PROGRESS (RTGS encodings landed maps#204; lexicon corpus staged; training arm + IPA layers = WO82 pending)
Lexicon phase DONE: corpora/tha-phonemic.yaml -- 28,644 train / 3,225
test (word -> phonemic-with-tones pairs, ORST vocabulary x pythainlp
royin engine); 6,291 engine-corrupt rows filtered and documented;
bucket run-080-thai-lexicon, size-verified. NOTE the layer honesty:
royin emits PHONEMIC+tones, NOT RTGS -- the RTGS layer requires
encoding bgnpcgn-tha (a BGN/PCGN gap-system row: ROMANIZATION OF
THAI.pdf, whole-document transcription) then the rule composite.
NEXT: bgnpcgn-tha encoding; hit-rate metric over the eval set; the
three-layer (RTGS/IPA/IPA+tone) eval harness.
Goal: published PER < 2; lexicon hit-rate reported; tone accuracy for
the TTS layer (RTGS / IPA / IPA+tone tracked separately).
Method: Royal Institute dictionary (or equivalent licensed lexicon) as
first-class lexicon layer with hit-rate metric; ByT5 fallback for novel
tokens (names); RTGS rule composite over the inferred layer (banked:
CTC cannot); tiny contract for the edge tier.
Acceptance: three-layer eval published; hit-rate + PER external-
protocol certified.
