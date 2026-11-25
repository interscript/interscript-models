# IVRB — Interscript Vocalization-Romanization Benchmark

**Status:** active benchmark, v1 (2026-11-25). Normative for any published IVRB number.
**Scope:** the round-trip evaluation only Interscript can run — it owns both the
romanization-map corpus (the `interscript-maps` 457-system corpus) and the shipped
vocalization models (`models.yaml`).

## 1. Why this benchmark exists

Abjad languages (Hebrew, Arabic-script languages) write consonants and long
vowels; short vowels and some consonant distinctions are carried by optional
diacritics (nikud, haraqat). A romanization system is a **channel**: it takes the
vocalized (or unvocalized) native text and emits Latin text. Some systems encode
the diacritic information as Latin vowels and diacritics; others discard it.

Until IVRB, no one has published, per romanization system, **how much of that
diacritic information survives the system** and **which systems preserve the most
recoverable information**. The result directly informs romanization-system choice
for ML pipelines that transit through Latin (and back).

Only Interscript can run this: the measurement needs, in one place, the
vocalization models (the neural layer), the romanization systems (the map
corpus), and gold vocalized eval sets (the corpora registry).

This extends the WO37 doctrine ("we define the reference: publish our held-out
evaluation protocol + our artifacts' numbers") to the romanization axis.

## 2. The IVRB loop

Given a gold vocalized text `V` (native script with diacritics), its skeleton
`H = skel(V)` (the house stripping convention, §5), a vocalization model `M`
(native script → native script, adds diacritics), and a romanization system `S`
with forward function `f_S` (native script → Latin, from an Interscript map):

```
Direct arm (native space, the model ceiling):
    V_dir = M(H)                      the model re-vocalizes the skeleton
    CER_nat = CER(V_dir, V)           model quality, house protocol

Skel arm (system space, the no-information floor):
    CER_skel(S) = CER(f_S(H), f_S(V)) how far the bare skeleton's romanization
                                      sits from the gold vocalization's

Round-trip arm (system space, the measurement):
    CER_S = CER(f_S(V_dir), f_S(V))   the model's re-vocalization, observed
                                      through system S, vs the gold through S
```

The loop is a channel decomposition: the model recovers the diacritics from the
skeleton; the system either carries that recovery into Latin space or destroys
it. Both arms live in the same metric space, so their ratio isolates the
system's contribution.

**No reverse bridge.** A literal "romanize then re-vocalize the Latin" arm
would require a Latin → native bridge. The map corpus has none: exactly one map
in the corpus carries a curated reverse stage (`bgnpcgn-ukr-Cyrl-Latn-2019`),
and synthesized reverse output on the IVRB maps is unusable (verified: spurious
aleph insertion, wrong diacritics). The round-trip arm is therefore measured in
system space; §4 makes the metric unit-free. If a future corpus gains curated
reverse documents, a literal re-vocalization arm MAY be added as IVRB-2; it does
not retroactively change v1 numbers.

## 3. Metric definitions

All CERs are **corpus-level** (total character edit distance / total gold
character length over the full split), computed in the space stated per metric.
Character edit distance is Levenshtein distance over Unicode code points.

| metric | space | definition |
|---|---|---|
| `cer_nat` | native | `CER(V_dir, V)` — the model's direct vocalization quality; must be reported beside every IVRB row (comparability anchor) |
| `recovery_cer` (per system S) | Latin | `CER(f_S(V_dir), f_S(V))` — recovery CER: re-vocalized vs gold, both expressed through S |
| `skel_cer` (per system S) | Latin | `CER(f_S(H), f_S(V))` — the system's no-information floor: the error the system would show if no vocalization information existed |
| `retention` (per system S) | ratio | `1 − recovery_cer / skel_cer` — the fraction of the no-info error the model's recovery eliminates through S; **the headline metric** |
| `encode_rate` (per system S) | Latin | fraction of gold words `w` with `f_S(w_voc) ≠ f_S(w_skel)` — model-free system property: how often the system distinguishes a vocalized word from its skeleton |
| `mark_leak` (per system S) | Latin | fraction of rows whose `f_S(·)` output contains raw combining marks (§5 ranges) — the map fails to consume a diacritic and leaks it into the Latin output |

Conventions:

1. `retention` is a ratio of two CERs **in the same space**, so map-specific
   letter expansions (digraphs, dots) cancel; retention is comparable across
   systems. When `skel_cer = 0` (the system emits identical Latin for skeleton
   and vocalized text — it carries no vocalization information at all),
   `retention` is defined as **0**.
2. `recovery_cer` and `skel_cer` are corpus-level in Latin space; they are
   reported per system and MUST NOT be compared across systems directly (only
   their ratio is cross-system comparable).
3. `cer_nat` is corpus-level in native space and is the bridge to the shipped
   house numbers (§7); a large deviation from the shipped CER/DER invalidates
   the run.
4. **System ranking** = systems ordered by `retention` (descending) per
   language, with `encode_rate` and `mark_leak` reported beside each row.
   `retention` is the primary key; ties break on `encode_rate`.

## 4. Input sets (gold eval sets)

| language | set | rows | provenance | sha256 |
|---|---|---|---|---|
| urd | `urd-dia@v1#test` (`data-diacrit/test.jsonl`) | 11,940 | the WO37 held-out protocol set; bucket `rhtse/jobs-artifacts/rababa-urdu-cc174b96@data-diacrit`; rows `{"src": skeleton, "tgt": vocalized gold}` | `6d822ae70a383e5547ee82e841a65e83fac81ae47ff320999b8e6b101b1790bb` |
| heb | `hebrew-v4` test split (`test.jsonl`) | 1,864 | the crown-lineage held-out set (human-verified Nakdimon-derived split; heb-diac-1.x + plane family eval protocol); HF dataset `Interscript/hebrew-v4`; rows `{"src", "tgt": vocalized gold}`; skeleton derived from `tgt` per the crown protocol | `77e9b5dc3a3b9e7d70924e670f7361455b714ec8212e046662ea04187b153ccc` |

Every row is used whole (no sub-sampling) unless a `rows:` override is declared
with the run record. Persian (fas) joins when its gold-vocalized eval set lands;
the spec is written language-agnostic.

The harness re-verifies each sha256 at load time and refuses to run on
mismatch.

## 5. Conventions and comparability rules (house laws)

1. **Decode protocol:** single-row greedy decode, no batching, no repetition
   penalties, max_len 256 (the IMF runtime `translate()` default), ONNXRuntime
   CPU, `intra_op = inter_op = 1` (the WO79 byte-exact conformance law). No
   beam. Batched/masked-encoder modes are out of scope for v1.
2. **Byte table:** ByT5 byte-level, byte `b` → id `b + 3`, trailing EOS; the
   runtime owns this (the silent-garbage class of bugs is excluded by using the
   conformance-proven runtime, never hand-rolled encoding).
3. **Windows:** rows longer than 1400 UTF-8 bytes are decoded in word-boundary
   windows of ≤ 1400 bytes and stitched with the original separators (the
   crown protocol's windowing; the eval sets are sentence-length, so this is
   exercised only on outliers).
4. **Skeleton (`skel`):**
   - urd: the row's own `src` field (never re-derived).
   - heb: strip the NIKUD_MARKS set — sheva, hataf patach/segol/qamats, hiriq,
     tsere, segol, patach, qamats, holam, qubuts, dagesh, meteg, rafe, shin
     dot, sin dot (U+05B0–U+05BC, U+05BF, U+05C1, U+05C2, U+05C7; the
     rababa-evaluate set minus maqqaf U+05BE, which is spacing punctuation).
     Teamim (U+0591–U+05AF) are not in the v4 corpus targets (verified per
     corpus doc).
5. **Mark-leak ranges:** a Latin output "leaks" when it still contains any
   combining mark from the source script's diacritic ranges (Hebrew
   U+0591–U+05C7; Arabic U+0610–U+061A, U+064B–U+065F, U+0670, U+06D6–U+06ED).
