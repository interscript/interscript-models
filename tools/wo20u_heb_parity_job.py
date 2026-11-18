# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "onnxruntime>=1.23,<1.24",
#   "numpy>=1.26",
#   "pyyaml>=6.0",
# ]
# ///
"""WO20u publication parity gate — heb-vocalized-int8static-1.1 (job form).

The >=500-sample publication parity on the heb int8static candidate,
run on HF Jobs (cpu-xl, x86 onnxruntime CPUExecutionProvider) per the
house rule that ML runs never live on the laptop. One framing, both
precisions: single-row greedy CPU decode of the shipped fp32 zip
(reference; itself torch-parity-0.0 over 500 rows) vs the staged
int8static bytes (SHA256SUMS-verified; ONNX members byte-identical to
the published artifact).

Per-row checkpoints land on the bucket (/ckpt = isx-training mount) so
a re-dispatch resumes instead of redoing hours of decode (the
reference_decode resume pattern).

Usage:
    hf jobs uv run --flavor cpu-xl -d --timeout 4h --secrets HF_TOKEN \\
      -v hf://buckets/Interscript/isx-training:/ckpt:rw \\
      -v /tmp/isx-models-rc-publish:/mm:ro \\
      /tmp/isx-models-rc-publish/tools/wo20u_heb_parity_job.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

MM = Path("/mm")
sys.path.insert(0, str(MM / "src"))
sys.path.insert(0, str(MM / "runtime" / "src"))

OUT = Path("/ckpt") / "wo20u-rc" / "parity600"
CKPT_DIR = Path("/ckpt") / "wo20u-rc" / "parity600" / "heb-job-ckpt"
WORK = Path("/tmp/hebjob")
MAX_LEN = 512
CER_GATE_PP = 2.0
CONFIDENT_FLIP_GATE = 0.01
MIN_SAMPLES = 500
PUBLISH_ID = "heb-vocalized-int8static-1.1"
FP32_ID = "heb-vocalized-1.1"


def log(*a):
    print("[heb-job]", *a, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_fp32_zip(entry: dict, work: Path) -> Path:
    dest = work / (entry.get("filename") or "model.zip")
    if dest.exists() and dest.stat().st_size == entry.get("size"):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as out:
        for part in entry["parts"]:
            ppath = work / Path(part["url"]).name
            if not ppath.exists() or ppath.stat().st_size == 0:
                log(f"GET {part['url']}")
                with urllib.request.urlopen(part["url"]) as r, ppath.open("wb") as f:
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
    got = sha256_file(dest)
    if got != entry["sha256"]:
        raise SystemExit(f"whole-sha mismatch: {got}")
    log(f"verified {dest.name} sha {got[:12]}")
    return dest


def load_pairs():
    path = Path("/ckpt") / "wo20u-rc" / "eval600" / "heb_eval_600.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows.append({"src": r.get("src") or r.get("word") or "",
                         "tgt": r.get("tgt") or r.get("phonemic") or ""})
    committed = []
    for line in (MM / "conformance" / "wo20" / "heb_eval_400.jsonl") \
            .read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            committed.append({"src": r.get("src") or r.get("word") or "",
                              "tgt": r.get("tgt") or r.get("phonemic") or ""})
    if rows[:400] != committed:
        raise SystemExit("600-row slice is not a strict superset of the "
                         "committed WO20 400-row slice")
    return [(r["src"], r["tgt"]) for r in rows], True


def decode_with_resume(model, srcs, ckpt: Path, side: str):
    done = {}
    if ckpt.exists():
        for line in ckpt.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                done[r["i"]] = r["out"]
    outs = [None] * len(srcs)
    t0 = time.time()
    start = len(done)
    for i, src in enumerate(srcs):
        if i in done:
            outs[i] = done[i]
            continue
        outs[i] = model.translate(src, max_len=MAX_LEN)
        with ckpt.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"i": i, "out": outs[i]}, ensure_ascii=False) + "\n")
        if i % 20 == 0:
            rate = (i - start + 1) / max(time.time() - t0, 1e-9)
            log(f"{side}: row {i}/{len(srcs)} ({rate:.2f} rows/s this run)")
    return outs


def member_digests(zip_path: Path) -> dict:
    digests = {}
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.endswith(".onnx"):
                h = hashlib.sha256()
                with zf.open(name) as f:
                    for chunk in iter(lambda: f.read(1 << 20), b""):
                        h.update(chunk)
                digests[name] = h.hexdigest()
    return digests


def main():
    import gc

    import onnxruntime
    import numpy as np
    import yaml
    from imf.export import encode_bytes
    from imf.parity import _onnx_forced_logits, _sessions_from_zip
    from imf.text_metrics import char_error_rate
    from interscript_ml.model import Model

    WORK.mkdir(parents=True, exist_ok=True)
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    models_yaml = yaml.safe_load((MM / "models.yaml").read_text())

    pairs, prefix_ok = load_pairs()
    srcs = [p[0] for p in pairs]
    tgts = [p[1] for p in pairs]

    fp32_zip = fetch_fp32_zip(models_yaml["models"][FP32_ID], WORK)
    staged = Path("/ckpt") / "wo20u-rc" / "heb-vocalized-1.1-int8static.zip"
    sums = {}
    for line in (Path("/ckpt") / "wo20u-rc" / "SHA256SUMS") \
            .read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, fname = line.split()
            sums[fname] = digest
    staged_sha = sha256_file(staged)
    if staged_sha != sums[staged.name]:
        raise SystemExit(f"staged zip sha mismatch: {staged.name}")
    log(f"verified {staged.name} sha {staged_sha[:12]}")

    fp32 = Model(str(fp32_zip))
    log(f"fp32 reference decode over {len(srcs)} rows (cpu)")
    fp32_out = decode_with_resume(fp32, srcs,
                                  CKPT_DIR / "ckpt-fp32.jsonl", "fp32")
    del fp32
    gc.collect()

    int8 = Model(str(staged))
    loader_smoke = {"loader_id": int8.id,
                    "row0_out_chars": len(int8.translate(srcs[0], max_len=MAX_LEN))}
    log(f"int8static decode over {len(srcs)} rows (cpu)")
    int8_out = decode_with_resume(int8, srcs,
                                  CKPT_DIR / "ckpt-int8.jsonl", "int8")
    del int8
    gc.collect()

    cer_ref = 100.0 * sum(char_error_rate(t, o) or 0.0
                          for t, o in zip(tgts, fp32_out)) / len(srcs)
    cer_int8 = 100.0 * sum(char_error_rate(t, o) or 0.0
                           for t, o in zip(tgts, int8_out)) / len(srcs)
    cer_delta = abs(cer_int8 - cer_ref)
    exact = sum(a == b for a, b in zip(fp32_out, int8_out))

    log("margin analysis (fp32 reference, cpu)")
    enc32, dec32 = _sessions_from_zip(fp32_zip)
    enc8, dec8 = _sessions_from_zip(staged)
    margins_c, flips_c, kld_sum, tokens = [], [], 0.0, 0
    for n, (source, target) in enumerate(pairs):
        target_ids = encode_bytes(target)[:MAX_LEN]
        if len(target_ids) < 2:
            continue
        ref = np.asarray(_onnx_forced_logits(enc32, dec32, source, target_ids),
                         dtype="float64")
        got = np.asarray(_onnx_forced_logits(enc8, dec8, source, target_ids),
                         dtype="float64")
        k = min(len(ref), len(got))
        ref, got = ref[:k], got[:k]
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
        tokens += int(k)
        if n % 100 == 0:
            log(f"margins: row {n}/{len(pairs)}")
    margins = np.concatenate(margins_c)
    flips = np.concatenate(flips_c)
    p10 = float(np.quantile(margins, 0.10))
    n_flips = int(flips.sum())
    confident = int((margins[flips] >= p10).sum()) if n_flips else 0

    margins_report = {
        "tokens": tokens,
        "flip_rate": round(n_flips / max(tokens, 1), 6),
        "confident_flip_rate": round(confident / max(tokens, 1), 6),
        "confident_flips": confident,
        "flip_low_margin_share": round(
            float((margins[flips] < p10).mean()) if n_flips else 0.0, 4),
        "margin_p10": round(p10, 4),
        "margin_p50": round(float(np.quantile(margins, 0.50)), 4),
        "kld_mean": round(kld_sum / max(tokens, 1), 8),
    }

    passed = (len(pairs) >= MIN_SAMPLES and cer_delta <= CER_GATE_PP
              and margins_report["confident_flip_rate"] <= CONFIDENT_FLIP_GATE)
    report = {
        "publish_id": PUBLISH_ID,
        "fp32_reference_id": FP32_ID,
        "fp32_sha256": models_yaml["models"][FP32_ID]["sha256"],
        "fp32_sha256_verified": True,
        "staged_zip": staged.name,
        "staged_zip_sha256": staged_sha,
        "onnx_member_sha256": member_digests(staged),
        "measured_bytes_note": ("measured on the wo20u-rc staged bytes; "
                                "ONNX members byte-identical to the "
                                "published artifact (metadata-only repack)"),
        "eval_rows": len(pairs),
        "slice_prefix_verified_vs_wo20_400": prefix_ok,
        "decode_mode": "single-row-greedy",
        "framing": "CPU contract framing (single-row greedy, "
                   "onnxruntime CPUExecutionProvider, HF Jobs cpu tier "
                   "x86) — one framing both precisions; the WO20 "
                   "campaign B framing at >=500 samples",
        "onnxruntime_version": onnxruntime.__version__,
        "cer_reference_pp": round(cer_ref, 4),
        "cer_int8static_pp": round(cer_int8, 4),
        "cer_delta_pp": round(cer_delta, 4),
        "cer_gate_pp": CER_GATE_PP,
        "row_exact_match_int8_vs_fp32": exact,
        "margins": margins_report,
        "confident_flip_gate": CONFIDENT_FLIP_GATE,
        "min_samples_gate": MIN_SAMPLES,
        "loader_smoke": loader_smoke,
        "verdict": "PASS — publication parity gate green" if passed
                   else "FAIL — do not publish",
        "protocol": ("row-mean CER vs gold, single-row greedy decode, "
                     "512-step cap; int8static zip vs the shipped fp32 "
                     "zip (which carries its own torch-parity-0.0 "
                     "record), the WO20 campaign B framing"),
    }
    (OUT / f"{PUBLISH_ID}.parity600.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False))
    log(f"{report['verdict']} (cer_delta {report['cer_delta_pp']}pp on "
        f"{len(pairs)} rows, confident_flips "
        f"{margins_report['confident_flip_rate']}, row_exact "
        f"{exact}/{len(pairs)})")


if __name__ == "__main__":
    main()
