# ISO gaps

SOURCES STATUS (2026-11-03): only ISO-9-1995.pdf is in
interscript-private-references/iso/. ISO 259, ISO 7098 and ISO 15919
PDFs are NOT in the library — encoding them without the normative
tables would violate the no-fabrication law. OWNER-GATED: acquire the
three PDFs (or bless well-known secondary sources per table).

- ISO 9:1995 non-Russian — RESOLVED (2026-11-03, maps PR #246). The
  planned iso-mul-Cyrl-Latn-9-1995-t3 map was REDUNDANT:
  iso-rus-Cyrl-Latn-9-1995 already encodes the combined
  Slavic + non-Slavic sequence (its own description cites Table 3's 118
  characters). Transcription against the source scan (Table 3, page 10)
  verified the sequence and reduced to 7 row fixes in place: + І̆/і̆,
  У̊/у̊, ӧ̄ (was keyed о̄̈); Ј́/ј́ key mark U+0335 -> U+0301; ʼ ->
  U+02BC and ˮ -> U+02EE mojibake outputs fixed; embedded tests added.
  RECORDED FOR OWNER: the four comma-below rows (җ қ ԡ ң ҫ ҭ ҳ ҷ ҿ)
  use the cedilla/ogonek alternate forms throughout the map (source
  lists both); switching to the primary comma-below forms is an owner
  decision, not taken here.
- ISO 259 Hebrew letter table (pointed input = Track B companion) —
  BLOCKED on the source PDF.
- ISO 7098 pinyin (large syllabary — encode with the DIN 32708 kana
  approach) — BLOCKED on the source PDF.
- ISO 15919 Indic remainder — the corpus has 18 iso-*-15919 maps
  (asm ben guj hin inc kan mal mar nep ori pan pli x4 pra san tam tel).
  The 15919 script set also covers Sinhala, Lao, Khmer, Tibetan and
  per-script vowel extensions — BLOCKED on the source PDF; enumerate
  precisely once acquired.
