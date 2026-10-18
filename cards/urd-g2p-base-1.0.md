# urd-g2p-base-1.0

Urdu grapheme-to-phoneme, base tier (run-059): byt5-base seq2seq on
the full 610K-pair humair025 corpus. IMF v1 fp32 (2.16 GB).

## Metrics (full 12,699-row test split, raw char CER, row-mean)

CER **15.65** (urd-g2p-1.0 small tier: 15.78 baseline) — gate PASSED.
Normalized CER 10.75.

## Artifact parity (WO51 contract)

Single-row greedy decode, the runtime's actual decode mode: 500-row
probe recorded in the artifact metadata (the pre-WO51 batched
harness numbers were invalid — batched decode without an attention
mask measures nothing).

## License — RESEARCH-ONLY

The training corpus (humair025/urdu-g2p-dictionary) is
**non-commercial** (verified from the dataset card,
github.com/humair-m/urdu-g2p LICENSE). These weights are therefore
released **for research use only** — owner decision 2026-10-18
(recorded in `corpora/urd-g2p-dict.yaml` license_review). Code:
BSD-3-Clause.
