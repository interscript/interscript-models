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
- [ ] 17-improvement-backlog.md — the post-WF-1 improvement round
      (grammar single-sourcing, ruby parity closure, additivity in
      maps CI, WF-1 adoption sweep, conformance depth) — ranked,
      evidence-linked, next /goal executes it


## Corpus quality state (2026-11-09)

The registry's embedded tests are FULLY GREEN: 424 maps run, 423 with
tests, 12,337 passed, 0 failed (`iscrs test-all` on maps main
b9ea8c4, 2026-11-09). Previous state (2026-11-05): 400 maps / 11,048
tests after the repairs in maps PRs #255 and #256 (every change
source-anchored to the reference documents — test-vs-map decided per
failing row against the source page) — the corpus's first
zero-known-failure state. The 2026-11-09 growth (+24 maps /
+~1,289 tests) came from the ALA-LC batches 02-05 (maps
#263/#264/#265/#266), each map's tests carried from its own source
document; the 11,048-row golden additivity capture stayed zero-delta
throughout.

## Catalogue-note cleanup

The stray trailing index line for WO16 below the corpus-quality
section was a layout artifact; WO16 is fully recorded in its own file
and the execution log.
## Site catalogue top-up — DONE (was blocked on npm WF-1)

npm `interscript@5.11.0` shipped the WF-1 parser; the site dependency
bumped to `^5.11.0` and the catalogue regenerated **428/428, zero
drops** (site PR #230, 2026-11-11).

## Ruby lockstep probe: maps 3.0.0 vs `~> 2.5` (owner decision)

The weekly `lockstep-check` resolve job (interscript-ruby, cron Mon
06:00 UTC) fired red on 2026-11-09 exactly as designed: it clones
maps main and runs `bundle lock`, and the resolution now fails —
maps main carries `INTERSCRIPT_MAPS_VERSION = "3.0.0"` (released
2026-11-08) while `interscript.gemspec` line 36 constrains
`interscript-maps "~> 2.5"` (>= 2.5, < 3.0). Every bundler
resolution against the maps path source is unsolvable until the
constraint moves. Same-sha evidence: ruby main 346a957 resolved
green on 2026-11-08 13:01 UTC (pre-release maps state in CI) and
red on 2026-11-09 15:07 UTC.

RESOLVED 2026-11-11: the owner authorized reasonable version numbers
for the release round; ruby 3.4.0 ships with `interscript-maps
"~> 3.0"` (PR #837, tag v3.4.0, rubygems live) and the lockstep probe
was re-dispatched immediately — **green** (run 42942594684).

## Release round 2026-11-11 (owner: "use reasonable version numbers")

| package | version | channel | verification |
|---|---|---|---|
| interscript-maps | 3.1.0 | rubygems (release-gem@v1) + GitHub release | `/api/v1/versions` shows 3.1.0; release assets `interscript-maps-ir-3.1.0.tar.gz` + `interscript-maps-isc-3.1.0.tar.gz` with .sha256 sidecars |
| interscript (npm) | 5.11.0 | npm OIDC trusted publishing, provenance | dist-tag latest = 5.11.0; run 42940186512 green (lint/build/test/publish) |
| interscript (rubygems) | 3.4.0 | rubygems trusted publishing | `/api/v1/versions` shows 3.4.0; full spec suite green incl. the constraint move `~> 3.0`; lockstep probe re-dispatched green |
| interscript (crates.io) | 0.2.0 | crates.io trusted publishing (publish.yml) | max_version 0.2.0; run 42942246925 green — required two CI-mechanics fixes (#13 path→version rewrite with a proven published-form build; #14 `--allow-dirty`, the rewrite IS the dirty state) |
| site catalogue | — | interscript.github.io PR #230 (merged) | 428/428, zero drops, `^5.11.0` |

 interscript-py stays PyPI-locked (owner gate). 
## Ruby release-assets pipeline: dead since ≤ v3.1.0 (owner decision)

The `release-assets` workflow (vis_json.zip + metadata.json.zip per
release) failed on the v3.4.0 tag with two stacked causes: upstream
`thedoctor0/zip-release` retagged (v0.7.6 → 0.7.6; fixed in
interscript-ruby PR #838 with a dispatch tag input), and beneath that
the job runs the FROZEN interscript/ monorepo's `ruby/` tree — its
`generate_visualization_json` rake task calls
`Interscript::Node::Stage#to_visualization_array`, undefined in the
workflow's load path (and the layout predates the gem split: the
rake's `../maps` path source isn't even checked out).

History: **no release since at least v3.1.0 carries these assets**
(v3.1.0/v3.2.x/v3.3.0/v3.4.0 all verified via the releases API) —
three releases shipped without anyone missing them; the Astro site
renders rule charts from the catalogue, not this JSON.

OWNER DECISION (retiring a release-asset pipeline): either retire the
workflow (it ships artifacts nobody has received since 3.1.0), or
revive it properly — port `generate_visualization_json` to the gem's
own Rakefile (the gem already carries `visualize/json.rb` and
`generate_metadata_json`), check out ../maps in the workflow, and
teach the visualization the ISC-WF-1 nodes (Ruleset / Rule::Use /
LanguagesDecl / Sub#when_languages). PR #838's dispatch-tag input
supports either path. The v3.4.0 release is NOT missing anything it
ever had in the 3.x era.
