# TODO.all-sys — every remaining system, fully specified

Terminal: every identified transliteration system has an ISC map in the
registry, tested from its own source document, live on the site.

Status line: 318 done / ~45 open. Sources: all local
(interscript-private-references/alalc/ — 92 docs; din/, bsi/ present).

Rules (binding): visual transcription from scans is sanctioned; every
map carries tests from its own document's examples; one PR per batch;
never delete files; owner-held gates are recorded, never worked around;
versions are owner decisions.

- [ ] 01-ala-lc-batch-1.md — Brahmic/SE-Asian, 14 systems
- [ ] 02-ala-lc-batch-2.md — Arabic-script, 13 systems
- [ ] 03-ala-lc-batch-3.md — Cyrillic, 4 systems
- [ ] 04-ala-lc-batch-4.md — East Asian, 2 systems
- [ ] 05-ala-lc-batch-5.md — misc, 10 systems
- [ ] 06-din-columns.md — DIN 1460-2, 31635 fas/kur/urd, 31636 yid, 32708
- [ ] 07-pd6505-korean.md — promote the draft from staging
- [ ] 08-iso-gaps.md — ISO 9-Cyrl check, 259, 7098, 15919 remainder
- [ ] 09-icao-ungegn-diffs.md — source-doc diffs vs registry
- [ ] 10-b3-release.md — B3 stage 2 (auto after arms) + ship
- [ ] 11-urd-oracle.md — WO65 stage 1+2 (staged commands)
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
