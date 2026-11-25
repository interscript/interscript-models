#!/usr/bin/env python3
"""IVRB harness — the Interscript Vocalization-Romanization Benchmark runner.

Executes the IVRB-v1 loop per (language, romanization system, model) per
docs/benchmarks/IVRB-SPEC.md (normative):

    Direct arm:  V_dir = M(skel(V));  cer_nat = CER(V_dir, V)
    Skel arm:    cer_skel_S = CER(f_S(skel(V)), f_S(V))
    Round trip:  cer_S = CER(f_S(V_dir), f_S(V))
    retention_S = 1 - cer_S / cer_skel_S

plus the model-free system properties encode_rate and mark_leak.

Usage:
    python3 ivrb.py <model_id> [--rows N] [--out FILE] [--crossval]

Writes a JSON run record (per-metric values, pins, wall time).
Romanization runs in-process via the interscript-py engine; --crossval
additionally checks >= 200 sampled rows per system against the iscrs binary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------- pins ----
# Paths are env-overridable so the same pinned harness runs locally and
# inside HF Jobs (benchmarks/ivrb/hfjob.sh sets IVRB_*); the sha256 pins
# are the identity, never the path.

import os

ISCRS_BIN = os.environ.get(
    "IVRB_ISCRS", "/Users/mulgogi/src/interscript/interscript-rs/target/release/iscrs")
ISCRS_GIT = "interscript-rs@f054108 (release/0.2.2)"
MAPS_DIR = os.environ.get("IVRB_MAPS", "/Users/mulgogi/src/interscript/maps/maps")
MAPS_GIT = "interscript-maps@cc67dd3 (= maps release v3.2.0, maps/ byte-identical)"
PY_ENGINE_GIT = "interscript-py@bf3ac6f (wo20-fix-py)"
ML_RUNTIME_GIT = "interscript-py@bf3ac6f src/interscript/ml (Model, WO79 single-thread CPU)"
PROTOCOL = "ivrb-v1"

DATA = {
    "urd": {
        "path": os.environ.get(
            "IVRB_DATA_URD",
            "/Users/mulgogi/src/interscript/rababa-urdu/data-diacrit/test.jsonl"),
        "sha256": "6d822ae70a383e5547ee82e841a65e83fac81ae47ff320999b8e6b101b1790bb",
        "rows": 11940,
        "note": "urd-dia@v1#test, WO37 protocol set",
    },
    "heb": {
        "path": os.environ.get(
            "IVRB_DATA_HEB",
            "/Users/mulgogi/.cache/huggingface/hub/datasets--Interscript--hebrew-v4/snapshots/b5e6502d8e1eb99a443ed5c6e54b38e841a8dc86/test.jsonl"),
        "sha256": "77e9b5dc3a3b9e7d70924e670f7361455b714ec8212e046662ea04187b153ccc",
        "rows": 1864,
        "note": "hebrew-v4 test split, crown protocol set",
    },
}

OUT_DIR = os.environ.get("IVRB_OUT", "/tmp/ivrb-out")

SYSTEMS = {
    "heb": [
        "din-heb-Hebr-Latn-31636-2018",
        "icao-heb-Hebr-Latn-9303",
    ],
    "urd": [
        "alalc-urd-Arab-Latn-2013",
        "bgnpcgn-urd-Arab-Latn-2007",
        "din-urd-Arab-Latn-31635-2011",
        "odni-urd-Arab-Latn-2015",
        "un-urd-Arab-Latn-1972",
    ],
}

MODELS = {
    "urd-vocalized-1.0": {
        "lang": "urd",
        "zip": "/Users/mulgogi/.cache/secryst/models/urd-diac-1.0/urd-diac-1.0-fp32.zip",
        "sha256": "c299ea44a4da4851a52283f8e42d2fb6f8c7a9c443ba7eb0270f97372e10b8ea",
        "precision": "fp32",
    },
    "urd-vocalized-2.1": {
        "lang": "urd",
        "zip": "/tmp/ivrb-downloads/urd-vocalized-2.1-int8-dynamic.zip",
        "sha256": "993a441144342db400f9db912f133cb992f9c593710d1e78d111729c6c8f5525",
        "precision": "int8-dynamic",
    },
    "heb-vocalized-1.0": {
        "lang": "heb",
        "zip": "/Users/mulgogi/.cache/secryst/models/heb-diac-1.0/heb-diac-1.0-fp32.zip",
        "sha256": "b32fa239e0c56708b6004942de4b9e6e9f265e7cc3828f41d560e96386e20dd8",
        "precision": "fp32",
    },
    "heb-vocalized-1.1": {
        "lang": "heb",
        "zip": "/tmp/ivrb-downloads/heb11/heb.zip",
        "sha256": "f0022dde8d06e46e8f08cf0b2f7bbb887a05ed686b90f1d5aa82ca3ef690a0b0",
        "precision": "fp32",
    },
    "heb-vocalized-small-1.0": {
        "lang": "heb",
        "zip": "/Users/mulgogi/.cache/secryst/models/heb-diac-small-1.0/heb-diac-small-1.0-fp32.zip",
        "sha256": "905c53873d5a62bbe6252c6ec0ecef5f37e96e78cb01e8cd99b6b24c4d4d74ad",
        "precision": "fp32",
    },
}

# ------------------------------------------------------- house helpers ----

# SPEC section 5: the NIKUD_MARKS set (rababa-evaluate set minus maqqaf).
NIKUD_MARKS = frozenset("ְֱֲֳִֵֶַָֹֺֻּֽֿׁׂ")

# SPEC section 5: mark-leak ranges (Hebrew, Arabic diacritic ranges).
LEAK_RANGES = [(0x0591, 0x05C7), (0x0610, 0x061A), (0x064B, 0x065F),
               (0x0670, 0x0670), (0x06D6, 0x06ED)]

SEP_RE = re.compile(r"\s+")

# word-level memo across systems (urdu/heb words repeat heavily across rows)
_word_cache: dict[tuple[str, str, str], bool] = {}

# Decode budgets (ivrb-v1 amendment): base budget = the language's house
# protocol budget (urd: the recipe's maxlen 256; heb: the crown eval's
# max_new_tokens=512, eval_hebrew_s46_greedy.py). A row whose generation
# FILLS the budget without EOS is truncated: re-decode it with
# max_new = ceil(1.2 x generated length), iterated to stability (cap 4).
BASE_MAX = {"urd": 256, "heb": 512}
RESIZE_FACTOR = 1.2
RESIZE_PASSES = 4


def translate_sized(voc, text: str, lang: str) -> str:
    """House-budget decode with truncation-aware resizing."""
    from interscript.ml.tokens import decode
    from interscript.ml.model import first_alternates

    budget = BASE_MAX[lang]
    for _ in range(RESIZE_PASSES):
        ids = voc.generate(text, max_len=budget)
        if len(ids) < budget:  # EOS emitted — not truncated
            return first_alternates(decode(ids))
        budget = int(RESIZE_FACTOR * len(ids)) + 1
    return first_alternates(decode(ids))


def is_leak_char(ch: str) -> bool:
    o = ord(ch)
    return any(lo <= o <= hi for lo, hi in LEAK_RANGES)


def heb_skeleton(text: str) -> str:
    return "".join(c for c in text if c not in NIKUD_MARKS)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def split_windows(text: str, budget: int = 1400) -> list[str]:
    """SPEC section 5 rule 3: word-boundary windows of <= 1400 bytes."""
    if len(text.encode("utf-8")) <= budget:
        return [text]
    words, cur, n, wins = text.split(), [], 0, []
    for w in words:
        c = len(w.encode("utf-8")) + 1
        if cur and n + c > budget:
            wins.append(" ".join(cur))
            cur, n = [], 0
        cur.append(w)
        n += c
    if cur:
        wins.append(" ".join(cur))
    return wins


def stitch(original: str, translated_windows: list[str]) -> str:
    """Re-join translated windows with the original separators (crown protocol)."""
    words = original.split()
    raw_seps = SEP_RE.findall(original)
    sep_for = {i: (raw_seps[i] if i < len(raw_seps) else "") for i in range(len(words))}
    out: list[str] = []
    wi = 0
    for tw in translated_windows:
        for pw in tw.split():
            out.append(pw)
            out.append(sep_for.get(wi, " "))
            wi += 1
    return "".join(out)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein over Unicode code points, O(min) memory."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(dist: int, total: int) -> float:
    return dist / total if total else 0.0


# ------------------------------------------------------------ engines ----

# the py-engine/ml runtime source: local checkout by default, PYTHONPATH
# in HF Jobs (hfjob.sh exports IVRB_PY_SRC after the pinned clone)
PY_SRC = os.environ.get(
    "IVRB_PY_SRC", "/Users/mulgogi/src/interscript/interscript-py/src")


def _ensure_py_src() -> None:
    if PY_SRC and os.path.isdir(PY_SRC) and PY_SRC not in sys.path:
        sys.path.insert(0, PY_SRC)


def load_engine():
    _ensure_py_src()
    from interscript import add_load_path, transliterate

    add_load_path(MAPS_DIR)
    return transliterate


def iscrs_transliterate(map_id: str, text: str) -> str:
    r = subprocess.run(
        [ISCRS_BIN, "transliterate", map_id, text],
        capture_output=True, text=True, timeout=60, check=True,
    )
    return r.stdout.rstrip("\n")


# --------------------------------------------------------------- main ----


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_id", choices=sorted(MODELS))
    ap.add_argument("--rows", type=int, default=0, help="cap rows (0 = full split)")
    ap.add_argument("--out", default="")
    ap.add_argument("--shard", default="",
                    help="K/N — process rows with index %% N == K (protocol-clean: "
                    "rows are independent; shards merge by summing raw accumulators)")
    ap.add_argument("--crossval", action="store_true",
                    help="isurs cross-check vs iscrs (>= 200 sampled rows per system)")
    ap.add_argument("--seed", type=int, default=20261125)
    args = ap.parse_args()

    model = MODELS[args.model_id]
    lang = model["lang"]
    data = DATA[lang]
    # IVRB_ZIP relocates the artifact (HF Jobs fetches the same release
    # zip; the sha256 pin below is the identity, never the path)
    zip_path = os.environ.get("IVRB_ZIP") or model["zip"]

    # pins: verify data + model shas before anything runs (SPEC section 9)
    data_sha = sha256_file(Path(data["path"]))
    assert data_sha == data["sha256"], f"data sha mismatch: {data_sha}"
    model_sha = sha256_file(Path(zip_path))
    assert model_sha == model["sha256"], f"model zip sha mismatch: {model_sha}"
    print(f"[pins] data sha ok; model zip sha ok", flush=True)

    rows = [json.loads(l) for l in
            Path(data["path"]).read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(rows) == data["rows"], f"row count {len(rows)} != {data['rows']}"
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        rows_all = rows
        rows = [r for i, r in enumerate(rows) if i % n == k]
        print(f"[shard] {args.shard}: {len(rows)}/{len(rows_all)} rows", flush=True)
    if args.rows:
        rows = rows[: args.rows]
    print(f"[data] {len(rows)} rows", flush=True)

    # vocalizer: the conformance-proven runtime, single-row greedy (SPEC 5.1)
    _ensure_py_src()
    from interscript.ml import Model

    t0 = time.time()
    voc = Model.load(zip_path)
    print(f"[model] {args.model_id} loaded ({args.model_id and model['precision']}) "
          f"in {time.time()-t0:.1f}s", flush=True)

    transliterate = load_engine()

    systems = SYSTEMS[lang]

    # skeletons (SPEC 5.4): urd uses row src; heb strips NIKUD_MARKS from tgt
    if lang == "urd":
        golds = [r["tgt"].strip() for r in rows]
        skels = [r["src"].strip() for r in rows]
    else:
        golds = [r["tgt"].strip() for r in rows]
        skels = [heb_skeleton(g) for g in golds]

    # ---- direct arm: the model re-vocalizes the skeleton -----------------
    v_dir: list[str] = []
    t0 = time.time()
    for i, sk in enumerate(skels, 1):
        wins = split_windows(sk)
        v_dir.append(stitch(sk, [translate_sized(voc, w, lang) for w in wins]))
        if i % 200 == 0:
            rate = i / (time.time() - t0)
            eta = (len(skels) - i) / rate / 60
            print(f"[decode] {i}/{len(skels)} ({rate:.2f} rows/s, eta {eta:.0f}m)",
                  flush=True)
    decode_s = time.time() - t0
    print(f"[decode] done in {decode_s:.0f}s", flush=True)

    # cer_nat (corpus-level, native space)
    d_nat = sum(edit_distance(p, g) for p, g in zip(v_dir, golds))
    n_nat = sum(len(g) for g in golds)
    cer_nat = cer(d_nat, n_nat)
    print(f"[cer_nat] {cer_nat:.5f} (corpus-level)", flush=True)

    # ---- system arms ------------------------------------------------------
    results = {}
    for sysid in systems:
        # romanize: gold, skeleton, and model re-vocalization through S
        t0 = time.time()
        r_gold = [transliterate(sysid, g) for g in golds]
        r_skel = [transliterate(sysid, s) for s in skels]
        r_dir = [transliterate(sysid, p) for p in v_dir]
        rom_s = time.time() - t0

        # recovery CER + skel CER (corpus-level, Latin space)
        d_rec = sum(edit_distance(a, b) for a, b in zip(r_dir, r_gold))
        n_rec = sum(len(b) for b in r_gold)
        d_skl = sum(edit_distance(a, b) for a, b in zip(r_skel, r_gold))
        n_skl = sum(len(b) for b in r_gold)
        recovery_cer = cer(d_rec, n_rec)
        skel_cer = cer(d_skl, n_skl)
        retention = 1.0 - recovery_cer / skel_cer if skel_cer > 0 else 0.0

        # model-free encode rate: word-level f_S(voc) != f_S(skel), memoized
        same = diff = 0
        for g, s in zip(golds, skels):
            gw, sw = g.split(), s.split()
            for wv, ws in zip(gw, sw):
                pair = (sysid, wv, ws)
                if pair not in _word_cache:
                    _word_cache[pair] = (
                        transliterate(sysid, wv) == transliterate(sysid, ws)
                    )
                if _word_cache[pair]:
                    same += 1
                else:
                    diff += 1
        encode_rate = diff / (same + diff) if (same + diff) else 0.0

        # mark leak: rows whose f_S output contains raw combining marks
        leak = sum(1 for x in r_gold if any(is_leak_char(c) for c in x))
        leak_dir = sum(1 for x in r_dir if any(is_leak_char(c) for c in x))

        results[sysid] = {
            "recovery_cer": round(recovery_cer, 6),
            "skel_cer": round(skel_cer, 6),
            "retention": round(retention, 6),
            "raw": {
                "d_rec": d_rec, "n_rec": n_rec,
                "d_skl": d_skl, "n_skl": n_skl,
                "w_same": same, "w_diff": diff,
            },
            "encode_rate": round(encode_rate, 6),
            "mark_leak_gold_rows": leak,
            "mark_leak_dir_rows": leak_dir,
            "rows": len(golds),
            "romanize_wall_s": round(rom_s, 1),
        }
        print(f"[{sysid}] recovery={recovery_cer:.5f} skel={skel_cer:.5f} "
              f"retention={retention:.4f} encode={encode_rate:.4f} "
              f"leak={leak}/{len(golds)} ({rom_s:.0f}s)", flush=True)

    # ---- cross-validation vs iscrs (SPEC section 9.4) ---------------------
    crossval = None
    if args.crossval:
        rng = random.Random(args.seed)
        sample = rng.sample(range(len(golds)), min(200, len(golds)))
        crossval = {}
        for sysid in systems:
            agree = 0
            mism = []
            for idx in sample:
                for txt in (golds[idx], skels[idx]):
                    py_out = transliterate(sysid, txt)
                    rs_out = iscrs_transliterate(sysid, txt)
                    if py_out == rs_out:
                        agree += 1
                    elif len(mism) < 3:
                        mism.append({"py": py_out, "rs": rs_out})
            total = 2 * len(sample)
            rate = agree / total
            crossval[sysid] = {"agreement": round(rate, 4), "checked": total,
                               "sample_mismatches": mism}
            print(f"[crossval] {sysid}: {agree}/{total}", flush=True)

    record = {
        "protocol": PROTOCOL,
        "model_id": args.model_id,
        "lang": lang,
        "precision": model["precision"],
        "rows": len(golds),
        "shard": args.shard or "0/1",
        "cer_nat": round(cer_nat, 6),
        "raw": {"d_nat": d_nat, "n_nat": n_nat},
        "decode_wall_s": round(decode_s, 1),
        "systems": results,
        "crossval": crossval,
        "pins": {
            "data": data,
            "model_zip_sha256": model["sha256"],
            "iscrs": ISCRS_GIT,
            "maps": MAPS_GIT,
            "py_engine": PY_ENGINE_GIT,
            "ml_runtime": ML_RUNTIME_GIT,
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    shard_tag = args.shard.replace("/", "-") if args.shard else ""
    out = args.out or f"{OUT_DIR}/{args.model_id}{shard_tag}.json"
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print(f"[done] {out}", flush=True)


if __name__ == "__main__":
    main()
