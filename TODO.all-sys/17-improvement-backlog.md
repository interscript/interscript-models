# WO17 — improvement backlog (post ISC-WF-1 + ALA-LC batches)

Status: BACKLOG — ranked, evidence-linked; the next /goal executes it.
Everything else in this ledger is landed or owner-held.

## 1. Grammar single-sourcing (parsanol v2 → TS/Py codegen) — structural

The four runtimes hand-sync their grammar copies (ruby + rs vendor
`isc.parg`; ts + py are hand ports). The drift class is proven, not
hypothetical: TS shipped override rows as bare stage rules until the
maps pilot exposed it (§4.2.6 amendment + ts test); rs keeps
`ruleset` out of its keyword table (documented §2 divergence).
Direction: `.parg` stays the single source; the TS and Py parsers are
GENERATED from it. Land incrementally: (a) cross-grammar parity
harness (parse the 428-file corpus + WF-1 fixtures through ruby and
the candidate generator, require structural IR equality); (b) switch
the TS parser to generated output behind full-corpus + conformance
parity; (c) same for Py. The rs vendored copy joins when its grammar
hosting moves to parsanol-rs's published artifact.

## 2. Ruby parity closure — bug class

`Item::Alias#max_length` raises NotImplementedError; 33 golden rows
diverge across 4 Arabic maps (un-ara-Arab-Latn-1971/1972, odni-rus
Arabic variants — the ruby gate lists them as pre-existing). Fix
max_length for alias items in the reference runtime; the
cross-runtime comparison drops to zero deltas outside nothing — the
standing 33-row exemption retires. Prove with
`ruby -Ilib tools/isc_wf1_golden_gate.rb --parity` reaching 0 and the
rs golden unchanged.

## 3. Additivity as infrastructure (maps CI, all four runtimes)

The golden harness lives in rs tests (sibling-gated) with ad-hoc
mirrors: ts `test/golden-isc-wf0.test.ts`, ruby
`tools/isc_wf1_golden_gate.rb`. py has NO permanent test (verified
manually during #833). Promote: a maps-CI job that, on every PR,
runs all four gates against `tests/golden/isc-wf0.jsonl`
(12,337 rows / 428 maps) + a permanent golden test in interscript-py
mirroring ts's (sibling-gated, adopting-maps exempt list honored).
Also cover the rs quirk while there: `iscrs capture` skips the
ruleset-only `thai-latn` lib at direct load (no stages) — the loader
should accept ruleset-only docs.

## 4. WF-1 adoption sweep (reuse the new language)

Candidates with proven duplication: (a) the Arabic-script
sukun-strip / mark-order / long-vowel machinery now copied across the
11 batch-2 maps (din-ara technique notes) — shared ruleset + per-map
overrides, byte-identical per-pass proof required; (b) ODNI/UN
Cyrillic table overlaps; (c) Devanagari medial tables (partial share
— overrides heavy, measure before committing). W3's first real
adoption: only with document evidence (the ISO 9 pilot dissolved on
PDF evidence; ICAO 9303's split multi-language map #168 is the
candidate to re-examine). Each conversion: adopting-maps.txt entry +
golden zero delta (refactors) or justified deltas (semantic, owner-
visible).

## 5. Conformance depth

Embedded tests cover rows the documents exemplify. Where the source
document has a machine-readable text layer, generate exhaustive
per-row tests (every table row, upper+lower) — batch-3's chu/rue did
this by hand (176 rows); make it a tool. Test-from-source stays the
rule; generated tests get a generation-commit note.

## Owner-held (unchanged)

PyPI publisher registration + first py version (workflow in place,
ruby #839); Hebrew vocalization data; urd-g2p license_review; B3
stage-2 ship (MIXED verdict); ISO 259/7098/15919 source acquisition;
release-assets pipeline retire-or-revive (#429); monorepo vestigial
disposition.
