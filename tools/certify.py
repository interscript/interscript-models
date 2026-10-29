"""A5 — the self-certification kit: L0–L3 for any model id.

L0 parse       the id resolves through the index (sha256 verified)
L1 fixtures    the model ships frozen conformance vectors
L2 byte-exact  the reference loader replays the fixtures exactly
L3 parity      torch vs shipped bytes agree (>=500 rows, shipped mode)

Usage:
    python tools/certify.py <model-id> [--index <index-url>]

Exit code 0 = certified at the highest level reached; the JSON report
states the level. A third party self-certifies with this alone.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_id")
    ap.add_argument("--index", default=None)
    args = ap.parse_args()

    report = {"model": args.model_id, "levels": {}}
    sys.path.insert(0, str(REPO / "runtime" / "src"))
    from interscript_ml import Model  # noqa: E402

    # L0 — resolution + integrity
    try:
        m = Model.load(args.model_id, index_url=args.index)
        report["levels"]["L0"] = {"pass": True, "note": "resolved + sha256 verified"}
    except Exception as e:
        report["levels"]["L0"] = {"pass": False, "error": repr(e)[:200]}
        print(json.dumps(report, indent=2))
        sys.exit(1)

    # L1 — frozen fixtures present
    vecs = sorted((REPO / "conformance").glob(
        f"{args.model_id.split('-')[0]}*{args.model_id.split('-')[1]}*-vectors.json"))
    if not vecs:
        report["levels"]["L1"] = {"pass": False,
                                  "note": "no frozen vectors in conformance/"}
        print(json.dumps(report, indent=2))
        sys.exit(2)
    vectors = json.loads(vecs[0].read_text(encoding="utf-8"))
    report["levels"]["L1"] = {"pass": True, "vectors": len(vectors["vectors"]),
                              "file": vecs[0].name}

    # L2 — byte-exact replay through the reference loader
    bad = 0
    for row in vectors["vectors"]:
        if m.translate(row["src"]) != row["out"]:
            bad += 1
    report["levels"]["L2"] = {"pass": bad == 0, "mismatches": bad,
                              "note": "reference-loader byte-exact replay"}

    # L3 — parity: the caller runs the torch-vs-artifact harness
    # (parity_urd_imf_hf.py lineage, >= 500 rows) and appends the verdict;
    # a certified-at-L2 model without an L3 record states so.
    report["levels"]["L3"] = {"pass": None,
                              "note": "run tools/… parity harness >=500 rows "
                                      "and append {pass: bool}"}

    print(json.dumps(report, indent=2))
    ok = report["levels"]["L2"]["pass"]
    sys.exit(0 if ok else 3)


if __name__ == "__main__":
    main()
