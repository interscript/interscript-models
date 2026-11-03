# WO81 — VRR: valid-reading-rate, the ambiguity-aware metric

Status: IN_PROGRESS — metric SHIPPED (models#340: build_lexicon /
score_predictions_vrr / score_text_vrr, word-level); first verdict
computed 2026-10-22 (run-081-vrr, cpu job; tools/vrr_lexicon_verdict.py):

| run | student VRR | teacher VRR | words |
|---|---|---|---|
| run-006 (rung 2.0) | 0.7974 | 0.8101 | 51,808 |
| run-007 (rung 2.1) | 0.8004 | 0.8101 | 51,808 |

Lexicon: tashkeela-full train (declared source — classical register),
309,508 skeletons. Verdict artifact:
bucket Interscript/isx-training/run-081-vrr/vrr-verdict.json (release
asset rides E3). NEXT: gold-column ceiling (oracle VRR) to separate
model error from lexicon coverage; publish VRR into the models.yaml
metric blocks once the rung-2.0 DER provenance question (WO64/B9) is
resolved.

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
