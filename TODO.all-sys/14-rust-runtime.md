# Rust runtime (parsanol-rs) + model inference via ort

New crate: interscript-rs. (a) MAP RUNTIME: execute compiled ISC via
parsanol-rs; conformance = the frozen fixtures in interscript-models/
conformance/ byte-identical. (b) MODEL INFERENCE: load IMF v1 artifacts
(encoder.onnx/decoder-kv.onnx/metadata.yaml; sha256 verify; byte+3
tokenizer, trailing EOS) with the ort crate — ONNX Runtime gateway —
greedy + KV decode; parity vs the Ruby/TS runtimes >= 500 samples
single-row greedy before shipping. (c) Optional: batched KV decode for
 labeling jobs (kv graphs are batch-safe; plain are batch=1-traced).
