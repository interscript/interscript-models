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

**Re-dispatch footnote (2026-11-25, live-log driven).** The two fp32
Hebrew base legs ran at the measured cpu-basic rate of ~73–110 s/row
(single-thread ORT decode), putting the sequential 0/2+1/2 plans past
the 23 h timeout: heb-1.1 measured eta 890 min for shard 0 alone
(~30 h total), and heb-1.0 produced zero 200-row decode prints after
~6 h (rate floor ≥ 104 s/row → shard 0 alone ≥ 26.9 h). Both jobs were
canceled after log-verified identification and re-dispatched as four
independent per-shard jobs each (k=4 → 466 rows/shard → 9.5–14.3 h
measured-band, margin ≥ 8.7 h), same harness sha `93b7977f…`, same
pins, same decode budgets — protocol unchanged, records stay
merge-compatible:

- heb-vocalized-1.1: `ivrb-heb-11-s0` `6b06fea5b6a90bbe997dca35`,
  `-s1` `6b06fea7d91f621b93083bd8`, `-s2` `6b06fea8d91f621b93083be0`,
  `-s3` `6b06feaab6a90bbe997dca3c` (all cpu-basic RUNNING)
- heb-vocalized-1.0: `ivrb-heb-10-s0` `6b06feb5d91f621b93083bfc`,
  `-s1` `6b06feb6d91f621b93083c01`, `-s2` `6b06feb8d91f621b93083c05`,
  `-s3` `6b06feb9b6a90bbe997dca66` (all cpu-basic RUNNING)

heb-vocalized-small-1.0 stays on its original job (log eta 504 min →
~21 h total, margin ~1.8 h — within timeout, watch item). Flavor note:
cpu-upgrade (8 vCPU) was considered and rejected — ORT decode is
single-thread (`intra_op = inter_op = 1`), so the extra vCPUs do not
improve per-row rate, and its per-core clock is unmeasured; the
measured-rate k=4 shape on cpu-basic is the guaranteed fit.

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
