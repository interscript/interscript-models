# Model BOMs (SPDX 3.0-style)

Every shipped model in this registry carries a **Model BOM**: a
self-contained SPDX 3.0-style JSON document formalizing the provenance the
org already records — artifact sha256/size/urls, sha-pinned training-data
splits, `trained_from` chains, licenses, and eval metric references.

## What goes in

| BOM element | registry field(s) | SPDX 3.0 form |
|---|---|---|
| the model | `models.yaml` entry (or a gated-pending entry in `bom/lineage.yaml`) | `Package` (checksums, license, release asset refs) |
| task/precision/kind/parity | `models.yaml` | `Package.x-interscript` extension |
| eval metrics + protocol + source | `models.yaml` `metrics` | `Package.x-interscript.evaluations` |
| training corpora | `bom/lineage.yaml` `corpora` -> `corpora/*.yaml` | `Dataset` (split `sha256` pins as checksums) |
| training-data dependency | implicit | `Relationship dependsOn` (model -> corpus) |
| `trained_from` chain | card/TODO lineage notes; teacher model ids | `Relationship descendantOf` (model -> teacher Package) + `x-interscript.lineage` notes |
| compliance gate state | `bom/lineage.yaml` `gate` (gated-pending models) | `Annotation` (verbatim verdict + records path) |

Generation is deterministic given the registries (the only varying field is
the creation timestamp carried in `creationInfo`/`documentNamespace`):

```
python scripts/generate_model_bom.py --model heb-vocalized-plane-3.0
python scripts/generate_model_bom.py --model urd-vocalized-2.0
python scripts/generate_model_bom.py --all      # every bom/lineage.yaml entry
```

Output: `bom/<model>.spdx.json` + `bom/<model>.spdx.json.sha256` (the house
sidecar pattern).

## Distribution

- **Shipped models**: the BOM (+ sha256 sidecar) is attached as an
  additional asset to the model's **existing** release tag. The ship
  runbook is unchanged — the attach is a follow-up step after the release
  exists.
- **Gated-pending models** (e.g. `urd-vocalized-2.0`): no release exists
  and none may be created; the BOM lives in `bom/` as the pending record.
  By owner law, gated-pending BOMs carry **no artifact sha256/urls** —
  the `models.yaml` ship entry is created at ship time with real artifact
  data (TODO.sota/92). The document records the recorded gate verdict
  (Clause 16(e) FAIL, 2026-11-23) and the public-only lineage instead.

## Format notes

- SPDX 3.0-style graph serialization (`@graph` of `Package` / `Dataset` /
  `Relationship` / `Annotation` elements), `spdxVersion: SPDX-3.0`,
  `dataLicense: CC0-1.0`. SPDX 3.0's Dataset profile and relationship
  vocabulary express sha-pinned data lineage and trained-from chains
  natively; registry fields are preserved verbatim under `x-interscript`
  extension blocks so nothing is lost in translation.
- This is deliberately a different format from the **package SBOMs** of the
  runtime repos (rs/ruby/ts/py), which use CycloneDX 1.6 JSON: package SBOMs
  ride each ecosystem's first-party CycloneDX emitter (`npm sbom`,
  `cargo-cyclonedx`, `cyclonedx-py`, syft), while model BOMs are generated
  from the org's own lineage registries, where SPDX 3.0's AI/Dataset model
  fits the recorded data. Both formats checksum-pin every dependency; both
  attach to releases with a sha256 sidecar.
