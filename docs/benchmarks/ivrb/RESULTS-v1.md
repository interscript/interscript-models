# IVRB v1 — first results (SKELETON — legs in flight)

> Status: **decode legs running as detached HF Jobs.** This file is the
> assembly skeleton; `benchmarks/ivrb/merge.py` regenerates it from the
> landed run records (`ivrb-v1.json` + final tables). The sanity anchors
> below are 10-row smoke checks, NOT results, and never enter the
> published tables.

Protocol `ivrb-v1` (docs/benchmarks/IVRB-SPEC.md): greedy single-row
decode (base budgets urd 256 / heb 512 new tokens; truncated rows
re-decoded at ⌈1.2 × generated⌉, iterated), ONNXRuntime CPU
single-thread; corpus-level CER; retention = 1 − recovery CER /
skeleton CER, both in the system's own Latin output space; systems
ranked by retention. Sha-pinned inputs; ≥ 200-row iscrs cross-validation
per system before ranking (SPEC §9.4).

## Legs (dispatch 2026-11-25)

| leg | job id | state at dispatch | harness sha | artifacts |
|---|---|---|---|---|
| urd-vocalized-1.0 (fp32, 11,940 rows, shards 0/2+1/2) | `6b06c26ed0582cfbbefe540e` | RUNNING | `7213461` | bucket `rhtse/jobs-artifacts/ivrb/` |
| urd-vocalized-2.1 (int8-dynamic, full split) | `6b06c30d1460ffe1d5ea860e` | RUNNING | `93b7977` | bucket |
| heb-vocalized-1.1 (fp32, 1,864 rows, shards 0/2+1/2) | `6b06c312d0582cfbbefe55bc` | RUNNING | `93b7977` | bucket |
| heb-vocalized-1.0 (fp32, shards 0/2+1/2) | `6b06c3191460ffe1d5ea862e` | RUNNING | `93b7977` | bucket |
| heb-vocalized-small-1.0 (fp32, shards 0/2+1/2) | `6b06c2a51460ffe1d5ea84f7` | RUNNING | `7213461` | bucket |

Shared pins: interscript-py `bf3ac6f` (engine + IMF runtime), maps
`cc67dd3` (= maps release v3.2.0, `maps/` byte-identical), data shas
`6d822ae7…` (urd, WO37 set) and `77e9b5dc…` (heb, crown set) — both
sha256-verified in-job before decode.

## Smoke sanity anchors (10-row checks, not results)

- urd-vocalized-1.0 post-decode-budget-fix: direct CER 0.0350 vs the
  shipped 3.74 — the harness reproduces the house number on smoke scale.
- urd-vocalized-2.1 post-fix smoke: retention 0.56–0.75 across the five
  urd systems with encode rate 0.70–0.76 — the loop carries signal.
- Hebrew pre-fix truncation pathology (CER 0.557, negative retention) is
  what the decode-budget amendment eliminates; heb smoke re-validation
  is part of the landed-leg assembly check.

## Ranking tables

PENDING — filled by `merge.py` from the landed leg records:

- urd: 2 models × 5 systems (alalc-2013, bgnpcgn-2007, din-31635-2011,
  odni-2015, un-1972)
- heb: 3 models × 2 systems (din-31636-2018, icao-9303)
