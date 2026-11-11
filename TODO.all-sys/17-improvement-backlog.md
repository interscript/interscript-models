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

## Execution log (2026-11-11)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 2 | Ruby parity closure | DONE | interscript-ruby PR #840 MERGED: `Item::Alias#max_length` counts 1 for any alias (rs parity, the golden source). Ruby golden gate: `rows: 12337 ... delta vs golden (cross-runtime): 0` — was 33 (un-ara-Arab-Latn-1971/1972, odni-rus Arabic variants). TDD: both new specs watched failing first; suite 409 examples 0 failures. The standing cross-runtime exemption is retired. |
| 3 | Additivity as infrastructure | DONE | (a) PERMANENT py golden test: interscript-ruby PR #841 MERGED — `interscript-py/tests/test_golden_capture.py` replays 12,337 rows byte-identically through the in-process py runtime (83 s); harness detection proven against a doctored golden (one flipped row → failure names exactly that map). (b) The py port of the ts #124 constraint class-context fix rode in the same PR — the in-process path diverged on exactly 5 rows pre-fix (all alalc-ell-Grek-Latn-2010), 4 regression specs watched failing first. (c) MAPS-CI GATES: maps PR #268 MERGED — `.github/workflows/additivity-gates.yml`, four parallel jobs (rs/ts/ruby/py) replaying the golden on every PR + main push; first run surfaced two workflow bugs (ruby gate needed `bundle exec`; rs gate hits the parsanol dev path dep — rewritten to the version requirement, mirroring rs publish.yml) and a merge race on the py test file; all four gates green on the fixed run. |
| 4a | WF-1 adoption sweep: Malay/Jawi pilot | DONE | maps PR #269: `libs/jawi-latn.isc` carries the two shared runs of alalc-zsm-Arab-Latn-2011 / alalc-jav-Arab-Latn-2012 (`malay_jawi_common_a` 50 rules, `malay_jawi_common_b` 10 rules — 60 of zsm's 61 rules are byte-identical to jav's; jav inserts 3 Javanese consonants ڎ/ڟ/ۏ between the runs). Per-pass proof: compiled IR before/after IDENTICAL once sequential composition is flattened (60/63 ordered rules byte-equal; the `sequence` wrapper flattens away). rs sweep 12,337/0; ruby golden gate 0 delta, 0 exempt. |
| 4b | WF-1 sweep: remaining clusters | OPEN | Hebraic pair (alalc-lad-Hebr-Latn-2025 ∩ alalc-jba-Hebr-Latn-2011: 27 identical plain rows) is the next candidate; the Arab-script maps share only ~12 rows each — low value. Use `use` at STAGE level only: splicing inside a `sequence` block silently emits zero rules (the converter expands stage-level items only; §2 makes `use` a stage_item) — a spec question for the grammar round. |
| 4c | W3 adoption | OPEN | No corpus adoption; ICAO 9303's split multi-language map (#168) remains the candidate to re-examine — document evidence required. |
| 1 | Grammar single-sourcing | IN PROGRESS | Step 4a: the cross-grammar parity harness (maps `scripts/parse-parity.mjs`, ts+py normalizers, 434-file corpus) — agent campaign in flight. The generated-parser switch follows behind its audit. |
| 5 | Conformance depth | OPEN | Exhaustive per-row test generation from source text layers (batch-3's chu/rue did it by hand, 176 rows). |
| 6 | rs loader ruleset-only libs | OPEN | `iscrs capture` skips the ruleset-only `thai-latn` lib at direct load (no stages); the loader should accept ruleset-only documents. |

Owner-held (unchanged): PyPI publisher registration + first py version
(workflow in place, ruby #839); Hebrew vocalization data; urd-g2p
license_review; B3 stage-2 ship; ISO 259/7098/15919 source
acquisition; release-assets pipeline retire-or-revive (#429); monorepo
vestigial disposition.

## Harness audit (2026-11-11, step 4a landed)

The cross-grammar parity harness landed as maps PR #270
(`scripts/parse-parity.mjs`: ts `parseIsc`+`expandDocument` and py
`parse_isc` projected onto one canonical schema; deterministic,
~11 s/corpus run, `--json` report, non-zero exit on divergence).

**Audit at origin/main 3bc9098: parity 408/433; 6 divergence kinds in
four stories:**
1. py `none`→empty-string lowering (documented behavior in py's
   builder) — 493 items / 16 files; normalizer-level note.
2. `any_character` typing (ts function-item vs py alias-item) — 47
   items / 3 files; normalizer-level.
3. Written constraint order lost by py (fixed field order) — 5 files;
   normalizer-level.
4. **SEMANTIC: py `use`-with-override placement** — ts/ruby join ALL
   override rows into the trailing parallel block (§4.2.6); py
   appended unmatched additions as bare stage rules (bgnpcgn-tha
   344 vs 327+17; alalc-tha 1523 vs 327+1196). FIXED in
   interscript-ruby PR #842 with failing-first placement specs; the
   in-process golden (12,337 rows) stayed green in-suite.

**Hardening finding (unfixed, both ts and py):** the stage/rule/
override body loops lack an end-of-source guard — an unrecognized
token that swallows its closing brace spins forever at EOF (synthetic
one-liner repro hangs tsx at 100% CPU; the corpus is safe today; the
harness's `--timeout` watchdog flags any file that trips it). Fix in
the grammar single-sourcing round.

Expected post-#842 parity: 410/433 (the two thai pilot files join);
the remainder is the three normalizer-level stories, which the
generated-parser switch (step 4b) resolves at the root.
