# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "onnxruntime-gpu>=1.20",
#   "onnx>=1.17",
#   "numpy>=1.26",
#   "pyyaml>=6.0",
# ]
# ///
"""WO20 campaign B — static-int8 sweep on released fp32 artifacts (issue #441).

For each target model: fetch the shipped fp32 zip from its GitHub
Release (sha256 verified against models.yaml), build the int8static
variant with the shipped export path (dynamic-int8 encoder +
static-calibrated decoder, calibration from the model's own eval
slice), then judge fp32-vs-int8static under the SAME single-framing:

  - parity CER-delta on the eval slice (int8 gate: <= 2.0pp, WO03);
  - teacher-forced margin analysis with the fp32 zip as the reference
    (argmax flip rate; confident flips = flips at margin >= p10 of the
    reference margins, gate <= 1% of tokens — the shipped precedent);
  - conformance-kit rows where the model has a pinned kit (byte-exact
    count + CER delta reported; byte-exactness is the same-precision
    runtime contract, not expected across precision);
  - fixture rows (first 12 kit-style rows from the fp32 outputs) for
    models without a kit, emitted as candidate fixtures;
  - artifact size and KV-greedy decode latency (fp32 vs int8static).

A model failing tolerance keeps its fp32 artifact — the verdict is
recorded, nothing is published.

Usage (a10g-small, resume-safe: per-model DONE markers on the bucket):
    hf jobs uv run --flavor a10g-small -d --timeout 4h \\
      --secrets HF_TOKEN \\
      -v hf://buckets/Interscript/isx-training:/ckpt:rw \\
      -v /Users/mulgogi/src/interscript/interscript-models:/mm:ro \\
      /mm/tools/wo20_static_int8_sweep.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

MM = Path("/mm")
sys.path.insert(0, str(MM / "src"))
sys.path.insert(0, str(MM / "runtime" / "src"))

CKPT = Path("/ckpt") / "wo20-quant"
EVAL_N = int(os.environ.get("WO20Q_EVAL_N", "120"))
CALIB_N = 64
MAX_LEN = 512
LATENCY_ROWS = 10
CER_GATE_PP = 2.0          # WO03 int8 limit
CONFIDENT_FLIP_GATE = 0.01  # shipped precedent

# model id -> eval slice in /mm/conformance/wo20/ (first EVAL_N rows;
# src is decode input, tgt is the scoring reference)
TARGETS = [
    {"id": "urd-vocalized-1.0", "slice": "urd"},
    {"id": "tha-phonemic-base-1.0", "slice": "tha"},
    {"id": "tha-phonemic-1.0", "slice": "tha",
     "kit": "conformance/tha-phonemic-vectors.json"},
    {"id": "heb-vocalized-1.0", "slice": "heb"},
    {"id": "heb-vocalized-small-1.0", "slice": "heb"},
    {"id": "heb-vocalized-1.1", "slice": "heb"},
]


def log(*a):
    print("[wo20q]", *a, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_slice(name: str) -> list[dict]:
    path = MM / "conformance" / "wo20" / f"{name}_eval_400.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        # the tha-phonemic corpora store (word, phonemic); diacritization
        # slices store (src, tgt) — normalize to the sweep's keys
        rows.append({"src": r.get("src") or r.get("word") or "",
                     "tgt": r.get("tgt") or r.get("phonemic") or ""})
    return rows[:EVAL_N]


def fetch_fp32_zip(model_id: str, entry: dict, work: Path) -> Path:
    """models.yaml pins either a single url+sha256 or split parts with
    per-part digests plus the whole-file digest — support both."""
    dest = work / (entry.get("filename") or "model.zip")
    if "parts" in entry:
        if dest.exists() and dest.stat().st_size == entry.get("size"):
            return dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as out:
            for part in entry["parts"]:
                ppath = work / Path(part["url"]).name
                if not ppath.exists() or ppath.stat().st_size == 0:
                    log(f"GET {part['url']}")
                    with urllib.request.urlopen(part["url"]) as r, \
                            ppath.open("wb") as f:
                        while True:
                            chunk = r.read(1 << 20)
                            if not chunk:
                                break
                            f.write(chunk)
                got = sha256_file(ppath)
                if got != part["sha256"]:
                    raise SystemExit(f"part sha mismatch: {ppath.name}")
                log(f"verified part {ppath.name}")
                out.write(ppath.read_bytes())
    else:
        url = entry["url"]
        dest = work / Path(url).name
        if dest.exists() and dest.stat().st_size > 0:
            return dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        log(f"GET {url}")
        with urllib.request.urlopen(url) as r, dest.open("wb") as f:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                f.write(chunk)
    got = sha256_file(dest)
    if got != entry["sha256"]:
        raise SystemExit(f"sha mismatch for {model_id}: {got}")
    log(f"verified {dest.name} sha {got[:12]}")
    return dest


def make_model(zip_path: Path):
    """The runtime reference loader, untouched: the CPU single-row-greedy
    contract framing. (The job image's onnxruntime-gpu cannot load the
    CUDA EP — onnxruntime-gpu 1.23 requires CUDA 13 libs — so there is
    exactly one framing in every measurement, both precisions.)"""
    import interscript_ml.model as im_model

    return im_model.Model(str(zip_path))


def translate_all(model, texts: list[str]) -> list[str]:
    return [model.translate(t, max_len=MAX_LEN) for t in texts]


def margin_pair(fp32_zip: Path, int8_zip: Path, pairs):
    """fp32-as-reference margin analysis: per-position fp32 top1-top2
    margins, int8 argmax flips, KL. Sessions built once per zip."""
    import numpy as np
    from imf.export import encode_bytes
    from imf.parity import _onnx_forced_logits, _sessions_from_zip

    enc32, dec32 = _sessions_from_zip(fp32_zip)
    enc8, dec8 = _sessions_from_zip(int8_zip)
    margins_c, flips_c, kld_sum, tokens = [], [], 0.0, 0
    for source, target in pairs:
        target_ids = encode_bytes(target)[:MAX_LEN]
        if len(target_ids) < 2:
            continue
        ref = np.asarray(_onnx_forced_logits(enc32, dec32, source,
                                             target_ids), dtype="float64")
        got = np.asarray(_onnx_forced_logits(enc8, dec8, source,
                                             target_ids), dtype="float64")
        n = min(len(ref), len(got))
        ref, got = ref[:n], got[:n]
        top2 = np.sort(ref, axis=-1)[:, -2:]
        margins = top2[:, 1] - top2[:, 0]
        flips = ref.argmax(-1) != got.argmax(-1)
        logp_ref = ref - ref.max(-1, keepdims=True)
        logp_got = got - got.max(-1, keepdims=True)
        p_ref = np.exp(logp_ref)
        logp_ref -= np.log(np.clip(p_ref.sum(-1, keepdims=True), 1e-30, None))
        p_got = np.exp(logp_got)
        logp_got -= np.log(np.clip(p_got.sum(-1, keepdims=True), 1e-30, None))
        kld_sum += float((p_ref * (logp_ref - logp_got)).sum())
        margins_c.append(margins)
        flips_c.append(flips)
        tokens += int(n)
    margins = np.concatenate(margins_c)
    flips = np.concatenate(flips_c)
    p10 = float(np.quantile(margins, 0.10))
    n_flips = int(flips.sum())
    confident = int((margins[flips] >= p10).sum()) if n_flips else 0
    return {
        "tokens": tokens,
        "flip_rate": round(n_flips / max(tokens, 1), 6),
        "confident_flip_rate": round(confident / max(tokens, 1), 6),
        "flip_low_margin_share": round(
            float((margins[flips] < p10).mean()) if n_flips else 0.0, 4),
        "margin_p10": round(p10, 4),
        "margin_p50": round(float(np.quantile(margins, 0.50)), 4),
        "kld_mean": round(kld_sum / max(tokens, 1), 8),
    }


def latency(model, texts: list[str]) -> dict:
    toks = 0
    t0 = time.time()
    for t in texts:
        toks += len(model.generate(t, max_len=128))
    dt = time.time() - t0
    return {"rows": len(texts), "tokens": toks,
            "seconds": round(dt, 2),
            "tokens_per_sec": round(toks / max(dt, 1e-9), 2)}


def sweep_one(target: dict, models_yaml: dict, work: Path) -> dict:
    import gc
    import yaml
    from imf.export import build_int8_static_zip
    from imf.text_metrics import char_error_rate

    model_id = target["id"]
    entry = models_yaml["models"][model_id]
    done = CKPT / f"{model_id}.DONE.json"
    if done.exists():
        log(f"{model_id}: already done (bucket marker) — skipping")
        return json.loads(done.read_text())

    fp32_zip = fetch_fp32_zip(model_id, entry, work)
    slice_rows = load_slice(target["slice"])
    srcs = [r["src"] for r in slice_rows]
    tgts = [r["tgt"] for r in slice_rows]
    calib_texts = srcs[:CALIB_N]

    # phase A: fp32 reference decode (CPU contract framing)
    fp32 = make_model(fp32_zip)
    log(f"{model_id}: fp32 reference decode over {len(srcs)} rows (cpu)")
    fp32_out = translate_all(fp32, srcs)
    kit_fp32_out = None
    if target.get("kit"):
        kit = json.loads((MM / target["kit"]).read_text())
        kit_fp32_out = translate_all(fp32, [v["src"] for v in kit["vectors"]])
    lat_fp32 = latency(fp32, srcs[:LATENCY_ROWS])
    del fp32
    gc.collect()

    # phase B: build the int8static variant (transient sessions inside)
    out_zip = work / f"{model_id}-int8static.zip"
    with zipfile.ZipFile(fp32_zip) as zf:
        has_kv = "decoder-kv.onnx" in zf.namelist()
    if not has_kv:
        log(f"{model_id}: no decoder-kv.onnx — the static recipe "
            "re-quantizes the KV decode path; recording N/A")
        report = {
            "model": model_id,
            "base_id": entry.get("id"),
            "fp32_zip": entry.get("filename"),
            "fp32_sha256_verified": True,
            "verdict": ("N/A — artifact has no decoder-kv graph; the "
                        "static-int8 recipe applies to KV artifacts; "
                        "keeps its fp32 artifact"),
        }
        done.write_text(json.dumps(report, indent=1))
        return report
    log(f"{model_id}: building int8static (calibration {len(calib_texts)})")
    build_int8_static_zip(None, fp32_zip, calib_texts, out_zip)
    gc.collect()

    # phase C: int8 decode + kit rows + cpu latency
    int8 = make_model(out_zip)
    log(f"{model_id}: int8static decode over {len(srcs)} rows (cpu)")
    int8_out = translate_all(int8, srcs)
    conf = None
    if target.get("kit"):
        kit = json.loads((MM / target["kit"]).read_text())
        kout_int8 = translate_all(int8, [v["src"] for v in kit["vectors"]])
    lat_int8 = latency(int8, srcs[:LATENCY_ROWS])
    del int8
    gc.collect()

    cer_ref = 100.0 * sum(char_error_rate(t, o) or 0.0
                          for t, o in zip(tgts, fp32_out)) / len(srcs)
    cer_int8 = 100.0 * sum(char_error_rate(t, o) or 0.0
                           for t, o in zip(tgts, int8_out)) / len(srcs)
    cer_delta = abs(cer_int8 - cer_ref)
    exact = sum(a == b for a, b in zip(fp32_out, int8_out))

    log(f"{model_id}: margin analysis (fp32 reference, cpu)")
    margins = margin_pair(fp32_zip, out_zip, list(zip(srcs, tgts)))
    gc.collect()

    # conformance rows: pinned kit or emitted fixtures
    if target.get("kit"):
        kit = json.loads((MM / target["kit"]).read_text())
        conf = {
            "kit": target["kit"],
            "pinned_rows": len(kit["vectors"]),
            "fp32_byte_exact_vs_pinned": sum(
                a == v["out"] for a, v in zip(kit_fp32_out, kit["vectors"])),
            "int8_byte_exact_vs_pinned": sum(
                a == v["out"] for a, v in zip(kout_int8, kit["vectors"])),
            "int8_vs_fp32_row_exact": sum(
                a == b for a, b in zip(kit_fp32_out, kout_int8)),
            "int8_vs_fp32_cer_delta_pp": round(abs(
                100.0 * sum(char_error_rate(v["out"], b) or 0.0
                            for v, b in zip(kit["vectors"], kout_int8))
                / len(kit["vectors"])
                - 100.0 * sum(char_error_rate(v["out"], a) or 0.0
                              for v, a in zip(kit["vectors"], kit_fp32_out))
                / len(kit["vectors"])), 4),
        }
    else:
        fixture = {"model": model_id,
                   "index_version": entry.get("index_version"),
                   "decode": {"mode": "single-row-greedy"},
                   "source": (f"first 12 rows of the {target['slice']} eval "
                              "slice (conformance/wo20 manifest); fp32 zip "
                              "outputs, generated by the WO20 sweep"),
                   "vectors": [{"src": s, "out": o}
                               for s, o in zip(srcs[:12], fp32_out[:12])]}
        (CKPT / f"{model_id}.candidate-kit.json").write_text(
            json.dumps(fixture, ensure_ascii=False, indent=1))
        conf = {"kit": None,
                "fixture_rows": 12,
                "int8_vs_fp32_row_exact": sum(
                    a == b for a, b in zip(fp32_out[:12], int8_out[:12]))}

    size_fp32 = fp32_zip.stat().st_size
    size_int8 = out_zip.stat().st_size

    passed = (cer_delta <= CER_GATE_PP
              and margins["confident_flip_rate"] <= CONFIDENT_FLIP_GATE)
    report = {
        "model": model_id,
        "base_id": entry.get("id"),
        "fp32_zip": Path(entry["url"]).name if "url" in entry
                    else entry.get("filename"),
        "fp32_sha256_verified": True,
        "eval_rows": len(srcs),
        "calibration_rows": len(calib_texts),
        "cer_reference_pp": round(cer_ref, 4),
        "cer_int8static_pp": round(cer_int8, 4),
        "cer_delta_pp": round(cer_delta, 4),
        "cer_gate_pp": CER_GATE_PP,
        "row_exact_match_int8_vs_fp32": exact,
        "margins": margins,
        "confident_flip_gate": CONFIDENT_FLIP_GATE,
        "conformance": conf,
        "size_fp32_bytes": size_fp32,
        "size_int8static_bytes": size_int8,
        "size_ratio": round(size_int8 / max(size_fp32, 1), 4),
        "latency_fp32": lat_fp32,
        "latency_int8static": lat_int8,
        "cpu_speedup": round(
            lat_int8["tokens_per_sec"] / max(lat_fp32["tokens_per_sec"], 1e-9), 4),
        "framing": ("everything on the CPU contract framing (single-row "
                    "greedy; onnxruntime default providers): the CUDA EP "
                    "is unavailable in the job image (onnxruntime-gpu "
                    "1.23 needs CUDA 13 libs), so decode, margins, kit "
                    "rows and latency are one framing, both precisions"),
        "verdict": "PASS — int8static viable" if passed
                   else "FAIL — keeps fp32 artifact",
    }
    done.write_text(json.dumps(report, indent=1))
    # persist the variant for owner inspection
    import shutil
    shutil.copy(out_zip, CKPT / out_zip.name)
    log(f"{model_id}: {report['verdict']} "
        f"(cer_delta {report['cer_delta_pp']}pp, "
        f"confident_flips {margins['confident_flip_rate']}, "
        f"size x{report['size_ratio']}, cpu speed x{report['cpu_speedup']})")
    return report


def main():
    import yaml

    models_yaml = yaml.safe_load((MM / "models.yaml").read_text())
    work = Path("/tmp/wo20q")
    work.mkdir(parents=True, exist_ok=True)
    CKPT.mkdir(parents=True, exist_ok=True)
    reports = []
    for target in TARGETS:
        try:
            reports.append(sweep_one(target, models_yaml, work))
        except Exception as e:  # a failed model keeps its fp32 artifact
            log(f"{target['id']}: FAILED with {type(e).__name__}: {e}")
            reports.append({"model": target["id"], "verdict": "ERROR",
                            "error": f"{type(e).__name__}: {e}"})
    (CKPT / "sweep-summary.json").write_text(
        json.dumps({r["model"]: r.get("verdict", "ERROR") for r in reports},
                   indent=1))
    log("SUMMARY " + json.dumps({r["model"]: r.get("verdict")
                                 for r in reports}))


if __name__ == "__main__":
    main()
