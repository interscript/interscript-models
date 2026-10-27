# IS-1 v2 — the ISC language specification (normative semantics)

Status: **DRAFT v2** (2026-10-27) — accumulates the A4 rulings
(ruby PRs #818, #820, #821, #822, #823, #828; 22 frozen vectors in
`interscript-ruby spec/isc/semantics_spec.rb`). Each section below is
normative; the vector suite is its executable form.

## 1. The language

ISC (Interscript Specification Code) is a declarative language for
script conversion. A `.isc` file denotes exactly one conversion
function from an input script to an output target. One document, one
function: every runtime computes the same mathematical object.

## 2. Document structure

```
system "<AUTHORITY>:<lang>-<SrcScript>:<DstScript>[-<variant>]:<year>" {
  metadata { authority_id <id>  id <n>  language iso-639-3:<code>
             source_script <Scr>  destination_script <Scr>  [name "..."] }
  [aliases { <name> = <item> ... }]
  [dependency { ... }]
  stage <name> { <rule-items> }
  [tests { "<input>" -> "<expected>" ... }]
}
```

- **Metadata** fields are newline- or semicolon-separated inside the
  braces; `authority_id`, `id`, `language`, `source_script`,
  `destination_script` are required.
- **Embedded tests** (`tests { input -> expected }`) are normative
  data on the document. Ruling (batch 4): they are **never executed by
  `transliterate`** — the verification layer (conformance runner,
  artifact build) executes them.

## 3. Stage composition (batch 1, #818)

- A **sequence** block executes its rules in order; each rule consumes
  and produces the string.
- A **parallel** block is **single-pass longest-match**: one scan over
  the input, the longest applicable rule wins at each position.
- **Ruling**: duplicate rules in a parallel resolve
  **last-declared-wins** (deterministic; vector `tst-tie-1`).

## 4. Contexts (batch 2, #820)

- `before X` / `after Y` are **zero-width lookbehind/lookahead**: they
  constrain the match without consuming (vectors `tst-before-2`,
  `tst-after-2`).
- `not_before` / `not_after` are their negations.

## 5. Item algebra (batches 4–5, #822, #828)

- `any("abc")` — a character **set** of length 1.
- `any("0".."9")` — an **inclusive codepoint range**.
- `any_character` — any single character.
- `maybe(x)` — zero-or-one; **participates in longest-match**.
- `capture(x)` + `ref(N)` — the captured source text is substituted in
  the target (`ref` only in target position).
- **Concatenation** is `+` (whitespace-separated atoms in the DSL
  sugar).
- **No alternation operator exists.** Alternatives are separate rules.
- **Aliases** (`aliases { name = item }`) bind named item expressions
  at parse time and are usable in **both from and to** positions
  (batch 5).

## 6. Boundary (batch 4)

`boundary` is a **zero-width word edge** (regex `\b`-equivalent):
string edges match; mid-word never (vector `tst-item-4`).
`line_start` / `line_end` / `word_boundary` are the same class.

## 7. Run dispatch (batches 3, #821)

- `run stage.<name>` — execute a stage of this document.
- `run map.<dep>.stage.<name>` — execute a stage of a declared
  dependency (dependency-aliased dispatch).
- **Ruling (strict parse, #828)**: `run` accepts **no other form**.
  Stray identifiers anywhere in a stage body are a **parse error** — a
  typo'd map fails loudly (the batch-4 silent-no-op hazard is closed;
  the corpus gate passed 295/295 strict-clean, maps#207).

## 8. String-case and stdlib directives

- **Stage-level directives** (`downcase`, `upcase`, `title_case`,
  `compose`, `decompose`, `separate`, `unseparate`) execute at their
  rule position on the whole string (batch 4: downcase-then-sub
  ordering pinned).
- `rababa <kwargs>` is a **declared funcall directive**: kwargs are
  mandatory and passed through to the ML adapter.
- **Ruling (batch 5, #823)**: ML funcalls without a provisioned model
  raise a **named provisioning error**
  (`Interscript::ML::IMF::RegistryError` enumerating known ids) —
  never an accidental crash.
- **Ruling (strict parse)**: `run` takes no stdlib names — stdlib
  string functions are the bare stage directives; `run downcase` is a
  parse error (the accidental form, unpinned).

## 9. Charset and casing directives

`sub <from> to upcase` / `to downcase` uppercase/lowercase **the
matched text** (not the whole string).

## 10. Cross-runtime guarantee

Every section above has a frozen vector in
`interscript-ruby spec/isc/semantics_spec.rb`. The TypeScript and
Python engines compute the same functions (the C1 conformance matrix
byte-executes the corpus across runtimes). A divergence is a bug in
the runtime, not in this document.

## 11. Open items (tracked)

- The TypeScript/Python parsers' strict-parse adoption (the ruby
  grammar leads; the corpus gate holds all interim).
- The ML-adapter provisioning contract's deeper surface
  (rababa_reverse semantics).
- IS-1 v2 as a citable release (D2) — this text is its nucleus.
