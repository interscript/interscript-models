# WO79 — fp16 artifacts cannot run on ruby/ts; the IO-boundary fix

Status: **DIAGNOSED** (2026-10-21, by the C1 conformance matrix on its
first live run — the gate caught a shipped-artifact defect)

## The findings

1. **ruby**: `Unsupported element type: float16` — the onnxruntime gem
   materializes outputs through numo, which has no Float16 type. The
   fp16 artifacts (urd-diac-base-1.0, fas-diac-base-1.0) cannot execute
   at all. The shipped gem cannot run the shipped base models.
2. **ts**: urd-diac-base 12/12 mismatched; output for `سربراہ` is
   `�q��q…` — fp16 bytes interpreted as fp32. Systematic corruption at
   the encoder→decoder boundary.
3. **py** (reference): fas-diac 1/12 flipped in CI but 12/12 byte-exact
   when regenerated locally — fp16 near-tie argmax is sensitive to ORT
   build/threading. The generator pins `intra_op_num_threads=8`; CI's
   ORT build resolves ties differently.

## Root cause

The fp16 export leaves the graph IO in float16 (`last_hidden_state`,
`encoder_hidden_states`, `logits` are elem=10; only `input_ids` is
int64). Python ORT transparently widens fp16 outputs to fp32 numpy —
so the reference path already decodes the boundary in fp32. Every
other runtime must either reimplement that luck or break.

## The fix (recommended): normalize at the export, not per-runtime

Exporter (export_imf_hf.py) wraps the fp16 graph outputs in
`Cast(to=FLOAT)` — weights stay fp16 (size unchanged), all graph IO
becomes fp32, every runtime executes the same reference math with zero
per-runtime code. Then:

- re-export the fp16 artifacts, re-upload (sha256 changes → index
  digest + sidecar update; artifact locator unchanged)
- ruby/ts run the matrix unmodified; py stays the reference
- determinism: sessions set `intra_op_num_threads=1` everywhere
  (including the vector generator) — single-row greedy + fp32 boundary
  + single-thread = environment-independent byte-exactness; all vector
  sets regenerate under that configuration
- CONFORMANCE.md gains the determinism clause

## Alternatives rejected

- per-runtime fp16 handling: three implementations (ruby needs raw
  OrtValue casting the gem does not expose; ts needs IEEE-half
  conversion; ongoing tax on every new runtime)
- fp32-only conformance tier: concedes that shipped fp16 artifacts are
  undistributable — unacceptable

## Owner decision needed

Re-exporting changes artifact bytes → new sha256s → index digest
update. Locator and model ids unchanged; decode math is the reference
math python already produces. Recommend proceeding; awaiting the call.
