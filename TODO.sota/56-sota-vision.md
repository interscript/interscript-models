# WO56 — The SOTA vision: terminal definition and full task set

Status: **VISION** (owner-directed 2026-10-20) — every task below gets
its own WO before execution; negatives recorded with the same rigor as
positives.

## Purpose (the abstract statement)

Script conversion is the problem of moving language across writing
systems: transliteration (authority-decreed convention), vocalization
(recovering hidden readings — Arabic harakat, Hebrew nikud), and
grapheme-to-phoneme (script to sound). The world's conventions for
these exist as prose tables in standards documents — unexecutable,
untestable, and re-implemented differently by every consumer.

Interscript's purpose, stated abstractly: **turn social conventions
into computational objects with provable behavior.**

1. **Formalization** — the ISC language is the specification layer:
   declarative, executable transduction with context conditions,
   priority, dependencies, and a neural escape hatch for the
   underdetermined residue. ISC is to transliteration what BNF is to
   parsing.
2. **Verification** — one document denotes one function; every runtime
   computes it (cross-runtime parity, frozen conformance vectors,
   embedded tests). Reference-implementation plus differential testing
   as the interoperability guarantee.
3. **Learned completion** — where the authority table underdetermines
   the answer (abjads without vowels, abugidas with incomplete
   marking), the mapping is a relation, not a function; models resolve
   it under the same proof regime (pinned artifacts, byte-exact
   runtimes, declared metrics, license provenance).
4. **Distribution** — maps and models as verifiable, addressable,
   versioned artifacts: the reproducibility layer.
5. **Science** — the formalism, the corpus, the technique doctrine, and
   the benchmarks are publishable, citable contributions.

Terminal state (all five planes green) is the goal; "SOTA everywhere"
is plane B's row set.

## Plane A — Formal (the deterministic core)

| id | task | acceptance |
|----|------|-----------|
| A1 | Authority-completeness audit: enumerate the universe (UN 1968–2016, BGN/PCGN current, ALA-LC full language list, ISO 9/233/259/3609/7098/843/9984/9985, ICAO 9303, national systems: DIN, RTGS, Korean RR, HK/ROC…), diff vs the 293 in `maps/` | coverage matrix published; every gap encoded or cited out-of-scope with authority reference |
| A2 | Invertibility study: per-system round-trip analysis (map∘reverse = id?), loss conditions (homophone mergers, digraph ambiguity); generate reverse maps where authorities provide them | invertibility ledger for all systems; reverse maps shipped for every losslessly invertible one |
| A3 | Equivalence formalization: system-equivalence checker + minimal distinguishing test-corpus generator | tool in runtime + CI; justifies alias/dedup decisions mechanically |
| A4 | IS-1 v2: denotational semantics section — boundary, parallel priority, maybe composition, funcall typing; empty the ambiguity list | every runtime behavior derivable from the spec; zero open rulings |
| A5 | Conformance certification kit: vector generator from authority documents; levels L0 parse → L1 embedded tests → L2 frozen vectors → L3 full parity | a third party can self-certify; kit ships as a package |

## Plane B — Learned (the underdetermined residue)

Technique doctrine first (banked verdicts): CTC cannot model
phonotactics; RL is knowledge-limited at SFT convergence; LLM teachers
hallucinate haraqat (never); oracle relabel pays when teacher arms
disagree; distillation needs decorrelated teachers; greedy beats beam
on byte students; ByT5 is the byte-level backbone.

| id | task | target |
|----|------|--------|
| B1 | Encode the dispatch doctrine: (script class, ambiguity type, data regime) → recipe, as registry defaults | new language gets a recommended recipe automatically |
| B2 | Hebrew: close the data-supply asks (owner), plane large arm, learned-IPA v0 | ReNikud-protocol DER < 5 (int8 < 6) — beats published SOTA |
| B3 | Arabic: r8 noisy-student chain, r6-morph feature injection, register closure | SadeedDiac DER < 2.0; WikiNews WER < 8 |
| B4 | Urdu: commercial-license G2P data path (owner decision); diacritization push | diac CER < 3; G2P license cleared |
| B5 | Persian: register expansion (poetry, colloquial), Arabic-loan vocalization probe | hold CER < 0.7 across registers |
| B6 | Thai: hybrid latency tier, lexicon release, tiny contract | published PER < 2 |
| B7 | Khmer: Chuon Nath lexicon-conditioned learner (khmer-dict-spice) | CER < 15 (from 27.4) |
| B8 | Contribution proof: first 3 community languages through the 2-YAML path | framework story validated by outsiders |
| B9 | External-benchmark certification: every headline claim reconciled to an external leaderboard protocol package | no self-graded SOTA claims |

## Plane C — Verification

| id | task | acceptance |
|----|------|-----------|
| C1 | Model × runtime conformance matrix: every shipped model byte-exact in ruby/ts/py, CI-enforced | matrix green, sustained |
| C2 | Metric-convention enforcement: every metric in a gate declares convention + anchor | gate rejects undeclared metrics |
| C3 | Performance budgets in CI (decode latency, artifact size) | budgets enforced, regressions block |

## Plane D — Distribution

| id | task | acceptance |
|----|------|-----------|
| D1 | Python release (owner: PyPI publisher registration) | 0.2.x live; test-and-report, never nag |
| D2 | IS-1/ISC as citable standard: versioned spec releases, site pages, citation block | spec vN tagged; citable |
| D3 | Catalogue completeness on the site (maps + models + runtimes status) | every shipped object browsable |

## Plane E — Science

| id | task | acceptance |
|----|------|-----------|
| E1 | Paper 1: the ISC formalism + corpus + interoperability methodology | draft against LREC/COLING-class venue |
| E2 | Paper 2: technique dispatch for underdetermined mappings (the doctrine + per-language results) | draft with the full results matrix |
| E3 | Frozen benchmark artifacts: conformance suites + eval protocols as citable releases | artifact-evaluation-ready |

## Laws (unchanged, enforced by validators not memory)

PRs only, never commit main · versions/licenses/requirements are owner
decisions · no LLM as label teacher, ever · corpora pinned (dates or
versions, sha256) with PROVENANCE · UNVERIFIED/LicenseRef-* block
publish; owner waivers are `license_review:` records · data channel =
GitHub Releases only, never raw.githubusercontent · HF Jobs only
(--detach, --timeout ≥ 4h, step checkpoints, ≤ 2 concurrent GPU apps)
· single-row greedy decode contract unless the artifact carries a
masked encoder · ByT5 ids are byte+3 with trailing EOS · never delete
files you did not create · transcribe whole documents, every section ·
no fabricated claims — every number re-derives from a frozen artifact.
