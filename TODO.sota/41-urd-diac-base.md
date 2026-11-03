# WO41 — urd-diac-base: the untried base tier on diacritization

## Motivation

urd-diac-1.0 is SMALL-tier (1.42GB fp32 zip) at full-split raw CER
**0.0377** (11,940 rows, WO37 protocol). Every other task in the
portfolio has measured its base tier (urd-g2p-base PASSED at 0.1565
vs 0.1578 small; tha-g2p-base and fas-g2p-base shipped) — diac is the
only task where the tier lever remains unpulled. WO38's recipe
transfers 1:1: pretrained google/byt5-base, 3 epochs, bs 16 × accum 2,
lr 3e-4 cosine (200 warmup), bf16 autocast, MAXLEN 256.

## Arm

run-066-urd-diac-base — data `rababa-urdu-cc174b96/data-diacrit/`
(573,130 train pairs; 11,940 test), script
`train_urd_diac_base_hf.py` (epoch checkpoints + resume added — the
e12/run-062 lesson: a completed job with an unprocessed verdict is
lost work, and an overnight run without step-ckpts is lost training).

## Gate

Full-split raw CER < **0.0377** (urd-diac-1.0). Ship if PASS: int8
IMF export + torch/ORT parity (the run-059 export chain), staged zip
(name = owner's call). Fallback if MISS: epoch curve tells whether
capacity or data-quality — compare loss trajectory vs run-059's.

## Queue position

a100 contended: e12 (running) → HE decision tree (WO36 teacher v4 if
e12 misses AND the 500h slice is ready) → WO39 stage 2 (AR OOD, the
flagship gap) → **WO41** (last).

## Cost

≈ 5.5 GPU-h (run-059 measured 5h23m at the same scale).


## Verdict (2026-10-15): GATE PASS

run-066 full-split CER **0.0357 < 0.0377** (urd-diac-1.0),
word_acc 0.6981. Base tier confirmed on diacritization too. Ship:
fp32 IMF export (single-file-clean at base size) + repack tool +
publish — the urd publish chain applies verbatim.
