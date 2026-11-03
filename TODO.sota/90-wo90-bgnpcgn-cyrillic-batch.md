# WO90 — BGN/PCGN Cyrillic batch: 8 systems + Kurdish 2012 verdict

Status: SHIPPED (2026-10-28) — PR #215
Goal: encode the eight remaining BGN/PCGN Cyrillic systems from the reference
collection; resolve the "Kurdish 2012 revision" item.
Method: transcribe each table in full (every row and note), embed per-row tests plus
the source examples, verify under the Ruby interpreter, strict-parse the corpus,
ship as one PR.
Reference collection: `interscript-references/bgn-pcgn/` (text extracted to
/tmp/wo90-{0..8}.txt; glyph anomalies verified against the PDF text layer).

## Systems

| File | Source doc | System date | Checked | Entries | Context rules |
|------|-----------|-------------|---------|---------|---------------|
| bgnpcgn-ady-Cyrl-Latn-2012 | ROMANIZATION OF ADYGHE.pdf | 2012 | 2017-10 | 68 | У word-initial w |
| bgnpcgn-ava-Cyrl-Latn-2011 | ROMANIZATION OF AVAR.pdf | 2011 | 2017-10 | 47 | Е word-initial + post-vowel ye |
| bgnpcgn-chv-Cyrl-Latn-2011 | ROMANIZATION OF CHUVASH.pdf | 2011 | 2017-10 | 37 | Е/Ё initial + post-vowel/post-й-ъ-ь ye/yë |
| bgnpcgn-kbd-Cyrl-Latn-2011 | ROMANIZATION OF KABARDIAN.pdf | 2011 | 2017-10 | 59 | У word-initial w |
| bgnpcgn-krc-Cyrl-Latn-2008 | TABLE OF CORRESPONDENCES FOR KARACHAY-BALKAR.pdf | 2008 | 2017-10 | 38 | У post-vowel w; ъ/ь omitted outside digraphs |
| bgnpcgn-oss-Cyrl-Latn-2009 | ROMANIZATION OF OSSETIAN.pdf | 2009 | 2017-11 | 43 | У three-way (adjacent vowel / post-labializing / u) |
| bgnpcgn-udm-Cyrl-Latn-2011 | ROMANIZATION OF UDMURT.pdf | 2011 | 2017-11 | 38 | Е ye initial, post-vowel, post-йъь, post-дзлнст |
| bgnpcgn-sah-Cyrl-Latn-2012 | ROMANIZATION OF YAKUT.pdf | 2012 | 2017-11 | 40 | Е/Ё initial + post-vowel ye/yë |

## Source anomalies (documented in the maps, not silently corrected)

- ADYGHE + KABARDIAN note 4 prints the H̱ inventory codepoint as "0048+0031";
  the glyph shown is h + combining macron below (U+0331) and the tables render the
  romanization as the precomposed ẖ (U+1E96). The maps output ẖ (U+1E96) and quote
  the note as printed.
- CHUVASH presents Ҫ/ҫ with the Latin Ç codepoints U+00C7/U+00E7 in the document's
  text layer. The map accepts both those codepoints and the standard Chuvash
  Cyrillic U+04AA/U+04AB, all to ś.
- YAKUT pairs capital Ѳ (text-layer U+0472, FITA) with lowercase ө (U+04E9). The
  standard Yakut pair is Ө/ө (U+04E8/U+04E9). The map accepts both capitals to Ö
  and records the source pairing.
- OSSETIAN note 2's example output prints "Respublikӕ" with the CYRILLIC ӕ where
  the Roman æ (U+00E6) belongs. The embedded test uses Respublikæ and the map
  records the source typo.
- YAKUT prints the lowercase form of НЬ as the ligature њ (U+045A). The map maps
  нь (U+043D+044C), НЬ, and U+045A to ny and records the presentation.

## Kurdish "2012 revision" — VERDICT: reissue, no new map

`Kurdish_system_30April2012.pdf` is headed "ROMANIZATION SYSTEM FOR KURDISH
BGN/PCGN 2007" — the 30 April 2012 file restates the 2007 system already encoded as
`bgnpcgn-kur-Arab-Latn-2007.isc` (all 32 consonant rows, 10 vowel rows, notes 1-7,
special rules 1-7, inventory). No separate system exists; the A1 inventory item
closes as "reissue of 2007".

Observation recorded for a separate owner decision: in the existing 2007 map the
vowel row 9 (و with macron above, romanized ö, "rare") appears as
`sub "و" "ö"` after `sub "و" "u"` in the same parallel block — dead code
under first-match; the rare row is not reachable. Fix candidate for a dedicated PR;
not bundled here.

## Acceptance

- 8 new maps, each with the full table + all notes transcribed and embedded tests
  covering every row (upper and lower) plus the source examples.
- All tests pass under the Ruby interpreter; corpus strict-parses (293 files).
- One PR to interscript/maps; coverage docs updated after merge.

## Result (2026-10-28)

- 8 maps encoded, 777 embedded tests, all passing under the Ruby interpreter:
  ady 137/137, ava 97/97, chv 84/84, kbd 118/118, krc 80/80, oss 90/90,
  udm 82/82, sah 89/89.
- Corpus strict parse: 300/300 .isc files.
- Branch `feat/bgnpcgn-cyrillic-batch`, commit 9ef9448, PR
  https://github.com/interscript/maps/pull/215
- Kurdish verdict recorded above (reissue of 2007; no new map).
- Latent-gap observation on bgnpcgn-kur-Arab-Latn-2007 (dead و→ö row)
  recorded for a separate owner decision; not bundled here.
