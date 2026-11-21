# heb-vocalized-plane-3.0

Hebrew nikud diacritization, plane-factorized: ByT5-**base** encoder +
per-character nikud-class head, K=3 mask-predict greedy decode,
int8-dynamic ONNX, 416 MB. New Hebrew frontier: **6.6078 DER** on the
crown protocol (Nakdimon test, 1,864 human-verified rows) — **−1.57pp**
vs the shipped heb-vocalized-plane-2.0 (8.18).

First plane artifact trained with the WO92 curriculum: stage-1
weak-pretrain on 1.5M deduped knesset-v6 units (Dicta machine labels —
weak supervision only) COMBINED with the full gold corpus, then stage-2
gold SFT with the exact crown recipe. The s45 curriculum verdict
reproduces on the plane lineage and doubles its effect.

## Metrics (crown protocol — greedy, single-row, seq2seq_der)

| benchmark | value |
|---|---|
| Nakdimon test DER (greedy K=3, full 1,864 rows) | **6.6078** (2.0: 8.18) |
| parity vs fp32 ONNX reference (classification law #459) | DER delta **+0.0549pp** on 600 samples (gate ≤ 0.25pp) |
| eval slice | conformance/wo20/eval600/heb_eval_600.jsonl (sha-pinned) |

## Features

- `kind: plane` contract — same runtime family as the Arabic planes;
  K=3 mask-predict greedy decode, single-row.
- Parity per the classification gate law (#459): per-char flips under
  quantization are expected behavior; the quality criterion is the DER
  delta vs the fp32 reference (int8-dynamic measured DER-neutral,
  +0.0549pp).

## Provenance

- Training: WO92 stage-2 gold SFT
  (`train_hebrew_sft_hf.py`, run-094-heb-gold-sft, HF Jobs a100-large)
  resumed from run-093-heb-weak-pretrain best (stage-1: 1,500,000
  deduped knesset-v6 weak units + 50,303 gold combined, 1 epoch).
  Inventory inherited byte-identical (labels.sha `edd595d96d09`).
- Gate chain: crown-protocol DER 6.6078 (verdict.json) → export PASS →
  parity per #459 PASS → conformance 600 frozen vectors → publish guard
  PASS (version 3.0.0).
- sha256: `d6833fc79751ad39ee6a6a7d45632038997ec060955e46f77d39c1fdb848959a`.

## Data attribution (Schedule D convention)

- **Phonikud/phonikud-data** `knesset_nikud_v6` (MIT) — machine-labeled
  weak-pretrain corpus, deduped 2,667,695 of 5,329,211 lines (WO92
  prep). The CLE schedule does not apply to this lineage (no CLE
  material in the Hebrew corpora).
- **hebrew-v4** gold corpus (Interscript internal assembly: Nakdimon +
  Sefaria + distilled + expanded; 50,433 train / 1,864 held-out
  human-verified test rows) — the crown lineage's training and eval set.

## License

BSD-3-Clause (code + weights).
