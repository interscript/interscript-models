# WO16 — ISC workflow-extension layer (spec for owner review)

Status: LANDED as ISC-WF-1 (maps docs/isc-wf-1.md) — ruby/py/ts
merged, pilots merged; rs in flight. Execution log below.
Authority: owner directive 2026-11-07 ("this is clearly a workflow
definition problem in ISC"); /goal directive 2026-11-07 ("finish the
ISC workflow-extension layer (WO16) end-to-end").

## Problem

ISC composes pipelines (`dependency` + `run`) but has no workflow
vocabulary for reuse-with-specialization. The corpus paid for this gap
repeatedly, most recently in this campaign:

- **Duplicated machinery, drifted independently**: the Thai/Lao-style
  leading-vowel reordering was hand-copied across four ALA-LC maps and
  drifted; the repairs landed map-by-map (maps PRs #255/#256) instead
  of once.
- **Silent coupling through composition**: alalc-ben runs un-ben's
  stage; a semantics change in the base map changed the child's output
  (the ত্য → tj̱a incident, maps fix/unben-conjunct-order) — with no
  override mechanism to localize the difference.
- **A regression from the previous language**: the .imp era had
  `language()` selectors (ICAO 9303's multi-language map used them);
  the .isc migration split that map into per-language files (#168),
  losing the conditioning capability.
- **Inexpressible shapes**: ISO 9's annex-C structure (one table,
  per-language row subsets) and the khm multi-task `<latn>`/`<ipa>`
  variant pattern are both worked around by hand (consolidated maps,
  parallel training lines).

## The three constructs (proposed semantics)

All constructs are ADDITIVE: a map not using them behaves
byte-identically before and after (proof obligation: the full
conformance corpus, currently 11,048 embedded tests, must show zero
delta on untouched maps).

### W1. Named rulesets

A `ruleset` is a named, versionless (corpus-addressed) block of sub
rules — the reuse unit today forced into whole maps or comments.

```
ruleset romanize_descenders {
  sub "җ" "ž̧"
  ...
}
```

Semantics: a ruleset is expanded inline wherever referenced. It does
not run by itself; it contributes its rules to a stage.

### W2. Override/merge composition

A stage may import a ruleset and override rows:

```
stage main {
  use romanize_descenders
  override romanize_descenders {
    sub "җ" "ž̦"
    sub "қ" "k̦"
    ...
  }
  parallel {
    sub "а" "a"
    ...
  }
}
```

Merge semantics (precise, implementable):
- Effective rule set = imported rules + overrides + local rules,
  applied as ONE longest-match pass (the existing parallel semantics).
- An override row replaces an imported row on exact `from` equality
  (same from-string, byte-exact). No partial-prefix precedence.
- Overrides may ADD rows absent from the imported ruleset.
- `before`/`after` constraints attach to the row they are declared on
  and are evaluated against the input string at match time, exactly as
  today. Imported constraints are inherited with their rows unless
  overridden.
- Run order within a stage is unchanged (document order, run first).

### W3. Language conditioning

The .imp `language()` successor. A map declares the languages it
serves; rules may be conditioned on the declared language; the caller
selects:

```
system "ISO:rus-Cyrl:Latn:9-1995" {
  languages kur ckv abk tgz ...
}
stage main {
  parallel {
    sub "җ" "ž̦"  when kur
    sub "ҫ" "ş"   when chv
  }
}
```

Semantics: `when` guards evaluate against the language selected for
the transliteration call (`iscrs transliterate --language kur`);
unguarded rules always apply. Unmatched input under a selected
language passes through unchanged (existing pass-through semantics).
The conditioning is MAP-DECLARED (static), not text-detected —
detection remains the separate `/v1/detect` surface.

## Runtime landing (lockstep)

1. Grammar: isc.parg gains `ruleset`/`use`/`override`/`languages`/
   `when` (parsanol v2 single-source grammar).
2. Reference implementation: interscript-ruby (the conformance-proven
   runtime), including the Node/builder layer.
3. Then ts, py, rs in lockstep; each runtime's merge is gated by the
   conformance matrix AND the additivity proof (below).
4. Corpus CI gains a rule: maps using W1-W3 carry a marker so the
   additivity check can assert old-corpus byte-stability every run.

## Additivity proof harness

- Freeze a golden transliteration capture of all current maps ×
  embedded tests × the invertibility probe set, before any runtime
  change.
- After each runtime lands W1-W3, re-run the golden capture: zero
  delta on maps not using the new constructs = the merge gate.
- The khm-style corpus growth continues on the plain subset during
  migration.

## First adoption pilots (after owner sign-off of the spec)

- ISO 9: the nine descender rows switch to the printed primaries in
  the base map; a conditioned alternate set carries the cedilla
  renderings for the languages whose tradition uses them
  (replaces the WO08 variant ruling with expressed capability).
- ALA-LC Thai/Lao/Khmer/Burmese: the leading-vowel machinery becomes
  one shared ruleset with per-map overrides (retires the batch-B
  duplication).

## Non-goals / rejected alternatives

- Build-time generation as the composition layer (proposed and
  rejected by the owner 2026-11-07: the gap is a language gap).
- Text-based language detection inside maps (detection stays a
  separate surface).
- Un-undone semantics changes to existing constructs.

## Owner gates

1. This spec (the semantics above).
2. The grammar + reference implementation.
3. Each additional runtime.
4. Every corpus conversion that flips a map to the new constructs.

## Execution log (2026-11-08)

The owner approved the direction via the /goal directive (step 1:
"rebase-merge and continue to write code"). The normative spec was
written as **ISC-WF-1** (maps `docs/isc-wf-1.md`) — grammar additions
(§2), W1 expansion (§3, incl. dependency-referenced `use
alias.<ident>`), W2 merge semantics (§4), W3 conditioning (§5),
conformance requirements (§6), the additivity harness (§7), worked
examples (§8). One post-landing amendment: §4.2.6 pins where O lands —
overrides join the expansion's trailing parallel block (the whole
expansion shares one longest-match pass; replacement acts on the
source-script pass), otherwise append as stage-level rows. The TS
implementation initially appended overrides as bare stage rules; the
ambiguity was surfaced by the pilot design and closed in the same
landing (TDD: failing test first, interscript-ts wf1.test.ts).

| # | Step | Where | Evidence |
|---|------|-------|----------|
| 1 | Spec published | maps PR #259 (merge 0728c0d, `docs/isc-wf-1.md`) | repo docs |
| 2 | Golden capture + additivity gate | interscript-rs `tests/golden/isc-wf0.jsonl` (11,048 rows, 399 maps), `tests/golden_capture.rs`, `tests/golden/adopting-maps.txt`; merged (feat/golden-capture, f727eee) | `cargo test --release --test golden_capture` green (~163 s); `iscrs capture` reproduces |
| 3 | Grammar (isc.parg) | ruleset/use/override/languages/when productions; ruby worktree parses+compiles clean (parsanol 1.3.134) | `parsanol` compile run in interscript-ruby PR #834 CI |
| 4 | Ruby reference | interscript-ruby PR #834 MERGED (feat/isc-wf1-ruby 99b9d78 + 52ace5f) | 57 new examples; 138 isc + 305 full-suite examples 0 failures; corpus parse 408/408 before+after; ruby golden gate zero delta; `standardrb` clean |
| 5 | Python runtime | interscript-ruby PR #833 MERGED (interscript-py, b4a87ad) | 74 new tests; parse fidelity vs TS-built artifact 404/404; independent golden re-verification on fresh artifact: 11,043/11,048 byte-identical, 5 deltas = the pre-existing alalc-ell-2010 constraint rows |
| 5 | TS constraint fix | interscript-ts PR #124 MERGED (582d912) | root cause: `compileItem` class-context bug (imported charsets compiled as literal sequences → unsatisfiable lookarounds); 8 constraint units watched failing pre-fix; golden 11,048/11,048 post-fix |
| 5 | TS runtime | interscript-ts PR #125 MERGED (7b39941 + 5e20210 + a0d5970) | 120 isc tests; TS golden gate 11,048 rows byte-identical vs refactored corpus; CI matrix green |
| — | JSON-IR artifact build resolves WF-1 uses at compile time | maps PR #260 MERGED (89265b8) | full corpus build 408 maps; IR stays flat |
| 6 | Pilot: ALA-LC leading-vowel machinery | maps PR #261 MERGED (17e8034): new `libs/thai-latn.isc` `ruleset leading_vowel_digraphs` (327 rows common to alalc-tha-Thai-Latn-2011's 738 and bgnpcgn-tha-Thai-Latn-2002's 344 digraph rows; 159 byte-identical, 168 convention-differing, BGN/PCGN forms as base); bgnpcgn uses the ruleset + 17 map-only override rows; alalc overrides the 168 ALA-LC forms + 1196 map-only rows | per-pass compiled IR set-identical before/after (alalc 5 passes, bgnpcgn 9, row multisets equal); 11,048 golden rows zero new deltas through py AND ruby runtimes; pilot-map golden rows byte-identical |
| 6 | Pilot: ISO 9 descender rows — DISSOLVED | superseded by evidence, not done | owner-directed PDF validation (2026-11-07, `tools/iso9-1995-textlayer.txt`): the printed ISO 9:1995 table has ONE Latin rendering per row; the comma-below forms sit in the CYRILLIC column; the corpus map is faithful as-is. No variant ruling, no W3 conditioning needed. The goal's pilot premise ("comma-below-primary with cedilla language-conditioned") is void — changing the map would falsify the printed standard. |
| 7 | Website documentation | interscript.github.io PR #228 MERGED (`src/content/docs/Workflow_Extension.adoc`) | CI green |
| 5 | RS runtime | agent in flight (branch `feat/isc-wf1-rs`, grammar+builder+interpreter staged, tests/wf1.rs 21 fns) — sync note sent (trailing-parallel join §4.2.6, constraint fix, pilots corpus) | pending |
| — | Flaky ML funcall spec (blocks CI) | interscript-ruby PR #835 open: contract pinned against a local index fixture (offline-deterministic) | 3 CI failures today (Net::ReadTimeout/502 on the registry fetch), all this spec |

Verification commands (reproducible):
- `cargo test --release --test golden_capture` (interscript-rs) — additivity gate.
- `ruby -Ilib tools/isc_wf1_golden_gate.rb --golden ~/src/interscript/interscript-rs/tests/golden/isc-wf0.jsonl --maps-root ~/src/interscript/maps --parity` (interscript-ruby) — zero gated delta; only the 33 pre-existing Arabic `NotImplementedError` parity rows.
- `npx vitest run test/golden-isc-wf0.test.ts` (interscript-ts) — 11,048 rows byte-identical.
- `node scripts/build-json-ir-artifact.mjs <ts-dir> <out>` (maps) — 408 maps compile with WF-1 resolution.

Owner-gated leftovers (not mine to decide): npm/rubygems/crate release
versions for the WF-1-capable runtimes; rs merge timing; any future W3
corpus pilot (W3 remains exercised by runtime conformance fixtures
only, since both planned corpus pilots resolved to W1/W2 or dissolved).