6. **Determinism:** one engine version, one binary, one model set per published
   table; §9 pins everything. Any change in any pin is a new IVRB revision —
   numbers are never mixed across revisions.
7. **Honesty rules:** greedy decode only (the shipped beam numbers are not
   comparable); int8/fp16 artifacts are labeled with their precision in every
   table; negative or zero findings (e.g. a system with zero encode rate) are
   published, not dropped.

## 6. Romanization systems per language (maps corpus)

System ids are corpus map ids; the corpus is the single source of truth. v1
uses every corpus system whose source script matches the language ( heb: Hebr,
urd: Arab) — no cherry-picking.

| language | map id | system |
|---|---|---|
| heb | `din-heb-Hebr-Latn-31636-2018` | DIN 31636:2018 (the ISO 259-lineage scholarly system in the corpus) |
| heb | `icao-heb-Hebr-Latn-9303` | ICAO Doc 9303 (machine-readable travel documents) |
| urd | `alalc-urd-Arab-Latn-2013` | ALA-LC 1997 (2013 implementation) |
| urd | `bgnpcgn-urd-Arab-Latn-2007` | BGN/PCGN 2007 |
| urd | `din-urd-Arab-Latn-31635-2011` | DIN 31635-lineage (2011) |
| urd | `odni-urd-Arab-Latn-2015` | ODNI 2015 (personal names) |
| urd | `un-urd-Arab-Latn-1972` | United Nations 1972 |

