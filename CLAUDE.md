# CLAUDE.md — interscript-models

The contract, zoo, and training spine for Interscript's neural layer.
Project purpose and direction live in README.md.

## Layout

- `models.yaml` + published `index-vN` tags — the resolution point for
  every runtime (sha256-pinned, split-part support).
- `SPEC.md` — IMF v1 artifact format (normative). `runtime/` — the
  conformance-proven reference loader; source of the frozen fixtures in
  `conformance/`.
- `recipes/<lang>-<task>.yaml` + `corpora/<source>.yaml` — a language is
  two YAML files plus a held-out eval set. Training config is data.
- `src/pipeline/` — the spine: contracts, gates (registry pattern),
  planner, runner (HF Jobs), publish guard, housekeeper.
- `TODO.sota/` — the campaign ledger: work orders, verdicts, negatives.
  Write the work order before doing the work; record negative results
  with the same care as positives.

## Ship gates (enforced by `src/pipeline/publish.py`, not by memory)

- Explicit owner-stated semver; green gates (quality / parity / license
  / conformance / regression); conformance fixtures present.
- Parity >= 500 samples in the SHIPPED decode mode (single-row greedy by
  default; batched mode only for artifacts exported with a masked
  encoder, `EXPORT_ATTENTION_MASK=1`).
- Metric conventions declared per metric (row-mean vs corpus-level CER).
- `UNVERIFIED` / `LicenseRef-*` licenses block publishing. Owner waivers
  are `license_review:` records — the license string itself never
  loosens.

## Hard rules

- PRs only, never commit to main. Versions are owner decisions — never
  pick a number.
- NEVER use an LLM as a label teacher for diacritization — they
  hallucinate haraqat. Enforced as a registry law, not a convention.
- Training on HF Jobs, never Modal: `--detach`, `--timeout >= 4h`, step
  checkpoints, bucket I/O via HfFileSystem mount; <= 2 concurrent
  big-GPU apps.
- Data channel: GitHub Releases + sha256 sidecar only — never
  raw.githubusercontent.com.
- License: BSD-3-Clause for all ML code and weights.
- The package is immutable at runtime: artifacts ship to Releases/HF;
  nothing writes inside the installed package.

## Runtime expectations

- ByT5 byte table: ids are byte + 3 with trailing EOS (id 1). Raw
  `text.bytes` is silent garbage; parity alone cannot catch this bug.
- Exports take only `input_ids` unless built with a masked encoder;
  batched padded decode on unmasked encoders corrupts encoder states
  (the WO51 finding).
