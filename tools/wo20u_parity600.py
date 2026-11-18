# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "onnxruntime>=1.23,<1.24",
#   "numpy>=1.26",
#   "pyyaml>=6.0",
# ]
# ///
"""WO20u publication parity gate — >=500-sample parity on the two PASS
int8static candidates, in the shipped decode mode (single-row greedy,
CPU framing — the WO20 campaign B framing, one framing both precisions).

The M2 sweep gated at 400 rows (conformance/wo20/ slices); the release
parity bar is >=500 samples (imf.schema.Parity.MIN_SAMPLES). This job
re-runs the identical measurement machinery on 600-row slices that are
verified strict supersets of the M2 slices (prefix check against the
committed 400-row files):

  - fp32 zip (sha256-verified from models.yaml) = the reference side;
    the fp32 zips carry their own torch-parity-0.0 records
    (urd 11,940 rows, heb 500 rows), so fp32-zip output is the
    torch-equivalent reference under the one-framing methodology;
  - int8static zip (sha256-verified against wo20u-rc/SHA256SUMS) = the
    measured side, decoded via the runtime reference loader;
  - row-mean CER vs gold on both sides -> cer_delta (int8 gate <= 2.0pp);
  - teacher-forced margin analysis (fp32-as-reference margins, int8
    argmax flips, confident flips at margin >= p10, gate <= 1% of tokens);
  - loader smoke through interscript_ml.Model (id + row-0 decode).

Everything is CPU single-row greedy. Nothing is published by this job;
it writes JSON reports to the bucket for the publish round.

Usage (a10g-small, ~1h):
    hf jobs uv run --flavor a10g-small -d --timeout 4h \\
      --secrets HF_TOKEN \\
      -v hf://buckets/Interscript/isx-training:/ckpt:rw \\
      -v /tmp/isx-models-rc-publish:/mm:ro \\
      /mm/tools/wo20u_parity600.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

MM = Path("/mm")
sys.path.insert(0, str(MM / "src"))
sys.path.insert(0, str(MM / "runtime" / "src"))

OUT = Path("/ckpt") / "wo20u-rc" / "parity600"
MAX_LEN = 512
CER_GATE_PP = 2.0           # WO03 int8 limit
CONFIDENT_FLIP_GATE = 0.01  # shipped precedent
MIN_SAMPLES = 500           # imf.schema.Parity.MIN_SAMPLES

# publish id -> (fp32 models.yaml id, staged zip name, slice stem)
TARGETS = [
    ("urd-vocalized-int8static-1.0", "urd-vocalized-1.0",
     "urd-vocalized-1.0-int8static.zip", "urd"),
    ("heb-vocalized-int8static-1.1", "heb-vocalized-1.1",
     "heb-vocalized-1.1-int8static.zip", "heb"),
]


def log(*a):
    print("[parity600]", *a, flush=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_fp32_zip(model_id: str, entry: dict, work: Path) -> Path:
    """models.yaml pins either a single url+sha256 or split parts with
    per-part digests plus the whole-file digest — support both."""
    import urllib.request

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


def load_slice(name: str) -> tuple[list[dict], bool]:
    """The 600-row slice from the bucket stage, prefix-verified against
    the committed WO20 400-row slice. Returns (rows, prefix_ok)."""
    path = Path("/ckpt") / "wo20u-rc" / "eval600" / f"{name}_eval_600.jsonl"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        rows.append({"src": r.get("src") or r.get("word") or "",
                     "tgt": r.get("tgt") or r.get("phonemic") or ""})
    committed = []
    for line in (MM / "conformance" / "wo20" / f"{name}_eval_400.jsonl") \
            .read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        committed.append({"src": r.get("src") or r.get("word") or "",
                          "tgt": r.get("tgt") or r.get("phonemic") or ""})
    prefix_ok = rows[:400] == committed
    return rows, prefix_ok


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
        "confident_flips": confident,
        "flip_low_margin_share": round(
            float((margins[flips] < p10).mean()) if n_flips else 0.0, 4),
        "margin_p10": round(p10, 4),
        "margin_p50": round(float(np.quantile(margins, 0.50)), 4),
        "kld_mean": round(kld_sum / max(tokens, 1), 8),
    }


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


def parity_one(publish_id: str, fp32_id: str, staged_name: str,
               slice_name: str, models_yaml: dict, work: Path) -> dict:
    import gc

    import onnxruntime
    import yaml
    from imf.text_metrics import char_error_rate
    from interscript_ml.model import Model

    rows, prefix_ok = load_slice(slice_name)
    if not prefix_ok:
        raise SystemExit(f"{slice_name}: 600-row slice is not a strict "
                         "superset of the committed WO20 400-row slice")
    srcs = [r["src"] for r in rows]
    tgts = [r["tgt"] for r in rows]

    fp32_zip = fetch_fp32_zip(fp32_id, models_yaml["models"][fp32_id], work)
    staged = Path("/ckpt") / "wo20u-rc" / staged_name
    sums = {}
    for line in (Path("/ckpt") / "wo20u-rc" / "SHA256SUMS") \
            .read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, fname = line.split()
            sums[fname] = digest
    got = sha256_file(staged)
    if got != sums[staged_name]:
        raise SystemExit(f"staged zip sha mismatch: {staged_name}")

    # phase A: fp32 reference decode (CPU contract framing)
    fp32 = Model(str(fp32_zip))
    log(f"{publish_id}: fp32 reference decode over {len(srcs)} rows (cpu)")
    fp32_out = [fp32.translate(t, max_len=MAX_LEN) for t in srcs]
    del fp32
    gc.collect()

    # phase B: int8static decode via the runtime loader (loader smoke)
    int8 = Model(str(staged))
    loader_smoke = {"loader_id": int8.id, "row0_out_chars":
                    len(int8.translate(srcs[0], max_len=MAX_LEN))}
    log(f"{publish_id}: int8static decode over {len(srcs)} rows (cpu)")
    int8_out = [int8.translate(t, max_len=MAX_LEN) for t in srcs]
    del int8
    gc.collect()

    cer_ref = 100.0 * sum(char_error_rate(t, o) or 0.0
                          for t, o in zip(tgts, fp32_out)) / len(srcs)
    cer_int8 = 100.0 * sum(char_error_rate(t, o) or 0.0
                           for t, o in zip(tgts, int8_out)) / len(srcs)
    cer_delta = abs(cer_int8 - cer_ref)
    exact = sum(a == b for a, b in zip(fp32_out, int8_out))

    log(f"{publish_id}: margin analysis (fp32 reference, cpu)")
    margins = margin_pair(fp32_zip, staged, list(zip(srcs, tgts)))
    gc.collect()

    passed = (len(rows) >= MIN_SAMPLES
              and cer_delta <= CER_GATE_PP
              and margins["confident_flip_rate"] <= CONFIDENT_FLIP_GATE)
    report = {
        "publish_id": publish_id,
        "fp32_reference_id": fp32_id,
        "fp32_sha256": models_yaml["models"][fp32_id]["sha256"],
        "fp32_sha256_verified": True,
        "staged_zip": staged_name,
        "staged_zip_sha256": got,
        "onnx_member_sha256": member_digests(staged),
        "eval_rows": len(rows),
        "slice_prefix_verified_vs_wo20_400": prefix_ok,
        "decode_mode": "single-row-greedy",
        "framing": "CPU contract framing (single-row greedy, "
                   "onnxruntime CPUExecutionProvider), one framing both "
                   "precisions — the WO20 campaign B framing at >=500 "
                   "samples",
        "onnxruntime_version": onnxruntime.__version__,
        "cer_reference_pp": round(cer_ref, 4),
        "cer_int8static_pp": round(cer_int8, 4),
        "cer_delta_pp": round(cer_delta, 4),
        "cer_gate_pp": CER_GATE_PP,
        "row_exact_match_int8_vs_fp32": exact,
        "margins": margins,
        "confident_flip_gate": CONFIDENT_FLIP_GATE,
        "min_samples_gate": MIN_SAMPLES,
        "verdict": "PASS — publication parity gate green" if passed
                   else "FAIL — do not publish",
        "protocol": ("row-mean CER vs gold, single-row greedy decode, "
                     "512-step cap; int8static zip vs the shipped fp32 "
                     "zip (which carries its own torch-parity-0.0 "
                     "record), the WO20 campaign B framing"),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{publish_id}.parity600.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False))
    log(f"{publish_id}: {report['verdict']} (cer_delta "
        f"{report['cer_delta_pp']}pp on {len(rows)} rows, confident_flips "
        f"{margins['confident_flip_rate']}, row_exact {exact}/{len(rows)})")
    return report


def main():
    import yaml

    models_yaml = yaml.safe_load((MM / "models.yaml").read_text())
    work = Path("/tmp/parity600")
    work.mkdir(parents=True, exist_ok=True)
    reports = {}
    for target in TARGETS:
        try:
            reports[target[0]] = parity_one(*target, models_yaml, work)
        except Exception as e:  # noqa: BLE001 — a failed gate must stop the publish round
            log(f"{target[0]}: FAILED with {type(e).__name__}: {e}")
            reports[target[0]] = {"verdict": "ERROR",
                                  "error": f"{type(e).__name__}: {e}"}
    (OUT / "parity600-summary.json").write_text(
        json.dumps(reports, indent=1, ensure_ascii=False))
    log("SUMMARY " + json.dumps(
        {k: v.get("verdict") for k, v in reports.items()}))


if __name__ == "__main__":
    main()
