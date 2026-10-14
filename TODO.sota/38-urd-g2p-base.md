# WO38 — urd-g2p-2.0 candidate: byt5-base on the full humair025 split

urd-g2p-1.0 is the portfolio's weakest measured axis (CER 0.1578 /
33% word on its own held-out test, n=3000; WO37). The 1.0 recipe:
byt5-small, 3 epochs, 610K train pairs (humair025/urdu-g2p-dictionary
via rababa-urdu/data). The AR-proven upgrade path applies directly:
same data, same schedule, byt5-BASE.

Arm: run-056-urd-g2p-base — byt5-base, 3 epochs, bs 16 × accum 2,
max_len 256, gradient checkpointing, fp32→bf16 autocast. Gate: test
CER (raw char, the WO37 protocol) < 0.1578 on the FULL 12.7K-row
test split. Ship: byt5-base artifact export if passed (owner names
urd-g2p-2.0).

Fallback if missed: small was capacity-capped, base underperformed →
data-quality arm (dedupe/normalize) before any bigger swing.

Status: GATE PASS — run-059 full-split CER **0.1565 < 0.1578**
(a100, 5h23m; verdict processed 2026-10-14). Anatomy: nCER 0.1075;
errors = vowels 41.7% / consonants 34.2% / ins 24.2%. Ship chain:
int8 IMF export + torch-vs-ONNX parity job (run-059-export-parity,
RUNNING); zip staged as urd-g2p-base-staged — release name/number is
the owner's call.
