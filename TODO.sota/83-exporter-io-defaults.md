# WO83 — Exporter defaults: fp32 graph IO always

Status: PLANNED · Plane B/C (WO79 follow-through — the decision is
recorded, the DEFAULT is not enforced)

WO79's owner decision: exporter-side fp16→fp32 graph-IO normalization.
The fix exists as a post-hoc tool (`tools/normalize_fp16_io.py`) and
was applied to urd/fas by hand. Future exports can still ship raw-fp16
boundaries unless the exporter itself defaults to normalized IO.

Goal: no export path can produce an artifact whose graph boundary is
fp16; the normalizer becomes the exporter's default, not a repair step.

Method:
- Fold the IO-normalization into `export_imf_hf.py` (interscript-train):
  weights may stay fp16; graph outputs always Cast(to=FLOAT), fp16
  decoder inputs narrowed via internal Cast, raw tensors internal.
- Publish guard: reject (or auto-normalize + record) any artifact whose
  graph IO carries fp16 — enforced in `src/pipeline/`, not by memory.
- Verification: one fresh export decodes reference-identically (torch
  vs artifact, ≥500 samples in shipped decode mode).

Acceptance: exporter default normalized; publish guard blocks raw-fp16
IO; a fresh export passes parity unchanged.
