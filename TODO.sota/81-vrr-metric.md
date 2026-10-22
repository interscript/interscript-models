# WO81 — VRR: valid-reading-rate, the ambiguity-aware metric

Status: PLANNED · Plane B (B3 closure requirement, WO56 structural rule 1)

Single-gold DER systematically undercounts legitimate ambiguity: when a
skeleton has several dictionary-licensed readings, scoring against one
gold penalizes a correct alternative. VRR scores a prediction as valid
when it matches ANY licensed reading.

Goal: VRR reported alongside DER for every Arabic (then Hebrew/Urdu)
headline claim; the first number lands for `ara-diac-2.0` on
SadeedDiac-25.

Method:
- Build the licensed-reading lexicon: skeleton (undiacritized form) →
  set of fully-vocalized forms, extracted from the pinned vocalized
  training corpora (provenance in `corpora/*.yaml`); dedupe by exact
  diacritic pattern.
- Implement `score_predictions_vrr` + CLI in interscript-ml-tools:
  VRR = |{pred form ∈ licensed(skeleton)}| / |rows|, computed per row
  and corpus-level, convention-declared (row-level match, exact
  including diacritics).
- Run against the frozen predictions in the
  `frontier-predictions-v1` release — no model calls needed.
- Record in `models.yaml` as a second metric block (protocol + anchor
  per the C2 anchor law).

Acceptance: VRR tool shipped; `ara-diac-2.0` VRR published next to
DER 2.29; the metric convention declared and gated.
