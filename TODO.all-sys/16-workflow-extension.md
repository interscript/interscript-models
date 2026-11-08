# WO16 — ISC workflow-extension layer (spec for owner review)

Status: SPEC DRAFT — no code until the owner approves the semantics.
Authority: owner directive 2026-11-07 ("this is clearly a workflow
definition problem in ISC").

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
