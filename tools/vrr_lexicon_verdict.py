"""WO81 — the first VRR verdict: lexicon from pinned tashkeela, scored
against the frozen frontier-predictions-v1 runs.

Lexicon source is DECLARED in the verdict (tashkeela, classical
register, community-vintage vocalization) — VRR is reported beside
DER, never instead of it; the licensed set is only as good as its
source.

Usage (cpu-basic, isx-training mounted rw at /ckpt):
    python /ckpt/run-081-vrr/vrr_lexicon_verdict.py
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from sadeedbench.vrr import score_text_vrr, strip_harakat

OUT = Path("/ckpt") / "run-081-vrr"
RELEASE = ("https://github.com/interscript/interscript-models/releases/"
           "download/frontier-predictions-v1/")
RUNS = ["run-006-r7-muon-final_preds.jsonl",   # rung 2.0
        "run-007-r7-muon-6ep-final_preds.jsonl"]  # rung 2.1
LEXICON_FILES = [f"tashkeela-full/train-00{i}.txt" for i in (1, 2, 3)]


def build_lexicon() -> dict[str, set[str]]:
    lex: dict[str, set[str]] = defaultdict(set)
    for name in LEXICON_FILES:
        p = hf_hub_download("Interscript/arabic-r8", name, repo_type="dataset")
        t0 = time.time()
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                for w in line.split():
                    s = strip_harakat(w)
                    if w != s:
                        lex[s].add(w)
                        n += 1
        print(f"[lex] {name}: +{n} readings ({time.time()-t0:.0f}s), "
              f"skeletons={len(lex)}", flush=True)
    return dict(lex)


def fetch_preds(name: str) -> list[dict]:
    url = RELEASE + name
    rows = []
    with urllib.request.urlopen(url, timeout=120) as r:
        for line in r:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    lex = build_lexicon()
    api = HfApi(token=os.environ.get("HF_TOKEN"))

    verdict = {
        "lexicon": {
            "source": "Interscript/arabic-r8@main tashkeela-full/train-001..003",
            "skeletons": len(lex),
            "note": "classical community-vintage vocalization; declared "
                    "source, not an authority",
        },
        "runs": {},
    }
    for name in RUNS:
        rows = fetch_preds(name)
        agg = {"student": [0, 0], "teacher": [0, 0]}
        for r in rows:
            for col, key in (("student", "student"), ("teacher", "teacher")):
                v, t = score_text_vrr(r["src"], r[key], lex)
                agg[col][0] += v
                agg[col][1] += t
        entry = {
            col: {"valid": v, "total": t,
                  "vrr": round(v / t, 4) if t else 0.0}
            for col, (v, t) in agg.items()
        }
        verdict["runs"][name] = entry
        print(f"[vrr] {name}: {json.dumps(entry)}", flush=True)

    out = OUT / "vrr-verdict.json"
    out.write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"[done] {out}", flush=True)


if __name__ == "__main__":
    main()
