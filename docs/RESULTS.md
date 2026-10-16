# interscript-ml results

Evaluated results for models produced in this repository. Each section
anchor is the provenance target referenced by model metadata
(`models/*/` metadata.yaml) and `models/metrics-sources.yaml`.

## tha-g2p-base-1.0 — Thai G2P distillation (2026-08-19)

Sequence-level KD: B-K/umt5-thai-g2p-v2-0.5k teacher -> ByT5-base
student over 48,757 beam-4 teacher-generated labels (Kaikki + epitran
Wikipedia corpus, deduplicated, degenerate outputs filtered). Harness:
beam-4, corpus-level PER (total_ed / total_gold over characters of
joined-piece decode), 1,219 held-out Kaikki Thai test sentences
(`src/gpu/modal_distill.py::evaluate_per`).

| Model | PER (beam-4) | PER (greedy) | EM (greedy) |
|---|---|---|---|
| Teacher (B-K/umt5 hub base) | 4.43% | 1.25% | 95.16% |
| **Student (ByT5-base, gate)** | **9.19%** | **3.53%** | 90.48% |

Same-protocol distillation cost: +2.28pp greedy-to-greedy (was +4.76pp
beam-vs-beam), comfortably inside the +5pp budget. Greedy measured
2026-08-26 through the same harness at num_beams=1 — see the
tha-g2p-small correction for the decode pathology.

**Tier inversion at greedy:** the client tier (ByT5-small int4, 2.85%
through the runtime ONNX path) outperforms this server-tier student
(3.53% through the torch harness); the 0.08pp ONNX parity delta cannot
account for a 0.68pp gap, so the ordering is real on this harness. The
beam-4 figures had the tiers reversed.
(docs/DISTILL-SOURCE-PROMPT.md). ByT5-small ablations for reference:
12.63% on 23K labels, 12.06% on 48.7K labels (capacity-limited, both
rejected by the gate).

Context: the secryst-published 2.32% umt5 teacher is unrecoverable
from saved artifacts (transformers 5.15 save drops the untied umt5
lm_head) and the volume's epitran augmentation corpus is tone-less;
this release distills the best verified teacher available. A repaired
2.32%-tier teacher re-enters this pipeline when secryst regenerates it.

The 1,219-sentence test set is now published as a citable benchmark:
`benchmarks/thai-kaikki-g2p/` (data, protocol, reference points). No
external Thai comparison exists to date; systems evaluating on the
published benchmark can be ranked against the reference points above.

## fas-g2p-1.0 — Persian G2P (2026-08-19)

The v1 ByT5-small teacher shipped directly (byte-level, client-tier
size — no distillation step applies). REF teacher: persian-g2p-checkpoints
`persian_g2p/run-001/best`, RELEASE-FROZEN per rababa
docs/DISTILL-SOURCE-PROMPT.md (RL variants and the v5/mapped
representation line are closed negative; v1 is final).

| Metric | Value |
|---|---|
| CER (v1 test split, greedy, editdistance) | ≈1.6% |
| SentenceBench homograph (ezafe-normalized) | 77.34% |

Published reference: Homo-GE2PE homograph 76.89% — v1 is above the
published best on this benchmark. Claim scope (2026-08-26): SentenceBench
homograph accuracy only. Concurrent Persian G2P lines report on their own
PER benchmarks — prompted LLMs with post-processing (arXiv 2409.08554,
best 8.30% PER) and intermediate-language transliteration trained on
LLM-generated data (arXiv 2505.06599) — none shares an evaluation set
with SentenceBench, so no cross-paper ranking is claimed.

## heb-diac-small-1.0 — Hebrew student distillation (2026-08-20)

Logit KD from the s43 teacher (rababa_hebrew_byt5_s43/run-001/best):
KL + CE on hebrew-v4, ByT5-small init. Harness: greedy decode, Nakdimon
IMF test split (1,864 long sentences), same harness for both models
(`src/gpu/modal_distill.py::evaluate`).

| Model | DER | CER |
|---|---|---|
| Teacher (s43, ByT5-base) | 24.79% | 22.14% |
| **Student (ByT5-small, gate)** | **30.37%** | 24.47% |

Shrink cost +5.58pp — inside the ~5.6pp budget pre-accepted for this
pair (rababa docs/DISTILL-SOURCE-PROMPT.md section 2).

## tha-g2p-small-1.0 — Thai G2P client tier (2026-08-22)

The client-tier release of the Thai G2P distillation: run-003,
ByT5-small student on the full label set (48,757 usable beam-4 labels
from the B-K/umt5-thai-g2p-v2-0.5k teacher). Same harness as
tha-g2p-base-1.0 (beam-4, corpus-level PER, 1,219 held-out Kaikki Thai
test sentences, `src/gpu/modal_distill.py::evaluate_per`; checkpoint
re-measured 2026-08-22 for this release).

| Model | PER | Exact match |
|---|---|---|
| Teacher (B-K/umt5 hub base) | 4.43% | 95.57% |
| **Student (ByT5-small, client rung)** | **12.06%** | 87.94% |

Shrink cost +7.63pp — outside the +5pp server-tier gate (that gate is
met by tha-g2p-base-1.0 at 9.19%): shipped anyway per the frontier
below, as the smallest artifact that does not collapse. Exported at
int8 (~300MB); see the frontier table for why no smaller rung exists
today.

**Correction (2026-08-24): greedy is the real decode, and it is far
better than the beam-4 harness numbers.** Re-measured on the shipped
int4 zip through the Python runtime (the exact ONNX KV decode users
get), true Levenshtein, full 1,219-sentence set:

| Decode | Teacher PER | Student PER | Student EM |
|---|---|---|---|
| beam-4 (published, torch harness) | 4.43% | 12.06% | 87.94% |
| **greedy (runtime protocol)** | **1.25%** | **2.85%** | **88.93%** |

The teacher is also affected by the beam pathology (4.43 beam-4 → 1.25
greedy, measured 2026-08-25 through the same harness at num_beams=1):
same-protocol, the client tier's true shrink cost is **+1.60pp**, not
the +7.63pp the beam-vs-beam comparison suggested.

The beam-4 numbers are inflated by length-normalized beam preferring
long garbage on this model's flat per-token distributions (top-1
logprob ≈ -4.6 vs uniform -5.6): exact-match barely moves but every
non-exact output runs long, multiplying edit distance. Beam decode is
COUNTERPRODUCTIVE for these students; the runtimes ship greedy and
that is optimal. The runtime exposes num_beams as an opt-in (verified
correct against per-beam batch-1 references); the published beam-4
figures stand as measurements under that decode, not as quality
claims. All future gates decode greedy (the Arabic harness already
does).

## Client-tier size–quality frontier (2026-08-22)

Thai G2P, same harness (beam-4 corpus PER, 1,219 Kaikki sentences; teacher
B-K umt5 4.43%):

| Student | Init | Params | Artifact (int8) | PER |
|---|---|---|---|---|
| custom 8+8 d384 | random | 33M | ~30MB | 75.80 (collapsed) |
| custom 8+8 d384 + bridges | random | 33M | ~30MB | 71.12 |
| custom 10+10 d512 + bridges | random | 70M | ~70MB | 78.51 |
| ByT5-small | pretrained | 300M | ~300MB | 12.06 |
| ByT5-base (server tier) | pretrained | 580M | 1.2GB fp32 | 9.19 |

Findings: (1) random-init byte-level seq2seq collapses regardless of
capacity at this scale — the microkimi bridges improve structure (75.8 →
71.1) but cannot rescue G2P accuracy; enlarging without pretraining does
not help (70M = 78.5). (2) ByT5-small's width (d=1472) dominates its
parameter count — depth-pruning yields no useful intermediate rung
(263M). (3) The pretrained rung is the whole quality cliff: 300M at
12.06% (run-003, full labels; 12.63% on the 23K subset) vs 70M at 78.5%.

Conclusion: G2P client tier ships at the ByT5-small rung — 246MB at
int8, 202MB at int4 (parity 0.0734pp, quality cost ~0.17pp CER; PRs
#30/#31) — today; a 30–70MB G2P tier requires byte-level pretraining
of the small model first (future work). Copy-task languages are
evaluated separately below.

## ara-diac-tiny verdict — 33MB from-scratch student collapsed (2026-08-23)

The Arabic copy-task hypothesis test: a 33M-parameter custom byte-level
student (d384, 8+8) trained CE on 11,792 r6-teacher labels for 3
epochs (train CE converged to 0.46). Gate harness: windowed DER-CE at
the 1400-byte r5 window, greedy, haraqat-projected, Misraj evaluator —
identical to rababa's eval_sadeed_windowed; validated by the teacher
reproducing its documented tier on this replication.

| Model | DER-CE (300 Sadeed paragraphs) |
|---|---|
| Teacher (r6, run-006-morph) | 1.32% |
| **Student (33M from-scratch)** | **83.08%** — REJECTED |

Gate ≤ teacher + 0.5pp: the student misses by two orders of magnitude.

**RETRACTION (2026-08-24):** this verdict is CONFOUNDED — every Arabic
label generated before the byt5 `decode_joined` fix was mojibake
(double-encoded targets); both Arabic students trained on corrupted
labels, and their identical DER scores are the bare-text constant, not
a capacity result. The numbers stand as measured but the capacity
conclusion for Arabic is UNPROVEN pending a clean-label re-run. The
Thai tiny verdict is unaffected (umt5/sentencepiece labels were
byte-exact); the pretrained-backbone law rests on Thai evidence.

## ara-diac-tiny run-004 — the retracted verdict reproduced, on poisoned data (2026-08-29)

The spec intended to rerun the tiny tier on clean labels silently
consumed the Aug-23 label snapshot (pre `decode_joined` fix). Evidence
chain:

- run-004/best decodes `كتاب` as `ÙÙØ§ØªÙØ¨` — UTF-8-as-Latin1 mojibake,
  the exact label corruption the retraction describes
- the 300-paragraph windowed gate (n=300, teacher reproduces its
  documented 1.3205) scores the student **83.0797** vs the retracted
  **83.08** — identical to four decimals: the poisoned-data constant,
  not a capacity result
- `final_eval.json` in the run dir is the durable provenance

Verdict: run-004 says nothing about from-scratch capacity; the
retraction stands. **run-005** (fresh teacher labels, no snapshot,
2026-08-29) is the actual clean-label falsification test — in flight.

## ara-diac-tiny run-005 — clean-label verdict: from-scratch collapses (2026-08-29)

The falsification test the Aug-24 retraction called for: same 33M
from-scratch student (d384, 8+8), labels regenerated live from the r6
teacher (11,793 units, no snapshot), 4,422 steps / 3 epochs, final CE
~0.9. Windowed gate, 300 SadeedDiac-25 paragraphs, teacher reproduces
1.3205:

| Model | DER-CE (300) |
|---|---|
| Teacher (r6) | 1.3205% |
| Tiny, mojibake labels (run-004) | 83.08% |
| **Tiny, clean labels (run-005)** | **74.68% — REJECTED** |

Clean labels recover ~8pp of the collapse — the student learns real
signal — but remains two orders off the <= 3.07 gate. **The
pretrained-backbone law now rests on Arabic evidence as well as
Thai**: from-scratch byte-level students at this width do not work.
The viable path to a sub-100MB browser tier is width reduction FROM a
pretrained ByT5-small (closed-form stitch across widths, microkimi
protocol), not from-scratch training.

[CORRECTED 2026-09-05: the 4.8218 figure below did not reproduce; the corrected 2.0 number is 5.08 (see the correction entry above).]
## ara-diac-small-1.0 — Arabic client tier (2026-08-24)

Sequence-level KD from the r6 teacher (rababa_arabic_byt5/run-006-morph,
2.5793 windowed DER-CE full-protocol): 29,322 greedy labels on r5-units
(domain + replay, 1400-byte windows), ByT5-small init, 3 epochs. Same
windowed harness as the ara-diac-tiny verdict (300 SadeedDiac-25
paragraphs, Misraj evaluator, haraqat projection):

| Model | DER-CE (300-para subset) |
|---|---|
| Teacher (r6) | 1.3205% |
| **Student (ByT5-small, client rung)** | **3.6580%** |

**Full-set correction (2026-08-26): the subset was not representative.**
Re-measured on the full 1,200-paragraph SadeedDiac-25 benchmark (same
harness; teacher reproduces its documented value at 2.5815 vs 2.5793,
confirming protocol consistency):

| Model | DER-CE (full 1,200) |
|---|---|
| Teacher (r6, full-set) | 2.5815% |
| **Student (ByT5-small, full-set)** | **8.2590%** |

The first 300 paragraphs sit in the student's training-domain
neighborhood; the remaining 900 expose a domain-generalization gap the
subset hid. The student's catalog number is the full-set 8.26; the
300-para figures above stand as measurements of that subset only.

Gate discussion: against the full set the strict budget (teacher
+0.5pp) is missed by +5.68pp — the capacity-plus-domain cost of
ByT5-small trained on 29K r5-unit labels, consistent in direction with
the Thai client tier. Shipped as the Arabic client rung with that
number disclosed: the student generates real, well-voweled Arabic at a
fraction of the teacher's artifact (1.3 vs 2.6 GiB) and the strict gate
is met by the teacher release (ara-diac-1.0, 2.58 full-set). On the
SadeedDiac-25 leaderboard the student at 8.26 sits just behind
Sadeed-1.5B (7.2915 published) and ahead of nothing measured below it —
the earlier "between Gemini-Flash and GPT-4" reading was an artifact of
the unrepresentative subset and is withdrawn.

Training notes: this is the third training of run-002 — the first on
mojibake labels (byt5 decode_joined bug), the second silently resumed
from the poisoned lineage's checkpoints (now guarded by labels.sha
digest matching), this one clean end-to-end. CE plateaued at ~0.016.

### run-003-pkm — memory-layer student (2026-08-28, research run)

The qwen-next capacity experiment (EXPERIMENTS.md E2): identical to
run-002 except three product-key memory layers (+85.9M lookup params,
zero-init gates) on the ByT5-small decoder — single-variable.

| Model | DER-CE (full 1,200) |
|---|---|
| Teacher (r6, full-set) | 2.5815% |
| **Student + PKM memory (run-003-pkm)** | **7.5553%** |
| Student vanilla (run-002) | 8.2590% |

0.704pp of the 5.677pp teacher-student gap closed (12.4% relative) at
near-zero added compute — below the pre-registered ≥1.0pp win bar, so
the memory axis is real but not the dominant term of the gap. Gates
verified engaged (0.034-0.053 at completion). Not shipped; the vanilla
client rung stands.

### run-004-pkm-muon — optimizer A/B on the memory student (2026-08-28)

Identical to run-003-pkm except the optimizer (Muon on 2D hidden
matrices, AdamW group for embedding-like params; EXPERIMENTS.md E3):

| Model | DER-CE (full 1,200) |
|---|---|
| Teacher (r6, this container) | 2.5997% |
| **ByT5-small + PKM + Muon (run-004)** | **4.8287%** |
| ByT5-small + PKM + AdamW (run-003) | 7.5553% |
| ByT5-small vanilla + AdamW (run-002) | 8.2590% |

**−2.727pp from the optimizer alone** — the adopt gate (≥0.3pp)
exceeded 9x; 3.430pp of the 5.677pp canonical gap closed (60.4%)
combining memory + optimizer. Training CE ~0.007 vs ~0.02 at equal
steps; ~1.2s/step vs ~3.4s; no stability events. The teacher-student
gap at this rung decomposes: ~0.70pp capacity + ~2.73pp optimization
+ ~2.25pp residual (domain coverage). The vanilla+Muon factorial cell
(run-005-muon) completes the decomposition.

### run-005-muon — factorial cell 4: vanilla + Muon (2026-08-28)

| Model | DER-CE (full 1,200) |
|---|---|
| ByT5-small + Muon (run-005) | 5.2945% |
| ByT5-small + PKM + Muon (run-004) | 4.8287% |
| ByT5-small + PKM + AdamW (run-003) | 7.5553% |
| ByT5-small vanilla + AdamW (run-002) | 8.2590% |

The 2x2 closes cleanly: optimizer alone −2.96pp; memory alone −0.70pp
(−0.47 under Muon); combined −3.43pp (60.4% of the 5.677pp canonical
gap) — roughly additive, slightly sub-additive on memory. Residual
~2.2pp is domain coverage. Optimization is the dominant recoverable
term of the distillation gap at the ByT5-small rung.

### run-006-r7-muon — E4: the 2.0 release candidate (2026-08-29)

The two measured wins compounded on the vanilla architecture: r7
canonical teacher (fresh greedy labels) + Muon optimizer, same
corpus/limits/seed family. Pre-registered E4 gate ≤ 6.26 (prediction
4.3–5.0):

| Model | DER-CE (full 1,200) |
|---|---|
| Teacher (r7, in-run) | 2.2890% |
| **ByT5-small, r7 labels + Muon (run-006)** | **4.8218%** |
| ByT5-small, r6 labels + Muon (run-005) | 5.2945% |
| ByT5-small, r6 labels + AdamW (run-002, shipped 1.0) | 8.2590% |

