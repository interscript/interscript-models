# Rust runtime (parsanol-rs) + model inference via ort

New crate: interscript-rs. (a) MAP RUNTIME: execute compiled ISC via
parsanol-rs; conformance = the frozen fixtures in interscript-models/
conformance/ byte-identical. (b) MODEL INFERENCE: load IMF v1 artifacts
(encoder.onnx/decoder-kv.onnx/metadata.yaml; sha256 verify; byte+3
tokenizer, trailing EOS) with the ort crate — ONNX Runtime gateway —
greedy + KV decode; parity vs the Ruby/TS runtimes >= 500 samples
single-row greedy before shipping. (c) Optional: batched KV decode for
 labeling jobs (kv graphs are batch-safe; plain are batch=1-traced).

STATUS (2026-11-04): slices 1, 1.1 and 2 SHIPPED —
github.com/interscript/interscript-rs (slice 1 + sweep re-inclusion as
PRs #1/#2 lineage on main; slice 2 in review).

- (a) MAP RUNTIME: parses 404/404; corpus embedded tests 10,772+ pass
  (29 known aspirational failures across 9 maps, same under the other
  runtimes); full corpus sweep green including the dependency-stage
  case (alalc-ben) once the un-ben conjunct-order data bug was fixed
  (maps fix/unben-conjunct-order). Reverse chains implemented with
  Ruby-generated ground truth from a fresh origin/main clone (11
  tests, incl. the real alalc-bul map).
- (b) MODEL INFERENCE: IMF v1 loader (envelope, sha256 + byte_checksum,
  single-URL/parts/file:// resolution, atomic install) + ort greedy
  single-row decode (ort 2.0.0-rc.15 / onnxruntime 1.31). CONFORMANCE
  BYTE-EXACT: khm-phonemic-1.0 12/12, tha-phonemic-1.0 12/12,
  tha-g2p-lex-1.0 12/12 vs the frozen fixtures; fas/urd families skip
  pending their artifacts locally. >= 500-sample parity BEFORE SHIP
  remains a ship-gate for any rust-served artifact.
- (c) batched KV decode: NOT implemented (labeling-job optimization;
  future).
- Slice 3 (release): crates.io publish — VERSION AND PUBLISH = OWNER
  decisions; nothing pushed to any registry.
