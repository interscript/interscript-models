# WO91 — DIN + BSI + ICS Annex D batch

Status: IN_PROGRESS (2026-10-28) — 1 of 8 items shipped (PR maps#216)
Goal: encode the five DIN gaps, the two BSI documents, and ICS Annex D;
A1 items D-classes all deterministic (WO89 section A3/A4/A5).
Reference collection: `interscript-private-references/{din,bsi,ics-630-01}/`;
text extracted to /tmp/wo91-*.txt.

## Item states

| Item | Doc | Contents | State |
|------|-----|----------|-------|
| DIN 32706 Armenian | din-32706.pdf (8 pp) | 39-row table aligned with ISO 9985 | **SHIPPED — maps PR #216** (also closes the ISO 9985 scope gap in WO89 A6) |
| BS 2979:1958 | BS-2979-1958.pdf (24 pp) | FIVE systems in one document: "British" Cyrillic (Table A/B), "International" Cyrillic (= ISO/R9, Table C), Church Slavonic (Table D), Rumanian Cyrillic (Table E), Greek (Table G) | PENDING — split into separate maps: bsi-rus-Cyrl-Latn-1958, bsi-chu-Cyrl-Latn-1958, bsi-ron-Cyrl-Latn-1958, bsi-ell-Grek-Latn-1958; the ISO/R9 table cross-references the existing iso maps (cite, do not duplicate) |
| PD 6505:1982 | PD-6505-1982.pdf (49 pp) | Greek transliteration | **SCANNED — no text layer (252 chars total)**; needs OCR or manual transcription; owner decision on OCR tooling |
| DIN 1460-2 | din-1460-2.pdf (29 pp) | Cyrillic alphabets, part 2 | PENDING — 52.8k chars |
| DIN 31635 | din-31635.pdf (29 pp) | Arabic | PENDING — 35.8k chars |
| DIN 31636 | din-31636.pdf (14 pp) | subject confirmed at encoding | PENDING — 22k chars |
| DIN 32708 | din-32708.pdf (19 pp) | subject confirmed at encoding | PENDING — 35.8k chars |
| ICS 630-01 Annex D | ANNEX D + Appendices A/B/C | Main annex is name-formatting policy (pinyin; title case; surname first; ü→u; no apostrophes/hyphens; STC codes); the transliteration table is Appendix A | PENDING — Appendix A is a large Hanzi→pinyin table; Appendix B is the Wade-Giles/Gwoyeu/Yale conversion table; Appendix C is the surname list; scope decision: encode Appendix A as the map (large table), record B/C as reference notes |

## Method notes

- BS 2979's four encodable systems each become their own map; the document's
  "International" Cyrillic table is ISO/R9 and is cited against the existing
  iso corpus maps rather than duplicated (WO89 A6 convention).
- PD 6505 has no text layer; options: OCR pass, or manual transcription from
  page images. Owner picks the tooling before work starts.
- The ICS Annex D map's input script is Hans/Hant with the Appendix A table;
  the name-formatting rules (title case per word, no apostrophe) apply as
  post-rules per the main annex text.