**4.8218 — gate passed; −3.44pp / 42% relative vs the shipped 1.0** at
identical architecture and artifact size. Matches the PKM arm's 4.829
without the memory layers. Release: ara-diac-small-2.0 (run-006
checkpoint; strict teacher+0.5pp still missed at +2.53pp, disclosed).

Leaderboard context (SadeedDiac-25, Misraj evaluator, zero-skip,
harakat-projected DER-CE): the teacher tier (r6, 580M) at 2.5793
(reproduced at 2.5815, 2026-08-26) is the best dedicated model measured
under this protocol — second only to Claude-3.7-Sonnet's published
1.3941, ahead of GLM-5.2 zero-skip (2.6911), Gemini-Flash-2.0 (3.1926),
GPT-4 (3.8645), Sadeed-1.5B (7.2915; source table in rababa
docs/RESULTS.md), and GLM-5.3-Flash (8.5721 raw / 8.7978 zero-skip,
effort=low, 2026-08-31 — behind Sadeed-1.5B; protocol note: the API
rejects disabled thinking combined with reasoning_effort, HTTP 400
code 1210, so effort is pinned per row). The client student's full-set
8.26 lands behind Sadeed-1.5B; see the correction above.

## IMF runtime benchmarks — E1 node tier (2026-08-29)

Paper-C evaluation axis (benchmarks/imf-runtime; SPEC.md defines
tiers x environments x metrics). First measurements, node tier
(Apple Silicon, node 24, interscript@4.1.0, production Release path):

| tier | cold resolve+fetch+verify | warm cache-hit | sha256 tax | session create | decode (short/long) | peak RSS |
|---|---|---|---|---|---|---|
| ara-diac-small-1.0-int8 (257MB) | 25.0s (network) | 528ms | 110ms | 13.1s | 994ms / 2.76s | 953MB |
| tha-g2p-small-1.0 (int8, 202MB) | — | 397ms | 114ms | 12.1s | 85ms / 3.18s | 983MB |
| tha-g2p-small-1.0-int4 (202MB) | — | 369ms | 87ms | 7.3s | 213ms / 6.48s | 711MB |

Headline: **the integrity discipline is free** — whole-file sha256 is
~0.1s against 7-13s session creation; the verified-index + cache-hit
path is ~0.4s. int4 halves load time but decodes ~2.5x slower than
int8; int8 is the client default. E2 (Modal 4-vCPU / 8 GiB — the production serving shape, 2026-08-29):

| tier | cold load (zip + verify + ORT) | decode short/med/long |
|---|---|---|
| tha-g2p-small-1.0 (257MB) | 3.92s | 130 / 409 / 671 ms |
| ara-diac-small-1.0-int8 (257MB) | 4.04s | 395 / 525 / 973 ms |

Server vs node-laptop tier: cold load 4s vs 13s session create, decode
~2.5-3x faster — the serving tier trades network for speed. E3 (browser
WASM/WebGPU) pending.

## ara-diac-small-layerdrop — the depth-cut rung PASSES on the subset (2026-08-30)

Encoder 12->6 from pretrained ByT5-small, layers copied VERBATIM
(no projection - the width-cut rungs failed at 74.68/82.96), Muon,
same clean r6 labels, 10,995 steps, final CE 0.016 (the scratch rung
converged near 0.9 - 50x lower train loss at the same step count).
300-paragraph subset gate (teacher reproduces 1.3205):

| rung | params | subset DER-CE |
|---|---|---|
| ByT5-small 1.0 (AdamW, full) | 300M | 3.658 |
| **layerdrop (enc 6, Muon)** | ~190M | **3.8088** |

Halving encoder depth costs 0.15pp on the subset - the pretrained
representation survives a depth cut that width surgery destroyed.
Full-set gate (1,200 paragraphs) in flight; int8 ~190MB, int4 ~95MB
(the browser-budget artifact). Survived two infra failures en route
(eviction without watchdog; a regressed d_kv derivation) - both fixed.

## ara-diac-small-layerdrop — full-set verdict: 7.44 (2026-08-31)

The 1,200-paragraph gate (teacher reproduces 2.5815):

| rung | params | full-set DER-CE | subset DER-CE |
|---|---|---|---|
| 1.0 (full depth, AdamW, r6) | 300M | 8.259 | 3.658 |
| **layerdrop (enc 6, Muon, r6)** | **~190M (63%)** | **7.4413** | 3.8088 |
| r6 + Muon (full depth) | 300M | 5.2945 | — |
| 2.0 (r7 + Muon, full depth) | 300M | 4.8218 | — |
| scratch d384 | 33M | 74.68 | 83.08 |
| SVD width-stitch d384 | 29M | 82.96 | — |

Reading: halving encoder depth + Muon BEATS full-depth AdamW (7.44 vs
8.26) at 63% of the parameters — but the depth cut costs 2.15pp against
its optimizer-matched peer (5.29). Strict gate (teacher+0.5) failed.
This is the THIRD instance of the first-300 subset overstating quality
(3.66 vs 8.26; 3.81 vs 7.44) — the subset sits in the training-domain
neighborhood; full-set-only stands as the publication rule, now with a
quantified repeat rate. The size-quality frontier is complete and
monotone: 33M/74.7 - 29M/83.0 - 190M/7.4 - 300M/5.3 - 300M/4.8
(teacher 2.28-2.58). Browser-tier decision (user): ship
layerdrop-int4 (~95MB, ~7.5 DER with int4 flip risk ungated) as the
lite rung, or hold the tier at 2.0-int8 (264MB, 4.82).

## ara-diac-small-d768 — gentle stitch fails too: the width-cut closure is complete (2026-08-31)

The untested 2x ratio (d1472->d768, ~105M, Muon, same r7 labels,
10,995 steps, train CE recovered to 0.95): 300-subset DER 78.23
(teacher in-run 1.2887). SVD width-stitching now fails at BOTH tested
ratios (3.8x: 82.96; 2x: 78.23) while the depth cut works (7.44).
The law sharpens: the pretrained WIDTH is load-bearing - projection
destroys the representation at any compression; depth is the
compressible axis. First verdict carrying the label-provenance hash
(labels sha256 e70ce991..., 137.2MB recorded in final_eval.json).

## ara-diac-small-2-6ep — doubling epochs collapses the residual (2026-08-31, subset)

Same as the 2.0 rung (r7 labels, Muon, vanilla ByT5-small) at 6 epochs
instead of 3 (21,990 steps, final CE 0.0013). 300-subset verdict:
teacher in-run 1.2887, student **2.0062** — gate_delta 0.72, within
striking distance of the strict teacher+0.5 gate, vs 3.66 (1.0) and
3.81 (layerdrop) on the same subset. **This overturns the E2/E3
residual attribution**: the 2.25pp residual was mostly optimization
(undertraining), not domain coverage. Full-set gate running - given
three prior subset-overstatement instances, the honest number waits
there. Provenance: labels sha256 e70ce991 (137.2MB) recorded.

## ara-diac-small-2-6ep — full-set verdict: 4.5701; the discipline vindicated (2026-08-31)

Full 1,200-paragraph gate (teacher in-run 2.289): student **4.5701**,
gate_delta 2.28. Doubling epochs bought 0.25pp over the 3-epoch 2.0
rung (4.8218 -> 4.5701) - the residual is NOT mostly undertraining;
the E2/E3 domain attribution substantially stands (~0.25pp epochs,
~2.0pp domain/other). The subset had said 2.0062 / delta 0.72 - a
near-overturn of the decomposition that the full set corrects: the
FOURTH subset-overstatement instance and the most dramatic (subset
delta 0.72 -> full delta 2.28, a 3.2x inflation). The full-set-only
publication rule earns its keep here: this entry is the paper's
strongest measurement-discipline exhibit.

## ara-diac-small-layerdrop-6ep — subset 2.6495 (2026-09-01)

A2 (TODO.improve-compare): the lite rung with G2a's full lever set
(6 epochs, Muon, r7 labels, half depth). 300-subset: teacher in-run
1.3014, student **2.6495**, paired bootstrap delta 1.4842
[1.079, 1.975], p=0. The epochs lever moved the lite rung 3.81 -> 2.65
(full-depth moved 3.66 -> 2.01): most of the optimization gain
transfers at half depth; the depth cost widened from 0.15pp (3ep) to
0.64pp (6ep) on this subset. Full-set gate in flight - the honest
number per the four-instance subset-overstatement record. First lite
verdict carrying its own CI.

## ara-diac-small-layerdrop-6ep — full-set 5.784: the frontier closes (2026-09-01)

Full 1,200-paragraph gate (teacher r7 in-run 2.2921): student
**5.784**, paired bootstrap delta 3.2455 [3.033, 3.491], p=0. The
complete full-set frontier: 1.0 (3ep AdamW, 300M) 8.259 -> lite (6ep
Muon, 190M) **5.784** -> full (6ep Muon, 300M) 4.5701 -> teacher 2.29.
Depth cost at 6 epochs: 1.21pp (CIs non-overlapping vs G2a [1.91,
2.35] - statistically real). Subset said 0.64pp: the FIFTH
subset-overstatement instance. The lite tier is shippable: 28% smaller
artifact for 1.21pp; int4 (~95MB) export is the browser-budget item.

## CI table complete — every frontier row bracketed (2026-09-02)

The 1.0 baseline's retrofit lands the final interval: student 8.2576,
delta CI [4.596, 5.651] (n=1200). The full-set table, all rows with
non-overlapping sequential intervals:

| rung | full-set DER | delta CI95 vs teacher |
|---|---|---|
| 1.0 (AdamW, r6, 3ep) | 8.2576 | [4.596, 5.651] |
| lite (Muon, r7, 6ep, half-depth) | 5.784 | [3.033, 3.491] |
| 2.0 (Muon, r7, 3ep) | 4.8218 | [2.358, 2.823] |
| G2a (Muon, r7, 6ep) | 4.5701 | [1.911, 2.352] |

Every lever claim in paper B now carries its interval; the monotone
separation between rungs is statistically real end to end.

## ara-diac-tiny-max — the gapless title test: 73.95, collapse confirmed (2026-09-02)

The 30M class with EVERY lever (full 24k+6k corpus, r7 labels, Muon,
6 epochs, 21,990 steps, CE ~0.51): full-set **73.9489**, delta CI
[70.222, 71.093], p=0. The maximal run improves on the handicapped
scratch collapse (74.68) by 0.7pp: data quality and optimization do
NOT rescue 30M from-scratch. Conclusion from evidence: the
"30M-parameter encoder" title claim is closed; the thesis repositions
per PAPER-ALIGNMENT.md.

## ara-diac-small-2-6ep-tashkeela (G2b) — full-set 4.8231: the add-direction test is FLAT-NEGATIVE (2026-09-04)

The domain-residual causal test (TODO.publish-client 01): the G2a
recipe with the FULL cleaned Tashkeela corpus added (5x classical
coverage, 48k units, 39,018 steps, final CE ~0.002). Full 1,200-para
gate: teacher in-run 2.289, student **4.8231**, paired bootstrap delta
2.3717 [2.194, 2.554], p=0 — vs G2a's 4.5701 [1.91, 2.35]. The point
estimate moved the WRONG direction by 0.25pp with overlapping CIs:
statistically flat. Gate (>=0.5pp improvement) FAILED.

Verdict: combined with E6 (register swap at constant budget, -0.98pp),
BOTH directions of the classical-corpus manipulation fail to close the
residual — the student-tier gap is NOT a classical-domain coverage
deficit. The domain-coverage attribution is rejected in the add
direction and the swap direction; the residual reframes as a
teacher-student interaction the corpus cannot reach (candidate next
levers: on-policy distillation — GKD in flight; label-distribution
effects). G2a (2.1) remains the best student; G2b stands as the
closing negative of the data-side program. Provenance: labels sha256
b59e2f56 (235.0MB).

## heb-diac-small-s46-layerdrop — the depth-cut does NOT transfer: 77.48 DER (2026-09-05)

Item 04 (TODO.publish-client): the Arabic width/depth finding
replicated on Hebrew — encoder 12->6 verbatim layer copy from
pretrained ByT5-small, single variable vs run-002-s46 (same s46
teacher, hebrew-v4 corpus, 3 epochs, logit-KD recipe). Training
converged normally (val_loss 0.550); the full Nakdimon gate did not:

| Model | DER (n=1864) |
|---|---|
| teacher s46 | 23.72 (reproduces exactly) |
| full-depth student (run-002, 1.1) | 30.38 |
| **layerdrop student (run-003)** | **77.48** — collapse |

Paired delta +53.77pp [51.64, 55.92], p=0.

Verdict: the "depth is the compressible axis" finding does NOT
transfer as-is. Confound, stated honestly: the Arabic rung used
sequence-KD (teacher labels, Muon, 6 epochs); this run used the Hebrew
lineage's logit-KD (alpha-KL + CE) at its native 3 epochs — so the
collapse may be recipe-dependent (depth-cut + logit-KD), not purely
linguistic. Either way the cross-lingual generalization claim is
closed as a negative: depth-compressibility is NOT a universal
property of pretrained ByT5-small; it held under one recipe on one
language. Paper B's depth paragraph is scoped accordingly (this entry
is its counterexample).

## CORRECTION: ara-diac-small-2.0 full-set is 5.08, not 4.8218 (2026-09-05)

The published 2.0 number (2026-08-30, in this ledger and the shipped
metadata) does not reproduce. Two independent later measurements of
the same checkpoint agree and disagree with it:

| Measurement | Path | DER-CE |
|---|---|---|
| published (2026-08-30) | harness, in-run | 4.8218 |
| harness re-eval (final_eval.json, bootstrap CI [2.358, 2.823]) | torch, same protocol | 5.0821 |
| **artifact-level (this entry)** | shipped zip sha d9aa95d0 (= index pin = release bytes), windowed ONNX runtime decode, sadeedbench scoring | **5.0321-class** (5.0329) |

The artifact-level measurement is the governing one: it scores the
exact bytes users download. The 4.8218 figure is withdrawn; the 2.0
rung's catalog number is 5.08 (harness) / 5.03 (runtime path). The
cause of the original reading is not reconstructed; both later
measurements postdate it and agree to 0.05pp across independent decode
paths.

Consequences, stated plainly:
- the E4 error-reduction claim becomes 8.259 -> 5.08 (38%, not 42%)
- the "matches the PKM arm (4.829)" statement is wrong: the vanilla
  2.0 rung (5.08) does NOT match the PKM arm; the PKM arm was better
  by 0.25pp at its measurement
- frontier ordering 1.0 -> lite -> 2.0 -> 2.1 is unchanged; G2b
  (4.8231) sits between 2.0 and 2.1 rather than above 2.0
- every other frontier row re-verified exactly by the same
  artifact/preds-level tooling (8.2576 / 4.5701 / 5.784 / 4.8231)

Predictions for all five frontier runs publish alongside this entry
(release frontier-predictions-v1) so the numbers above are re-derivable
by anyone.

## ara-diac-small-2-gkd — on-policy distillation NEGATIVE: 6.0036 (2026-09-06)

The on-policy rung (GKD: student-generated mistakes scored by the
teacher, 10,995 steps, labels sha e70ce991): teacher reproduces 2.289,
student **6.0036** full-set, paired bootstrap delta 3.4083 [3.109,
3.743], p=0 — gate FAILED, and 1.43pp WORSE than the off-policy
sequence-KD rung it was meant to improve (G2a 4.5701).

This completes the residual-attribution program with a clean pattern:
every lever tested fails to close the teacher-student gap —
* classical corpus add (G2b): flat-negative
* register swap (E6): negative
* on-policy distillation (GKD): negative, worse than off-policy
* memory layers (PKM): real but small (0.70pp), below bar
* epochs: small (0.25pp)
The residual is not data, not domain coverage, not an off/on-policy
deficit. It is a property of the compression itself at this rung —
the honest open question for the paper. On-policy stays listed in
Paper B's future work with its measured negative attached.

## Cross-runtime byte-parity is precision-scoped (2026-09-07, golden-v1)

The golden matrix (12 models x 25 rows, generated from the released
zips on x86/ORT-1.23.2) exposes the true boundary of the byte-parity
contract, measured three ways (Python-x86 generator, Python-arm64,
TS-arm64; ORT 1.23.2 everywhere):

- **fp32-class artifacts: byte-stable.** ara-diac-1.0 reproduced
  exactly on arm64 before the run reached the quantized models.
- **Quantized artifacts (int8/int4): prefix-consistent,
  stop-point-unstable.** Every divergent output is an exact PREFIX of
  the golden (no contradictory content anywhere); the divergence is
  exclusively WHERE decode emits EOS — the stop decision sits at a
  near-tie on these flat distributions, and architecture-level float
  accumulation differences (x86 container vs arm64, ORT-web vs
  ORT-native) flip it. Same mechanism family as the beam-decode
  pathology: likelihood ranking on near-uniform distributions.

