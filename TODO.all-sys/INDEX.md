# TODO.all-sys — every remaining system, fully specified

Terminal: every identified transliteration system has an ISC map in the
registry, tested from its own source document, live on the site.

Status line: 318 done / ~45 open. Sources: all local
(interscript-private-references/alalc/ — 92 docs; din/, bsi/ present).

Rules (binding): visual transcription from scans is sanctioned; every
map carries tests from its own document's examples; one PR per batch;
never delete files; owner-held gates are recorded, never worked around;
versions are owner decisions.

- [x] 01-ala-lc-batch-1.md — Brahmic/SE-Asian, 14 systems — LANDED:
      all 14 in the corpus (cjm carries the Cham system; corpus check
      2026-11-09)
- [ ] 02-ala-lc-batch-2.md — Arabic-script, 13 systems — IN FLIGHT
      (agent campaign 2026-11-09): ara/aze/fas already in the corpus;
      kazakh, kurdish, ladino, malay/jawi, sindhi, uighur, urdu,
      pushto, ottoman sources present; moghol has no source PDF
      (record, don't encode)
- [ ] 03-ala-lc-batch-3.md — Cyrillic, 4 systems — IN FLIGHT (agent
      campaign 2026-11-09) for chu (church slavic) + rue (rusyn),
      the two with sources; bak/chv/udm/kv/sah have no source PDF
      (record, don't encode); bel/srp already in the corpus
- [ ] 04-ala-lc-batch-4.md — East Asian, 2 systems — IN FLIGHT (agent
      campaign 2026-11-09): chinese (Wade-Giles syllabary) + japanese
      (McCune-Reischauer kana, M-remainder noted); kor already in the
      corpus
- [ ] 05-ala-lc-batch-5.md — misc, 10 systems — IN FLIGHT (agent
      campaign 2026-11-09) for the 8 with sources (armenian, coptic,
      deseret, cherokee, manchu, tamazight, tamashek, vai); nko +
      tod-oirat have no source PDF (record, don't encode)
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
