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

CONFIRMED post-#842 (harness re-run against ruby main with the fix,
2026-11-11): parity 410/433, 3 divergence kinds (item-kind 678,
constraints 144, item-value 4) — the two thai pilot files joined; the
remainder is the normalizer-level stories, which the generated-parser
switch (step 4b) resolves at the root. 4b campaign in flight.

## Step 4b landed (2026-11-12): the TS parser is generated from the .parg

interscript-ts PR #128 MERGED (branch `wo17/generated-parser`): the
ISC parser is now generated from the canonical ruby `.parg`
(vendored verbatim in `src/isc/grammar/grammar-source.ts`,
sha256-pinned with a no-drift test; refreshed via
`scripts/sync-isc-grammar.mjs`). Four modules: parg-reader (PARG
lexer/parser/compiler ported from Parsanol), peg.ts (table-driven PEG
interpreter + parsanol's CanFlatten semantics), actions.ts
(capture tree → IscDocument, each deliberate quirk carrying a
DEVIATION comment). `parseIsc`'s public API unchanged (parser.ts
re-exports the generated entry).

**Measured evidence (harness runs pasted in the PR body):**
- Capture trees vs the ruby artifact parser: **434/434
  byte-identical**.
- Documents vs the replaced hand parser: **434/434 identical**.
- Cross-grammar harness (generated on the ts side): **411/434 — the
  SAME 23 files and divergence-kind counts as the hand parser on the
  same day** (the gap is by design of the py normalizers: py re-sorts
  constraint kinds into fixed fields and lowers `none` to `""`; the
  incumbent sits at exactly the same 411/434).
- ts suite: 364 passed / 4 skipped / 0 failed; tsc + eslint +
  prettier clean; PR CI green incl. the ISC parser parity (289 maps),
  conformance matrix, Node 20/22.

**Owner-flagged findings (alignment decisions, not regressions):**
1. Three grammar extensions live only in the generated parser's
   documented `GRAMMAR_EXTENSIONS` block (corpus-proven dormant):
   `any_arg` item fallback (ruby DSL has it, canonical `.parg` drops
   it, rs copy keeps it); block-rule outside-brace `when` (ruby
   parses INSIDE-brace only — ts and py only outside: a newly-found
   cross-runtime divergence); hyphenated `run map.x-y` dep names
   (ts-only lenience; ruby rejects).
2. `\UXXXX` escapes: the grammar decodes them; hand-ts and py both
   mangle to `U`+digits. Six corpus maps use `\U` — the generated
   parser mirrors the incumbent for swap-safety; aligning all three
   runtimes is an owner decision.
3. Performance: the interpreter runs the full corpus in ~18 s
   (packrat-memoized; harness timeout 600 s).

**Status: WO17 steps 1-4 complete.** The py parser switch to
generated output remains the follow-up (the harness judges it; the
py normalizer stories above are resolved at the root by the same
move). Open sweep items: Hebraic cluster ruleset, W3 corpus adoption,
conformance depth, rs ruleset-only lib loading, EOF-spin hardening
(subsumed by the grammar round). Owner-held set unchanged.

## Py leg landed (2026-11-12): the py parser is generated from the same .parg

interscript-ruby PR #843 MERGED: `interscript-py/src/interscript/grammar/`
mirrors the ts milestone module-for-module (grammar_source.py vendoring
the SAME sha256-pinned .parg as ts; parg_reader.py; peg.py with two
py-specific additions — match-span recording for the byte-exact
from_source override key, and failure diagnostics rendering the two
suite-pinned hand-parser error messages from real parse state;
actions.py → IscDocument). The W1/W2 expansion, document model and
converter stay in isc.py; `parse_isc`'s public API unchanged; the ~900
-line hand scanner is replaced.

