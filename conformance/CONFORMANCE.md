# IMF conformance — the frozen-fixture contract

Every runtime that mounts an Interscript ML model (python, ruby,
typescript, the API worker) must reproduce a model's conformance
vectors **byte-exactly** under the declared decode mode. If a runtime
change alters any fixture output, the change does not merge — same
rule KLF runs on its tokenizers ("frozen fixtures are the conformance
contract").

## What ships here

| file | model | decode mode | rows |
|---|---|---|---|
| `urd-diac-base-vectors.json` | urd-diac-base-1.0 | single-row-greedy | 12 |

## Decode mode contract (byt5 IMF artifacts)

**single-row-greedy** — WO51 proved this is the artifact contract:

- encode: UTF-8 bytes, ids `byte + 3`, **trailing EOS (id 1)** appended
  (raw `text.bytes` without the table/EOS is silent garbage — the
  byt5-byte-table rule)
- encoder: one row per call, no padding, no attention mask (the
  exported encoder takes `input_ids` only)
- decoder: greedy argmax until EOS, 512-step cap
- output: tokens `t -> byte(t - 3)`, decoded UTF-8

Batched decode without an attention mask corrupts encoder states
(PAD_GAPS up to 0.13 observed) and is NOT part of the contract. A
runtime may batch only against an artifact whose encoder declares an
attention-mask input (future exporter option; gated by a batched
conformance fixture set).

## Running

```sh
isxml conformance --vectors conformance/urd-diac-base-vectors.json \
                  --zip /path/to/urd-diac-base-1.0-fp16.zip   # exit 0 = conformant
```

The vectors file schema is validated (`pipeline.conformance.validate_vectors`);
outputs compare byte-exact (no normalization, no CER tolerance).

## Adding fixtures for a new model

Generate vectors with the reference decoder against the shipped zip
(see `interscript-train/gen_conformance_vectors.py` for the pattern),
pin the models.yaml id + index_version, and note the source split +
its sha256 in the file. Model release gate (WO52) requires a
conformance file before a models.yaml entry ships.
