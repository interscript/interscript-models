# WO45 — ara-diac-news-large-1.0 static-int8 export (the >2GB encoder)

## Blocker (measured 2026-10-14)

byt5-large's ENCODER cannot ship as single-file ONNX at any all-fp
precision: fp32 ≈ 2.4GB and fp16 ≈ 2.45GB serialized both exceed the
2GB protobuf message cap (`onnx.save` EncodeError reproduced). The
exporter's external-data escape hatch produces a stub + hundreds of
sidecar files — the IMF zip contract (metadata.yaml + encoder.onnx +
decoder.onnx, checksummed) has no room for sidecars, and extending it
means loader changes in all three runtimes.

The old staged "1.2" int8 zip was quantized FROM a 1MB stub encoder —
doubly broken and never shippable.

## Arm

`run-070-large-static-int8` — static quantization (QDQ, QInt8 weights
+ calibration activations) over ~500 WikiNews-train-style windows:

1. Export encoder/decoder fp16 (re-fuse decoder single-file; encoder
   stays external-data on disk in-job).
2. Calibrate with the runtime's own windowed inputs (the static-int8
   lever that WORKED in the DeepSeek campaign, vs dynamic-int8's
   measured 0.44-vs-0.16 CER catastrophe on urd-g2p-base).
3. `quantize_static` encoder → ~1.2GB single-file (fits); decoder
   likewise (parity gate decides decoder precision).
4. Zip + shipped-bytes parity (300 WikiNews windows, torch-vs-ORT
   first-alt WER/DER, positional feeds). Gate: engine delta ≤ 0.30
   WER on first-alt (fp16-vs-bf16 torch baseline; tighter if the
   data supports it) AND raw WER < 4.10 (must beat the shipped 1.0
   through the artifact).
5. Ship: `ara-diac-news-large-1.0` — precision "int8-static" in
   metadata (the models.yaml precision vocabulary).

## Fallback

If static-int8 parity misses the gate: the large tier's numbers
(3.5607/1.4588) stand as MEASUREMENTS in RESULTS/models.yaml, the
shipped client artifacts remain ara-diac-news-1.0 (base) + 1.1
(base-strip, pending its green zip parity), and external-data-in-zip
becomes a runtime-arch work item (WO16 parking lot candidate).

## Cost

Export + calibrate + parity ≈ 2-3 GPU-h (l4x1), no training.

## Status: PARKED at the toolchain wall (2026-10-14, three attempts)

1. ORT quantize_static: the calibrator's augment_graph must serialize
   the full 2.4GB fp32 graph → EncodeError (external-data not
   threaded through augmentation).
2. fp16 export + refuse: encoder serializes >2GB even at fp16 →
   EncodeError on onnx.save.
3. torch.ao quantize_dynamic before export: quantized attention
   modules return tuples with Nones — untraceable by
   torch.onnx.export (RuntimeError, Type Tuple[Tensor, NoneType...]).

Fallback clause fires: the large tier's **3.5607/1.4588** stands as a
MEASUREMENT (models.yaml/RESULTS); the shipped client artifacts are
ara-diac-news-1.0 + ara-diac-news-1.1 (base tier). Unblocking the
large artifact requires the loader contract to carry external-data
files inside the IMF zip (all three runtimes) — runtime-arch work
item, not an export fix.
