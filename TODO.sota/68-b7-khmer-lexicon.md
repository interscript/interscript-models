# WO68 — B7: Khmer — Chuon Nath lexicon conditioning (CER < 15)

Status: PLANNED · launchable now (data on disk: khmer-dict-spice)
Goal: khm-latn 27.4 → CER < 15 with hit-rate reported.
Method: build the Chuon Nath-conditioned dataset (headword→reading
pairs, syllabification-aware); lexicon-conditioned ByT5 (retrieval or
prefix conditioning); fp16 zip hygiene (khm fp32 corruption lesson);
conformance fixtures for the new artifact.
Acceptance: gates green; hit-rate + CER on held-out; release via the
strict publish path.
