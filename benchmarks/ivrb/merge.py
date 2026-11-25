#!/usr/bin/env python3
"""Merge IVRB shard run records into the v1 results artifact + markdown table.

Reads the run records produced by ivrb.py (sharded or whole), merges shards
per model by summing the raw accumulators (protocol-clean: rows are
independent under single-row greedy), recomputes every metric from the raw
sums, cross-checks pins across records, and writes:

    <out-dir>/ivrb-v1.json    the combined machine-readable record
    <out-dir>/RESULTS-v1.md   the per-language ranking tables

Usage:
    python3 merge.py /tmp/ivrb-out [--out docs/benchmarks/ivrb]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

PROTOCOL = "ivrb-v1"


def cer(d: int, n: int) -> float:
    return d / n if n else 0.0


def merge_records(records: list[dict]) -> dict:
    """Merge shard records of one model into one row set."""
    assert len({r["model_id"] for r in records}) == 1, "mixed models in shard set"
    out = {
        "model_id": records[0]["model_id"],
        "lang": records[0]["lang"],
        "precision": records[0]["precision"],
        "rows": sum(r["rows"] for r in records),
        "cer_nat": cer(sum(r["raw"]["d_nat"] for r in records),
                       sum(r["raw"]["n_nat"] for r in records)),
        "decode_wall_s": sum(r["decode_wall_s"] for r in records),
        "pins": records[0]["pins"],
        "shards": sorted(r["shard"] for r in records),
        "systems": {},
    }
    systems: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        for sysid, s in r["systems"].items():
            systems[sysid].append(s)
    for sysid, shards in systems.items():
        d_rec = sum(s["raw"]["d_rec"] for s in shards)
        n_rec = sum(s["raw"]["n_rec"] for s in shards)
        d_skl = sum(s["raw"]["d_skl"] for s in shards)
        n_skl = sum(s["raw"]["n_skl"] for s in shards)
        w_same = sum(s["raw"]["w_same"] for s in shards)
        w_diff = sum(s["raw"]["w_diff"] for s in shards)
        recovery = cer(d_rec, n_rec)
        skel = cer(d_skl, n_skl)
        out["systems"][sysid] = {
            "recovery_cer": recovery,
            "skel_cer": skel,
            "retention": 1.0 - recovery / skel if skel > 0 else 0.0,
            "encode_rate": w_diff / (w_same + w_diff) if (w_same + w_diff) else 0.0,
            "mark_leak_gold_rows": sum(s["mark_leak_gold_rows"] for s in shards),
            "mark_leak_dir_rows": sum(s["mark_leak_dir_rows"] for s in shards),
            "rows": sum(s["rows"] for s in shards),
        }
    return out


def fmt(x: float, pct: bool = True) -> str:
    return f"{100 * x:.2f}%" if pct else f"{x:.4f}"


def table_for(models: list[dict]) -> str:
    lines: list[str] = []
    for m in sorted(models, key=lambda m: m["model_id"]):
        lines.append(
            f"#### {m['model_id']} ({m['precision']}, {m['rows']} rows, "
            f"direct CER {fmt(m['cer_nat'])})\n"
        )
        lines.append(
            "| romanization system | retention | recovery CER | skeleton CER | "
            "encode rate | mark leak (gold rows) |"
        )
        lines.append("|---|---|---|---|---|---|")
        ranked = sorted(m["systems"].items(), key=lambda kv: -kv[1]["retention"])
        for rank, (sysid, s) in enumerate(ranked, 1):
            leak = f"{s['mark_leak_gold_rows']}/{s['rows']}"
            lines.append(
                f"| {rank}. `{sysid}` | {fmt(s['retention'])} | "
                f"{fmt(s['recovery_cer'])} | {fmt(s['skel_cer'])} | "
                f"{fmt(s['encode_rate'])} | {leak} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    in_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/ivrb-out")
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    records = [json.loads(p.read_text()) for p in sorted(in_dir.glob("*.json"))
               if not p.name.startswith("smoke")]
    assert records, f"no run records in {in_dir}"
    protocols = {r["protocol"] for r in records}
    assert protocols == {PROTOCOL}, f"protocol mix: {protocols}"
    pins = {json.dumps(r["pins"], sort_keys=True) for r in records}
    assert len(pins) == 1, "pin mismatch across run records"

    by_model: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_model[r["model_id"]].append(r)
    merged = {mid: merge_records(recs) for mid, recs in by_model.items()}

    combined = {
        "benchmark": "IVRB",
        "protocol": PROTOCOL,
        "models": merged,
        "pin": json.loads(pins.pop()),
        "notes": [
            "greedy single-row decode, ONNXRuntime CPU single-thread (WO79)",
            "corpus-level CER; retention = 1 - recovery/skel (same space)",
            "no reverse-map bridge exists in the corpus (spec section 2)",
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ivrb-v1.json").write_text(
        json.dumps(combined, indent=2, ensure_ascii=False))

    md = ["# IVRB v1 — first published results",
          "",
          "Protocol `ivrb-v1` (docs/benchmarks/IVRB-SPEC.md). Greedy single-row "
          "decode, ONNXRuntime CPU single-thread; corpus-level CER; retention "
          "= 1 - recovery CER / skeleton CER. Systems ranked by retention.",
          ""]
    for lang in ("urd", "heb"):
        ms = [m for m in merged.values() if m["lang"] == lang]
        if ms:
            md += [f"## {lang}", "", table_for(ms)]
    (out_dir / "RESULTS-v1.md").write_text("\n".join(md))
    print(f"merged {len(records)} records, {len(merged)} models -> "
          f"{out_dir}/ivrb-v1.json + RESULTS-v1.md")


if __name__ == "__main__":
    main()
