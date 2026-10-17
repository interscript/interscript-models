# WO51 — Artifact parity gates: the bf16/fp32 "export defect" case

Status: **CLOSED 2026-10-17** — artifact exonerated; the harness was the defect
Priority: unblocks urd-diac-base / urd-g2p-base / ara publishes (ship flavor = fp16)

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

**CONFIRMED + CLOSED (run-066-single-parity, 2026-10-17):**
`PAD_GAPS [0.048, 0.0769, 0.063, 0.1078, 0.0, 0.0541, 0.1338, 0.0607]`
— 7/8 rows' encoder states differ single-vs-padded-batch (0.0 rows =
longest-in-batch, nothing padding them); `ort_single_cer = 0.0352` ==
torch-batched-mask == gate; `single_vs_batched_agree = 1.0` on 300/300
rows. **The artifact was always correct; the maskless batched parity
harness was the entire defect.** No re-export required.

**fp16 recheck (run-066-fp16-single): `ort_single_cer = 0.0352`,
`single_vs_batched_agree = 1.0` — fp16 ≡ fp32 ≡ gate.** The 0.1938
"refutation" was entirely the poisoned harness. **Ship flavor: fp16**
(1.35GB) over fp32 (2.16GB), identical verified quality.

**Remedy adopted: (a) + (b) as capability.** Current artifacts ship
under the single-row decode contract (runtime already conforms;
contract now schema-enforced in recipes via `parity.mode`); the
framework exporter (WO52 M5) grows an attention-mask option for future
batched serving, gated by a batched-parity conformance fixture.

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

urd-diac-base: fp16 zip CLEARED (gate 0.0357 torch / artifact 0.0352
single-row). urd-g2p-base and ara int8 cleared by the same contract
(their zipchecks ran the real single-window runtime path). Publishing
waits for the complete ship set (WO52 M2 proof lane + fas run-077
verdict + relabel stage-2) per the owner's only-ship-when-complete
order — nothing ships half-fixed.
