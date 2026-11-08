# TODO.all-sys — every remaining system, fully specified

Terminal: every identified transliteration system has an ISC map in the
registry, tested from its own source document, live on the site.

Status line: 339 done / ~7 open (owner-gated). Sources: all local
(interscript-private-references/alalc/ — 92 docs; din/, bsi/ present).
2026-11-09: the ALA-LC batches 02-05 landed (maps #263-#266, 24 new
maps, ~1,292 new embedded tests); the corpus is 428 system maps; the
only open work orders left are owner-gated (08 source acquisition,
10 B3 ship, 11 urd-oracle license, 12 misc gates).

Rules (binding): visual transcription from scans is sanctioned; every
map carries tests from its own document's examples; one PR per batch;
never delete files; owner-held gates are recorded, never worked around;
versions are owner decisions.

- [x] 01-ala-lc-batch-1.md — Brahmic/SE-Asian, 14 systems — LANDED:
      all 14 in the corpus (cjm carries the Cham system; corpus check
      2026-11-09)
- [x] 02-ala-lc-batch-2.md — Arabic-script, 13 systems — LANDED maps
      #266 (2026-11-09): kazakh, kurdish, ladino (Hebr!), judeo-arabic
      (jba — source found in the collection beyond the WO's list),
      malay/zsm, jawi/jav-Arab, sindhi, urdu, uighur, pushto, ottoman
      (1997 edition per the ALA-LC system; source undated, flagged).
      681 embedded tests. NOT encodable: moghol (no source PDF).
      ara/aze/fas were already in the corpus.
- [x] 03-ala-lc-batch-3.md — Cyrillic, 4 systems — LANDED maps #263
      (2026-11-09): church slavic (chu-Cyrl-2022, 48 letters × case,
      yuses/ksi/psi/fita/izhitsa/both uks) + rusyn (rue-Cyrl-2013, tied
      digraphs, Vojvodinian-i variant documented). 176 embedded tests.
      NOT encodable: bashkir, chuvash, udmurt, komi, yakut/sakha (no
      source PDFs). bel/srp were already in the corpus.
- [x] 04-ala-lc-batch-4.md — East Asian, 2 systems — LANDED maps #265
      (2026-11-09): japanese (jpn-Hrkt-2022, both MR charts A+B,
      deterministic rules; kanji readings = documented M remainder) +
      chinese (zho-Hani-2012, PINYIN-based — the WO's Wade-Giles
      premise applies to the pre-2000 superseded tables; 321 attested
      readings) + the document's complete Wade-Giles→Pinyin
      correspondence table as zho-Latn-Latn-2012 (all 397 rows).
      214 embedded tests. kor was already in the corpus.
- [x] 05-ala-lc-batch-5.md — misc, 10 systems — LANDED maps #264
      (2026-11-09): armenian 2022, coptic 2014, deseret
      (und-Dsrt-2016, language-neutral script — no corpus precedent,
      flagged for owner), cherokee 2012, manchu 2012, moroccan
      tamazight 2012, tamashek 2013, vai 2010. 221 embedded tests.
      NOT encodable: nko, tod-oirat (no source PDFs).
- [x] 06-din-columns.md — DIN 1460-2, 31635 fas/kur/urd, 31636 yid,
      32708 — LANDED: all columns in the corpus (din-fas/kur/urd-31635,
      din-yid-31636, din-jpn-32708; corpus check 2026-11-09)
- [x] 07-pd6505-korean.md — promote the draft from staging — LANDED:
      bsi-kor-Kore-Latn-6505-1982 + Table VIII map in the corpus
- [ ] 08-iso-gaps.md — ISO 9-Cyrl check, 259, 7098, 15919 remainder —
      OWNER-GATED (source acquisition; recorded 56f2c02)
- [x] 09-icao-ungegn-diffs.md — source-doc diffs vs registry — DONE
      (maps #247; UNGEGN library acquired; fc4ad68)
- [ ] 10-b3-release.md — B3 stage 2 (auto after arms) + ship —
      OWNER DECISION (stage-2 verdict MIXED, 2026-11-02: multiref
      green, stretch + SadeedDiac missed; no ship)
- [ ] 11-urd-oracle.md — WO65 stage 1+2 (staged commands) — OWNER
      DECISION (urd-g2p license_review gate)
- [ ] 12-owner-gates.md — Hebrew data, PyPI, urd-g2p license, corpus
      duplicates (record; owner decides)


## Corpus quality state (2026-11-05)

The registry's embedded tests are FULLY GREEN: 400 maps run, 399 with
tests, 11,048 passed, 0 failed (rust iscrs test-all; ruby parity
confirmed per map during the repairs). The last 29 known aspirational
failures across nine maps were repaired in maps PRs #255 and #256,
every change source-anchored to the reference documents (test-vs-map
decided per failing row against the source page). This is the corpus's
first zero-known-failure state.
- 16-workflow-extension.md — ISC workflow layer: rulesets, override, language conditioning (spec for owner review)
