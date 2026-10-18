# urd-diac-base-1.0

Urdu diacritization, base tier (run-066): byt5-base seq2seq on the
full 573,130-pair urdu-diacrit corpus. IMF v1 **fp16**.

## Metrics (full 11,940-row test split, raw char CER, row-mean)

CER **3.57** (urd-diac-1.0 small tier: 3.77 baseline) — gate PASSED.
Word accuracy 69.8%.

## Artifact parity (WO51 contract)

Single-row greedy decode, the runtime's actual decode mode: ONNX
artifact CER **3.64** — identical to torch on **500/500 rows**
(agreement 1.0; three-way bf16/fp32/ORT agreement 1.0). Batched
decode without an attention mask is outside the artifact contract
(CONFORMANCE.md).

## Conformance

The shipped runtime reproduces all 12 frozen vectors byte-exactly
(`conformance/urd-diac-base-vectors.json`).

## Data / license

Weights depend on the original training-data license (the urdu-diacrit
corpus; provenance in `corpora/PROVENANCE.md`, owner-approved ship
decision 2026-10-18). Code and weights: BSD-3-Clause.
