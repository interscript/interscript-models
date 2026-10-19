"""Probe: why did heb-diac-1.1-fp32 fail the parity gate?

Runs the exact parity harness (torch reference vs ONNX kv decode) but
PRINTS the report numbers and sample outputs instead of raising.

    modal run --detach src/gpu/probe_heb_parity.py
"""

from __future__ import annotations

from pathlib import Path

import modal

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

IMAGE = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("torch==2.12.1", "transformers==5.14.1", "onnx==1.22.0",
                 "onnxruntime==1.23.2", "pyyaml>=6.0")
    .add_local_dir(str(REPO_ROOT), "/root/interscript-ml", copy=True)
    .workdir("/root/interscript-ml")
)

CHECKPOINT_VOLUMES = {"/volumes/rababa-checkpoints": modal.Volume.from_name("rababa-checkpoints")}
DATASET_VOLUMES = {"/datasets/rababa": modal.Volume.from_name("rababa-datasets")}
MODELS_VOLUME = modal.Volume.from_name("secryst-models")

app = modal.App("probe-heb-parity", image=IMAGE)


@app.function(
    cpu=8,
    memory=32 * 1024,
    timeout=2 * 3600,
    volumes={**CHECKPOINT_VOLUMES, **DATASET_VOLUMES, "/outputs": MODELS_VOLUME},
)
def probe() -> dict:
    import json
    import sys

    sys.path.insert(0, "/root/interscript-ml/src")

    for v in list(CHECKPOINT_VOLUMES.values()) + list(DATASET_VOLUMES.values()) + [MODELS_VOLUME]:
        v.reload()

    from imf.export import load_byte_seq2seq
    from imf.parity import reference_decode, run_parity

    ckpt = Path("/volumes/rababa-checkpoints/rababa_hebrew/run-s46-phonikud-plus/run-002-gold-ft/best")
    zip_path = Path("/outputs/imf/heb-diac/heb-diac-1.1-fp32.zip")

    model = load_byte_seq2seq(ckpt)

    pairs = []
    for line in Path("/datasets/rababa/nakdimon/test-imf.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        pairs.append((row.get("input", row.get("src", "")), row.get("target", row.get("tgt", ""))))
    pairs = [(s, t) for s, t in pairs if s][:40]
    print(f"[probe] {len(pairs)} pairs", flush=True)

    reference = reference_decode(model, [s for s, _ in pairs], max_len=128)
    for i in [0, 1, 2]:
        print(f"[ref {i}] {reference[i][:90]!r}", flush=True)

    report = run_parity(model, zip_path, pairs, max_len=128, reference=reference)
    print(f"REPORT: samples={report.samples} cer_ref={report.cer_reference}pp "
          f"cer_onnx={report.cer_onnx}pp delta={report.cer_delta}pp "
          f"mismatches={report.token_mismatches} passed={report.passed}", flush=True)
    return {"samples": report.samples, "cer_ref": report.cer_reference,
            "cer_onnx": report.cer_onnx, "delta": report.cer_delta,
            "mismatches": report.token_mismatches}


@app.local_entrypoint()
def main():
    print(probe.remote())
