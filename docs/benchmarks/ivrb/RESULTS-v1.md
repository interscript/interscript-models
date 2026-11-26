# IVRB v1 — first results (records landed 2026-11-25/26)

> Status: **all 13 decode records landed in bucket `rhtse/jobs-artifacts/ivrb/`;
> merged into the tables below by `benchmarks/ivrb/merge.py`.** The urd and
> heb record sets carry different data pins, so the merge runs once per
> language group (3 urd records, 10 heb records); shards merge by summing the
> raw accumulators and every metric is recomputed from the sums. The sanity
> anchors below are 10-row smoke checks, NOT results, and never enter the
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

Merged results, `merge.py` output verbatim. Ranking per SPEC §3.4:
systems ordered by `retention` (descending) per language, with
`encode_rate` and `mark_leak` beside each row — no ties occurred, so
the `encode_rate` tie-break did not fire. Metric names are SPEC §3's:
`cer_nat` (the direct arm, the model ceiling, reported beside every
table), `recovery_cer`, `skel_cer`, `retention` (the headline metric),
`encode_rate`, `mark_leak` (rows whose Latin output leaks raw
combining marks / total rows).

### urd — 2 models × 5 systems

#### urd-vocalized-1.0 (fp32, 11940 rows, direct CER 3.74%)

| romanization system | retention | recovery CER | skeleton CER | encode rate | mark leak (gold rows) |
|---|---|---|---|---|---|
| 1. `un-urd-Arab-Latn-1972` | 67.95% | 5.80% | 18.11% | 65.58% | 119/11940 |
| 2. `bgnpcgn-urd-Arab-Latn-2007` | 67.59% | 5.79% | 17.87% | 65.46% | 119/11940 |
| 3. `alalc-urd-Arab-Latn-2013` | 67.05% | 5.28% | 16.01% | 69.10% | 102/11940 |
| 4. `odni-urd-Arab-Latn-2015` | 65.62% | 5.07% | 14.74% | 70.18% | 59/11940 |
| 5. `din-urd-Arab-Latn-31635-2011` | 65.18% | 5.69% | 16.33% | 65.29% | 59/11940 |

#### urd-vocalized-2.1 (int8-dynamic, 11940 rows, direct CER 3.59%)

| romanization system | retention | recovery CER | skeleton CER | encode rate | mark leak (gold rows) |
|---|---|---|---|---|---|
| 1. `un-urd-Arab-Latn-1972` | 69.21% | 5.57% | 18.11% | 65.58% | 119/11940 |
| 2. `bgnpcgn-urd-Arab-Latn-2007` | 68.91% | 5.56% | 17.87% | 65.46% | 119/11940 |
| 3. `alalc-urd-Arab-Latn-2013` | 68.46% | 5.05% | 16.01% | 69.10% | 102/11940 |
| 4. `odni-urd-Arab-Latn-2015` | 67.01% | 4.86% | 14.74% | 70.18% | 59/11940 |
| 5. `din-urd-Arab-Latn-31635-2011` | 66.65% | 5.45% | 16.33% | 65.29% | 59/11940 |

Ranking (best-to-worst by `retention`; identical order under both
models): `un-urd-Arab-Latn-1972` > `bgnpcgn-urd-Arab-Latn-2007` >
`alalc-urd-Arab-Latn-2013` > `odni-urd-Arab-Latn-2015` >
`din-urd-Arab-Latn-31635-2011`.

Run-validity anchors: direct CER 3.74% reproduces the shipped 3.74
(urd-vocalized-1.0, WO37 protocol); 3.59% sits 0.04 pp from the shipped
3.632 (urd-vocalized-2.1).

### heb — 3 models × 2 systems

#### heb-vocalized-1.0 (fp32, 1864 rows, direct CER 25.18%)

