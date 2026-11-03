# WO50 — IMF zip external-data contract (PROPOSAL, owner-gated)

## The blocker it removes

byt5-large's encoder cannot serialize single-file at fp32 or fp16
(2GB protobuf cap — WO45's three toolchain walls). The IMF v1 zip
contract (metadata.yaml + encoder.onnx + decoder.onnx, checksummed)
has no room for ONNX external-data sidecar files, so the
ara-diac-news-large tier (best: 3.5607/1.4588 first-alt) cannot ship
as an artifact.

## Proposal

IMF v2 (additive): zip MAY contain additional `encoder.onnx.data`-
style members; `metadata.yaml` gains a `graphs:` block listing every
ONNX member + its sha256; loaders (py/ts/ruby) materialize ALL
listed members to the session directory before ORT init and verify
each checksum. Backward compatible: v1 zips validate unchanged.

## Cost

~1 loader change × 3 runtimes + spec text + golden update. Owner
gate: the version bump (IMF v2) and the 3-runtime release train.

## Interim state

The large tier's numbers stand as measurements; the shipped client
artifacts are ara-diac-news-1.0 (+1.1) and urd-g2p-base-1.0 — all
single-file-clean.
