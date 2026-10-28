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
| BS 2979:1958 | BS-2979-1958.pdf (24 pp) | FIVE systems in one document: "British" Cyrillic (Table A/B), "International" Cyrillic (= ISO/R9, Table C), Church Slavonic (Table D), Rumanian Cyrillic (Table E), Greek (Table G) | **BLOCKED-OWNER — Tables A-F are full-page scans (pages 7, 10-19 are ~4000x5000 images); Table G has a text layer but in a legacy 8-bit font (Greek letters stored as mojibake, e.g. "Z, a-acute" for "Z, zeta"). Recovering Table G requires font-cmap forensics; Tables A-F require OCR or manual transcription. Owner decides the tooling.** |
| PD 6505:1982 | PD-6505-1982.pdf (49 pp) | Greek transliteration | **BLOCKED-OWNER — pure scan (252 chars of text layer total)**; same tooling decision as BS 2979 |
| DIN 1460-2 | din-1460-2.pdf (29 pp) | Cyrillic alphabets of NON-SLAVIC languages (part 2), 2011-10 | PENDING — 52.8k chars |
| DIN 31635 | din-31635.pdf (29 pp) | Arabic | PENDING — 35.8k chars |
| DIN 31636 | din-31636.pdf (14 pp) | HEBREW (2018-10 edition, replaces 2011-01): Table 1 consonants Hebr/Jiddish (alef as glottal mark or ignored, bet/vet, double-vav, end forms, ayin as e in Yiddish, tav as s-with-grave in Yiddish), Table 2 neo-Hebrew additions (geresh-marked), Tables 3/4 Hebrew/Yiddish vowels, Table 5 special characters | PENDING — full norm is a work item of its own; the D+M companion is the existing heb-vocalized lineage for unvocalized input |
| DIN 32708 | din-32708.pdf (19 pp) | JAPANESE (2014-08) | PENDING — kana rows deterministic; kanji readings are the one true M-part (WO89 A2) |
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

## Negative / blocker record (2026-10-28, second pass)

- BS 2979 and PD 6505 are NOT encodable from their text layers: both documents
  present their tables as page images (BS 2979 additionally stores its Greek
  table in a legacy 8-bit font). WO89 section A4's class-D assumption for the
  BSI pair is corrected to X (owner-gated on OCR/manual-transcription tooling).
  No map is written for them; nothing is fabricated from the mojibake.
- DIN subjects confirmed from title pages: 31636 = Hebrew (2018), 32708 =
  Japanese (2014), 1460-2 = non-Slavic Cyrillic (2011).
