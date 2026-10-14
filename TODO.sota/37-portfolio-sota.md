# WO37 — SOTA EVERYWHERE: the uncovered portfolio languages

The campaign matrices covered AR/HE/TH. The shipped stable also
carries fas-g2p-1.0, khm-latn-1.0, urd-diac-1.0, urd-g2p-1.0 —
shipped in earlier waves, never measured against 2026 frontiers.

## Survey (2026-10-11, verified — no dedicated external benchmarks exist)

- **Persian G2P**: fragmented; nearest venue = SIGMORPHON multilingual
  G2P shared tasks; g2p-fa (LSTM, PyPI) is the main Persian tool.
  No 2025+ Persian-specific benchmark surfaced.
- **Urdu diacritization**: no dedicated benchmark; QCRI EMNLP-2025
  Arabic-diacritization work is the script-family reference; URDUTTS
  (LREC 2026, 89h TTS) is phonetics-adjacent only.
- **Khmer transliteration**: no external benchmark on record.

## Doctrine where no frontier exists

We DEFINE the reference: publish our held-out evaluation protocol +
our artifacts' numbers, and lead by construction (the AR/HE/TH
playbook inverted). This is cheaper than the big-language program and
makes the claim honest: "best published, protocol included".

## Remaining work

1. **Protocol packaging (fas/khm/urd)**: for each shipped artifact,
   build a fixed held-out test set + evaluation script + published
   metric (PER for g2p; DER-style for diac; CER for khm) in the
   models repo — the same bench format as WikiNews-2024/phonikud.
2. **Nearest-external anchoring**: run g2p-fa (Persian) and any
   reproducible Urdu baselines on OUR protocol; record as anchors.
3. **Gap arms only if an anchor beats us**: no speculative training.
4. **Khmer**: khm-latn-1.0 serves the ISC maps program, not a
   benchmark axis — measure with the maps-corpus conformance suite
   instead (round-trip + corpus fixtures).

## Status: IMPLEMENTED (2026-10-12)

- Portfolio numbers PUBLISHED (run-056, n=3000): fas 0.0147 ·
  urd-diac 0.0386 · urd-g2p 0.1578 CER.
- fas anchor CONFIRMED (run-058, n=1000): g2p-fa = 0.3629
  consonant-skeleton CER / 0.7025 raw (notation-mismatched) vs our
  0.0147 — measured lead ~25×, methodology published (word-by-word
  per its design; both metrics reported for fairness).
- Full-split refinement (run-057) in flight.
- khm: maps-conformance spec'd. urd anchors: no reproducible tool
  found (survey stands) — our protocol remains the reference.
- urd-g2p (15.78 CER): the one language with headroom — candidate
  training arm when compute frees (byt5-base on 635K pairs).
