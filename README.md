# interscript-models

The **contract** for Interscript's phonological layer — the normative
definition of what a "hidden reading" model is, and the zoo that
publishes models conforming to it.

Interscript turns the world's transliteration standards from paper
tables into executable, verifiable software. Authority schemes
(BGN/PCGN, ISO, UN/UNGEGN, ALA-LC, ICAO, ODNI, ...) are encoded once in
the ISC language; every runtime produces provably identical output; and
languages that rules cannot fully carry — Arabic, Urdu, Persian, Hebrew
diacritization; grapheme-to-phoneme — are served by neural models
published under the same proof regime: pinned artifacts, sha256
verification, frozen conformance vectors, byte-exact runtimes. Users
are libraries (MARC), media (subtitles), gazetteers (GeoNames), and
name pipelines that must romanize reproducibly under a named authority.

This repo owns three things and nothing else:

1. **The `models.yaml` index** — the stable URL every runtime resolves
   model ids against (with per-artifact sha256s and split-part support).
2. **The IMF v1 model-zip format** — the artifact contract:
   `metadata.yaml` + ONNX graphs + member sha256 manifest. The normative
   text is [SPEC.md](SPEC.md); the reference loader is [`runtime/` in this
   repo](https://github.com/interscript/interscript-models/tree/main/runtime).
3. **The model zoo + publish pipeline** — teachers from
   [secryst-train](https://github.com/secryst/secryst-train)
   are distilled, gated (parity written into the artifact), and released
   as index entries here.

## Verify us — every number re-derives

| Piece | Where |
|---|---|
| Benchmark | [Misraj/SadeedDiac-25](https://huggingface.co/datasets/Misraj/SadeedDiac-25) (auto-fetched) |
| Protocol CLI | `pip install interscript-ml-tools[sadeed]` ([PyPI](https://pypi.org/project/interscript-ml-tools/)) |
| Python runtime | [`runtime/`](runtime/) in this repo — the reference loader (PyPI distribution pending publisher registration) |
| Raw predictions, every frontier run | Release [`frontier-predictions-v1`](https://github.com/interscript/interscript-models/releases/tag/frontier-predictions-v1) |
| Teachers + provenance labels | Release [`teachers-arabic-v1`](https://github.com/interscript/interscript-models/releases/tag/teachers-arabic-v1) |
| Student artifacts | `models.yaml` (index-v12) — sha256-verified in every runtime |

    interscript-sadeed-eval score --preds <file> --data Misraj/SadeedDiac-25

The measurement ledger — every verdict with confidence intervals,
corrections, and provenance hashes — is [docs/RESULTS.md](docs/RESULTS.md).

## The system

```
interscript            deterministic transliteration maps + engines
(ruby · js · py)         │ maps that need vocalization dispatch to a
                        │ crystal through stdlib adapters (optional)
                        ▼
secryst crystals       Ruby gem · pip install secryst · npm i secryst
(secryst org)          implement IMF v1 + models.yaml — nothing else
                        │
                        ▼
interscript-models  ◄────── models/zips resolve through this index
(THIS repo)     ──────► golden sets: crystals diffed against each other

secryst-train          teachers (arabic · persian · urdu + hebrew docs);
(secryst org)          secryst's own product; students ship through the zoo
```

Dependency directions, stated once:

- **interscript-models depends on nothing.** It is the contract: an index,
  a format, golden sets, and release tooling.
- **Crystals depend only on the contract.** A crystal has zero
  interscript-core dependency — a TTS front-end can phonemize Khmer
  with `pip install secryst` and nothing else.
- **Engines depend on crystals only optionally.** An engine without a
  crystal simply cannot execute maps that declare a vocalization step.
- **Training is config-driven and lives here.** Recipes + corpora + the
  `isxml` spine (below) train and gate every model in this repo;
  teachers live in the train monorepos. This repo publishes the
  distilled students through the export gate.

## Models ready to use (index-v12)

Every entry below is a shipped, sha256-verified IMF v1 artifact on this
repo's GitHub Releases, listed in `models.yaml` and the published
`index-v12`, mirrored to Hugging Face (`Interscript/<id>`), and gated by
torch↔artifact parity in the runtime's decode mode. Metrics are quoted
from `models.yaml` (protocol + anchor recorded per metric; row-mean
CER unless stated).

| model | task | size | headline metric |
|---|---|---|---|
| `ara-diac-2.0` | Arabic diacritization | 2.78 GB fp32 | SadeedDiac-25 DER **2.29%** (beats GLM-5.2 2.69); WikiNews-2024 17.38 WER |
| `ara-diac-news-1.1` | Arabic news register | 2.16 GB fp32 | WikiNews multiref 8.85 WER |
| `ara-diac-small-2.1` | Arabic, fast tier | 1.42 GB fp32 | fullset DER 4.57 (teacher 2.29) |
| `ara-diac-plane-large-1.0` | Arabic, int8 fast tier | 0.87 GB int8 | DER 2.74 / WER 8.61 |
| `urd-diac-base-1.0` | Urdu diacritization | 1.35 GB fp16 | CER **3.57%** |
| `urd-diac-1.0` | Urdu, small tier | 1.42 GB fp32 | CER 3.74% |
| `urd-g2p-base-1.0` | Urdu G2P | 2.16 GB fp32 | CER 15.65% — **RESEARCH-ONLY** (non-commercial data) |
| `fas-diac-base-1.0` | Persian diacritization | 0.71 GB fp16 | CER **0.603%** row-mean / 0.777% corpus, 82.3% word-acc (CC0 data) |
| `fas-g2p-1.0` | Persian G2P | 2.78 GB fp32 | CER 1.6% |
| `tha-g2p-base-1.0` | Thai G2P | 2.78 GB fp32 | teacher PER 1.25% |
| `tha-g2p-small-1.0` | Thai G2P, int8 | 0.26 GB int8 | PER 2.85% (beam-4 12.06%) |
| `khm-latn-1.0` | Khmer → Latin | 1.42 GB fp32 | CER 27.42% / EM 59.66% |
| `heb-diac-plane-2.0` | Hebrew nikud, int8 | 0.42 GB int8 | DER 8.18% |
| `heb-diac-1.1` | Hebrew nikud, fp32 | 2.78 GB fp32 | DER 16.44% |

Quantized variants (int8/int4/fp16) ship as assets of their base
model's release. Hebrew remains data-supply-limited: newer lanes are
blocked upstream, not on models.

### Using a model today

Artifacts are plain public downloads; any IMF v1 runtime works
(single-row greedy decode: ids = byte + 3 with trailing EOS —
`conformance/CONFORMANCE.md`). The reference python loader is
`runtime/src/interscript_ml` (conformance-proven, source of the frozen
fixtures).

Runtime status:

| runtime | release | state |
|---|---|---|
| Python | reference loader in this repo (`runtime/src/interscript_ml`) | current; PyPI distribution pending publisher registration |
| TypeScript | `interscript` npm **5.9.0** | current — behaviorally identical to main, conformance matrix green; pins `index-v12` (no env override) |
| Ruby | `interscript` gem **3.2.0** | decode caveat — predates the 512-step cap and the UTF-8 scrub: outputs truncate at ~100 tokens and invalid UTF-8 raises instead of U+FFFD. Fine for short strings; for long documents use the reference loader or npm until a patch release |

All three pin `index-v12` by default — no override needed for the
models above. Python (`SECRYST_INDEX`) and ruby
(`INTERSCRIPT_ML_INDEX`) accept an override to track a newer index.

```python
from interscript_ml import Model           # reference runtime (this repo)
m = Model.load("urd-diac-base-1.0")        # resolves via the index, verifies sha256
print(m.translate("کلیدهای پرکینزمانند"))
```

Artifact notice (2026-10-21): `urd-diac-base-1.0` and
`fas-diac-base-1.0` were re-published with exporter-side fp16→fp32
graph-IO normalization — same weights, portable graph boundary (node
ONNX Runtime no longer corrupts fp16 bytes; the ruby loader, which
lacks Float16 materialization, decodes them). The re-published digests
are in `index-v12`; an index fetched before that date fails loudly on
sha256 verification and must be re-fetched.

## Not yet ready

In training, not shipped: the Arabic r8 noisy-student chain (stage 2),
the Khmer lexicon-conditioned arm, and the Thai lexicon-first arm —
each ships only after its stage-3 external-benchmark verdict clears
the gates. `urd-g2p-base-1.0` ships but is **research-only**
(non-commercial training data). `models.yaml` also carries
legacy/superseded generations (e.g. `ara-diac-1.0`, `layerdrop`,
`ara-diac-small-1.0/2.0`) that resolve via the index but are not
recommended for new use; the table above is the recommended set.

## Repositories

| repo | role |
|---|---|
| [interscript/interscript-models](https://github.com/interscript/interscript-models) | this — contract + zoo + isxml framework |
| [interscript/interscript](https://github.com/interscript/interscript) | ISC map DSL (the transliteration contract) |
| [interscript/interscript-ruby](https://github.com/interscript/interscript-ruby) | Ruby ISC gem — maps + `Interscript::ML` model runtime |
| [interscript/interscript-py](https://github.com/interscript/interscript-py) | Python crystal — live |
| [secryst/secryst](https://github.com/secryst/secryst) · [secryst/secryst-py](https://github.com/secryst/secryst-py) · [secryst/secryst-ts](https://github.com/secryst/secryst-ts) | **archived** original crystals (est. 2020; the ML ruby gem's default index URL is dead — override `INTERSCRIPT_ML_INDEX`) |
| [interscript/interscript-train](https://github.com/interscript/interscript-train) · [rababa-farsi](https://github.com/interscript/rababa-farsi) · [rababa-urdu](https://github.com/interscript/rababa-urdu) | archived origins of the train monorepo (full history merged there) |

`runtime/` in this repo is the conformance-proven **reference IMF
runtime** — the executable definition of the artifact contract, and the
source of the frozen conformance fixtures.

## Contributing a language or a technique (the isxml framework)

Training is config-driven: a language is **two YAML files plus a
held-out eval set**, never a fork of the pipeline.

- `corpora/<source>.yaml` — pinned, licensed dataset artifacts
  (rows + sha256; see `corpora/PROVENANCE.md` for the evidence and the
  license gate)
- `recipes/<lang>-<task>.yaml` — the stage DAG (sft, oracle_relabel,
  distill, decode policy), the gates (quality threshold **with its
  metric convention**, runtime-mode parity, license), and the
  negative-results registry so nobody re-treads a refuted technique

The spine validates everything before any GPU time is spent:

```sh
isxml validate                                  # contracts (CI-enforced)
isxml plan <recipe> --run <run-id>              # exact job argv, dry-run
isxml gate <recipe> --metrics m.json --parity p.json
isxml conformance --vectors conformance/… --zip model.zip
```

Standing laws are enforced by the validators, not by memory: no
LLM-teacher stages for diacritization, corpus pins are dates or
versions (never moving refs), held-out test splits mandatory,
`UNVERIFIED`/`LicenseRef-*` licenses block publishing, and publication
requires an explicit owner version, green gates, and frozen conformance
fixtures (`conformance/CONFORMANCE.md`).


## Direction (audit 2026-10)

1. **SOTA everywhere, per-language technique dispatch.** The isxml
   spine makes a language two YAML files and a technique a registered
   stage; per-language rows (Hebrew plane/IPA, Arabic noisy-student
   chains, Thai hybrid tiers, Urdu/Persian base models) land as config
   PRs gated by machine-checkable thresholds. Refuted techniques (RL
   for diacritization, LLM teachers, CTC for Thai phonotactics,
   stage-2 distillation on correlated arms) stay in the registry as
   negatives so nobody re-treads them.
2. **Contract-first distribution.** Every model ships only with
   provenance-encoded corpora, resolved licenses, >=500-sample runtime
   parity, and frozen conformance fixtures in every client runtime.
3. **The spec as the standard.** IMF v1 + the index + conformance
   vectors are the implementable contract; third-party runtimes adopt
   the contract, not our code.
4. **Ecosystem surfaces.** api.interscript.org (edge),
   interscript.org (front door), MARC / subtitles / GeoNames as demand
   channels.

## Environment (as implemented by every crystal)

`SECRYST_INDEX` (index URL or path; default: `models.yaml` on this
repo's main) · `SECRYST_CACHE` (default `~/.cache/secryst`). Cache hits
are re-verified against the index on every load.

License: BSD-3-Clause.