Contract, scoped and honest: **byte-identical across runtimes and
hardware for fp32/fp16; for quantized artifacts, quality parity (the
published per-model cer_delta gates) plus prefix-consistency.**
golden-v1's quantized rows are reference outputs (documented
hardware/ORT provenance), not byte-assertions.

## Speculative decode across the tier ladder: acceptance 0.9886, output-preserving (2026-09-11)

The shipped artifacts form a drafter/verifier pair: ara-diac-layerdrop-1.0-int4
(190M) drafts, ara-diac-small-2.1-int8 (300M) verifies. Measured over
all 25 golden-v1 Arabic rows (CPU, K=8, greedy verification):

- acceptance 0.9886 mean (min 0.955, median 0.991) — the int4 drafter's
  argmax matches the int8 verifier's at ~99% of positions
- 8.85 tokens per verifier pass (K=8 plus the bonus token on full
  acceptance): ~9x fewer verifier invocations than token-by-token
  decode
- output preservation holds by construction and by measurement: every
  exactness-checked row (18 of 25; the O(T^2) plain-path reference is
  capped to <=600B rows) is byte-identical to the verifier's
  plain-path greedy; plain and KV paths agreed on all checked rows

Source: TODO.qwen-next/10 (DeepSeek-V4.1-Flash learnings, DSpark
pattern), probe at scripts/probe_speculative.py. Runtime:
interscript-ts SpeculativeModel (PR #77). The lite tier stays the
standalone fast path; this is a middle tier — 2.1 outputs at a
fraction of the decode calls.

## Speculative wall-clock on CPU: the first implementation is SLOWER (2026-09-12)

Follow-up measurement to the acceptance entry (bench:
interscript-ts/scripts/bench-speculative.mts, 5 golden rows, warm,
arm64 CPU / ORT-native):

| path | total s | tokens/s |
|---|---|---|
| 2.1 int8 plain (KV greedy) | 19.8 | 67 |
| lite int4 plain (KV greedy) | 61.5 | 22 |
| 2.1 via speculative | 113.8 | 12 |

Acceptance held at the bench (0.9880, matching the probe's 0.9886) —
the acceptance math is sound. The wall-clock is not, for two measured
reasons:

1. **Both speculative paths rebuild KV from zero every block** — the
   drafter re-prefills [PAD]+prefix per block and the verifier runs the
   full sequence with zero pasts per review: O(T^2) against the plain
   path's O(T). This is an implementation defect, not a property of
   the method; the production design carries pasts across blocks.
2. **int4 decode is slower than int8 on this CPU** (61.5s vs 19.8s for
   the plain paths): ORT's CPU int4 path (MatMulNBits decompression)
   loses to the int8 kernels on arm64 — the drafter is the expensive
   model here, inverting the small-drafter premise on this hardware.

Consequence for positioning: the tier's published claims ("~9x fewer
verifier invocations", output-preserving) stand; no wall-clock speedup
is claimed anywhere, and none should be until the KV-carrying
implementation is measured. On hardware with fast int4 (or GPU
verifier batches) the cost model inverts in the tier's favor.

## Decode framing is a third parity axis on dynamic-int8 artifacts (2026-09-12)

The KV-carrying rewrite of the runtime's speculative decode exposed a
mechanism the cross-hardware study (2026-09-07) did not cover:

**Dynamic-int8 ONNX graphs compute activation quantization scales per
fed tensor.** Decode framing — how many tokens share one decoder call
— therefore changes the numerics materially, on the SAME machine, same
runtime, same artifact:

- batched feed (K tokens with pasts) vs single-step feed: present
  values differ up to ~0.03 per element (fp32 KV would be ~1e-6);
  inner-position argmax flips are routine
- the batched-framing greedy is a DIFFERENT DECODE than the
  single-step one: drafter==verifier self-acceptance measured 33/66
  despite identical final strings via self-correction; the
  int4->int8 pair's batched-verifier output lost a word
  ("امُ عليكم" vs "السلام عليكم")
- measured pair acceptance under runtime framing (single-step
  drafting vs batched verification): **0.4614**, vs the probe's
  0.9886 measured under uniform plain-path framing — the probe
  number is framing-relative, and the runtime number is the real one

Wall-clock (arm64 CPU, warm, 5 golden rows): plain 2.1 int8 21.4s;
lite int4 75.7s (int4 CPU kernels lose to int8 — MatMulNBits); the
O(T) speculative pair 155.4s at 0.46 acceptance. Verdict: **the
speculative tier is not viable on quantized CPU artifacts** — the
int4 drafter is the expensive model AND framing divergence collapses
acceptance. The technique's domain is fp-class artifacts or serving
paths with consistent framing. The playground tier was pulled
accordingly; the runtime keeps SpeculativeModel as measurement
infrastructure with the constraint documented.

## r6+r7 weight soup: same-basin, no free lunch — 2.4188 (2026-09-12)

50/50 weight average of the two measured Arabic teachers (580M,
run-006-morph and run-007-news), scored under the windowed protocol
on all 1200 rows: **2.4188** vs r6's 2.5997 and r7's 2.289. Per
domain: classical 1.38 (r7 1.36), news 3.31 (r7 3.21), wiki 2.66
(r7 2.08) — strictly between the parents everywhere; r7 remains the
best available teacher and the supervision choice is unchanged.

Two conclusions: (a) the checkpoints are same-basin (the soup is a
functional model, confirming linear connectivity between the two
teacher lineages — model-soup mechanics apply), and (b) at this pair
and scale the soup buys nothing over the better parent. The axis
closes negative; recorded so it is not re-derived.

## ara-diac-small-lite2 — trained-init depth cut is WORSE: 7.1402 (2026-09-12)

The lite cell's one untested variable was the layer-drop INIT SOURCE
(TODO.impl/04): run-009 (5.78) drops from generic pretrained
byt5-small; lite2 drops the same layers from the TRAINED 2.1 student,
then runs the identical 6-epoch sequence-KD distill (canonical r7
labels, sha e70ce991; teacher re-scores 2.2921 on the same run).

Result: **7.1402** full-set (n=1200), paired-bootstrap gap to teacher
4.29pp [3.83, 4.78]. The trained init is 1.36pp WORSE than the
generic init, not better.

Reading: generic pretraining keeps encoder layers redundant and
interchangeable, so every-other-layer deletion survives; task
adaptation prunes that redundancy — the layers become co-specialized,
and deleting half of a co-adapted stack breaks more learned
computation. Depth compression on this family survives on generic
init and degrades on adapted init, from either direction (the Hebrew
layerdrop collapsed from generic init under a weaker recipe; the
Arabic adapted-init collapses under the strong one). The lite tier
remains run-009 (5.78); init-source closes negative and the depth
axis now reads 2-of-3 negative. Remaining architecture lever:
TODO.impl/10 (lexical memory), gated as before.

## Framing completes as a distribution×precision matrix (2026-09-12, final)

The same single-vs-batched greedy test (5 golden rows x 96 steps, same
machine, ORT 1.23 everywhere), run to its endpoints:

| runtime | precision | single==batched |
|---|---|---|
| Python ORT | fp32 | 480/480 |
| Python ORT | dynamic int8 | 480/480 |
| Python ORT | static int8 | 480/480 |
| onnxruntime-node | fp32 | **101/485** |
| onnxruntime-node | dynamic int8 | 97/485 |
| onnxruntime-node | static int8 | 89/485 |

The framing instability is NOT a quantization property: the node build
diverges across batch shapes at fp32, and static activation scales
(pre-computed into the graph — TODO.impl/11's proposed fix) do not
repair it. It is a property of the onnxruntime-node kernel paths
(multi-token inputs take numerically different code paths than
single-token inputs), absent from the Python build at every precision.

Contract consequences, final form:
- cross-FRAMING parity holds under the Python reference at all
  precisions and does not hold under onnxruntime-node at ANY precision
- the shipped TS runtime is unaffected in practice: every shipped path
  (translate, worker, CLI) is single-framing; framing becomes a
  parity variable exactly when a runtime mixes batch shapes
  (speculative decode, batched serving) — which is why the speculative
  tier degraded and was pulled
- static int8 remains a POSITIVE byproduct: quality-clean vs fp32 on
  this sample (0/480 drift) and ~8% faster than dynamic on CPU —
  candidate for the export path on its own merits, decided by
  full-set quality, not framing

## Static-int8 full-set gate: 4.6241 — quality-clean, +8% CPU speed (2026-09-12)

The static-activation artifact (TODO.impl/11's byproduct: quantize_static
over 365 real decode feeds, MatMul-only, head fp32, QUInt8 acts,
remainder addressing) scored under the windowed protocol on all 1200
rows: **4.6241** vs the shipped dynamic int8's 4.5701 — a +0.054pp
delta, the same order as artifact-vs-checkpoint drift (the 2.0
artifact measured 5.0329 vs the checkpoint's 5.08). Together with the
framing matrix's speed leg (+8% tok/s vs dynamic on CPU: 78 vs 72),
static int8 clears quality and wins speed.

Decision state: the RE-EXPORT of all quantized artifacts through the
static path (modal_export gains the calibration stage; index-v6;
golden rows regenerate) is a release-scale operation and carries a
release-scale bar: re-run this gate with --out so the delta ships
with a paired-bootstrap CI. The point estimate stands recorded; the
export path change is small and the calibration corpus recipe is in
scripts/static_int8_experiment.py.

## Static-int8 release bar met: the paired CI (2026-09-17)

Both artifacts scored full-set with per-row predictions saved
(dynamic 4.5619; static 4.5952 — its second run, inside the drift
band with the first's 4.6241). Sentence-level paired bootstrap
(seed 42, n=1000, the campaign's standard) on the per-item DER delta:

**static − dynamic = +2.71pp, CI95 [−1.54, +7.11] (n=1195)** — the
interval crosses zero: not separated. Micro aggregates differ by
0.03pp; the macro point is dominated by short rows where a few haraqat
swings are a large per-sentence percentage.

Verdict by the standing rule: static and dynamic are
quality-indistinguishable at our measurement power, and static
carries +8% CPU decode speed. The re-export decision (index-v6,
golden regen, browser-size composition gated separately) is now fully
informed; the export path is one command (modal_export::static,
merged in PR #217).

## Static matrix completed: composition B (int8 enc) at 4.6045 (2026-09-17)

The browser-size premise corrected itself on measurement: the static
decoder graph (QOperator + casts) is LARGER than dynamic — composition
B (int8-dynamic encoder + static decoder) lands at 491 MiB vs the
shipped dynamic int8's 264 MiB. Static trades SIZE for SPEED; it is
the CPU-speed tier, not a browser play. Quality completes cleanly:

| composition | encoder | decoder | size | full-set DER |
|---|---|---|---|---|
| shipped dynamic | int8 | int8 (dynamic acts) | 264 MiB | 4.5619 / 4.5701 |
| static A | fp32 | int8 (static acts) | 1.17 GiB | 4.5952 / 4.6241 |
| static B | int8 | int8 (static acts) | 491 MiB | **4.6045** |

The int8 encoder costs ~0.01pp over A; everything sits inside the
drift band and inside the not-separated paired CI. Static's place in
the catalog, when the release is called: a server/CPU tier where
decode speed outweighs artifact size.

## ara-diac-small-2-1-engram — 4.6679: NOT SEPARATED from 2.1 (2026-09-29)

The lexical-memory run (TODO.impl/10): one 2M×32 byte-n-gram table at
encoder block 3, zero-init, table on the Sinkhorn-balanced rule (5× lr),
identical 6ep sequence-KD recipe and canonical r7 labels (sha
e70ce991), single variable vs run-007 (2.1, 4.5701).

Result: **4.6679** full-set (n=1200), gap to teacher 2.25pp CI95
[2.03, 2.47] — the delta vs 2.1 (+0.10pp) is small and inside the
drift band; paired bootstrap does not separate it from 2.1. Eval
methodology note: the first eval accidentally dropped the memory
(vanilla loader — the PKM lesson again); the gate number is
with-table via load_student_with_engram. The dropped-table score is
the no-memory control.

Verdict: FLAT. Lexical memory neither helped nor hurt at this scale
and dose — the encoder absorbed the capacity without converting it to
frontier movement on the news/wiki residual. The architecture ledger
now reads: depth cut ✗ (2 variants), lexical memory ✗ (flat),
on-policy ✗, teacher routing ✗, soup ✗. The 2.1 recipe remains the
frontier at 4.5701. Remaining measurable levers live in the recipe
lane (r8: headwise Muon + Sinkhorn arm) and the release lane
(static-int8 re-export).

## ara-diac-small-int8static-2.1 — the gated static-int8 artifact SHIPS (2026-09-30)

The TODO.impl/11 positive branch, released. Composition B (dynamic-int8
encoder + static-int8 decoder, calibrated QUInt8 activations, head fp32),
built from the verified release fp32 bytes (the volume staging copy had
torn; repaired from the release asset) with the full WO03 gate stack run
locally on the banked 2,480-reference:

| gate | value | limit |
|---|---|---|
| parity cer_delta | **0.1038pp** (2,480 samples) | 2.0pp (int8) |
| flip rate | 0.0324% | — |
| **confident flips** | **0.000000** | ≤1% |
| size | 491 MiB (515,362,212 B) | — |

Zero confident-position flips — the cleanest margin report any artifact
has produced. Published as release tag `ara-diac-small-int8static-2.1`
(id variant rides the slug; canonical asset
`ara-diac-small-int8static-2.1-int8.zip`), indexed on **index-v6**,
runtime shipped in **npm 5.5.1** (registry pin + tests), golden fixture
on golden-v1, site dep bumped, tag-protection rulesets active on both
repos. The CPU-speed tier of the static recipe is now shippable
infrastructure.

## Recipe arms verdict — headwise Muon SEPARATED-NEGATIVE, Sinkhorn embeddings FLAT (2026-10-01)

The DeepSeek-V4.1-Flash optimizer levers, measured single-variable off
the 2.1 recipe (run-007, 4.5701; canonical r7 labels e70ce991; teacher
2.2890 reproduced exactly in both runs; full 1,200-para windowed
protocol):

| arm | DER-CE | paired Δ vs 2.1 | CI95 | verdict |
|---|---|---|---|---|
| headwise Muon (run-014) | 4.8164 | **+0.2267pp** | [+0.016, +0.411], p=0.017 | **NEGATIVE — separated** |
| Sinkhorn embeddings (run-015) | 4.5547 | −0.0903pp | [−0.267, +0.069], p=0.858 | FLAT — not separated |

Head-wise Muon (positive at DeepSeek's 671B scale, sec 2.5) is
significantly HARMFUL on a 300M byte-student distillation — a clean
scale-boundary data point. The Sinkhorn-balanced embedding update
(Alg. 1) is indistinguishable from AdamW on the tied tables. **2.1
remains the frontier student.** The TODO.impl recipe ledger is now
fully measured: every optimizer/architecture lever is closed; the only
frontier mover on record is data-side (teacher r5→r6→r7).

## 2026-09-30 arXiv sweep — no new competitor; our premises externally validated

Monthly sweep (window Aug 26 → Sep 30, 2026: distillation, byte-level
modeling, diacritization, optimizer literature). Competitive position
unchanged: **no new text-only Arabic diacritization system appeared on
SadeedDiac-25** — the field's Arabic-diacritization energy moved to the
speech modality (KSAA-2026 Task 2 winner, 23.26% WER, speech input:
not protocol-comparable). r7 (2.2864) remains the best dedicated model
measured under our protocol; only Claude-3.7-Sonnet's published 1.3941
sits above it.

Four findings enter the record:

- **arXiv 2609.12303 (Meta/FAIR), "Breaking the Token Ceiling"** —
  first large-scale distillation × tokenization study (~1B params, up
  to 1T bytes): distilled *byte* students start worse but surpass
  token students with compute (predicted +4% asymptote, 6× data
  efficiency, 256-symbol vocab eliminates top-k logit truncation).
  Independent scaling-law validation of the byte-student lineage we
  ship.
- **arXiv 2609.37510, MAESTRO** — teacher intervention in on-policy
  distillation injects off-policy load; always-on intervention is the
  worst point of the axis. Mechanistic account of our measured GKD
  negative (6.0036); corroborates closing the on-policy lever without
  a re-run.
- **arXiv 2608.27729, "Below the Noise Floor"** — per-seed σ
  2.8–48.7pp in small-model KD; single-seed gains below ~5pp are
  unresolvable; 3/7 KD variants collapse bimodally. Validates our
  full-set + paired-bootstrap discipline and motivates the
  seed-variance caveat recorded in the next entry.
- **arXiv 2609.10153, YallaMorph (EMNLP 2026)** — 663,804 controlled
  Arabic morphological-generation instances (CamelMorph MSA). The
  concrete teacher-side data lever for the next teacher rung
  (TODO.sota-2026/01); also confirms the field's morphology work
  targets LLM evaluation rather than text-diacritization SOTA.

## Student-side lever family closed; seed-variance caveat recorded (2026-10-01)

The residual ledger, complete: corpus scale ✗, register mix ✗ (both
directions), on-policy GKD ✗ (6.0036), PKM memory (real, −0.70pp),
epochs (−0.25pp), headwise Muon ✗ (separated-negative), Sinkhorn
embeddings ✗ (flat), engram lexical memory ✗ (flat). The 2026-09-30
literature sweep surfaced no student-side method that escapes the
closure — the current on-policy wave (MAESTRO 2609.37510, RIDE
2609.36484, Fisher-sparsity 2609.36262, sparse supervision 2609.04565)
targets reasoning-trajectory distribution shift that a deterministic
dense-label task does not have.

Standing rule: **no further GPU spend on student-side levers without a
pre-registered mechanism novel to this ledger.** Frontier experiments
continue teacher-side (TODO.sota-2026/01) and via the kill-gated RIDE
direction probe (TODO.sota-2026/05) — the only student-side item with
a cheap probe before any training compute.

Caveat (per 2608.27729): every arm verdict above is a single training
seed; the paired between-students bootstrap resamples predictions, not
seeds. The headwise-Muon separated-negative (+0.2267pp, p=0.017) is
directionally consistent for its size class, but the seed axis is
unmeasured. Future arms run multi-seed or carry this caveat. Ship
decisions are unaffected — the base recipe shipped on its own merits.

## RIDE displacement arm — SEPARATED-NEGATIVE; student-side ledger closed on evidence (2026-10-02)

The one student-side lever that passed a mechanistic probe still
failed at the outcome. Probe (2026-10-01): the r7−r6 SFT residual
direction is domain-general in encoder layers 0–8 (cos 0.94/0.95/0.92
… decaying to noise L11+; max 0.9513 vs the 0.5 kill bar). Arm
(run-016-ride): the 2.1 recipe verbatim + encoder-hidden regression
toward ridge-projected displaced targets
h_t + λ(h_t − h_b) (λ=1.0, layers 0–8, frozen r7 teacher + r6 base
both resident, β auto-calibrated to 10% of CE at start — 3.576e-05).
Training converged normally (CE 0.57→0.29, 13,026 steps); teacher
reproduced at 2.2921.

| measure | value |
|---|---|
| run-016 DER-CE (full 1,200) | **5.8627** |
| paired Δ vs 2.1 (4.5701) | **+1.3926pp [1.156, 1.646], p=0.0** |
| Δ vs teacher | 3.5038 [3.222, 3.792] |

Reading: a domain-general direction is necessary but not sufficient —
regressing a 300M byte student's encoder toward ridge-projected 580M
targets displaces representations the decoder relies on, competing
with the CE objective instead of sharpening it. Ledger row #9; the
residual is now closed **on evidence, not exhaustion**: corpus scale,
register mix, on-policy GKD, PKM memory, epochs, headwise Muon,
Sinkhorn embeddings, engram memory, and representation displacement
(the only arm with a measured mechanistic premise) have all been run
to verdict. The frontier mover remains teacher-side data only —
run-009-yallamorph (TODO.sota-2026/01) is the active lever.

## run-009-yallamorph teacher — NEGATIVE on both surfaces; r7 stays canonical (2026-10-02)

The 2026-09-30 sweep's identified teacher-side lever (YallaMorph/
CamelMorph morphological paradigm aux, 25% dose, r7-init) measured
**worse on both surfaces**: SadeedDiac-25 windowed zero-skip DER
2.4895 (r7: 2.2864 — gate bar 2.389 failed) and WikiNews-2024
multi-ref 17.4265/12.1093 WER/DER (r7: 17.3794/11.8273) — no ID
improvement and no OOD trade. **r7 remains canonical**; run-009 is
recorded as the lineage's first negative teacher-side result.

Mechanism, data-backed: the paradigm corpus's vocalization convention
is 1.5–2.0× denser than benchmark text (fatha 43.0 vs 28.4, damma
11.9 vs 7.1, shadda 8.6 vs 4.3 marks per 100 letters; tanwīn nearly
absent) and its forms are isolated words rather than running text.
At 25% dose the aux stream injected convention drift — the teacher
over-marks the plain stream — instead of morphology. The knowledge-
injection template survives with a sharper edge: r6's aux worked as
running text in benchmark convention; delivery vehicle matters as
much as the knowledge. Paradigm-table aux is closed (no dose tuning,
no convention-normalization retry recorded as future work; a lexical
lever, if ever revisited, must be rendered into benchmark-convention
running text). The frontier mover on record remains the r7 news mix.

## run-018 plane v2 — the 4.5701 rung CLEARED: new on-device frontier on all axes (2026-10-04)

The plane-factorized encoder (Stoicheia WO, TODO.sota-2026/04) at its
second configuration clears the student rung decisively:

| model | full-set DER | int8 size | CPU ms/window |
|---|---|---|---|
| ara-diac-small-2.1 (shipped) | 4.5701 | 491 MB | 3,459 |
| **plane v2 (run-018, K=2)** | **3.5905** | **219 MB** | **1,145** |
| r7 teacher | 2.2864 | — | — |

−0.98pp DER (−21% relative), −45% size, −67% latency — all three
on-device axes at once. v1→v2 came from the grid's evidence: uncapped
corpus (551,431 units), 2 epochs, K=2 (K flat across 2/4/8; the
parallel-refinement depth is not where quality lives — bidirectional
conditioning is). Architecture: ByT5-small encoder + diacritic-plane
embedding + per-position haraqat classification; Mask-Predict
self-conditioning; one ONNX graph, host-side K-pass loop, no KV
cache. Morph DER 2.2149. Teacher-tier phase (ByT5-large encoder,
run-019) attacks the 2.2864 SOTA-dedicated gate next.

## run-019 plane-large — 3.0078: beats Gemini-Flash, SOTA gate open at 1 epoch (2026-10-04)

ByT5-LARGE plane encoder (~1.3B), 551k units, 1 epoch, K=2: full-set
Total DER **3.0078** / Morph 1.8486. The teacher gate (r7 2.2864) not
cleared (+0.72pp), but the model passes Gemini-Flash-2.0 (3.1926) —
the dedicated podium is now r7 2.2864, plane-large 3.0078, plane v2
3.5905. The 1-epoch budget is half of run-018's recipe (the epoch
effect measured −1.17pp at the small tier); the teacher's three-
generation curriculum lineage (r5→r6→r7) also remains un-matched by
any single run. Two arms follow: epoch-2 extension and r7-label
distillation into the plane architecture.

## run-020 plane-distill — label-limited distillation loses to raw-text scale (2026-10-05)

Arm B of the plane-large verdict follow-up: ByT5-small plane encoder
trained on r7 teacher labels (29,322 unique pairs ×6, 3 epochs) scores
full-set **Total DER 4.4462 / Morph 2.8620**. Two clean readings:
(a) on MATCHED teacher-label supervision the plane architecture beats
the seq2seq student (4.4462 vs 4.5701 — architecture advantage
confirmed independent of supervision); (b) label-limited distillation
loses to raw-text diversity at scale (run-018's 551k unique units →
3.5905) — for the plane family the lever is unique-data volume, not
supervision source. A full-corpus teacher labeling pass (~15-20h GPU)
is the conditional distill follow-up, only if the epoch-2 arm falls
short of the 2.2864 gate.

## run-019 epoch-2 — 2.7397: second epoch closes a third of the gap, SOTA gate still open (2026-10-05)

The epoch-2 extension of plane-large scores full-set **Total DER
2.7397 / Morph 1.6717 / Total WER 8.6083** — down from 3.0078/1.8486
at 1 epoch (−0.27pp, −9%). The dedicated podium becomes r7 2.2864,
plane-large-e2 2.7397, plane-large 3.0078: still ahead of Gemini-Flash
(3.1926), still behind the teacher (+0.45pp). A third epoch is not
scheduled — the per-epoch gain (−1.17pp small tier, −0.27pp here) is
shrinking faster than the 0.45pp gap.

Process note: the first epoch-2 eval was invalid — it resumed from the
epoch-1 eval progress file, found every window already "saved", and
re-scored epoch-1 predictions (bit-identical 3.0078). Fixed by a
per-marker progress file (EVAL_DONE_E2B) and re-run in full; the
number above is the corrected measurement. The 2026-10-04 epoch-1
verdict was a fresh eval and is unaffected.

## run-021 heb-plane — 12.48% nakdimon DER: the plane family generalizes, seq2seq student beaten at 3.96pp (2026-10-07)

First Hebrew plane model (TODO.final 12): the Arabic run-018 recipe
applied unchanged — ByT5-small encoder + plane embedding + per-position
head, K=2 mask-predict, 2 epochs — over the v4 combined corpus (50,303
units, 135 order-preserving nikud classes). Nakdimon test, greedy,
seq2seq_der (the exact heb-diac-1.1 protocol): **DER 12.48%** vs the
shipped seq2seq student's 16.44 — the dedicated on-device economics
(219 MB-class int8, parallel K-pass) now beat the larger seq2seq at
Hebrew too.

Process note: the first reported verdict was 32.64% — a harness bug,
not a model bug. Window stitching joined with single spaces, collapsing
the corpus's double spaces and shifting every unit after the first
anomaly; per-example analysis (balanced missing/extra, divergent text
in worst rows) isolated it, and re-derivation from cached window
predictions with exact separator re-attachment gives 12.48% with zero
reconstruction mismatches. Same lesson as run-019's E2: every verdict
number earns a mechanism check before it enters the ledger. nikud
cluster order is preserved as written (the corpus has no uniform canon:
בְּ is sheva-then-dagesh; שָׁ is dot-then-qamats).

## WO01 WikiNews-2024 multiref reconciliation — harness verified against EvalDiac.java; the QCRI gap is register, not vocabulary (2026-10-07)

Fidelity (WO01, TODO.sota): our multiref scorer is a line-by-line port of
QCRI's `Evaluation/EvalDiac.java`
(Abubakr17/advancing-arabic-diacritization). Normalization tables
(removeDefaultDiac), cluster codes, empty-ref acceptance, shadda-only
acceptance, and ANY-alternate word matching all match. Two deltas found
and closed/recorded: (1) the cross-letter FATHATAN swap was missing from
the port — added in interscript-train#107; (2) we keep our own
letter-accounting for failed multi-ref words (once, max-scoring
alternate) instead of Java's once-per-attempted-alternate — WER is
identical either way, DER differs only in the third decimal for
multi-ref-heavy sets. Input provenance: our bench copy is byte-identical
to the official release
(`sha256 f750fa11ad7c8b775dff7a5054e24b36bf6587881ffa02c2919cf7321be87587`).

| model (protocol: WikiNews-2024 multiref, greedy, zero-skip) | WER | DER |
|---|---|---|
| r7 / ara-diac-2.0 (dedicated teacher) | **17.38** | 11.83 |
| ara-diac-plane-1.0 (int8, on-device) — NEW measurement | 18.69 | **11.35** |
| QCRI BiLSTM (EMNLP 2025, self-reported, in-domain training) | 2.70 | — |

Reconciliation verdict: the 2.70-vs-17.38 gap is NOT vocabulary
coverage — WikiNews-2024 token OOV against our training vocabulary
(tashkeela-full + arwiki, 982,798 types) is only **1.61%**. The model
has seen these word forms; it fails to select the news-register READING
(contextual sense, named-entity conventions, gold-set diacritization
style). This refines the paper's "classical hadith vs news text" domain
framing: the gap is register/reading-selection, deeper than OOV, and
closes only with in-register gold supervision — which is why the
teacher-labeled news mix in r7 moved in-domain DER but not this number.
Never quote QCRI's 2.70 against our numbers without this paragraph.

## WO03 Thai hybrid tier — dictionary fast-path beats the neural model on BOTH axes (2026-10-07)

FastThaiG2P (arXiv 2608.12814) response built as specced in TODO.sota/03:
Kaikki Thai headword IPA (17,434 munch keys, >=2-char) as a maximal-munch
fast path, neural model as whole-span OOV fallback
(interscript-py thai_hybrid; bench at benchmarks/thai_hybrid_bench.py).

| mode (kaikki test, 1,219 sent, greedy, int8, CPU) | corpus PER | ms/utt |
|---|---|---|
| dict-only | 0.2217 | 0.66 |
| **hybrid (dict + neural OOV)** | **0.1478** | **0.73** |
| model-only (tha-g2p-small-1.0 int8) | 2.9166 | 82.11 |

Gate: hybrid within 1.2x dict latency (1.10x) and within +0.3pp PER of
model-only — CLEARED with margin (hybrid BEATS model-only by 2.77pp).

Honest caveats: (1) the benchmark is kaikki-derived, so dictionary
coverage/quality are inflated versus wild text — wild OOV runs go to the
neural model and hybrid converges toward model-only; (2) FastThaiG2P's
0.15 ms/utt is ~5x faster than our pure-python munch (optimizable, and
not the bottleneck: TTS decode dwarfs G2P); (3) their PER (26.9) is on
their own synthetic set — never quote across sets. The lexicon artifact
(tha-lexicon-kaikki.json) ships as a model-release asset with CC BY-SA
3.0 attribution to Wiktionary/Kaikki — it is deliberately NOT committed
to this BSD-3 repo.

## WO05 heb-g2p-benchmark adopted — our nikud plane + rules land between Dicta and Phonikud (2026-10-07)

phonikud/heb-g2p-benchmark (250 sentences, undiacritized Hebrew ->
stressed IPA; their jiwer WER/CER on raw phoneme strings). Our chain:
heb plane artifact -> nikud_to_ipa rules (WO07, glottal-ʔ convention) ->
symbol adapter (their chi/ts/e conventions). No stress is produced —
that is structural for a rule layer, so plain WER is 1.0 by construction
(every gold word carries a stress mark) and the comparable numbers are
CER and stress-stripped CER.

| system (their benchmark, their scoring) | WER | CER | CER (no stress) |
|---|---|---|---|
| ReNikud (their leaderboard, self-reported) | 0.1261 | 0.0244 | — |
| Phonikud | 0.2202 | 0.0495 | — |
| Dicta | 0.4475 | 0.1027 | — |
| **heb-diac-plane-1.0 + rules** | 1.0* | 0.2551 | **0.1575** |
| **heb-diac-plane-2.0 + rules** (pending release) | 1.0* | 0.2393 | **0.1389** |

*structural (no stress). Verdict: a zero-training deterministic rule
chain over our nikud plane is already within striking distance of
Dicta/Nakdimon-class G2P on CER; the remaining gap to Phonikud/ReNikud
is exactly stress + learned spoken-norm phonology — the audio-supervised
direction (WO09/2027). Bench: benchmarks/heb_g2p_bench.py; gold vendored
with sha256 and attribution.

## run-022 heb-plane-base — 8.18 DER at the artifact level: gate CLEARED, Hebrew -4.30pp (2026-10-07)

WO04 (TODO.sota/04): run-021 recipe scaled to byt5-base, 4 epochs, K=3,
trained on HF Jobs (a100-large, 1h03m wall). In-job nakdimon verdict
8.31 (bf16, exact run-021 protocol). Exported int8 (dynamic QInt8,
415.9 MB) and measured at the artifact level under the runtime protocol
(py PlaneModel, CPU, skeleton windows, original-separator stitching,
seq2seq_der; benchmarks/heb_plane_eval.py):

| artifact (nakdimon test, 1,864 lines / 223,872 positions) | DER | size |
|---|---|---|
| heb-diac-plane-1.0 (byt5-small, K=2) | 12.48 | 219 MB |
| **heb-diac-plane-2.0 (byt5-base, K=3, int8)** | **8.18** | 416 MB |

Harness note: the first artifact-eval run read 55 DER — the harness was
feeding diacritized text to the runtime (marks treated as base
characters); fixed by stripping via nikud_planes before windowing. The
trainer's in-job eval was always correct. Staged zip:
heb-diac-plane-2.0 (sha256 9c8f0432294e…) — release pending owner
version confirmation; heb-g2p-benchmark side-number in the WO05 entry.

## WO18 ship-time parity — heb-diac-plane-2.0; ruby-vs-py K=3 skew found and documented (2026-10-07)

First 3-leg parity run for a byt5-base/K=3 artifact exposed two things:
(1) a macOS-generated golden diverged 2.86% corpus on ubuntu CI (K=3
amplifies int8 cross-platform flips past the smoke tier) — the reference
is now generated on linux via an HF cpu job (sha b296cd9d); (2)
**ruby-vs-py skews 9.25% corpus on this artifact on the SAME platform**
(int8 dynamic-kernel divergence between the gem's ORT build and py ort
1.20.1 — K=3 conditioning cascades single kernel flips). py-vs-golden is
byte-exact; ts leg matches py within tolerance. The ruby corpus tier got
an explicit per-dispatch override (`corpus_bound` workflow input →
`SECRYST_E2E_CORPUS_BOUND`); defaults unchanged; follow-up = align the
gem ORT build (interscript-ruby#803 documents the knob). Shipped DER
numbers (8.18) are py-runtime measurements and unaffected.

## WO17/20 verdict wave — self-silver moves OOD but pays ID; byt5-large saturates (2026-10-08)

**r8a (gold 400K + r7-arwiki silver 11,330)**: dual-surface gate FAILED
on dominance — SadeedDiac-25 Total DER **2.9087** (r7: 2.2864) while
WikiNews-2024 multiref improved to **16.71/10.83** (r7: 17.38/11.83).
The register direction is CONFIRMED (news silver moves OOD even at a
2.7% mixture dose), but the trade is not free: silver pulled the model
off the gold distribution. r8b (QCRI silver, 33% dose) and r8c (both)
are pending — the dose/lr response curve decides whether a gentle
variant (r8d) can hold ID while keeping the OOD gain.

**run-026 (byt5-large, 3ep, K=4): NEGATIVE** — in-job nakdimon DER
**8.48** vs base's 8.31 (same protocol). 1.2B params on 50K units
saturates; base stays shipped at 8.18. Capacity is not the Hebrew
constraint at this data scale — data is.

## WO17 verdict wave 2 — the dose-response curve mapped; r8d launched at the knee (2026-10-08)

r8b (QCRI silver, 33% dose) completes the curve. All arms r7-init,
1 epoch, WINDOW=600, dual-surface gate:

| arm | silver dose | SadeedDiac-25 DER (ID) | WikiNews-2024 multiref WER/DER (OOD) |
|---|---|---|---|
| r7 baseline | 0 | **2.2864** | 17.38 / 11.83 |
| r8a (arwiki self) | 2.7% | 2.9087 | 16.71 / 10.83 |
| **r8b (QCRI)** | 33% | 4.3911 | **11.03 / 9.24** |

Readings: (1) news-register silver moves OOD monotonically and STEEPLY —
r8b takes **6.35 WER / 2.6 DER** off the OOD number, the largest
single-lever move of the campaign; (2) the ID cost is also monotone —
the frontier is Pareto, not a winner; (3) r8b doubles as a strong
NEWS-DOMAIN SPECIALIST (11.03 OOD, approaching QCRI's in-domain 2.70
where our 17.38 was measured).

**r8c (both, +arwiki blend): ID 4.2158 / OOD 11.73/9.40** — tracks
r8b (the 200K QCRI units dominate the 11K arwiki windows; both surfaces
within ~0.2 of r8b). The blend adds nothing material.

| arm | silver | ID DER | OOD WER/DER |
|---|---|---|---|
| r7 | none | 2.2864 | 17.38 / 11.83 |
| r8a | 2.7% arwiki | 2.9087 | 16.71 / 10.83 |
| r8b | 33% QCRI | 4.3911 | **11.03 / 9.24** |
| r8c | 33% QCRI + arwiki | 4.2158 | 11.73 / 9.40 |
| r8d | 1.2% arwiki, lr 2e-5 | RUNNING | RUNNING |

Actions: **r8d at the knee** (arwiki, 5K windows, lr 2e-5 — dose knobs
train#115) targeting OOD ~13-15 with ID ≤2.5. Register-specialist ship
option staged (WO24): ara-diac-news-1.0 (r8b) alongside ara-diac-2.0,
two-families doctrine.

## WO12 Thai tiny tier — NEGATIVE (caveated): the 12M student misses by an order of magnitude (2026-10-08)

run-025 (three attempts: two decode harness bugs — device mix, vocab
scope — fixed train#113/#114; third attempt trained cleanly to loss
~0.30 then scored **PER 2038%** greedy on the kaikki gate, followed by
a third device bug in the export step). Verdict: the gate (≤3.5 PER,
<10MB) FAILED as measured. Two honest readings, both recorded:
(a) the in-job greedy decode was never unit-tested and shows runaway
repetition — a decode rewrite could change the number; (b) even a
perfect decode cannot rescue a 12M-param student to 2.85%-class Thai
phonotactics from ~200K teacher pairs. Sub-10MB tier CLOSED unless the
owner wants a tested-decode rerun. The shipped Thai tier remains
tha-g2p-small (219MB, 2.92% model-only) + the hybrid (0.1478 PER
@0.73ms) — the client story is already won at the dictionary tier.

## WO17 verdict wave 3 — the knee FAILED: generalist blending is dead, specialists confirmed (2026-10-08)

r8d (arwiki 1.2% dose, lr 2e-5 — the gentle-knee hypothesis): ID
**3.1913** (still regressed vs 2.2864) AND OOD **17.35/11.23** (vs
17.38/11.83 — nothing moved). With the full five-point curve:

| dose | ID DER | OOD WER/DER |
|---|---|---|
| 0 (r7) | 2.2864 | 17.38 / 11.83 |
| 1.2% (r8d, lr 2e-5) | 3.1913 | 17.35 / 11.23 |
| 2.7% (r8a) | 2.9087 | 16.71 / 10.83 |
| 33% (r8b, QCRI) | 4.3911 | **11.03 / 9.24** |
| 33%+blend (r8c) | 4.2158 | 11.73 / 9.40 |

The response is STEP-LIKE, not smooth: sub-3% doses cost ID without
buying OOD; only the full-dose in-register training moves OOD
materially. **Generalist register blending is closed** — the doctrine
is register SPECIALISTS: ara-diac-2.0 (ID crown) + ara-diac-news-1.0
candidate (run-029, register-pure full-scale, RUNNING) + plane
transfer (run-028, RUNNING). Hebrew noisy student (WO26) also running.

## WO27/28 — the large dedicated arm launched; cross-system oracle measured, naive voting closed (2026-10-08)

**run-031 (byt5-large dedicated, r7 lineage corpus, no silver)** — the
heb-large negative does not transfer: Arabic's 400K+ unit corpus is a
different regime. Gate: ID < 2.2864.

**WO28**: complementarity across our three families measured on word-
exact (52,906 words): r7 93.22 / r8b 93.36 / plane-large 91.81 solo;
**oracle any-of-3 = 96.78%**. The ceiling is real — but naive 2-of-3
word voting is CATASTROPHIC (DER 28.77; 74.6% under-diacritized): the
families' conventions conflict at sentence level, so mixing words from
different conventions is incoherent under DER. Harvesting the ceiling
needs a learned convention-aware router — staged as a candidate WO.
Generalist mixing is now closed in BOTH training space (WO17) and
output space (WO28); the specialist doctrine is total.

## WO21 verdict — plane transfer moves OOD −3.14 WER, ID cost confirms the doctrine family-wide (2026-10-08)

run-028 (run-018 recipe + QCRI silver 60K units ≈ 10%): SadeedDiac-25
Total DER **4.3983** (plane-large 2.7397 / plane-small 3.5905) while
WikiNews-2024 multiref improved to **15.55 / 10.46** (plane-large
baseline: 18.69 / 11.35). Dominance gate FAILED on ID — and the
specialist doctrine now holds in BOTH model families and BOTH spaces:
register silver buys OOD and costs ID, monotonically, everywhere
measured. Stageable candidate: ara-diac-plane-news-1.0 (4.40 ID still
beats the old small-tier rung 4.57; OOD −3.14) — owner decision.

## SOTA verdict wave 4 — OOD crown 10.13; capacity closed on Arabic too; audio alignment GO (2026-10-09)

**run-029 (news specialist, register-pure, 900K QCRI silver units,
2ep)**: WikiNews-2024 multiref **10.13 / 8.98** (r8b: 11.03/9.24; r7
baseline: 17.38/11.83 — a **7.25-WER move in 48h**), SadeedDiac-25
Total DER 5.5008 (specialist doctrine: ID reported as-is). Export
staged as ara-diac-news-1.0 (IMF v1, int8).

**run-031 (byt5-large dedicated, r5 corpus)**: Sadeed **2.5765** /
morph 1.5279 vs r7's 2.2864/1.5317 — PARITY, not a win. Capacity is
now closed on BOTH languages: data/curriculum is the binding
constraint everywhere measured (Hebrew large: 8.48; Arabic large:
2.58).

**WO09 stage 2: GO.** Median phoneme PER **0.395** vs the 0.45 gate
(after fixing two probe bugs: FLEURS matching needs the
extension-included filename column; scoring must compare per-PHONE
tokens, not per-word). ASR phoneme supervision aligns with our
plane+rules reference chain — the ReNikud-style campaign is
unblocked end-to-end: $0.28/audio-hour labeling + viable alignment.

**WO26 stage 2 RUNNING** (run-030: gold v4 50K + 40K hewiki
plane-2.0-labeled windows, byt5-base, 3ep; gate < 8.18).

## WO26 verdict — Hebrew noisy student NEGATIVE: 8.72 vs crown 8.18 (2026-10-09)

run-030 (gold v4 50K + 40K hewiki plane-2.0-labeled windows, byt5-base,
3ep, K=3): in-job nakdimon DER **8.72** — worse than the shipped
heb-diac-plane-2.0 (8.18). The self-labeled wiki text reinforces the
teacher's own errors rather than adding signal. Hebrew state after
three closed levers: crown **8.18** (data scale ✗ at 50K→90K, capacity
✗ byt5-large 8.48, noisy-student ✗ 8.72). The remaining Hebrew lever
is the AUDIO campaign — WO30 v0 student RUNNING now on the GO-grade
supervision.

## WO30 verdict — Hebrew learned-IPA v0 FAILED: CER 1.18; the weak link is the ASR teacher (2026-10-09)

run-032 v0 (FLEURS 4,359 audio-labeled pairs → byt5-small): training
converged on its labels (loss 0.11) but scores **CER 1.18** on the
phonikud board (gate <0.2393). Diagnosis, recorded before any scale
spend: (1) format divergence — the student faithfully reproduces the
ASR's space-separated phone style vs the board's compact stressed
strings; (2) the deeper cause — the universal phoneme CTC
(wav2vec2-espeak-cv-ft) is a weak Hebrew teacher (stage-2 PER 0.395
was alignment-viability, not label quality; its FLEURS outputs showed
non-Hebrew phonemizations). ReNikud's pipeline builds a Hebrew-capable
phoneme recognizer FIRST. The $500 ivrit.ai scale decision is therefore
NOT triggered — scaling a weak teacher wastes it. The audio path
remains open but requires: fine-tune the phoneme CTC on Hebrew audio
(FLEURS he ~10h is exactly that training set), then relabel, then
v1. Spec'd as WO31; needs owner green-light for the next compute block.

## The "same corpus must win" program — convergence CLOSED, both matched arms in flight (2026-10-09)

**Contamination audit: CLEAN** — 0/356 WikiNews-2024 test sentences
share even one 8-gram with the QCRI 5M-word corpus; their 2.70 is
honest generalization, ours is too. **run-029c (+2 epochs, seq2seq
specialist): 10.03/8.95** (from 10.13) — the seq2seq line has
CONVERGED; doubling training bought 0.10 WER. The remaining 7.3-point
gap is therefore ARCHITECTURE (tagging vs generation) + teacher quality,
and two arms now attack it directly on their exact recipe:

- **run-033** (byt5-large PLANE = our tagging family + full 900K-unit
  corpus, news-pure, 3ep, K=3, gradient checkpointing) — their class
  with a far stronger backbone.
- **run-034** (literal BiLSTM tagger, Fadel/QCRI-style: char-emb →
  3×BiLSTM-512 → per-position haraqat head, from scratch, same corpus)
  — their architecture, rebuilt and run at our data scale.

Fixes en route (train#128-#131): haraqat split_planes mark-only crash
(QCRI silver has pure-combining-mark windows — latent library bug, now
tested); byt5-large OOM → PLANE_CHECKPOINT gradient checkpointing;
LSTM OOM → BIL_BS; padded-label loss smearing → ignore_index=-100.

## WO32 verdict 1 — the literal BiLSTM: architecture-class hypothesis REFUTED (2026-10-10)

run-034 (char-embedding → 3×BiLSTM-512 → per-position haraqat head,
from scratch, news-pure 900K silver; fp32 after the bf16 NaN collapse):
WikiNews-2024 multiref **14.30 / 10.10**, SadeedDiac-25 **5.27**.

Reading: reproducing their architecture CLASS on their corpus does NOT
reproduce their 2.70 — our BiLSTM is 5× their number and loses to our
own seq2seq (10.03/8.95). Their edge is not "BiLSTM" but the
components we did not replicate: the WORD-identity channel (Fadel's
design: word embeddings + char-CNN — lexical memorization is the
strongest diacritization feature), labels self-consistent with their
evaluation conventions (the corpus IS their model's output), and
tuning maturity. Implication: lexical knowledge is the battleground —
and byt5 byte pretraining (run-033, RUNNING) is our version of that
channel. The char-only BiLSTM closes as an anchor, not a contender.

## WO26 rerun + WO33 launch — Hebrew noisy student re-confirmed negative; the word channel decomposed (2026-10-10)

run-030-heb-noisy (HF rerun of the noisy student: 50K gold + 40K
hewiki pseudo, K=3, 16,350 steps): **DER 8.72** vs crown 8.18 — gate
failed, WO26 negative re-confirmed on the new substrate. Hebrew text
levers remain exhausted (capacity 8.48, noisy 8.72, convergence 10.03);
the remaining path is audio (WO09/31).

WO33 — lexical-channel decomposition (local, free): pure
most-frequent-reading lookup over the same corpus scores **25.15 WER /
13.18 DER** with **18.10% OOV** (482,609-type table). So: lexical
memorization ≈ 75% of words; the rest is context disambiguation among
each word's few observed readings — exactly the word-identity channel
(WO32's battleground). run-035 (RUNNING): variant-disambiguation
tagger — word-emb 128 + char-CNN (k=2..5) → BiLSTM 2×512 → head over
{variant 0..5, OOV}, 62M params, fp32, same corpus as run-033/034.
Gates: <14.30 = word channel real; <10.13 = new news-successor
candidate; else the residue is convention alignment, closed under the
register-specialist doctrine. Complement probe (oracle-min over
run-029/035) staged post-verdict.

## WO33 verdict + WO34 launch — word-only fails on OOV; the synthesis arm is the joint design (2026-10-10)

run-035 (word-level variant disambiguator): **18.07 / 11.44** multiref,
Sadeed Total DER 18.75 — both gates failed. The failure mode is clean:
18.1% of benchmark word types are OOV to the corpus table and are
emitted bare, collapsing ID DER; the word channel in isolation cannot
compose unseen words. Combined with run-034 (char-only, 14.30/10.10),
the decomposition now says each half alone loses to the shipped
specialist (10.13/8.98) — Fadel's joint design (word identity AS A
FEATURE of a char-level tagger) is the actual recipe.

Convention-style probe (local): marked-letter density 0.8127 /
0.7625 / 0.7432 across WikiNews-2024 refs, wikinews2014 gold, and
news silver — the style-mismatch hypothesis is closed; there are no
cheap diacritic-drop points.

run-036 (RUNNING): char-emb ⊕ per-char bare-word embedding → 3×BiLSTM
→ plane head; same corpus, fp32. Gates <14.30 (word channel validated)
/ <10.13 (news-successor candidate). Variant-constrained decode and
the oracle-min complement probe staged post-verdict.

Tooling built while arms grind (2026-10-10): oracle_min.py (unit-tested
complement probe mirroring the multiref scorer); eval_r8_wikinews_preds
(exact-protocol regen of run-029 WikiNews preds); run-037 trainer
(hybrid + pretrained fastText cc.ar.300 word channel — the
lexical-density hypothesis; staged, launches on slot-free).

Launch incident (2026-10-10): run-036 v1 died at the 30-minute DEFAULT
job timeout (mid-training, no intra-run ckpt — lost). Lesson added to
the launch checklist: ALWAYS pass explicit --timeout (4h standard for
a100 arms). Relaunched as run-036-hybrid-r2 with 4h. run-037 hardened
pre-launch: ft_init cache (skips 1.2GB re-parse), periodic step-ckpt +
seeded-generator resume. Monitor coverage hole fixed: poll ps --all
(terminal states) — the ps-only monitors stayed silent on
disappearance.

WO34 tooling complete (2026-10-10): variant-constrained decoder
implemented + uploaded (scores observed variants under the hybrid's
per-position log-softmax vs free-greedy; OOV keeps free decode);
sweep knobs HYB_LR/HYB_HID wired into the hybrid trainer (grid queued
behind the three primary arms). All five follow-ups are now built or
running: run-033 (~98%), run-036-r2 (30%), run-037 staged, vcd + eval
jobs queued on slot-free.

## run-033 verdict — plane-large route closes Pareto-loser (2026-10-10)

run-033 (byt5-large plane + full 900K silver, news-pure, 3ep, K=3):
WikiNews-2024 multiref **10.78 / 9.16** (from 18.69/11.35 — large
backbone + dose moved OOD by 7.9 WER), Sadeed windowed **DER 6.80 /
WER 23.80**. Gate <10 missed by 0.78; the shipped seq2seq specialist
DOMINATES on both surfaces (10.13/8.98; ID 5.50). The plane family's
large route closes; the contested axis is the word channel class
(run-036-r2 hybrid + run-037 fastText). run-029 preds-regen launched
for the oracle probe.

## run-036 verdict — word channel VALIDATED (+0.77 WER), density hypothesis sharpens (2026-10-10)

run-036-r2 (char-emb ⊕ per-char word-emb → 3×BiLSTM → plane head,
36.2M params, 20,460 steps): WikiNews multiref **13.53 / 9.92**,
Sadeed DER 5.90. Gate 1 PASS (<14.30): the word channel is real at
char level — 0.77 WER over the char-only anchor (14.30). Gate 2
FAIL (>10.13): scratch 128-d embeddings over 156K types carry too
little lexical density. Hierarchy now: specialist 10.13 > plane-large
10.78 > hybrid 13.53 > char-only 14.30 > word-only 18.07. Data note:
silver pool = 202,680 units — the 900K cap never binds; corpus scale
is exhausted at what we hold. run-037 (fastText cc.ar.300, billion-word
lexical density) LAUNCHED — the decisive density arm.

## Oracle probe — routed blend closes NEGATIVE; run-037 is the last live arm (2026-10-10)

run-029 preds regenerated under the exact protocol: 10.032/8.9521 —
matches the converged number bit-for-bit at reporting precision.
Oracle-min over {run-029 specialist, run-036 hybrid}: **9.33 WER /
8.77 DER** — only **0.71 WER** over the specialist solo (decision
threshold was >2). Their errors overlap; the hybrid's word channel
adds nothing the specialist lacks on this benchmark. Confidence-routed
blending closes (WO28 lineage). vcd launched on run-036's ckpt
(last WO34 follow-up in flight).

## vcd verdict — constraint is an ID-only tweak, OOD untouched (2026-10-10)

run-036+vcd: Sadeed DER 5.90→5.75 (−0.16), multiref **13.5268/9.9211 —
bit-identical to free decode**. On every in-table word the free-greedy
candidate already wins the variant scoring; the hybrid's OOD residual
is not lexical-variant selection (consistent with the 0.71 oracle
gap). vcd closes as not-worth-integrating; WO34's live surface is
run-037 alone.

## run-037 verdict + WO34 CLOSES — the OOD front reaches its measured terminal state (2026-10-10)

run-037 (hybrid + fastText cc.ar.300, 93.9% coverage, 63.8M params):
multiref **13.59 / 9.89** — statistically identical to the scratch
channel (13.53/9.92), ID worse (6.50 vs 5.90). **Lexical density is
REFUTED as the bottleneck.** The tuning sweep is closed as
not-worth-compute: the hybrid class sits 3.5 WER behind the specialist
— no optimizer setting closes that.

WO34 final ledger — every lever measured, none moves OOD past the
specialist: converged training (10.03) · plane-large (10.78, dominated)
· char-only (14.30) · word-only (18.07) · joint hybrid (13.53) ·
billion-word vectors (13.59) · constrained decode (±0.00 OOD) · routed
blend (0.71 oracle ceiling). Corpus scale exhausted at 202,680 units.

TERMINAL READING: the shipped specialist (ara-diac-news-1.0, 10.13
shipped / 10.03 converged) is the crown on the comparable surface at
our data scale. The 2.70 delta lives in QCRI's FULL silver release +
their self-consistent label conventions — an external dependency
(their complete corpus is theirs to share), not a lever we hold.
Even the literal reconstruction of their architecture lands at 14.3
at our scale: the gap is data, not code.

## WO35 — THE ALTERNATE-FORMAT SCORING ARTIFACT: OOD corrects 10.03 → 4.10/1.56 (2026-10-10)

Error-typography probe of the specialist's 1,065 wrong words found 74%
were LENGTH mismatches — not reading errors. Root cause: the model,
trained on QCRI multi-reference silver, emits '/'-separated alternate
sets per token (7.44% of tokens; e.g. وِكَالَةُ/وِكَالَةُ); the multiref
scorer treated each such token as one word, breaking letter alignment
— every alternate-emitting word scored wrong even when the primary
choice was correct.

Same preds, same benchmark, first-alternate decode (deterministic,
shippable):

| protocol | WER | DER |
|---|---|---|
| prior scorer | 10.032 | 8.9521 |
| **first-alternate** | **4.0976** | **1.5606** |
| symmetric any-vs-any | 3.1839 | — |

run-036 hybrid re-scores 13.53 → 8.85/2.84 — the specialist remains
dominant. The 2.70 frontier is now a 1.4-point WER gap (and our DER
1.56 likely leads on letter-level). WO32-34 verdict waves were scored
on the broken surface; rankings hold (dominance unchanged) but every
absolute number above shifts under the corrected protocol.

Runtime contract FIXED in all three runtimes (TDD, parity):
interscript-py#35, interscript-ts#108, interscript-ruby#805 —
`first_alternates` strips to the primary choice in seq2seq translate;
plane family unaffected. Follow-ups: Sadeed rescore under first-alt
(12.6% of ID rows emit alternates; DER 5.50 is inflated), models.yaml
metric correction + card text, and the re-opened 1.4-point program
(sweep/stack arms now worth compute again).

## WO31 GREEN-LIT — the Hebrew audio program launches (2026-10-10)

Owner green-light received. run-038-heb-asr-ft RUNNING (stage 1):
espeak-ng transcript targets (do_phonemize disabled — targets arrive
pre-phonemized; the tokenizer's en-us default would have silently
mislabeled every utterance), per-phone dev PER gate < 0.395,
step-checkpoints, 4h timeout. run-039-heb-ipa-v1 STAGED: audio-derived
relabel with the tuned teacher + v0 student recipe (byte-correct
collate), gate CER < 0.2393 vs the rules layer on the phonikud
benchmark. This is the only open path to the HE g2p frontier
(ReNikud 0.0244).

Sadeed rescore under first-alt (WO35 follow-up 1, closed): Total DER
5.5008 → **5.4814**, Morphological DER 4.4458 — the ID surface was NOT
materially inflated (the evaluator letter-aligns tolerantly; alternate
words skipped rather than poisoning alignment). The artifact lived
almost entirely on the multiref surface: OOD −5.9 WER vs ID −0.02 DER.

WO31 stage-1 debugging ledger (2026-10-10): r1 missing protobuf
(vocab parse), r2 missing phonemizer (backend init runs even for
pre-phonemized input), r3 aborted by the unk-rate guard — root cause
was MY espeak --ipa segmentation assumption: espeak emits contiguous
phone strings per word; my space-split produced one giant token per
word → unk 0.9996. Fix: phonemize through the tokenizer itself
(init_backend("he")), whose separator conventions ARE the vocab's —
verified locally first (unk 0.0000 on a Hebrew sentence). r4 running.
The guard did its job: no garbage-trained checkpoint shipped.

## WO31 stage-1 verdict — GATE PASS: tuned ASR hears Hebrew at PER 0.2306 (2026-10-10)

run-038-r4 (30 epochs, 12,150 steps, 47m on a100): dev **PER 0.2306**
vs the universal model's 0.395 — a 42% teacher improvement. The
teacher bottleneck from WO30 v0 (CER 1.18) is broken. Stage 2 LAUNCHED
(run-039): relabel FLEURS with the tuned teacher (audio-derived
labels) → byt5-small v1 student → gate CER < 0.2393 on the phonikud
heb-g2p benchmark (rules layer). ReNikud 0.0244 is the frontier
beyond; ivrit.ai scale stays parked until this gate reads out.

## WO31 stage-2 verdict — CER 0.9142, gate FAILED; root cause is a CONVENTION, not the teacher (2026-10-10)

run-039 (tuned-teacher labels, v0 student recipe): CER **0.9142**
(v0: 1.18; gate < 0.2393). The samples decode the failure: the student
learned the teacher's inventory — espeak-he over UNPOINTED text emits
consonant skeletons (`h u t s f h`), while the benchmark gold is
espeak over POINTED (nikud) text — vowel-full with stress
(`hˈuʔ tsˈafah bəsˈeret`). Verified locally in one command:
unpointed → `hˈu tsfh vsrt`; pointed → `hˈuʔ tsˈafah bəsˈeret`.

The gold's generator was nikud-then-espeak. Our fix uses our own
crown asset (heb-diac-plane-2.0, DER 8.18; sha-verified release
artifact) to point the FLEURS transcripts before espeak — no LLM
teachers, no external dependency. run-041 (stage 1b): re-fine-tune
with pointed-espeak targets → stage 2 relabel + student re-run.
Prediction if the convention reading is right: stage-1 PER will move
only modestly (targets get denser), stage-2 CER collapses toward the
gate.

run-041 LAUNCHED (stage 1b): all 4,335 FLEURS transcripts pointed by
our own crown nikud model (100% coverage, spot-checked correct),
espeak now sees pointed text → vowel-full + stress targets matching
the benchmark's convention. Stage-2 rerun (run-042) fires on gate
pass, reusing the proven relabel+student script against the new
teacher.

run-041 stage-1b GATE PASS: dev PER 0.319 (< 0.395) on the vowel-full
inventory (denser target space + nikud noise account for the rise
from the consonantal 0.2306 — different inventories, not comparable).
The teacher now hears vowels in the benchmark's convention.
run-042 LAUNCHED (stage 2 rerun): relabel with the pointed teacher →
v2 student → gate CER < 0.2393. This is the decisive read on the
convention hypothesis.

run-042 verdict: raw CER 1.3021 — GATE-METRIC ARTIFACT, third of the
campaign. The v2 student predicts vowels in the right convention
(`tsafeh beseret` ≈ `tsafˈa besˈeʁet`) but its labels are
space-per-phone while gt.tsv gold is space-per-word; the string CER
counts every inter-phone space as an error (v0/v1 carried the same
mismatch — their CERs were also inflated). run-043 RUNNING: the fair
gate — space-and-stress-stripped char CER on both sides, the same
contiguous convention the rules layer's 0.2393 was measured under —
on the saved v2 checkpoint, with truncation flagging.

run-043 normalized gate: **CER 0.5463** — honest miss (rules 0.2393),
but the error anatomy is clean: repetition loops (byt5-small on 3.2K
noisy utterances) + vowel drift, labels carrying the teacher's 0.319
PER. WO31 iteration 3 LAUNCHED (run-044): pseudo-label quality gate
(audio-decode must agree with espeak(pointed text) within 0.35 nCER —
the WO06 filtering pattern; caught+fixed a phonemize-mode bug in the
reference path pre-launch) + no-repeat generation + normalized CER in
the in-job verdict. Prediction: filtering trades data volume for
label precision; the loop failures should collapse.

run-044 (v3) verdict: normalized CER **0.8851 — filtering NEGATIVE**
(v2 unfiltered: 0.5463). The agreement gate selected an easy-utterance
subset (3,452 pairs, 2,685 train) whose distribution shift cost more
than the noise removal bought — selection bias beats cleaning at this
data scale. run-045 LAUNCHED: v2's unfiltered pointed recipe at
**byt5-base** (repetition loops are the small-model symptom;
base-vs-small unmeasured in this regime). This is the last free lever
before the ivrit.ai scale decision ($500, owner-gated): if base also
misses < 0.2393, the 10-hour FLEURS ceiling is the binding constraint
and the rules layer (0.2393) stays shipped.

run-045 (byt5-base + no_repeat): normalized CER 0.8817 — CONFOUNDED
READOUT, my error: the no_repeat_ngram_size=3 added in v3 blocks
legitimate phone-sequence 3-grams (IPA recurringly repeats syllable
n-grams) → early-EOS truncation visible in the samples. v3's
"filter-negative" verdict is likewise confounded (two variables at
once). Clean A/B LAUNCHED (run-046): byt5-base, unfiltered labels, NO
repetition suppression — vs v2-small's 0.5463 this isolates capacity
alone. Lesson logged: one variable per arm, always.

## WO31 stage-2 ledger CLOSES at 0.5463 — rules layer stands; ivrit.ai is the open decision (2026-10-11)

run-046 (byt5-base, unfiltered, plain decode — the clean capacity
A/B): normalized CER **0.6318** vs small's 0.5463 — capacity NEGATIVE
at 3.2K utterances. Final ledger: v2-small 0.5463 (best) · base
0.6318 · filtered 0.885 (confounded) · rules layer 0.2393 (shipped,
stands). Every free lever measured: teacher conventions (fixed via
pointed-espeak), metric conventions (normalized CER), capacity
(negative), label filtering (unpromising under noise). The binding
constraints are structural: 10h FLEURS audio + 0.319-PER teacher.

DECISION FOR OWNER: the path to ReNikud-class (0.0244) Hebrew g2p is
the ivrit.ai audio scale ($500 → 100+ hours labeled through the
now-proven pipeline: pointed-espeak targets, tuned CTC teacher,
normalized-CER gate). All pipeline risk is retired; the remaining
risk is budget. Without it, the rules layer ships as our g2p answer.

## WO35 arm 1 verdict — stripped-corpus specialist GATE PASS: 4.0034/1.5457 (2026-10-11)

run-040 (byt5-base, run-029's exact recipe on first-alt-stripped
corpus, 290,575 units, 36,320 steps, 11h across two resume legs):
WikiNews first-alt **4.0034 WER / 1.5457 DER** — new best (shipped:
4.0976/1.5606); raw protocol improves too (9.98 vs 10.03); Sadeed ID
at parity (5.4840). Alternate emission shrank as designed. Export of
the stripped model as the ara-diac-news successor is STAGED for the
owner's version decision (bytes differ; new sha; 1.1 vs 2.0 naming).

run-047 LAUNCHED (WO35 arm 2): byt5-LARGE seq2seq from pretrained
scratch (no large adapted teacher exists) on the same stripped corpus
— the untried capacity point in the dominant family. 36h timeout.
Note: size+init both change vs run-040 (no pure A/B possible);
the readout answers the practical question: does large beat the base
specialist at this corpus.

WO36 audit verdict (2026-10-11): audio-v2 = 35,629 audio files,
1.21TB (README floor >20K hours; header probes 404'd on the smallest
files — hour count deferred to the teacher stage). The decisive find:
**crowd-transcribe-v5 (~165K rows) and audio-labeled (~87K rows) are
SELF-CONTAINED pairs** (audio bytes + verified transcript embedded)
— no VAD, no cutting, no pairing engineering. ~250K ready pairs ≈
10-20× FLEURS. Stage 2 RUNNING (run-049): text extraction + crown
nikud pointing over all pairs, 8-way multiprocessed in-job per the
no-local rule; audio stays in the parquets until the teacher stage.

Oracle re-probe under the corrected protocol (shipped r029 vs stripped
r040, both first-alt): **3.7302 WER / 1.4715 DER ceiling** — only
0.27 over the stripped best (threshold 2.0): same-family overlap,
routing not worth building. A 3-way re-probe (adding run-047 large)
opens when its verdict lands. Successor export STAGED as
ara-diac-news-1.1 (provisional id; owner renames at ship):
int8 IMF v1 zip with the corrected metrics in the manifest.

Successor artifact STAGED (2026-10-11): ara-diac-news-1.1.zip —
399,193,366 bytes, sha256 7441914844a4782519326da0bfca6a25ef1925b489
9ee086d5dea2e506c0faa0 (run-040-strip-alt/export/ in the bucket),
int8 IMF v1, ORT sanity green, corrected metrics in the manifest
(4.0034/1.5457). SHIP GATE: owner names the version (1.1 vs 2.0) and
cuts the GitHub Release + models.yaml entry + index bump + 3 runtime
pins (the established chain).

WO36 stage-2 debugging ledger: r2 died on missing model deps; r3
stalled 4h with ZERO shards — systematic-debugging probe (standalone
shard read: 1.4s total) isolated the classic fork+requests deadlock:
the module-level HfFileSystem forked into the 8-worker pool inherits
the parent's live connection state and hangs on first use. Fix:
worker-local fs construction. r4 running; lesson = never fork a
process that owns an HTTP session created pre-fork.

## run-047 verdict — GATE PASS: byt5-large stripped 3.5983/1.4715, NEW BEST; gap to frontier 0.90 (2026-10-12)

run-047 (byt5-large from pretrained scratch, stripped corpus, 4
epochs, 23h39m): WikiNews first-alt **3.5983 WER / 1.4715 DER** —
beats base-strip (4.0034/1.5457) and shipped (4.0976/1.5606); raw
protocol improves too (9.68 vs 10.03); Sadeed ID 7.39 (register cost
of the news specialist, consistent with the family). **Capacity
DOES pay in the dominant family once the corpus is stripped** — the
old large≈base finding was measured on the unstripped recipe.
Ladder: large-strip 3.60 > base-strip 4.00 > shipped 4.10; gap to
QCRI 2.70 = **0.90 WER**.

3-way N-way oracle {shipped, base-strip, large-strip}: **2.9484 WER
/ 1.2743 DER** — arms are complementary (0.65 over best single) and
the ceiling sits 0.25 from the frontier. Routing stays closed
(<2 threshold); the portfolio-ceiling claim is recorded.

run-054: export STAGED as ara-diac-news-1.2 (provisional id; int8
IMF v1; owner names at ship). Ship candidates now: 1.1 (base-strip)
and 1.2 (large-strip) — the latter dominates on both OOD protocols.

run-054 artifact verified: ara-diac-news-1.2.zip — 821,291,775 bytes,
sha256 93e318714f3f792db8d29764990cdba2df8315addf0185ce9b32770353de27
77, ORT sanity green. NOTE: 2× the 1.1 artifact (large backbone) —
server-tier deployment; the 100MB-capped edge tier remains on
ara-diac-small. Both staged artifacts await the owner's naming +
release chain (GitHub Release + models.yaml + index + 3 pins).

## WO37 verdict — portfolio reference numbers PUBLISHED (2026-10-12)

run-056 (run-056-portfolio-eval): our shipped artifacts on their own
held-out test splits, protocol now published (char CER + word accuracy,
n=3000 slices, artifacts sha-verified from the release chain):

| artifact | n | CER | word acc |
|---|---|---|---|
| fas-g2p-1.0 (HomoRich test) | 3000 | **0.0147** | 0.6307 |
| urd-diac-1.0 (held-out split) | 3000 | **0.0386** | 0.6750 |
| urd-g2p-1.0 (humair025 test) | 3000 | **0.1578** | 0.3313 |

Reading: fas-g2p at 1.47% CER is crown-grade (rules-layer league);
urd-diac 3.86% is strong; urd-g2p 15.78% is measured against the
harsh convention (IPA with stress + syllable dots, char-level) —
33% exact-word is the honest weak spot and the only candidate for a
future training arm. No external frontier exists for any of the
three (WO37 survey) — these published numbers + protocol ARE the
reference (define-and-lead). Full-split runs (n≈12K) can refine the
slices on demand.

fas anchor CONFIRMED (run-058-r3, n=1000): g2p-fa scores **0.3629
consonant-skeleton CER** (0.7025 raw char CER — notation mismatched:
narrow IPA vs the HomoRich broad scheme) vs our fas-g2p-1.0's
**0.0147 total CER** on the identical split, word-by-word per its
published design. The measured lead is ~25× notation-robust. The fas
row of the portfolio closes: reference protocol published, artifact
verified, only competitor measured and beaten.

WO38 launched (run-059): urd-g2p byt5-base arm on the full 610K
humair025 pairs, gate CER < 0.1578 (1.0's WO37 number) on the full
12.7K test split; export as urd-g2p-2.0 if passed (owner names).
Launch-dep notes for the WO36 chain: run-050 builder needs soundfile
in pip; run-051 teacher additionally needs torchaudio (native-sr
resample) + espeak-ng/phonemizer/protobuf (the tokenizer contract).

run-057 FULL-SPLIT confirmation (n = full test splits): fas-g2p-1.0
**0.0148** (10,576) · urd-diac-1.0 **0.0377** (11,940) · urd-g2p-1.0
**0.1592** (12,699) — all within 0.001 of the n=3000 slices. The
published portfolio protocols now stand on full splits: fas 1.48% CER
(crown-grade, anchor beaten 25×), urd-diac 3.77% (reference), urd-g2p
15.92% (the WO38 byt5-base arm's target: < 0.1578 slice / ≈0.159 full).

WO36 stage-2 COMPLETE (2026-10-12): **326,190 pointed pairs** (of
326,303 rows, 99.97% kept) in 11.07h across the pointing saga (r3
fork-deadlock, r5 spawn-hang, r7 context-manager bug — each
root-caused in the ledger; the thread design + resume markers
delivered). run-050 LAUNCHED: webdataset builder over the pair repos
(200h slice cap, WAV shards to the bucket, real hour count at
completion) — the teacher's runway.

run-050 COMPLETE (40.6 min): **200.61 audio-hours, 126 WAV tar
shards** in the bucket (1s-30s filter, pointed text paired by uuid,
deterministic order — extendable by rerun with a higher cap).
Teacher (run-051) staged and fires when an a100 slot frees (run-055
and run-059 both finish within ~2h; the ≤2-GPU law holds).

WO38 verdict — MARGINAL PASS (2026-10-12): urd-g2p byt5-base (610K
pairs, 5h23m): full-split CER **0.1565** vs 1.0's 0.1592 (word acc
0.3273 → 0.3467). Gate passes but the delta is thin — both models
cap near ~16% CER because the dictionary's IPA convention itself
carries ambiguity (stress/syllabification variants per word). The
meaningful next lever is the spec's fallback: data-quality arm
(dedupe/normalize targets) before any bigger swing. Export staging =
owner's call given the thin margin; recommendation: hold for the
data-quality arm.

urd-g2p error anatomy (run-059-anatomy, full test): normalized CER
**0.1075** (stress/dots carried only ~5pp of the raw 0.1565); the
remaining errors are genuine phonology — vowels/diacritics 41.7%
(short-vowel reduction ə/ɪ/a choices), consonants 34.2% (retroflex/
aspirate inventory), insertions 24.2% (epenthetic vowels, e.g.
fiːlæm for film). No notation escape hatch exists; the axis's
reference stands at ours (0.1565 raw / 0.1075 normalized), and a
future arm would need real phoneme-model improvements (data scale
beyond the 610K dictionary, or multilingual transfer) — queued as
the portfolio's optional arm, not an active chase.

run-051 teacher verdict — GATE PASS on FLEURS (0.2069 < 0.25, vs
0.319 from 10h) but in-domain ivrit dev PER anomalous at 0.8722 —
almost certainly an evaluation-convention artifact in the dev-gold
reconstruction path (a model trained ON ivrit cannot plausibly score
87% on ivrit). Decisive test launched (run-052): the labeler+student
chain against this teacher — its phonikud CER is the ground-truth
diagnostic. If the student screams, the dev path gets the fix; if it
clears < 0.2393, the anomaly was cosmetic.

run-055 verdict (e6 leg, 12h16m): first-alt **3.5607 WER / 1.4588
DER** — new best (4-epoch: 3.5983/1.4715; the +2 epochs bought
+0.038 WER: the leg is CONVERGED, tail thin like run-029c). Raw
protocol improves too (9.66 vs 9.98 → under 10 for the first time
on the unstripped-protocol comparison). Sadeed ID 7.48 (register
cost, family-consistent). Gap to QCRI 2.70: **0.86 WER**.
3-way oracle with e6 preds: 2.9861/1.2828 (complementarity holds;
routing stays closed <2). Re-export of ara-diac-news-1.2 from the
e6 ckpt LAUNCHED (replaces the staged 4-epoch zip; same provisional
name pending owner).

run-060-r2 EXPORT VERIFIED: ara-diac-news-1.2.zip (e6 checkpoint) —
821,320,781 bytes, sha256 12cb294d73318c7717b8e24ed1b95642d1510c2af
515127eb329fb88b1950548, ORT sanity green. Root cause of the failed
r2 recorded: torch.onnx.export auto-selects external-data format when
the model crosses the 2GB protobuf boundary (the e6 large encoder
crossed it; run-054's export sat just under) — fixed by pinning
use_external_data_format=False in both export calls (committed in
train repo PR #133's export script).

WO36 CORRECTION — the pointed-convention bug, caught before the gate
(2026-10-13): label spot-check revealed run-052's labels are
CONSONANT SKELETONS — run-051's teacher trained on r["text"]
(UNPOINTED transcripts → espeak-he → consonant skeletons) instead of
the crown-nikud pointed transcripts sitting in the same tars; the
labeling decode additionally ran on 2×-time-warped 32k audio (run
before the resample fix). run-052 killed at 15% student training —
training toward those labels was waste. FIXES: teacher v3 (run-061,
RUNNING) trains on the pointed field (vowel-full targets, primary
gate = ivrit dev same-convention; FLEURS reported as
convention-shifted); the labeler carries the resample fix; the
student gate (phonikud, vowel-full gold) is then CONSISTENT
end-to-end for the first time. The WO31 lesson generalizes: the
pointed-vs-unpointed convention must be asserted at EVERY stage —
targets, gates, and labels — not just the first espeak call.

Seed-variance result (run-061b, seed 1337 vs run-061 seed 42):
FLEURS 0.2055 vs 0.2069 · ivrit dev 0.8745 vs 0.8722 — seeds agree to
±0.002, so BOTH numbers are stable measurements. Conclusion: the
FLEURS gate pass is real (teacher improved 0.319 → 0.206 at 200h),
and the 0.87 ivrit-dev is seed-independent → confirmed as the EVAL
BUG hypothesized earlier: asr_phones' dict branch ignores the
recorded 32000 Hz sample rate (2×-time-warped audio → garbage decode).
The training path resamples correctly (pcm_to_16k uses r["sr"]).
run-062 LAUNCHED: labeler+student with the v3 teacher in a FRESH run
dir (run-062, not run-052 — the stale consonant-skeleton labels.jsonl
from the wrong-convention teacher cannot resume). Gate tonight:
phonikud nCER < 0.2393 on vowel-full labels — the first
end-to-end-consistent Hebrew g2p measurement.

run-062-r11 verdict — first end-to-end-consistent Hebrew g2p
measurement (2026-10-14): phonikud nCER **0.4415** (raw 0.6779) vs
gate 0.2393 (rules layer) — **GATE MISS**, but the first VALID number
of the whole audio-arm saga (everything before was convention-broken
or resample-broken). Context: beats the FLEURS-scale student's 0.546
despite spontaneous-speech labels; loss was still descending at
training end (0.30→0.17 over 4 epochs, no plateau) → the model is
UNDERTRAINED, not converged. Residual-error hypothesis: 200h-derived
labels carry podcast noise (hesitations, music, code-switching) the
teacher faithfully transcribed. NEXT LEVER (cheap first): +8 epochs
continuation from the epoch-3 checkpoint (run-062-ivrit-student-e12,
LAUNCHED — epoch-resume machinery now works). If still >0.24: label
quality filter, then WO36 stage-3 teacher scale (300-500h).

## run-059 urd-g2p-base gate pass

run-059 urd-g2p-base — GATE PASS, processed late (2026-10-14; job
completed 2026-10-12, verdict unprocessed until now): full 12,699-row
test split CER **0.1565 < 0.1578** (urd-g2p-1.0) — byt5-base on 610K
humair025 pairs beats the small-tier shipped model. word_acc 0.3467.
Anatomy (run-059-anatomy): cer_normalized **0.1075**; error mass —
vowels/diacritics 41.7% (sub 4368 / del 1366), consonants 34.2%,
insertions 24.2%. Ship per WO38: byt5-base IMF export staged (owner
names the release). Lesson (repeat offender): a COMPLETED job with an
unprocessed verdict is lost work — verdict-fetch must be part of the
launch, not an afterthought.

INFRA INCIDENT — hf upload ≠ bucket upload (2026-10-14): `hf upload
Interscript/isx-training <local> <path>` silently created a PUBLIC
MODEL repo of the same name on the org and wrote there instead of the
bucket (commit URLs printed = false success). Consequences caught:
run-059 export job died on a missing script; run-063 500h WDS build
ran the STALE bucket builder (no S_OUT) and started rewriting the
run-050 slice in place — killed at shard-0091; prefix is deterministic
but may diverge if ivrit repos grew → treat the 200h slice as
superseded by the 500h rebuild for any future labeling. All scripts
re-pushed via `hf buckets cp` and verified by listing; both jobs
relaunched green (run-063-v2 writes run-063 confirmed, export-parity-v2).
Phantom repo flagged to owner for deletion. Rule saved to memory:
bucket uploads = `hf buckets cp` + verify with `hf buckets ls` BEFORE
launching the consuming job.

run-059 EXPORT VERIFIED: urd-g2p-base-staged.zip — 399,894,914 bytes
(int8 tier), sha256 b1d9a319879d110c0d79d3377191b4a45be88c67fb8f2d40
325c706c0ce59f1a, ORT sanity green; task g2p, scripts [Arab, IPA].
Torch engine on the 300 parity rows: CER 0.1397 (full-split 0.1565 —
sample noise). First parity attempt crashed (numpy broadcast: assigning
(L+1,) np.append into an (L,) row view of the growing decoder input) —
fixed with a vectorized column append; parity-only job relaunched.

WO39-41 WAVE (2026-10-14, "SOTA everywhere" sweep of untried levers):
- WO39 stage-1 relabel LAUNCHED on l4x1 (a100 decontention): 300K QCRI
  rows × 3 arms, chunk-resume added (completed_lines truncation logic,
  9 tests green — catches partial trailing lines from killed jobs).
- WO40 teacher true-PER re-eval LAUNCHED (l4x1): run-061/best with the
  FIXED eval — decides WO36's next lever (<0.35 student-bottleneck,
  else teacher v4@500h mandatory). En route: found my morning resample
  patch had gone to the v2 script copy (run-051 dir); the v3 script
  (run-061 dir, pointed-override lineage) had a DIFFERENT eval bug
  shape — dict branch ignoring r["sr"] — now patched in bucket+local.
- WO41 urd-diac-base STAGED: the last untried tier lever in the
  portfolio (urd-diac-1.0 is small-tier; tha/fas/urd-g2p all have base
  tiers). run-059 recipe 1:1, gate < 0.0377, queued last on a100.
- Tier-lever audit: tha-g2p-base-1.0 and fas-g2p-base already shipped
  (models.yaml sizes 2.78GB = base fp32) — no other tiers remain.

WO40 VERDICT — teacher true-PER 0.1382 (2026-10-14): the fixed-eval
re-measurement of run-061/best gives ivrit_dev_per_true **0.1382**
(13.8%) vs the 0.8722 buggy report, and FLEURS 0.2059 (seed-consistent
with 0.2055/0.2069). Decision rule fires LOW: **the STUDENT is the
bottleneck; labels are good.** Consequences: (a) teacher v4@500h
(WO36 stage 3) DEMOTED to last-resort — only if e12 AND the
label-filter arm both fail; (b) the 200h slice is producing far better
labels than assumed — the 0.4415 student miss is a student-side
problem (undertraining being tested by e12 now; residual after
convergence would be podcast-vs-benchmark domain gap → label-filter
arm targets domain/quality outliers); (c) the 500h build keeps
running as cheap contingency (a 3.6% teacher-PER improvement might
still buy the last points). The eval-bug lesson repeats in miniature:
the SAME sr-ignoring bug had two shapes (v2: bytes+sf.read; v3: dict
branch) — one fix did not cover both.

PHANTOM REPO CLEANED (2026-10-14, owner-authorized): the accidental
public model repo Interscript/isx-training deleted (was created by
the hf-upload misuse; contained only training scripts, no secrets).
Org namespace verified: 29 legitimate mirrors, zero strays; rhtse
namespace clean. Memory rule stands: bucket writes = hf buckets cp.

RELEASE WAVE SPECS (WO42-44 written): label-filter arm (conditional,
self-consistency design), gold-nikud speech arm (micsell campus
VERIFIED available 28.6GB public), and the full release plan
(naming law derived from the 29-mirror convention; publish-state
audit: py 0.2.0 never published, npm 5.7.0 predates ts#108, gem
3.0.1 predates ruby#805; semver-minor recommendation 5.8.0/3.1.0/
0.2.0; index-v11; owner decisions D1-D5 enumerated).

CRITICAL FINDING — dynamic int8 destroys seq2seq decode quality
(2026-10-14, the release gate did its job): urd-g2p-base staged int8
zip parity FAILED (ONNX CER 0.4399 vs torch 0.1397, 5% row match).
Discrimination: the SAME decode loop on the fp32 ONNX graphs gives
CER 0.1633 vs torch 0.1397 (70% row match; the 0.024 residual is
bf16-autocast-vs-fp32 compute) — the loop is correct, the
QUANTIZATION is the killer. Consequences: (a) all seq2seq artifacts
ship FP32 (export script default EXPORT_PRECISION=fp32; 2-3 part
zips under the 2GiB part cap); (b) parity now verifies the SHIPPED
ZIP BYTES (zip mode), not loose graphs; (c) the SHIPPED
ara-diac-news-1.0 int8 zip is under suspicion — zip-check running
(run-029-zipcheck); static int8 remains the proven tier (plane
family 3-leg parity green), dynamic-int8 is a documented negative
(consistent with the DeepSeek campaign's "static-int8 the one
positive lever").

RELEASE WAVE STATUS (owner-approved D1-D5): npm interscript@5.8.0
PUBLISHED (provenance, GH release created; earlier 5.7.0 reading was
registry lag). py 0.2.0 BLOCKED on red CI — root cause: the release
workflow installed bare `-e .` while tests import
interscript.ml.loader (module-level `import yaml`); test.yml red on
main for the same reason since py#35. Fix PR interscript-py#36
(pyyaml in dev extra + release workflow mirrors test.yml maps
checkout). gem 3.1.0: bump PR interscript-ruby#806 open; PR CI fails
on PRE-EXISTING main failures (ml golden/imf fixture specs,
Isc::ParseError — present on the #805 merge run itself); also the
v3.x gem line has no working CI release path (the v3.0.0 workflow
run failed; 3.0.x were pushed manually) → gem ships via the
hand-rolled build+push path after main's specs are green.

fp32 re-export wave LAUNCHED (4 jobs, l4): urd-g2p-base-1.0 (final
id), ara-diac-news-large-1.0 (e6), ara-diac-news-1.1 (run-040) —
each export+zip-parity; plus the run-029 shipped-zip diagnostic.
GH Releases for the three models wait on green parity.

GEM CI ROOT CAUSE + FIX (2026-10-14): the red ml specs trace to ONE
map — acadsin-zho-Hani-Latn-2002.isc — which the SHIPPED parg
artifact misparses (rejects lowercase system codes at line 1 char 17;
charset = legacy uppercase+escape class) while the .parg source and
the Ruby-DSL grammar both accept it. The artifact carries no source
hash → staleness undetectable at load. Fix shipped on the release PR
(interscript-ruby#806): parser prefers the artifact, retries the DSL
grammar on ParseFailed (TDD: regression spec + end-to-end verified on
the failing map). parsanol issue DRAFTED for owner review: artifacts
should embed source-grammar hash + compiler version.

fp32 re-export relaunch: e6 + run-040 v1 jobs died on an
export-script bug (ORT sanity block referenced int8-only vars in
fp32 mode) — sanity now runs over the SHIPPED bytes; both relaunched
(run-047/040-export-fp32-v2). urd job was still queued → will mount
the fixed script.

parsanol issue FILED (owner-approved): parsanol/parsanol-ts#5 — PARG
artifacts should embed source-grammar SHA-256 + compiler version so
loaders can detect stale artifacts; includes the acadsin repro and
the compiler-mistranslation question. Our runtime fallback (#806)
defends independently; the artifact recompile via the parsanol
toolchain remains the upstream fix.

CLEAN-DATA RESOLUTION for the ISC artifact (2026-10-14, owner
directive "no legacy, fully clean"): the DSL-retry fallback was
REVERTED — the gem ships no known-bad derived bytes instead. Findings
that forced it: a FRESH `parsanol parg compile` (gem 1.3.91) of the
current isc.parg reproduces the identical misparse (expects the
test_line rule's `input` capture at the system line) → the parg
COMPILER mistranslates the grammar; the artifact path has never
parsed this corpus correctly (the long-standing red×77). The gem now
ships WITHOUT isc.artifact.json — the .parg source stays (canonical),
the runtime uses its documented artifact-missing→Ruby-DSL path, and
the artifact-dependent specs guard-skip (restored once the compiler
is fixed). parsanol#5 updated with the confirmed compiler repro.
Release train #806 now = version bump + #805 contract + clean-artifact
removal.

EXPORT WAVE FIXES: (1) export sanity now runs over the SHIPPED bytes
(fp32 mode previously referenced int8-only vars); (2) byt5-LARGE fp32
exceeds the protobuf boundary — torch emits external-data files and
the zip ships a stub encoder (the OLD staged e6 int8 zip was quantized
from that stub — doubly broken); the large tier now exports FP16
(single-file, gate numbers were bf16 anyway) via EXPORT_DTYPE=fp16;
(3) parity feeds ONNX sessions POSITIONALLY from get_inputs() — the
hardcoded encoder_hidden_states name did not match the declared graph
inputs. run-040 zip (2.16GB fp32) verified intact; its parity
relaunched.

PARITY LOOP CLOSED (2026-10-14): the "invalid input name" failures
were MY variable bug in parity_ar_imf_hf.py gen_windows — the DECODER
run was issued on the ENCODER session variable (sess), so the error
implicated the feed names spuriously; positional feeds were fine.
Fix: ds.run. Separately, byt5-large's fp16 ENCODER still split to
external data (decoder halved to 871MB fine) — export now post-processes
both graphs: onnx.load(load_external_data=True) + onnx.save inlines
them into single-file protobufs (fp16 graphs fit the 2GB cap).
Relaunched: run-040-parity-v3, run-029-zipcheck-v3, run-047-export-fp16-v2.

LARGE-TIER SHIP BLOCKED on a hard wall (2026-10-14): byt5-large's
encoder serializes >2GB at BOTH fp32 and fp16 (onnx.save EncodeError
on the re-fuse attempt) — single-file ONNX is impossible; external-
data files are outside the IMF zip contract. Old staged 1.2 int8 zip
confirmed quantized-from-stub (never shippable). Decision: the large
tier's 3.5607/1.4588 stands as a measurement; the artifact ships via
WO45 static-int8 (the proven lever) — spec written, arm staged.

e12 VERDICT — the student is CONVERGED at ~0.44 (2026-10-14): +8
epochs moved nCER 0.4415 → 0.4462 (noise). Undertraining REFUTED;
the undertrained-hypothesis lever is closed. The residual vs the
0.2393 gate is structural: podcast spontaneous-speech labels vs the
dictionary/read-style benchmark (plus whatever noise the 13.8%-PER
teacher passes through). Next per WO36/42: the label-filter arm
(decodes on l4 after the parity wave; retrain queued behind the AR
chain) with expectation set honestly — filtering narrows the gap,
the gold-nikud arm (WO43) attacks the OTHER contender path.
Fleet: a100 FREED by e12 → the l4 oracle-relabel (1-2 rows/s) was
KILLED and WO39 stage-1 relaunched on the a100 with per-arm resume
(~15h for all three arms) — the MUST-fix AR acceleration.

GEM 3.1.0 SHIPPED (2026-10-14): interscript 3.1.0 registered on
rubygems.org. The release train (interscript-ruby#806) carried:
version bump, the #805 decode contract (first_alternates), removal of
the broken isc artifact (parsanol#5), the rake.yml PR-overlay fix
(bootstrap tested remote main — PRs never exercised their own code),
repo-wide standardrb cleanup, and the windows tampered-zip platform
skip. CI: 10/10 green — the rake workflow's first fully green run in
its history (29 prior failures, 0 successes).

LARGE TIER PARKED (2026-10-14): third single-file toolchain attempt
(torch.ao quantize_dynamic → ONNX) failed on untraceable quantized
attention modules. WO45 fallback fires — 3.5607/1.4588 stands as the
measurement; the artifact awaits external-data-in-zip (runtime-arch).
The release ships ara-diac-news-1.0 + 1.1 + urd-g2p-base-1.0, all
verified.

RELEASE VERIFICATION CATCH (2026-10-14): post-publish smoke of npm
5.8.0 found imf.firstAlternates UNREACHABLE — the imf barrel never
re-exported it (ts#108's tests used source-tree imports). Fixed in
interscript-ts#109 (barrel + public-surface test), shipped as 5.8.1
(verified loading + export). Gem 3.1.0 smoke passed (loads,
first_alternates reachable). Also: fas-diac checkpoint CONFIRMED
alive on the Modal volume (sanctioned one-time export run; bucket
run-073-fas-diac/best) — WO47 proceeds to protocol verification.
UR lexicon lever DEAD (probe: oracle 0.2268 worse than model 0.1565).
he-wiki vocalized mining DUD (1,244 pairs) → Wikisource pivot spec'd.

WO42 PARKED WITH DATA (2026-10-15): the batched filter smoke (2
shards) shows 88% label retention under ±10% stretch-decode
self-consistency — the teacher's labels are largely stable; the
0.4462 student gap is podcast-vs-citation DOMAIN mismatch. Filter
cost would be ~134 GPU-h for a lever that cannot close a 2× domain
gap → parked. HE g2p path consolidates on WO48b (vocalized-supply →
nikud model → shipped rules chain). Also: the original 12h "hang"
was re-diagnosed — bs-1 decodes at ~95 min/shard with prints only
every 20 shards (a sizing bug, not a hang).

AR PARITY HARNESS ANOMALY (2026-10-15): the v5 parity jobs (bs-8
variant) scored torch WER ~73.14/73.17 — nearly IDENTICAL garbage on
TWO DIFFERENT checkpoints (run-040 and run-029) that score 4.00-4.33
under the v3 configuration. Identical garbage across different
models = harness/scoring failure in that configuration, not model
quality. Reverted to the exact v3 config (bs 16, no env) and
relaunched the shipped-1.0 diagnostic (run-029-zipcheck-v6); the 1.1
zip parity retries after v6 confirms the harness. Lesson: the AR
parity harness has a bs-sensitive failure mode — keep the known-good
configuration frozen until root-caused.

urd-diac-base PARITY v2-vs-v3 (2026-10-15): v2 accidentally fed the
G2P test split to the diac model (torch CER 1.2188 = wrong-data
garbage) — BUT the ONNX artifact tracked torch at delta 0.046 / 65%
row-exact even on garbage input: fp32 conversion fidelity confirmed
on a second model independent of data. v3 rerun on the correct
data-diacrit split pending (PARITY_DATA env added to the harness).

urd-diac-base PARITY v3 (correct split, 2026-10-15): torch 0.0352
(harness validated — matches the 0.0357 gate ✓) but ONNX zip CER
0.1391 with 89.3% row-exact — the arithmetic signature of ~11% rows
collapsing to near-empty outputs. Two hypotheses: (a) my python
parity decode loop has an edge-case (batch padding/EOS interaction),
(b) the exported graph drops rows. DISCRIMINATOR queued: run the
actual py runtime IMF loader on this zip — if the runtime decodes
correctly, the parity loop is the bug and the artifact ships with a
runtime-verified parity; if not, the graph export needs a fix before
urd-diac-base-1.0 publishes. Publish HELD either way until the
runtime-side check passes.

DISCRIMINATOR VERDICT — the artifact WORKS (2026-10-15): raw ORT
decode of the shipped urd-diac-base-1.0 zip on real rows produces
real diacritics (not empty, not identity). The ~11% collapsed parity
rows are a PARITY-HARNESS artifact: MAXLEN=256 truncated long rows
(collapsed-row CER ≈ 1.0), and the local discriminator loop's own
400-step cap truncated its sample tail the same way. Parity rerun at
MAXLEN=512 (the runtime's decode length) launched — its numbers are
the publish-parity of record. The over-marking visible in samples
(sukun-heavy) is a training-convention trait, scoreable, not a
defect gate.

THE BF16-IMPORT/FP32-ARTIFACT DIVERGENCE — session-closing finding
(2026-10-15): urd-diac-base parity at MAXLEN 512 is IDENTICAL to 256
(row-exact 89.33% both) — truncation REFUTED. The ~11% rows that
collapse to near-total mismatch are a NUMERIC cascade: the gate
engine runs torch under bf16 autocast (as trained); the exported
ONNX artifact is fp32 — when an autoregressive row crosses a
decision boundary under different numerics it cascades to garbage.
The same signature explains the urd-g2p fp32 delta growth (0.024@300
→ 0.078@1K) and likely part of the int8 "catastrophe". CONSEQUENCE:
byt5-base fp32 artifacts carry an artifact-level CER ~3-4× their
torch gate (0.176 vs 0.0357 measured here) — ALL THREE staged
byt5-base publishes (urd-g2p-base-1.0, urd-diac-base-1.0,
ara-diac-news-1.1) are HELD until resolved. Next-session fix
candidates: (a) EXPORT_DTYPE=fp16 (numerics-match the bf16 gate;
single-file fits at base size), (b) a torch-fp32 vs ORT-fp32
three-way probe to separate conversion error from model-edge
sensitivity. The plane family is unaffected (static int8, its own
parity GREEN).

FP16 EXPORT REFUTED — refined divergence hypothesis (2026-10-15):
urd-diac-base fp16 export (1.35GB zip, sanity green) parity → ONNX
0.1938 vs torch-bf16 0.0352 (delta 0.159, 89% row-exact — same
signature). Weight precision is NOT the variable: fp32→0.139,
fp16→0.194, both ~4-5× the gate engine. Remaining discriminator:
torch-fp32-decode vs torch-bf16 on identical rows — if fp32-torch
also collapses, the MODEL is numerically fragile (razor-edge
autoregressive decisions) and NO faithful export can carry the torch
gate number; the honest artifact CER (~0.14) becomes the gate, and
either the model retrains with numeric-robustness awareness or the
runtime ships bf16 graphs. Next-session: the three-way probe, then
the export fix or the retrain decision. ALL THREE byt5-base
publishes remain HELD. (The plane family remains unaffected —
static-int8, its own parity GREEN.)

urd-g2p-base-1.0 PUBLISH HELD — artifact-truth measured (2026-10-15):
the fp32 zip's 1,000-row parity: torch 0.1429 / **ONNX 0.2783**
(delta 0.135, 73% row-exact) vs the 0.1578 gate — the artifact misses
by ~1.8×, unambiguous at this sample size. Combined with the diac-base
signature (torch 0.0352 / ONNX 0.1391, 89% exact) the finding is
CONFIRMED on two models: byt5-base fp32 ONNX exports diverge from
torch-bf16 by ~0.08-0.14 CER with 73-90% row-exact and the remainder
cascading. The small-tier artifacts (urd-g2p-1.0, parity delta 0.0)
are FINE — the divergence scales with model size/sequence length.
NEXT SESSION OPENER — the three-way probe (torch-fp32-decode vs
torch-bf16 vs ORT-fp32 on identical rows): if fp32-torch ≈ ORT, the
bf16 gate numbers were numerics mirages and the base tiers genuinely
perform ~0.14-0.28 (retrain-for-robustness decision); if fp32-torch ≈
bf16-torch, the ONNX conversion is defective (fix the export). ALL
byt5-base publishes stay HELD pending that answer.

THREE-WAY PROBE VERDICT (2026-10-16, run-066-probe3way): torch-bf16
0.0343 / torch-fp32 0.0343 / agree 1.000 — the MODEL is numerically
robust. ORT 0.1301 / agree 0.8867 vs both — **the opset-14 ONNX
export is the defect**, diverging on ~11% of rows. The retrain-
for-robustness path is CLEARED; the fix is the export (candidates:
opset 17+, per-token logit diff on a failing row to find the first
diverging op, or the known T5 relative-position-bias export issue).
All byt5-base publishes remain HELD until an export passes parity at
its gate level. The fix is bounded debugging, next session's opener.

WO46 CLOSED — shipped int8 fleet clean (2026-10-16): zipcheck-v8 on
the RELEASED ara-diac-news-1.0 int8 zip: WER 4.15/DER 1.04 (30-row
harness-validated sample) — no withdrawal needed. The urd-g2p int8
catastrophe remains isolated to that export. Note: the int8 ONNX CPU
decode is extremely slow (~hours/batch) — the 30-row envelope was
required; future int8 parity runs need the CUDA EP or GPU-adjacent
environments.

LOGIT-DIFF PROBE VERDICT — case closed, fix reclassified (2026-10-16):
the local probe on the shipped zip shows enc_max_gap 0.0 (ONNX
encoder bit-identical to torch), first_divergence null (torch and
ORT argmax agree at EVERY step), and degenerate repetition-loop
predictions (ڈْھُواڈْھْوا...) with NUL bytes — **the MODEL itself
collapses to repetition loops on ~11% of rows in BOTH engines**. The
export is fully exonerated; the trainer's 0.0357 gate differed only
because the collapse is BATCH-NUMERICS-DEPENDENT (bs-16 eval masked
it; bs-1 inference exposes it). THE FIX IS DECODE-SIDE: repetition
penalty (or 3-gram blocking) in the three runtimes' seq2seq decode —
no retrain, no export change. All byt5-base artifact gates
re-evaluate WITH repetition-penalty decode; if clean, the held
publishes (urd-g2p-base-1.0, urd-diac-base-1.0, ara-diac-news-1.1)
unblock with a decode-contract note. Next session: implement
repetition penalty in the parity harness + the three runtimes
(penalty ~1.2 / no-repeat-3gram), re-run gates, publish.

PENALTY PARITY FINAL (2026-10-16): with repetition_penalty 1.2 +
3-gram blocking, BOTH engines converge (torch 0.1834 / ONNX 0.2010,
delta 0.018 — engine parity restored, conversion fidelity confirmed)
but NEITHER recovers the 0.0357 gate. Conclusion: the repetition
loop was a symptom; the root is BATCH-COMPOSITION-DEPENDENT collapse
in the model — the gate's 0.0357 was measured at bs 16, and
different batching exposes ~11% collapse rows. The artifact question
reduces to model numeric robustness: urd-diac-base-1.0's honest
decode numbers are ~0.18-0.20 (penalty decode) or ~0.14-0.28
(free decode) vs the 0.0357 torch-at-training-batching number.
NEXT SESSION: (1) characterize the collapse rows (input properties,
batch-position dependence), (2) evaluate at the trainer's EXACT
batching (bs 16) through ORT — if ORT@bs16 matches 0.0357, the
runtime fix is decode-batching standardization (decode at fixed bs
16 in the loaders), (3) re-gate and publish on the honest number.
ALL HOLDS REMAIN.

RELABEL DURABLE-SYNC: first fix wrong (2026-10-16). HfApi.upload_file
rejects repo_type="bucket" — valid types are [None, model, dataset,
space]. Decode is HEALTHY (resumed at 20,640 ✓, running). Next
session: change repo_type to None (bucket surfaces as a None-type
repo) or shell out to `hf buckets cp` in-job; verify one sync
succeeds, then the p047 remainder (~4h) + p029 + consolidation run
death-proof. The mount (/ckpt = the bucket) may itself be durable
for properly-closed files — untested; the explicit sync removes the
doubt.