**Measured: py-vs-py parity driver 434/434 identical-to-hand (canonical
schema AND raw field-for-field, byte-exact from_source); maps harness
411/434 — same score, same 23 files, zero status flips vs the
incumbent; py failure set byte-identical to a pristine origin/main run
(18 pre-existing environment gaps, parser-independent); golden
additivity green in-suite.**

**Owner-flagged tradeoff**: interpreter perf — 434-file corpus ~86 s vs
hand's ~7 s (megabyte jamo/hanja maps dominate; golden gate 86→187 s,
suite 107→306 s). Documented in isc.py with closure-compilation
follow-ups that don't touch semantics. A fourth GRAMMAR_EXTENSION
(use-in-pass splicing, pinned by the py suite, corpus-dormant) joins
the ts trio; the cross-runtime `when`-position and dep-name divergences
remain owner alignment decisions.

**WO17 COMPLETE: all four steps landed. The .parg grammar is now the
single semantic source for the ts and py parsers, judged continuously
by the parity harness and the maps-CI four-runtime additivity gates.**

## Follow-ups landed (2026-11-12)

| Item | Status | Evidence |
|------|--------|----------|
| rs loader ruleset-only libs | RESOLVED-AS-WORKING | thai-latn loads fine in rs (transliterate probe reaches stage execution; only a missing-main stage errors, like any map). The capture "1 load error" was always var-ara-Arab-Arab-rababa (the ML-funcall map rs slice 1 rejects — consistent with the other runtimes). interscript-rs PR #15 MERGED: capture now reports load errors by map + cause instead of a silent count. |
| EOF-spin hardening | RESOLVED by 4b | The malformed-input repro that hung both hand parsers at 100% CPU now rejects cleanly on the generated parsers: ts `IscParseError ... Failed to match isc_source` (line 4:0); py rejected in 0.01 s (line 4:18). The hand parsers carrying the bug no longer exist. |
| Hebraic cluster sweep | DONE by the OWNER | maps PR #273 (ronaldtse) MERGED: `libs/hebr-latn.isc` + alalc-lad-Hebr-Latn-2025 / alalc-jba-Hebr-Latn-2011 refactored to the shared rulesets — 12 CI checks green incl. the four additivity gates. (The coordinator's agent was stopped before opening a competing PR; the owner landed their own version.) Corpus sweep on the merged corpus: 12,337/0. |
| Conformance depth (tool + first map) | DONE | maps PR #272 MERGED: `scripts/gen-row-tests.mjs` (rows JSON → provenance-marked ISC tests block; duplicate/empty validation; generated-by marker) + `scripts/row-sources/alalc-vai-Vaii-Latn-2010.json` + alalc-vai-Vaii-Latn-2010 extended 11 → 251 tests (240/240 rule froms covered, ZERO transcribe-vs-map divergences — the map proven a complete faithful transcription; 251/251 pass through the ts runtime; all 12 gates green). |

Remaining (unchanged): W3 corpus adoption (document evidence required);
py generated-parser perf (closure compilation); grammar alignment
decisions (when-position, U-escapes, the four documented extensions) —
owner-held. The conformance-depth tool is now available for the other
thin-test maps (hye 134/12, zgh 43/14, chr 85/18) as future work.

## Full close-out (2026-11-12): releases + issue triage

**Release round ("fully release all engine and runtimes")** — every
channel verified live against its registry API:
- interscript-maps **3.2.0** — rubygems + IR/isc artifacts with
  sha256 sidecars. First attempt pushed the gem from a STALE local
  origin/main ref (tag landed on the pre-bump commit, built 3.1.0,
  rubygems rejected the duplicate — registry safe, nothing wrong
  shipped); tag deleted and re-pushed at the true 3.2.0 commit.
  Lesson: `git tag <v> origin/main` AFTER re-fetching, and verify the
  tagged tree's version file before pushing.
- interscript (npm) **5.12.0** — the generated-parser release
  (lint/build/test/publish, provenance), verified via dist-tag.
- interscript (rubygems) **3.5.0** — parity closure + py generated
  parser + override-placement parity; full suite green.
