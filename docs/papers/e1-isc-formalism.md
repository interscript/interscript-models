# Executable Authority: The Interoperable Script Conversion Language and its Verifiable Corpus

**Draft 1 — WO76/E1 (LREC/COLING-class systems paper). Owner review before any submission.**

## Abstract

Transliteration standards — the romanization systems published by the
United Nations, BGN/PCGN, ALA-LC, ISO, and national authorities — exist
as prose tables that cannot be executed, tested, or compared. Every
implementation is an independent act of scholarly interpretation, and
no two agree in detail. This paper presents the Interoperable Script
Conversion language (ISC), a declarative formalism that turns authority
tables into executable specifications, together with a corpus of 295
encoded systems, a differential-testing methodology that establishes
byte-identical interoperability across independent runtimes, and a
frozen-conformance regime that extends the same guarantees to learned
components. We report: full cross-runtime parity over the corpus test
surface; an authority-completeness audit method that quantifies
coverage against primary catalogs (exhibited on ALA-LC, BGN/PCGN, and
ISO); an invertibility analysis of authority pairs; and the
certification pathway by which third-party implementations verify
conformance. The result is a shift in genre: the transliteration
standard stops being a document and becomes a package.

## 1. Introduction

A romanization table is a social convention with the form of a
function: source-script strings in, target-script strings out. Three
properties of the genre make it resistant to software practice. First,
the tables are ambiguous: the same authority publishes revisions,
variant rows, and pronunciation-dependent exceptions. Second, they are
underverified: no authority ships executable tests. Third, they are
uncompareable: two implementations of "the same" system have had no
mechanical way to discover their disagreements.

Prior work falls into three groups. Finite-state transducer toolkits
(foma, HFST, OpenFst) provide the formal machinery but not the corpus
or the authority-alignment discipline. Per-language transliteration
systems implement single standards and are validated anecdotally.
Library-level romanization code (ICU, language-specific gem/npm
packages) embeds unpublished interpretations of the tables.

ISC (the Interoperable Script Conversion language) is a declarative
language whose programs are authority tables: stages of substitution
rules over items, with zero-width context guards, priority composition,
and dependencies between systems. Its design goals are, in order:
fidelity to the authority document; executability; independent
reimplementation; and mechanical comparability.

## 2. The formalism

An ISC document declares a system (authority, language, source and
target scripts, a versioning year) and one or more named stages. A
stage body is a sequence of rule groups. The two composition operators
carry the semantics:

- `parallel` blocks apply all rules in a single left-to-right pass
  with longest-match priority; duplicate matches resolve
  last-declared-wins. Parallel blocks are the default and map directly
  onto the authority-table genre: each table row is one rule.
- `before`/`after` guards attach zero-width lookbehind/lookahead
  assertions to a rule; they are not consumed. Word-final consonant
  columns ("the second romanization") are expressed as guards on the
  word boundary rather than as separate rules.

Items are literals, character ranges and classes, groups, optional
items (`maybe`), captures with positional references, and named
stdlib calls for operations beyond finite transduction (sorting,
casing, and — the extension point for learned components — external
function calls such as vocalization).

Two properties of the formalism do most of the work. First, rules are
*local*: a table row translates to one rule, and the row order of the
authority document is preserved in the encoding, which makes
whole-document transcription auditable. Second, contexts are
*zero-width*: the guards that express positional columns (initial vs
final) do not consume text, which keeps the encoding compositional and
the runtime implementations independent.

## 3. The corpus

The Interscript corpus encodes 295 systems from the UN Working Group on
Romanization Systems, BGN/PCGN, ALA-LC, ISO (9, 233, 233-3, 259, 7098,
843, 9984, 9985, 11940, 11941, 15919), ICAO, ODNI, and 23 national
authorities. Each system names its authority document; each encodes
the document's own worked examples as embedded tests.

The corpus is governed by an authority-completeness audit: for each
authority, the official catalog is captured from the primary source
and diffed against the corpus. Every difference is either an encoding
work item or a cited out-of-scope entry. Exhibit: the ALA-LC catalog
(78 tables) diffed to 30 encoded and 48 gap systems; the BGN/PCGN held
document set (55 systems) diffed to 17 gaps. The audit converts
"coverage" from an assertion into a ledger.

## 4. Interoperability by differential testing

ISC is implemented by three independent engines — Ruby, TypeScript,
and Python — with no shared code. The interoperability contract is
established in three layers:

1. **Grammar conformance.** All 295 documents parse in all engines
   (CI-enforced on every change).
2. **Embedded tests.** Each document's authority-derived examples pass
   in all engines.
3. **Cross-runtime parity.** A test-vector surface of 7,388 cases
   agrees byte-for-byte across the Ruby and TypeScript interpreters,
   CI-enforced; the Python engine reports measured coverage against
   the same surface.

Disagreements at any layer block merge. In practice the differential
surface functions as the specification's executable form: where the
prose standard underdetermines behavior (rule priority, duplicate
rules, context composition), the engines' agreed behavior is pinned as
normative vectors and promoted into the specification text.

## 5. Invertibility and system comparison

The corpus representation makes two classical questions mechanical.
Invertibility: composing a system with its reverse over the embedded
test surface yields a per-pair losslessness verdict; of the 10
authority pairs published with both directions, exactly one round-trips
losslessly, with the distinguishing examples enumerated. Equivalence:
a checker probes two systems over generated inputs and emits the
minimal distinguishing corpus, turning "these two standards are the
same" from an opinion into a report.

## 6. The certification pathway

The conformance suite ships as an artifact: frozen input/output
vectors per system, generated from the reference implementation and
hash-pinned. Third-party runtimes self-certify at three levels — parse
conformance, embedded tests, and frozen vectors — with the full
cross-runtime surface as the fourth. The same regime extends to
learned components (Section 7): a neural model ships with frozen
vectors that every runtime must reproduce byte-for-byte.

## 7. The learned extension

Roughly a dozen corpus systems target languages whose orthography
underdetermines the romanization (abjads: Arabic, Hebrew; abugidas:
Thai, Khmer). ISC systems declare an escape hatch (a function call
directive) at which a trained component supplies the hidden reading.
The component is governed by the same contract as the rules: pinned
artifacts, frozen vectors per runtime, and externally validated
benchmarks. This division — rules where the authority decrees, models
where it underdetermines, both under one proof regime — is the
paper's central design claim.

## 8. Conclusion

Authority romanization tables can be executable specifications. The
ISC corpus, its differential-testing regime, and its certification
pathway demonstrate the full pipeline at corpus scale, and the
completeness audit converts the path to full coverage into a counted
ledger rather than an aspiration.

## References (to complete)

- UN UNGEGN romanization resolutions and leaflets.
- BGN/PCGN Romanization Systems and Policies.
- ALA-LC Romanization Tables (Library of Congress).
- ISO 9, 233, 259, 7098, 843, 9984, 9985, 15919.
- ISO 24229 (system code convention).
- foma / HFST / OpenFst; ICU transform framework.
- SadeedDiac-25; ReNikud; sequitur G2P.
