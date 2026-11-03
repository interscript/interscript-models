# WO49 — UR g2p lexicon probe (zero-GPU, decisive)

## Rationale

UR g2p is ambiguity-limited (vowels 41.7% + insertions 24.2% of
errors; base ≈ small — capacity exhausted). A train-consensus
word→IPA lexicon is the classic G2P layer: covered words get the
majority reading, OOV falls back to the model. The tha-lexicon
(WO13) and lexicon-loader (WO19, py#33) precedents exist. The WO33
NEGATIVE does not transfer — that was disambiguation for AR diac;
this is plain lookup for g2p.

## Probe (RUNNING, run-072-ur-lexicon-probe, cpu)

Lexicon = most-frequent IPA per word over 610K train pairs. Measures
test coverage + lexicon-oracle CER on covered rows vs the 0.1565
gate. Decision: oracle gain ≥ 1.5pp on covered rows → runtime
lexicon layer (3-runtime work item); else the lever is DEAD — recorded.

## Runtime shape (if the probe passes)

Lexicon artifact (tha-lexicon pattern) + loader fallback in the
seq2seq translate path — owner-gated runtime work, WO22-adjacent.

## Verdict (2026-10-14): DEAD

covered_frac 0.303 · lexicon-oracle CER on covered rows **0.2268**
vs the model's 0.1565 gate — the train-consensus reading is NOISIER
than the model (multi-reading votes + segmenter drift on multi-word
rows). A runtime lexicon layer would degrade quality. Closed at
probe cost (zero GPU, one cpu job).
