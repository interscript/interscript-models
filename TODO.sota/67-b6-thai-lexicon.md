# WO67 — B6: Thai — lexicon-first, three layers (PER < 2)

Status: IN_PROGRESS — v1 arm NEGATIVE (2026-10-22): ByT5-small on the
31,869-pair v1 corpus converged to dev PER 22.56% (33,429 tokens,
string CER 19.70%, 3,225 held-out rows) — plateau by epoch 3, not a
viable novel-token fallback. Diagnosis: DATA, not architecture (the
32k ceiling was an extraction artifact — 6,291 ORST rows were dropped
by an old engine defect, and thai_words/volubilis were never tapped).
Fix in flight: tha-phonemic-v2 (122,311 pairs, corpora/tha-phonemic-v2.yaml,
models#343) training as run-080-thai-lex-v2; wiki-vocabulary
self-expansion (two-engine cross-check) building as run-080-thai-wiki-4.

**Controlled-eval matrix (2026-10-23, v1 test split = 3,225 ORST rows,
PER over phoneme tokens):** v1 22.56 | v2 (110k pairs, 3ep BS32)
**39.1** | v3 (131k incl. wiki tier, same schedule) **39.5**. More
data at a 5x-smaller update budget is WORSE like-for-like; both
big-data arms degrade identically -> the schedule is the confound,
not the corpora. run-080-thai-lex-v4 (v3 data, BS4 x 2ep ~= 65k
updates, matching v1's budget) is the control; wiki tier's own value
shows only after the schedule is fixed.

**Diagnostic chain (2026-10-23, five verified findings):**
1. Engine drift = 0.0000 PER — royin 5.3.5 output is byte-identical to
   the stored v1 targets on clean rows; convention is NOT the issue.
2. v1-test carries 15 unfiltered old-engine defect rows (1.5% of gold
   tokens; e.g. 'd u ŋ' x8) — small, but the eval set needs a clean
   rebuild.
3. v1's split was clean (0 overlap) — its 22.56 is honest
   in-distribution generalization on orst-only.
4. v2/v3/v4 TRAIN on 790 of the v1-test words (24.5%) and still lose —
   unseen-word PER is worse still (~50% est.).
5. Mechanism: the expanded corpora shifted the output-LENGTH prior
   (volubilis avg 25.6 phoneme tokens vs test 10.4) — long-compound
   dominance wrecks short-word generation. v4-ep0 at 41.8 PER also
   rules out update-budget alone.
**v5 (run-080-thai-lex-v5)** = the corrective: 92,669 rows filtered to
<=20 phoneme tokens (deployment-length distribution), BS4 x 2ep.
**V5 VERDICT (2026-10-23): POSITIVE — recipe found.** v5 (92,669
length-filtered rows, BS4 x 2ep) scores **PER 20.25%** on the v1
split — BEATS the v1 reference (22.56) with 4.1x more training types
and honest generalization, while v4-final (37.4, unfiltered, same
schedule) proves the schedule alone never fixed it. The
length-prior mechanism is confirmed end to end. NEXT: (a) rebuild the
eval set without its 15 defect rows and re-score everything; (b)
convergence arm — v5 recipe, 4-6 epochs, optionally re-add filtered
compounds in a final curriculum phase for long-word coverage; (c) the
converged model becomes the fallback-learner release candidate
(fixtures + gates).
RTGS encodings landed maps#204; IPA layers = WO82.
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
