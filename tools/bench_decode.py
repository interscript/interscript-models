"""WO73/C3 — decode-latency bench: the measured half of the
perf.decode_ms_per_row budget.

Decodes a model's frozen conformance fixtures through the shipped
decode mode (single-row greedy) and reports wall-clock ms/row. The
number feeds BudgetGate via ctx.extra["measured"]; a budget is never
assumed without it.

Usage:
    python tools/bench_decode.py <model-id> [--repeats 3] \
        [--vectors conformance/<id>-vectors.json]

Resolves the artifact through the index (sha256-verified), so the
measured number always corresponds to the shipped bytes.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "runtime" / "src"))

from interscript_ml import Model  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model_id")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--vectors", type=Path, default=None)
    args = ap.parse_args()

    vectors_path = args.vectors or (
        REPO / "conformance" / f"{args.model_id}-vectors.json")
    vectors = json.loads(vectors_path.read_text(encoding="utf-8"))
    rows = vectors["vectors"]
    if not rows:
        sys.exit(f"no vectors in {vectors_path}")

    model = Model.load(args.model_id)  # resolves via the index, verifies sha256

    # warm-up (index fetch, ORT session init, first-graph allocation)
    model.translate(rows[0]["src"])

    per_row = []
    for _ in range(args.repeats):
        t0 = time.perf_counter()
        for row in rows:
            model.translate(row["src"])
        per_row.append((time.perf_counter() - t0) * 1000 / len(rows))

    print(json.dumps({
        "model": args.model_id,
        "rows": len(rows),
        "repeats": args.repeats,
        "decode_ms_per_row_median": round(statistics.median(per_row), 2),
        "decode_ms_per_row_max": round(max(per_row), 2),
    }))


if __name__ == "__main__":
    main()