| romanization system | retention | recovery CER | skeleton CER | encode rate | mark leak (gold rows) |
|---|---|---|---|---|---|
| 1. `icao-heb-Hebr-Latn-9303` | 39.72% | 24.75% | 41.05% | 98.06% | 1193/1864 |
| 2. `din-heb-Hebr-Latn-31636-2018` | 35.44% | 25.34% | 39.25% | 98.06% | 851/1864 |

#### heb-vocalized-1.1 (fp32, 1864 rows, direct CER 30.46%)

| romanization system | retention | recovery CER | skeleton CER | encode rate | mark leak (gold rows) |
|---|---|---|---|---|---|
| 1. `icao-heb-Hebr-Latn-9303` | 26.28% | 30.26% | 41.05% | 98.06% | 1193/1864 |
| 2. `din-heb-Hebr-Latn-31636-2018` | 21.85% | 30.67% | 39.25% | 98.06% | 851/1864 |

#### heb-vocalized-small-1.0 (fp32, 1864 rows, direct CER 27.11%)

| romanization system | retention | recovery CER | skeleton CER | encode rate | mark leak (gold rows) |
|---|---|---|---|---|---|
| 1. `icao-heb-Hebr-Latn-9303` | 35.86% | 26.33% | 41.05% | 98.06% | 1193/1864 |
| 2. `din-heb-Hebr-Latn-31636-2018` | 31.13% | 27.03% | 39.25% | 98.06% | 851/1864 |

Ranking (best-to-worst by `retention`; identical order under all three
models): `icao-heb-Hebr-Latn-9303` > `din-heb-Hebr-Latn-31636-2018`.

## Provenance

Run records from bucket `rhtse/jobs-artifacts/ivrb/` (decode dates are
the record write times, UTC; shard rows sum to each full split):

| model | records | decode dates |
|---|---|---|
| urd-vocalized-1.0 | `urd-vocalized-1.0.urd-vocalized-1.00-2.json` (shard 0/2), `…1.01-2.json` (shard 1/2) | 2026-11-25 12:37 / 14:02 |
| urd-vocalized-2.1 | `urd-vocalized-2.1.urd-vocalized-2.1.json` (whole split, 0/1) | 2026-11-25 12:00 |
| heb-vocalized-1.1 | `heb-vocalized-1.1.heb-vocalized-1.10-4.json` … `…1.13-4.json` (shards 0–3/4) | 2026-11-25 23:17 → 2026-11-26 01:08 |
| heb-vocalized-1.0 | `heb-vocalized-1.0.heb-vocalized-1.00-4.json` … `…1.03-4.json` (shards 0–3/4) | 2026-11-26 04:04 → 06:33 |
| heb-vocalized-small-1.0 | `heb-vocalized-small-1.0.heb-vocalized-small-1.00-2.json` (0/2), `…1.01-2.json` (1/2) | 2026-11-26 16:22 / 16:52 |

Per-record pins: interscript-py `bf3ac6f` (engine + IMF runtime), maps
`cc67dd3` (= maps release v3.2.0, `maps/` byte-identical),
interscript-rs `f054108` (release/0.2.2); data shas `6d822ae7…` (urd) /
`77e9b5dc…` (heb) and each model zip sha256 verified in-job before
decode.

## Landed-run notes (published, not dropped)

- **SPEC §9.4 cross-validation did not run in these legs:** every landed
  record carries `crossval: null` — no ≥ 200-row iscrs cross-check per
  system was captured. The ranking above is published with that gate
  OPEN; adjudication is owner-side.
- **Hebrew direct-CER inversion:** heb-vocalized-1.1 shows direct CER
  30.46% vs heb-vocalized-1.0's 25.18%, although 1.1 is the stronger
  house model (DER greedy 16.44 vs 29.0). The shipped Hebrew anchors
  are DER, not corpus-level CER, so this is not an anchor violation —
  reported verbatim, not normalized.
- Hebrew `mark_leak` is material (icao 1193/1864, din 851/1864) — the
  genuine map-robustness finding SPEC §10.4 anticipates, published not
  dropped.
