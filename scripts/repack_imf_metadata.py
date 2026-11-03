"""WO44 — one-shot IMF zip publish-prep: metadata completeness repack.

The strict publish validator requires, inside the zip's
metadata.yaml: metric protocol + RESULTS anchor per metric, a parity
block, and a README.md member. Exports don't emit all of these (the
urd publish loop proved it four times) — this tool finishes an
artifact for publication in one deterministic pass and re-stamps
models.yaml.

Usage:
    python repack_imf_metadata.py <zip> --card cards/<id>.md \
        --protocol "greedy decode, ..." \
        --anchor "interscript/interscript-models docs/RESULTS.md#slug" \
        --parity-samples 300 --parity-delta 0.024 \
        --model-id urd-g2p-base-1.0
"""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

import yaml


def repack_meta(meta: dict, readme: bytes, protocol: str, anchor: str,
                parity_samples: int, parity_delta: float) -> tuple[dict, bytes]:
    """Return (updated_meta, new_metadata_yaml_bytes)."""
    for m in meta.get("metrics", []):
        m["protocol"] = m.get("protocol") or protocol
        m["source"] = anchor
    meta["parity"] = {"samples": parity_samples,
                      "cer_delta": parity_delta}
    meta["metrics"] = meta.get("metrics", [])
    return meta, yaml.safe_dump(meta, allow_unicode=True, sort_keys=False).encode()


def repack_zip(src: Path, out: Path, new_meta_yaml: bytes,
               readme: bytes) -> tuple[int, str]:
    with zipfile.ZipFile(src) as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in zin.namelist():
            data = new_meta_yaml if name == "metadata.yaml" else zin.read(name)
            zout.writestr(name, data)
        if "README.md" not in zin.namelist():
            zout.writestr("README.md", readme)
    b = out.read_bytes()
    return len(b), hashlib.sha256(b).hexdigest()


def restamp(models_yaml: Path, model_id: str, sha: str, size: int) -> None:
    import re

    s = models_yaml.read_text(encoding="utf-8")
    pat = re.compile(
        rf"({re.escape(model_id)}:.*?sha256: )([0-9a-f]{{64}})(\n    size: )(\d+)",
        re.S)
    s2, n = pat.subn(rf"\g<1>{sha}\g<3>{size}", s)
    if n != 1:
        raise SystemExit(f"models.yaml: expected exactly 1 entry for "
                         f"{model_id}, matched {n}")
    models_yaml.write_text(s2, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("zip")
    ap.add_argument("--card", required=True)
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--anchor", required=True)
    ap.add_argument("--parity-samples", type=int, required=True)
    ap.add_argument("--parity-delta", type=float, required=True)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--models-yaml", default="models.yaml")
    a = ap.parse_args()

    src = Path(a.zip)
    with zipfile.ZipFile(src) as z:
        meta = yaml.safe_load(z.read("metadata.yaml"))
    readme = Path(a.card).read_bytes()

    meta, new_yaml = repack_meta(meta, readme, a.protocol, a.anchor,
                                 a.parity_samples, a.parity_delta)
    out = src.with_name(src.stem + "-pub.zip")
    size, sha = repack_zip(src, out, new_yaml, readme)
    restamp(Path(a.models_yaml), a.model_id, sha, size)
    src.unlink(missing_ok=True)
    out.rename(src)
    print(f"[pub-prep] {src.name} bytes={size} sha256={sha}")


if __name__ == "__main__":
    main()
