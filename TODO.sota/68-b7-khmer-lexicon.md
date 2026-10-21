# WO68 — B7: Khmer — Chuon Nath lexicon conditioning (CER < 15)

Status: IN_PROGRESS (phase 1 landed 2026-10-21; phase 2 = training arm)
Phase 1 DONE: khm-dict corpus built + pinned (corpora/khm-dict.yaml) —
3,261 gold Chuon-Nath (word→IPA) pairs, 326-row holdout, 72,048 SBBIC
vocab rows; staged at bucket Interscript/isx-training/run-080-khm-lexicon
(size-verified). License LGPL-2.1 recorded; owner note on
LGPL-for-data semantics. NEXT: hit-rate vs the khm-latn eval set (in
the phase-2 job, which mounts it), lexicon-conditioned ByT5 fallback
training, three-way probe.
Goal: khm-latn 27.4 → CER < 15 with hit-rate reported.
Method: build the Chuon Nath-conditioned dataset (headword→reading
pairs, syllabification-aware); lexicon-conditioned ByT5 (retrieval or
prefix conditioning); fp16 zip hygiene (khm fp32 corruption lesson);
conformance fixtures for the new artifact.
Acceptance: gates green; hit-rate + CER on held-out; release via the
strict publish path.