- interscript (crates.io) **0.2.1** — capture load-error visibility;
  dispatch green on the first try (the publish.yml fixes held).
- interscript-py: PyPI remains owner-gated (publisher registration);
  the dispatch-ready workflow is in place (ruby #839).

**GH issue triage (68 open → 24 closed with evidence, rest triaged):**
- maps: 17 closed — every implementable system request verified at
  its exact requested id in the corpus (ava/sah/udm/syr+syc/oss/krc/
  kbd/chv BGN-PCGN Cyrillic set, odni-kur-2011, odni-bel as the 2015
  edition, bgnpcgn-prs-2007 + yaghoubi, bgnpcgn-pus-1968, iu-Cans-
  2013 with the itk-1976 source-gate noted), GHA currency (#177),
  the OGC 11-122r1 mapping fix (#50), the Arabic diacritic-drop
  stage (#4, var-ara-Arab-Arab-rababa), the superseded GNDB
  analysis (#7). Left open honestly: #10 (tir tests — Tigrinya
  ፀ-rows still missing; gen-row-tests applies), #24/#28/#29/#30/#31/
  #32/#37/#43/#44/#47/#48/#49 (source-gated systems), #51-54
  (pinyin-IPA variants), #162/#172/#173 (source-gated).
- ruby: 5 closed — the Rust runtime (#325: the shipped crate), ML
  integration (#351, #528: the in-gem IMF runtime + published
  models), Khmer (#717: alalc-khm + khm-phonemic-1.0), title_case
  docs (#205: the site reference). Roadmap/design items stay open.
- ts: #10 closed (browser support matrix documented, PR #133);
  #111 (the zero-size-tensor conformance failure on real artifacts)
  under active root-cause investigation (agent campaign).
- site: 3 closed — architecture alignment (#214: Astro 7/Tailwind 4/
  Vue islands shipped), Web API docs (#103: api.astro + api-docs
  pages), ICL documentation (#85: the ISC language reference +
  Workflow_Extension). #215 (ICS distribution page) stays open as
  content-roadmap.
- interscript org (#2/#4) and the ruby roadmap/design set (#713-709,
  #633, #687, #541, #342, #335, #334, #329, #309, #253, #204, #200,
  #45, #31, #743, #740): roadmap/owner-domain, open.

**Site**: Libraries page rewritten (the Rust runtime section, the
current Ruby surface — the legacy secryst gem path superseded —
289→428 systems, the grammar single-sourcing note), interscript dep
^5.12.0, catalogue regenerated 428/428 (PR #234).

## ts #111 closed (2026-11-12): root cause + runtime defense

interscript-ts PR #134 MERGED; issue #111 closed. Root cause
(re-established from live evidence): fp16 graph I/O meeting the
onnxruntime-node binding — the issue-era fp16 exports shipped
encoder/logits tensors as float16; ORT's JS Tensor constructor
converts float16 feeds to a native Float16Array view on Node >= 24,
and the N-API binding reads that buffer as 0 bytes (`expected N, got
0`, size-independently; the issue's own arithmetic proves it: 288512
= 98x1472x2 fp16 elements). Node-version dependence verified live
(20/22 decode; 24/26 break). The windows.ts suspicion in the issue
body is exonerated.

The shipped artifacts were repacked to fp32-IO in place (WO79,
2026-10-21), so both conformance legs pass today — but the runtime
had zero defense. The fix: reject fp16 feeds with a named
artifact-contract error pointing at normalize_fp16_io.py, locked by
a 1KB fp16-IO regression fixture on both runtime branches (red
before the fix). Full suite 352 green; fp16 conformance leg green
post-fix; PR CI all green (rebased onto main post-dependabot).

**Artifact-side follow-up for the owner**: SPEC.md does not yet
mandate fp32 graph I/O — a SPEC line would make the runtime guard's
contract normative.
