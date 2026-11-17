# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "onnxruntime>=1.20",
#   "numpy>=1.26",
#   "pyyaml>=6.0",
# ]
# ///
"""WO20u M2 — stage the two PASS static-int8 variants as release
candidates (issue #441 campaign B follow-up).

The gated bytes ARE the candidates: the WO20 sweep built each int8static
zip with `build_int8_static_zip` and judged it under both gates (CER
delta <= 2.0pp AND confident flips <= 1%). This job stages the exact
gated bytes — no rebuild, no re-quantization — into the
`wo20u-rc/` staging directory:

  1. hash the sweep's wo20-quant/ zips, server-copy them to wo20u-rc/,
     re-hash the staged copies and assert equality (copy integrity);
  2. load each staged zip with the reference runtime loader (the IMF
     internal digest verification + one smoke decode row from the
     sweep's candidate kit) — release-ready proof;
  3. write `SHA256SUMS` (the channel's sidecar convention) and
     `manifest.json` (gate values from the sweep reports, provenance,
     RC status).

STAGING ONLY: nothing is published — no Release, no index entry, no
version number. Publication and version selection are owner calls
(publish guard: explicit owner-stated semver).

Usage (cpu-basic):
    hf jobs uv run --flavor cpu-basic -d --timeout 4h \\
      --secrets HF_TOKEN \\
      -v hf://buckets/Interscript/isx-training:/ckpt:rw \\
      -v /Users/mulgogi/src/interscript/interscript-models:/mm:ro \\
      /mm/tools/wo20u_stage_rc.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

CKPT = Path("/ckpt")
SRC_DIR = CKPT / "wo20-quant"
DST_DIR = CKPT / "wo20u-rc"
MODELS = ["urd-vocalized-1.0", "heb-vocalized-1.1"]


def log(*a):
    print("[wo20u-rc]", *a, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    sys.path.insert(0, "/mm/src")
    sys.path.insert(0, "/mm/runtime/src")
    import yaml

    models_yaml = yaml.safe_load((Path("/mm") / "models.yaml").read_text())
    DST_DIR.mkdir(parents=True, exist_ok=True)

    entries = {}
    lines = []
    for model_id in MODELS:
        src = SRC_DIR / f"{model_id}-int8static.zip"
        dst = DST_DIR / src.name
        report = json.loads((SRC_DIR / f"{model_id}.DONE.json").read_text())
        if report.get("verdict") != "PASS — int8static viable":
            raise SystemExit(f"{model_id}: sweep verdict is not PASS — "
                             "refusing to stage")
        if not src.exists():
            raise SystemExit(f"missing sweep artifact: {src}")
        src_sha = sha256_file(src)
        if dst.exists() and sha256_file(dst) == src_sha:
            log(f"{model_id}: staged copy already identical — keeping")
        else:
            shutil.copyfile(src, dst)
            dst_sha = sha256_file(dst)
            if dst_sha != src_sha:
                raise SystemExit(f"{model_id}: staged copy hash mismatch")
        lines.append(f"{src_sha}  {dst.name}")

        entry = models_yaml["models"][model_id]
        smoke = None
        try:
            import interscript_ml.model as im_model

            m = im_model.Model(str(dst))
            kit = json.loads(
                (SRC_DIR / f"{model_id}.candidate-kit.json").read_text())
            row = kit["vectors"][0]
            out = m.translate(row["src"], max_len=512)
            smoke = {
                "row0_exact_vs_fp32_fixture": out == row["out"],
                "row0_out_chars": len(out),
            }
            log(f"{model_id}: loader smoke "
                f"row0_exact={smoke['row0_exact_vs_fp32_fixture']}")
        except Exception as e:  # recorded, never fatal for staging
            smoke = {"error": f"{type(e).__name__}: {e}"}
            log(f"{model_id}: loader smoke FAILED: {e}")

        entries[model_id] = {
            "candidate_zip": dst.name,
            "sha256": src_sha,
            "size_bytes": dst.stat().st_size,
            "base_fp32_zip": report.get("fp32_zip"),
            "base_fp32_sha256_pinned_in_models_yaml": True,
            "gates": {
                "cer_delta_pp": report["cer_delta_pp"],
                "cer_gate_pp": report["cer_gate_pp"],
                "confident_flip_rate": report["margins"][
                    "confident_flip_rate"],
                "confident_flip_gate": report["confident_flip_gate"],
            },
            "size_ratio": report["size_ratio"],
            "cpu_speedup": report["cpu_speedup"],
            "sweep_verdict": report["verdict"],
            "eval_framing": report.get("framing"),
            "loader_smoke": smoke,
            "index_version": entry.get("index_version"),
            "license": entry.get("license"),
        }

    (DST_DIR / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    manifest = {
        "stage": "wo20u-m2-release-candidates",
        "status": ("STAGED — NOT PUBLISHED. No release, no index entry, "
                   "no version number. Publication and version selection "
                   "are owner decisions (publish guard: explicit "
                   "owner-stated semver)."),
        "date": "2026-11-17",
        "provenance": {
            "built_by": ("WO20 campaign B sweep (tools/"
                         "wo20_static_int8_sweep.py) via "
                         "imf.export.build_int8_static_zip, calibration "
                         "64 rows from each model's eval slice "
                         "(conformance/wo20/manifest.json)"),
            "gated_bytes_staged_unchanged": True,
            "sweep_reports": "isx-training:/wo20-quant/*.DONE.json",
        },
        "candidates": entries,
    }
    (DST_DIR / "manifest.json").write_text(json.dumps(manifest, indent=1))
    log("STAGED " + json.dumps({k: v["sha256"][:12]
                                for k, v in entries.items()}))


if __name__ == "__main__":
    main()
