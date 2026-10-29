# WO91 — DIN + BSI + ICS Annex D batch

Status: IN_PROGRESS (2026-10-29) — BS 2979 COMPLETE + DIN 31635 Arabic SHIPPED (maps PR #223). WO91 remaining: PD 6505, DIN 1460-2/32708, DIN 31635 Persian/Kurdish/Urdu columns, ICS Annex D Appendix A
Goal: encode the five DIN gaps, the two BSI documents, and ICS Annex D;
A1 items D-classes all deterministic (WO89 section A3/A4/A5).
Reference collection: `interscript-private-references/{din,bsi,ics-630-01}/`;
text extracted to /tmp/wo91-*.txt.

## Item states

| Item | Doc | Contents | State |
|------|-----|----------|-------|
| DIN 32706 Armenian | din-32706.pdf (8 pp) | 39-row table aligned with ISO 9985 | **SHIPPED — maps PR #216** (also closes the ISO 9985 scope gap in WO89 A6) |
| BS 2979:1958 | BS-2979-1958.pdf (24 pp) | FIVE systems in one document: "British" Cyrillic (Table A/B), "International" Cyrillic (= ISO/R9, Table C), Church Slavonic (Table D), Rumanian Cyrillic (Table E), Greek (Table G) | **UNBLOCKED by owner directive (visual reading of the scans). Table A COMPLETE — Russian #219; ukr/bel/bul/srp/mkd #220 (160 tests; settled at 9x: Bulgarian щ=sht, Bulgarian ъ=ŭ — the examples-page S-ibreve-yuz was a breve-vowel confusion; Ukrainian и=ȳ; Byelorussian ы=ȳ; the Zapiski example uses pre-reform letters outside the bel column — recorded, not embedded). Rows 45-47 not rendered in any column. Table B/F are back-transliterations (skip; A2 territory). Table C = ISO/R9 (cite). Table D = pdf page 16, Table E = pdf 17, Table G = pdf 20+ (legacy-font text; now also readable visually). Document examples page (pdf 7) gives British+International renderings of 17 periodical titles - test material.** |
| PD 6505:1982 | PD-6505-1982.pdf (49 pp) | Greek transliteration | **UNBLOCKED by owner directive — read visually; not yet transcribed.** |
| DIN 1460-2 | din-1460-2.pdf (29 pp) | Cyrillic alphabets of NON-SLAVIC languages (part 2), 2011-10 | PENDING — 52.8k chars |
| DIN 31635 | din-31635.pdf (29 pp) | Arabic **SHIPPED — maps PR #223** (59 tests; vocalized-input core; the norm also carries Persian, Kurdish and Urdu sections — separate maps; its Ottoman-Turkish section is references-only, cited) |
| DIN 31636 Hebrew column | din-31636.pdf (14 pp) | HEBREW (2018-10): **SHIPPED — maps PR #217** (tables 1-6 + section 8 rules over vocalized input; Unicode mark-order normalization; reading-side items documented: matres lectionis, qamats qatan, furtive patah, sheva root exceptions, 8h/8j-k) |
| DIN 31636 Yiddish column | din-31636.pdf (14 pp) | Yiddish vowel table (Table 4), ayin as e, tav as s-with-grave, double forms | **SHIPPED — maps PR #218** (Table 4 spellings as sequence rules; reading-dependent cells resolve first-listed with alternative documented; loshn-koydesh = composition point) |
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

## Vision reading (2026-10-28, third pass) — owner directive

The owner directed visual reading of scan-only sources. Both BSI documents are
therefore unblocked; no OCR tooling decision is needed. Table A (Russian column)
and the DIN Yiddish column were read from high-resolution page crops
(3x-9x via PyMuPDF clip renders). Recording for the continuation:

- Table A structure: 48 rows x 5 language columns (Russian, Ukrainian,
  Byelorussian, Bulgarian, Serbian & Macedonian); parenthesized cells = obsolete
  characters; footnotes: dj/gj alternate to đ; final ъ disregarded.
- Key cross-column cells (from the scans): Г→g/h/h/g/g; Ґ→(g) for ukr/bel;
  и: ru i / ukr ȳ; ы→ȳ (ru, bel); й→ĭ; Ў→w (bel); Щ: shch/shch/-/sht;
  ъ: “or”/(“or”)/(“or”)/ŭ; Ё→ě (ru, bel); Э→é (ru, bel); ѣ→(ě) rus/ukr/bel/bulg;
  Х→kh×4 then h (srp); Ц→ts×4 then c; Ч→č; Ж/Ш→zh/š, sh/š; Тс→t-s ×4, ts (srp);
  Ђ→đ, Ѓ→đ, ћ→ć, ќ→ć, Џ→dž, Ѕ→dz, Љ→lj, Њ→nj, Ј→j.
- Rows 45-47 (Ѧ, Ѳ, Ѵ): Bulgarian/Russian cells render only as parenthesized
  obsolete marks not legible beyond doubt — not encoded, not guessed.
- Uncertain-by-design choices documented in the maps: ъ→” (of ” or "), ь→’
  (of ' or '), Bulgarian Щ→sht, the BS example diacritic-dropping (NOTE 1).

## Negative / blocker record (2026-10-28, second pass)

- BS 2979 and PD 6505 are NOT encodable from their text layers: both documents
  present their tables as page images (BS 2979 additionally stores its Greek
  table in a legacy 8-bit font). WO89 section A4's class-D assumption for the
  BSI pair is corrected to X (owner-gated on OCR/manual-transcription tooling).
  No map is written for them; nothing is fabricated from the mojibake.
- DIN subjects confirmed from title pages: 31636 = Hebrew (2018), 32708 =
  Japanese (2014), 1460-2 = non-Slavic Cyrillic (2011).

## Merge record (2026-10-28)

All campaign PRs rebase-merged on owner instruction: maps #211-#219 and
interscript-models #377. #215 (the 8-map batch) conflicted add/add with the
#211 restore, which had brought back earlier versions of five of the same
systems (ady, kbd, krc, sah, udm). Cross-running the test suites settled it:

- kbd, krc, udm: main's versions passed 100% of my suites — content-equivalent,
  mine retained for the fuller tests (506 vs 99 across the five) and the
  source-anomaly notes.
- ady: main's version was RIGHT on one cell where mine was wrong — the capital
  tied digraphs are Z͟H/S͟H (both capitals, U+035F over both) per the source's
  own inventory note; my map corrected to Z͟H/S͟H (137/137) and the branch
  rebased with my versions for all five.
- sah: main's version diverged from the source PDF — it rendered d as D’ and n
  as N’ (a palatalization-apostrophe scheme) and did not render fita or the nje
  ligature; the BGN/PCGN 2012 table itself specifies dj and ny. Mine retained
  (89/89), and the divergence is recorded here.

After the merge: corpus strict-parse 309/309; map-artifact CI green on the
resulting main push.

## Tables D and E (2026-10-29)

- Table D Church Slavonic (bsi-chu-Cyrl-Latn-1958, 90 tests): i-rows are
  glyph-variant pairs (i long/breve-marked short; i and i-diaeresis); yus series
  e-ogonek/o-ogonek + j-forms; omega o-macron; uk digraph = u-MACRON (20x crop)
  with monograph-uk variants; ksi ks; psi ps; fita = f-dot (20x); izhitsa =
  y-dot (20x); hard sign u-breve (after consonants, per footnote); numerical
  values documented, not encoded.
- Table E Rumanian Alfabetul Cirilic (bsi-ron-Cyrl-Latn-1958, 93 tests): k = c
  (ch before e & i, context rule over е/и/і/ї); yer a-breve; yery âi; yat ea;
  yuses ê/â; semiyus (row 42) = in (printed "i-circumflex (n)"); fita th;
  izhitsa y; row 43 = dzhe (ts-with-descender shape) = g before e & i.
  Codepoint catch: the semiyus is U+A64E/A64F (semiyus), NOT the lookalike
  neutral yer U+A65E/A65F first typed.
- Both read visually from the scans at 6x-20x; the two maps' uk renderings
  differ (CS macron, Rumanian breve) — distinct tables, distinct conventions.

## Table G, Greek (2026-10-29)

bsi-ell-Grek-Latn-1958 (54 tests): all 24 rows both cases; eta/omega with
macrons; phi = f (per the table's own English-to-Greek cross-references); the
special-signs notes implemented — rough breathing = apostrophe preceding its
vowel (decomposed combining dasia AND precomposed Greek-Extended forms),
disregarded over rho; smooth breathing deleted; diaeresis/accents left in
place; iota subscript = positional i including the precomposed diphthong
forms (ai, ei-macron-i, o-macron-i + capitals).

Negative recorded: the precomposed block was first written with psili/dasia
INVERTED (psili = smooth = even codepoints U+1F00..., dasia = rough = odd
U+1F01...); caught by the smooth-alpha test failing and fixed by swapping the
blocks and re-pointing the two example tests at the rough forms. The source's
own legacy-font text layer for this table was deliberately not used.

BS 2979 verdict: every encodable table is now in the corpus (A x5 columns + B
skip back-transliteration + C cite ISO/R9 + D + E + F skip + G). Rows 45-47 of
Table A remain unrendered (illegible cells, not guessed).

## DIN 31635 Arabic (2026-10-29)

din-ara-Arab-Latn-31635-2011 (59 tests), section 6 over vocalized input:
Table 1 in full; short-vowel signs; fathatan as -an; sukun stripped first
(keeps the article rule adjacent); shadda doubling for every consonant with
mark-order swaps; hamza carriers contribute nothing (a+damma-carrier renders
only the mark's vowel); alif/hamza omitted word-initially; madda per rule f;
taa marbuta h-after-long-a with the lookbehind accepting BOTH the raw alif
and the merged a-macron (the long-vowel merge rules run first and consume
the alif — first-order lesson from the Hebrew mark-order negative); the
word-initial article with sun-letter assimilation and hyphen including the
doubled shadda form (aš-š). Reading-side documented: unvocalized waw/ya,
hamzat al-wasl, article elision after vowel-final words, construct state,
Allah.

## .imp-era PR migration (2026-10-29, owner directive)

- PR #167 Modern Syriac: MIGRATED — maps/bgnpcgn-syr-Syrc-Latn-2011.isc replaces
  the .imp on the branch (30 tests, all CI checks green). The source table's three
  undetermined letters (waw, yod, taw) render deterministically (w, y, t) with the
  vocalization-dependent alternatives documented.
- PR #166 Dzongkha: MIGRATED — maps/bgnpcgn-dzo-Tibt-Latn-2010.isc re-derived from
  ROMANIZATION OF DZONGKHA (the .imp was an unfinished draft: unclosed blocks,
  duplicated conflicting rows, no valid tests). 71 tests, all CI checks green.
  Verified against the source: row 23 a-chung = z is genuinely the source's value.
- PR #168 ICAO 9303: PENDING — the .imp is a MULTI-LANGUAGE map using language()
  selectors (rus/bel/ukr/mkd/srb + shared Latin-diacritics section). The
  corpus-correct migration splits it into per-language maps; not yet converted.
- PR #169 enhance-iso-223-1: PENDING DECISION — the branch adds
  iso-ara-Arab-Latn-223-1-2021.imp but the content is ISO 233:1984 Arabic and the
  corpus already carries iso-ara-Arab-Latn-233-1984.isc on main. The relationship
  (redundant duplicate vs enhancement of the merged map) needs a semantic diff;
  closing vs updating is an owner decision.
- ISC semantics negative (recurring): before = lookbehind, after = lookahead -
  the Dzongkha suffix/cluster rules were first written with the contexts reversed;
  the Avar probe had established this earlier in the campaign.
