---
license: bsd-3-clause
language:
  - fa
tags:
  - diacritization
  - byt5
  - imf
  - persian
metrics:
  - cer
---
# fas-diac-base-1.0

Persian diacritization, base tier (run-077): byt5-small seq2seq on
the 445,869-pair HomoRich-derived corpus (CC0-1.0). IMF v1 fp16.

## Metrics (9,288-row docs split — byte-identical to the rababa-farsi
reference split; raw char CER, both conventions)

Row-mean CER **0.603%** · corpus-level CER 0.777% · word accuracy
**82.33%**. The historical 0.52% line is corpus-level under run-001's
undocumented recipe and does not reproduce (five controlled arms,
WO47); this is the best verified number.

## Improvement history (all closed with data)

epochs (3→6: 0.65→0.60) · backbone (small/base) · optimizer (docs-exact
5e-4/linear) · metric convention (row-mean vs corpus) · multi-arm
oracle distillation (run-080/081: arms too correlated, 10.0%
disagreement — MISS). Remaining untried: corpus rebuild to the raw
528,837 rows.

## License

Training data: HomoRich-G2P-Persian, **CC0-1.0** (verified via HF
cardData). Weights and code: BSD-3-Clause.
