# WO82 — Thai IPA and IPA+tone layers (the TTS layer)

Status: PLANNED · Plane B (B6 layers 2–3; layer 1 RTGS shipped in maps#204)

WO56 requires three separately-tracked Thai target layers: RTGS
(toneless, DONE — deterministic .isc encodings), IPA (toneless), and
IPA+tone (TTS). The phoneme layers need a tonal data supply that is not
yet identified.

Goal: `tha-phonemic` eval reporting IPA layer v0 and IPA+tone v0 with
tone accuracy; published PER < 2 on the RTGS layer stands from B6.

Method:
- Data supply (OWNER ASK): Royal Institute dictionary entries carry
  pronunciation + tone; identify the machine-readable source and its
  license (the 28,644-row staged lexicon covers orthographic→phonemic
  without tone marks — audit whether tone is recoverable from it before
  asking for more data).
- Learned-IPA fallback for novel tokens: ByT5 arm conditioned per the
  lexicon-first doctrine (hit-rate first-class).
- Tone accuracy metric: consonant-class × syllable-type computed tone
  vs lexicon tone, declared per C2.

Acceptance: three layers tracked in models.yaml; IPA+tone v0 shipped
with tone accuracy reported; RTGS layer unchanged.
