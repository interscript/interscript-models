# WO52 — The unified Interscript ML framework (recipes + spine + registry)

Status: **IN IMPLEMENTATION** — owner-approved 2026-10-17
Progress: M0 contracts + M1 runner + M2 gates/planner merged (#294);
M4 recipes landed (ara-diac, urd-g2p + corpora registry + license
provenance — `corpora/PROVENANCE.md`). Remaining: M3 (pins: rows +
sha256 manifests; probe/zipcheck absorbed as gate inputs), M5
(models.yaml resolver in clients, conformance fixtures, exporter
attention-mask option, deprecate src/gpu/modal_*).
Priority: strategic — makes every future language/technique a config PR

## Diagnosis (honest)

We have three bodies of work that do not connect:

1. **`interscript-models/src/framework/`** — a real abstraction skeleton
   (registry pattern: register_data_module/evaluator/model_module,
   TrainingPipeline, trainers, exporters; "new task = one dir under
   src/tasks/"). Built for the custom-arch era (sinkhorn, muon, ride).
2. **`interscript-train/`** — where actual winning practice lives:
   standalone per-language scripts (train_urd_diac_base_hf.py,
   distill_oracle_hf.py, export_imf_hf.py, parity_*, probe3way.py,
   publish_model.py) hand-launched on HF Jobs for 70+ runs.
3. **The release chain** — models.yaml, repack_imf_metadata.py,
   publish_model.py, IMF spec, npm/gem/py/worker runtimes.

Every SOTA result of the last quarter came from (2)+(3) while (1) sat
unused — because the techniques that won (byt5 SFT + oracle relabel +
decode policy) are recipes over shared ops, not new model modules, and
the framework had no stage for corpus→gate→publish.

**Target:** one spine where the proven scripts become stages, a
language is a pair of YAML files, a technique is a registered stage,
and nothing merges without machine-checkable gates. Adopted from KLF
(kotoshu): `route: legacy_*` honest routing — the framework declares
the contract while proven scripts remain the engines until each is
absorbed. No big-bang rewrite.

## Architecture: five layers

```
L0 CONTRACTS      corpora/<src>.yaml          (sources, license, pins, splits)
                  recipes/<lang>-<task>.yaml  (stage DAG, gates, decode policy)
L1 SPINE          src/framework/ + pipeline/  (isxml CLI: corpus|train|gate|publish)
                  runner: HF Jobs launcher w/ laws encoded
L2 GATES          parity (runtime-mode), probe3way, zipcheck,
                  quality thresholds (from recipe), license, claims-from-JSON
L3 PUBLISH        GH Releases (parts + sha256) ← primary channel
                  HF model repos (canonical) + models.yaml registry stamp
L4 CLIENTS        IMF spec + conformance fixtures
                  npm / ruby gem / python / CF worker all resolve
                  model-id@major from models.yaml → download → verify → run
```

### L0 — Contracts (the contribution surface)

`recipes/urd-diac.yaml` (illustrative):

```yaml
id: urd-diac
task: diacritization        # diacritization | g2p | transliteration
corpora:
  train: urd-dia-data@2026-06   # corpus registry ref (pinned, sha256)
  test:  urd-dia-data@2026-06#test
model:
  family: byt5-base           # registered model module
stages:                       # ordered DAG; each stage = registered plugin
  - stage: sft                # → legacy route: train_urd_diac_base_hf.py
  - stage: decode_policy      # repetition penalty 1.2, no-repeat-3gram
gates:
  quality: {cer_max: 0.045}   # from recipe; registry keeps best-known
  parity:  {mode: single-row, agree_min: 0.98, three_way: true}
  license: [data, weights]
publish:
  channel: gh-releases        # law: never raw.githubusercontent
negative_results:             # recorded so nobody retries these
  - rl-rollouts (knowledge-limited at SFT convergence)
  - llm-teacher labels (haraqat hallucination)
  - dynamic-int8 (destroys byt5 decode)
  - ctc for thai phonotactics (plateaus ~70% PER)
```

### L1 — Spine

`isxml <stage> <recipe>` — four verbs. The runner encodes the
operational laws that today live only in memory/agents:
`--detach` always (attached runs die with the client), `--timeout 4h+`,
step checkpoints, explicit `HfApi` bucket sync (`repo_type=None`) on
every append, ≤2 concurrent big-GPU apps, literal job commands (no
IFS-split assembly), smoke run before any batch.

### L2 — Gates (hardened by WO51)

| gate | check | blocking |
|---|---|---|
| parity | torch vs artifact **in the runtime's decode mode** (single-row today) | yes |
| three-way | bf16/fp32/ORT CER + row agreement recorded in metadata | yes |
| quality | recipe thresholds vs test split | yes |
| license | corpus licenses resolved before training (micsell = blocked) | yes |
| claims | model card derived from eval JSON only (never hand-written) | yes |
| regression | new metrics vs models.yaml best-known | flags, owner waives |

### L3/L4 — Publish & mount

Unchanged from the shipped system (parts ≤2GiB, sha256 sidecars,
models.yaml stamp); new: runtimes gain one shared resolver
(`load("urd-diac@1")`) + the conformance fixture set becomes the
client-side contract (KLF's frozen-fixture rule: byte-identical or
doesn't merge).

## Contribution flows

| I want to… | I write | CI runs |
|---|---|---|
| add a language | corpora/*.yaml + recipes/*.yaml + eval gold | schema+license check, 20-min smoke train, gate dry-run |
| add a technique | stages/<name>/ plugin + unit tests | tests; then a recipe opts in; A/B vs gold |
| add data | corpus source entry | purity + license gate |
| add a client | IMF runtime impl | shared conformance fixtures |
| fix the spine | framework code | everything re-runs gate dry-runs |

## Migration (route:legacy — each step a PR, spine never breaks)

- **M0** recipes/ + corpora/ schemas + validators + `isxml` CLI skeleton (TDD)
- **M1** runner.py: HF Jobs launcher w/ laws; wraps existing scripts verbatim
- **M2** urd-diac recipe end-to-end (corpus→sft→gate→publish) — proves the spine on the best-understood lane
- **M3** gates module absorbs parity_*/probe3way/zipcheck + WO51 contract
- **M4** ara + fas recipes; corpus registry with licenses + pins; absorb oracle_relabel as a stage (WO39)
- **M5** models.yaml resolver in npm/gem/py + conformance fixtures v1; deprecate src/gpu/modal_* (Modal retired)

## SOTA matrix (2026-10-17)

| lane | best verified | vs external SOTA | gate status |
|---|---|---|---|
| AR diac | r6 WER 2.58 / CER 1.53 (canonical teacher); int8 1.0 zipcheck GOOD | competitive; r7 conventional-density drift (negative) | release-ready, wording owner-gated |
| UR diac | base CER 0.0357 (gate) | artifact number pending WO51 single-parity | HELD on WO51 |
| UR g2p | 0.16 CER (torch) | held since int8/fp32 divergence | HELD on WO51 |
| FA diac | retrain 0.65% vs docs 0.52% MISS | epoch arm undecided | owner decision |
| HE g2p/nikud | CER poor; label-filter + license-walled data | blocked on data supply | WO42/43 parked (owner asks drafted) |
| TH g2p | ByT5 direction; CTC refuted; small tier shipped | plane family latency-only niche | small-tier contract met |
| Oracle relabel (WO39) | p040/p029 complete, p047 resuming (fixed durable sync) | stage-2 fires on completion | running |

## Relations

- Consumes verdicts of [[51-artifact-parity-gates]] (gate redesign).
- Encodes laws from memory: no-LLM-teachers (recipe validator rejects),
  no-local-large-data, data channel = GH Releases, versions
  owner-decided, HF-not-Modal, library packages side-effect-free.
- KLF cross-pollination: adopted route:legacy + laws-in-code +
  fixture-frozen conformance; our advantages kept: pinned/sha256
  corpora, numeric parity gates, models.yaml registry, negative-result
  registry. Gaps found in KLF filed as kotoshu/kotoshu#251.
