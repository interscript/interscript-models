# WO57 — A1: authority-completeness audit

Status: IN_PROGRESS (phase 1 DONE 2026-10-21: docs/coverage ledger + three authority diffs — alalc 30/47, iso, bgnpcgn 17 gaps; phase 2 = encode the gaps)
Goal: enumerate the UNIVERSE of authority romanization/transliteration
systems and diff it against the 293 encoded in `maps/`. Every gap is
either encoded or cited out-of-scope with an authority reference.
Method:
1. Build the catalog: UN WGRS (1968–2016 editions, ~25 systems),
   BGN/PCGN current schedule (~55), ALA-LC full language tables
   (~170 Romanization tables), ISO 9/233/259/3609/7098/843/9984/9985/
   233-3, ICAO 9303, national systems (DIN 14640, RTGS, Korean RR
   2000, HK Government, ROC, Thai Royal Institute…). Sources: the
   authority documents already collected in interscript-references +
   the ISO 24229 code convention.
2. Extract the corpus's system codes from maps/*.isc names; normalize
   per ISO 24229; join against the catalog.
3. Emit coverage matrix (authority × system × status: encoded /
   gap-encoded-possible / out-of-scope+reason) to
   docs/coverage/COVERAGE.md; gaps that are encodable become maps
   PRs (whole-document transcription law applies).
Acceptance: coverage matrix published with zero unexplained gaps;
enconding PRs opened for every encodable gap.
Owner gates: none for the audit; map encodings are ordinary PRs.
