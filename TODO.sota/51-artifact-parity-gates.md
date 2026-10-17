# WO51 — Artifact parity gates: the bf16/fp32 "export defect" case

Status: OPEN (decisive probe `run-066-single-parity` in flight)
Priority: blocks urd-diac-base, urd-g2p-base, fas-diac publishes (held)

## The anomaly

urd-diac-base: torch bf16 gate CER **0.0357** vs ONNX-fp32 artifact
**0.1391–0.2783** (~11% of rows cascade to garbage in ANY
ONNX/fp16/quantized decode). Same class seen on urd-g2p-base.

## Probes run (all in bucket `run-066-urd-diac-base/export/`)

| probe | verdict |
|---|---|
| probe3way (torch-bf16 vs torch-fp32 vs ORT-fp32, batched) | B≈A, C≠B → "export guilty" (misleading — see below) |
| probe_logit_diff v4 (single-row, manual byte ids) | enc gap **0.0**, per-step argmax **identical** all rows — torch≡ORT when fed identical single-row ids |
| fp16 re-export | 0.1938 — worse; precision is not the variable |
| dynamic int8 | 0.44 — dynamic quantization separately broken for byt5 decode (static-int8 fine) |

## Working hypothesis (probe_single_vs_batch.py, running)

The exported encoder takes **only `input_ids` — no attention_mask**.
Any batched decode that right-pads with id 0 corrupts encoder states;
single-row decode cannot. Explains every observation: probe3way
diverged only in batch-of-8; logit-diff agreed only single-row;
zipcheck-v8 (runtime = single-window) verified GOOD; "single-window
parity untouched".

**CONFIRMED (run-066-single-parity, 2026-10-17):**
`PAD_GAPS [0.048, 0.0769, 0.063, 0.1078, 0.0, 0.0541, 0.1338, 0.0607]`
— 7/8 rows' encoder states differ single-vs-padded-batch (0.0 rows =
longest-in-batch, nothing padding them); torch-batched-with-mask
reproduces the gate CER exactly (0.0352). Awaiting ort_single_cer to
close; every prior observation is explained by the missing mask.

**Remedies, pick per lane:**
(a) contract: IMF byt5 artifacts decode single-row (current runtime
already does) — write into IMF spec + gates; or
(b) re-export encoder WITH attention_mask input for batched serving.

## Permanent gate redesign (feeds WO52)

1. **Parity must evaluate in the runtime's actual decode mode.** A
   gate that batches when the runtime decodes single-row tests
   nothing.
2. Three-way probe is a release gate, not a debugging tool: record
   bf16/fp32/ORT CERs + row agreement in the artifact metadata.
3. Dynamic int8 is banned for byt5 seq2seq artifacts (recorded
   negative); static int8 (plane family) unaffected.
4. probe_logit_diff must use `tok()` encoding (manual `b+3` without
   trailing EOS is the known byt5 byte-table trap — v4 ran on garbage
   inputs; its engine-agreement result still valid, its CERs void).
5. parity-v7 verdict INVALID (torch half defaulted to the g2p
   checkpoint while zip was diac) — cross-model comparison; harness
   envs must pin both halves to the same run id.

## Release posture

urd/ara/fas publishes stay HELD until the single-parity verdict lands.
If export is exonerated: publish with the fp32 zip + recorded
three-way numbers; fp16 stays unpublished (worse, no benefit).
