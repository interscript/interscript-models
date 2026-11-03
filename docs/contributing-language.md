# Contributing a language — the 2-YAML path

Everything Interscript trains is **config-driven**: a language is two
YAML files plus a held-out eval set — never a fork of the pipeline.
This document is the complete onboarding; if you need something it
doesn't say, that's a framework bug — file it, don't work around it.

## What you bring

| you have | you contribute |
|---|---|
| An authority document (BGN/PCGN, ALA-LC, ISO, national standard) | a **map**: `.isc` in
[interscript/maps](https://github.com/interscript/interscript-maps) — deterministic, no model needed |
| A corpus of (input → output) pairs with a license | a learned model through the recipe path below |
| Both | both — the map is the deterministic layer, the model completes what the table underdetermines |

## The two YAMLs (in [interscript-models](https://github.com/interscript/interscript-models))

### 1. `corpora/<source>.yaml` — the pinned data

```yaml
id: mylang-dict
task: transliteration
sources:
  - kind: bucket
    id: Interscript/isx-training/run-NNN-mylang   # staged data
    revision: run-NNN-mylang
    license: CC-BY-SA-4.0        # SPDX code; LicenseRef-* blocks publish
    mount: /data-my
splits:
  train: {path: train.jsonl, rows: 10000, sha256: <sha256 of the file>}
  test: {path: test.jsonl, rows: 1000, sha256: <sha256>}
```

Laws: every row file is sha256-pinned; the license is an SPDX id or an
explicit `license_review:` block (owner waiver); provenance goes in
comments (who produced the data, from what upstream).

### 2. `recipes/<lang>-<task>.yaml` — the training contract

```yaml
id: mylang-diac
corpora:
  train: mylang-dict@<revision>
  test: mylang-dict@<revision>#test
stages:
  - name: sft
    route: legacy:some_trainer_hf.py   # or a registered stage type
    params: {EPOCHS: "3", BS: "16"}
    deps: [torch, transformers]
gates:
  quality: {cer_max: 0.10}
  parity: {agree_min: 0.98}
  convention: row-mean
```

Stages plan to HF Jobs (the planner translates params to the trainer's
environment); gates are enforced by `src/pipeline/gates.py` — quality,
parity, license, conformance, regression, graph-io, budgets. A gate
failure blocks publish; that is the point.

## The eval-set expectation

A held-out split your gate numbers are honest against — never rows the
model trained on. The regression gate compares against the registry's
best-known numbers; a worse candidate flags for owner review instead of
shipping silently.

## What happens on your PR

1. Contracts validation (`tests/test_pipeline_contracts.py` shape).
2. Gates run against your declared numbers.
3. Conformance: the model ships frozen fixtures (12+ vectors through
   the reference decoder) that the ruby/ts/py suites byte-execute.
4. Publish is owner-gated: explicit version, owner approval.

## A worked example to copy

The smallest complete path in the repo today: `khm-dict` +
`tha-phonemic-v3` (corpora) with the thai lexicon trainer — see
`TODO.sota/67-b6-thai-lexicon.md` for the full run log, and
`docs/naming/` for how models are named (names target the output
convention).
