# urd-g2p-base-1.0

Urdu grapheme-to-phoneme, base tier (run-059): byt5-base seq2seq on
the full 610K-pair humair025 corpus. IMF v1 fp32 (2.16 GB).

## Metrics (full 11,940-row test split, raw char CER)

CER **15.65** (urd-g2p-1.0 small tier: 15.78 baseline) — gate PASSED.
Normalized CER 10.75. Shipped-bytes parity: ONNX fp32 vs torch
cer_delta 0.024 on the 300-row sample, 70% row-exact.
