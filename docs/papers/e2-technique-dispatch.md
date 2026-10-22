# Learning the Underdetermined: A Dispatch Doctrine for Neural Completion of Rule-Definable Script Mappings

**Draft 1 — WO77/E2 (resources & evaluation paper). Owner review before any submission.**

## Abstract

Authority romanization systems are rules; the languages they romanize
are not always rule-complete. Abjads omit vowels, abugidas imply them,
and the residual ambiguity must be resolved by a model — a component
that authorities do not govern and that the field has no shared
methodology for building. This paper contributes a dispatch doctrine:
an empirically derived mapping from (script class, ambiguity type,
data regime) to training technique, grounded in a negative-results
registry from a systematic campaign, two structural rules that govern
the composition of learned components with rule systems, and an
ambiguity-aware evaluation metric (valid-reading rate) that corrects
the systematic undercounting of single-reference diacritization
error rates. We report per-language results under external-protocol
evaluation for Arabic, Urdu, Persian, Thai, Khmer, and Hebrew, and we
release every verdict — positive and negative — in a machine-checkable
registry.

## 1. The underdetermination spectrum

Script conversion mappings form a spectrum. At one pole, the mapping
is a function the authority fully decrees: Cyrillic → Latin with a
published correspondence table. At the other, the source orthography
genuinely underdetermines the target: an Arabic skeleton (كتب) is a
*relation* over readings (kataba, kutiba, kutub, ...), a Thai
orthographic syllable underdetermines its tone, a Khmer cluster
underdetermines its vowel. The intermediate zone — where the authority
decrees conventions *conditioned on an inferred layer* — is where
learned components belong.

The design error this paper argues against is treating the whole
spectrum as one problem class: applying one neural recipe to every
language, or conversely, hand-rolling a new pipeline per language. The
dispatch doctrine makes the technique choice a function of measurable
properties of the language pair.

## 2. The doctrine

**Rule 1 — Vocalization is composition, not a sibling task.** An
unvocalized skeleton is a relation over readings; vocalization upgrades
it to a function, which the rule system then applies. The two must not
be conflated: romanizing a bare skeleton by convention (what
bibliographic systems do) is a different product from predicting the
hidden reading. Composition, not pipeline ad-hocery: the rule language
declares the call, the model fills the relation, the decode policy
selects among licensed readings.

**Rule 2 — Abugidas presuppose a reading.** Thai and Khmer
orthographies are positional syllabaries: vowel signs interleave with
consonant clusters, inherent vowels are implied, tone is computed from
orthographic class — and the major romanization convention (RTGS)
discards the tone that the orthography computes. The rule system is
deterministic *over an inferred layer*. The doctrine: lexicon-first
(dictionary hit-rate is the first-class metric), trained fallback for
novel tokens, and a rule composite for the convention; the three
target layers (toneless romanization, phonemic, phonemic + tone) are
tracked separately.

**The dispatch table** (script class × ambiguity × data regime →
technique), with the registry-defaulted form: lexical ambiguity
dominant → lexicon + morphology-conditioned SFT; phonotactic
reordering → byte-level seq2seq (ByT5-class); register variance →
register-stratified data; teacher availability → oracle relabel only
when teacher arms disagree; distillation only across decorrelated
teachers.

## 3. The negative-results registry

Four refuted techniques are recorded with the same rigor as positives,
each with its motivating failure:

- **Reinforcement learning for diacritization** is knowledge-limited at
  SFT convergence: the reward signal cannot exceed what the supervised
  model already knows.
- **CTC** cannot model Thai phonotactics: the conditional independence
  of CTC paths escapes the mode collapse of seq2seq training but
  plateaus far above the byte-level seq2seq baseline.
- **LLMs as label teachers** hallucinate diacritics at rates
  incompatible with training; banned by registry law, enforced by the
  pipeline validators.
- **Distillation on correlated teacher arms** transfers nothing: arms
  trained on the same data family agree on the same errors, leaving no
  oracle signal. Complementarity, not accuracy, predicts transfer.

## 4. Per-language programs

| language | task | technique (dispatch) | result | external protocol |
|---|---|---|---|---|
| Arabic | diacritization | ByT5 SFT + oracle relabel + noisy-student chain | DER 2.29 (canonical), 4.57 (fast tier) | SadeedDiac-25 |
| Arabic | news register | register-closure specialist | WER 8.85 | WikiNews-2024 multiref |
| Urdu | diacritization | base-model SFT | CER 3.57 | held-out docs split |
| Persian | diacritization | SFT + register work | CER 0.603 row-mean | 9,288-row docs split |
| Thai | G2P | lexicon-first + ByT5 fallback (CTC refuted) | PER 2.85 | published G2P suite |
| Khmer | transliteration | lexicon-conditioned ByT5 (in progress) | CER 27.4 → target < 15 | held-out corpus |
| Hebrew | nikud | plane architecture (data-gated) | DER 8.18 int8 | ReNikud protocol |

## 5. Evaluation: valid-reading rate

Single-reference DER counts every divergence from one gold reading as
an error, systematically undercounting models that produce *other
licensed readings*. We propose reporting valid-reading rate (VRR) —
the proportion of predictions that are dictionary-licensed readings —
alongside DER/WER, and evaluating multireference sets with
oracle-validity rather than best-match. The multireference
reconciliation failures that motivated this are documented with
examples.

## 6. Governance

Every claim in Section 4 links to a frozen artifact: a pinned corpus
(SHA-256, license-reviewed), a conformance-vector set reproduced
byte-exactly in three independent runtimes, a prediction file, and an
external protocol. Verdicts live in a machine-checkable registry that
the training pipeline consults; refuted techniques require a new
register entry to retry.

## 7. Conclusion

The dispatch doctrine converts per-language modeling from craft to
policy: measurable properties select the technique, the registry
prevents re-treading refuted ground, and the evaluation admits
legitimate ambiguity. The doctrine is released as registry defaults so
that the next language is a configuration, not a research project.

## References (to complete)

- ByT5; sequitur G2P; SadeedDiac-25; ReNikud; PyThaiNLP.
- The negative-results registry (interscript-models TODO.sota).
- RTGS; UNGEGN romanization; the ISC formalism (companion paper).