Notes: (a) the corpus has **no ISO 259 Hebrew map**; the ISO 259 family is
represented by DIN 31636 (its 2018 edition is the German-national implementation
of the same scholarly tradition). (b) Hebrew-script maps for other languages
(`alalc-jba-*`, `alalc-lad-*`, `din-yid-*`) are other languages — out of scope.
(c) `heb_Hebr2Latn_ALA_1997` etc. exist only as ogc11122 aliases to maps the
corpus does not carry for heb — not runnable, excluded.

## 7. Model set (shipped vocalizers)

All shipped seq2seq vocalizers of the language, per `models.yaml` at the pinned
index (§9). The plane-factorized classifier family is a different runtime
contract (per-character classification, not generation); it joins in a later
revision and is excluded from v1 tables. Precision is labeled per row.

| language | model id | precision | shipped quality (house protocol) |
|---|---|---|---|
| urd | `urd-vocalized-1.0` | fp32 | CER 3.74 (WO37 protocol, 11,940-row split) |
| urd | `urd-vocalized-2.1` | int8-dynamic | CER 3.632 (WO37 protocol, 11,940-row split) |
| heb | `heb-vocalized-1.0` | fp32 | DER greedy 29.0 (crown protocol, 1,864-row split) |
| heb | `heb-vocalized-1.1` | fp32 | DER greedy 16.44 (crown protocol) |
| heb | `heb-vocalized-small-1.0` | fp32 | DER student greedy 30.37 (crown protocol) |

`cer_nat` from an IVRB run is computed with the same decode protocol as these
house numbers and serves as the run-validity anchor (a large deviation =
invalid run; report, do not silently normalize).

## 8. Home (why the models repo)

The benchmark lives in `interscript-models`: it owns the vocalization models
(the `models.yaml` index + releases), the gold eval sets (the `corpora/`
registry with sha-pinned splits), the decode protocols and ship gates (the
house laws IVRB reuses), and the WO37 "we define the reference" doctrine this
benchmark extends. The romanization side is an external input pinned by sha
(the maps corpus + the engines), exactly like any other dataset dependency.
`urdu-dev` was rejected as home: it is a private, access-controlled repository
(CLE license); IVRB is a published benchmark.

Layout: this spec (`docs/benchmarks/IVRB-SPEC.md`), the harness
(`benchmarks/ivrb/`), and per-run records (`docs/benchmarks/ivrb/RESULTS-v1.md`).

## 9. Reproducibility contract

A published IVRB table MUST carry:

1. **Data pins:** the §4 sha256s, re-verified at run time.
2. **Model pins:** model id + release tag + zip sha256 per model (from the
   pinned `models.yaml`; verified at run time).
3. **Engine pins:** the romanization engine (repo + commit + the binary/library
   identity), the maps corpus commit, the vocalizer runtime (repo + commit).
4. **Cross-validation:** the in-process romanization engine is cross-validated
   against the rs engine (`iscrs transliterate`) on ≥ 200 randomly sampled rows
   per system; the agreement rate is published with the table. A system below
   100% agreement is flagged, and its rows are excluded from ranking until the
   divergence is adjudicated.
5. **Protocol:** §5 verbatim (this revision's protocol id: `ivrb-v1`).
6. **Run record:** every table links a machine-readable run record (JSON) with
   per-metric values, wall time, and the pins above.

## 10. Known limitations (stated up front)

1. Greedy decode only — the vocalizer ceiling is understated vs beam (the
   house heb beam delta is material).
2. Corpus-level CER weights long rows more than row-mean would; stated per §3.
3. `retention` inherits the vocalizer's errors (a weak vocalizer depresses
   every system's retention uniformly); cross-system ranking stays valid,
   cross-model comparisons do not, and the spec does not make them.
4. Maps are consumed as-is: real-corpus mark-order variants can leak raw marks
   (the `mark_leak` column quantifies this per system; it is a genuine finding
   about map robustness, not a harness bug — verified against the map sources).
5. The gold sets are Urdu/Hebrew news-and-scripture domain; retention numbers
   are domain-conditional.
