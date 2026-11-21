# WO92 — Hebrew weak-pretrain: knesset-v6 deduped curriculum on the plane crown lineage

**Priority:** P1 · **Cost:** ~0.5 CPU-h prep + ~10–14 GPU-h stage 1
(`a100-large`) · **Owner go:** 2026-11-19 · **Run:** run-093

## Position in the campaign

The crown `heb-vocalized-plane-2.0` (DER **8.18**, nakdimon test, greedy
crown protocol) is data-limited: 50,433 gold units (hebrew-v4 train).
WO26's verdict — "capacity arms are closed; only data moves Hebrew" —
plus the s45 curriculum VERDICT (2026-08-20: weak-pretrain + gold-FT
beats gold-only, −0.88 DER on the custom stack) and the ReNikud-validated
plane factorization define this arm: port the curriculum to the plane
lineage. Machine-labeled mass supplies the nikud prior; gold corrects it.

## Data contract (built by prep, never hand-maintained)

Source: `Phonikud/phonikud-data` `knesset_nikud_v6.txt.7z`
(MIT, verified via the dataset card cardData 2026-11-19; sha256 pinned
at fetch — 142,845,067 B observed). Labels are the **Dicta machine
diacritizer** (+ ~1k manual high-frequency corrections): **weak
supervision only — never the quality or eval signal** (no-teacher-poison
law). v6 is single-column: nikud + `|` syllable separators + stress/
teamim. The separators, per phonikud's own source: `PREFIX_CHAR = "|"`
(ASCII U+007C — inside the printable band, so dropped **explicitly**;
the s45 comment said drop but its ASCII range kept it) and
`HATAMA_CHAR = U+05AB` (stress; teamim range — dropped by the plane set).

Prep policy (run in-job, corpora never touch the laptop):
plane-mark-set normalization (`nikud_planes.NIKUD_MARKS` — the trainer's
own definition), s45 filters (src 10–300 chars, Hebrew fraction ≥ 0.6,
nikud density ≥ len/12), **exact-input (skeleton) dedupe** first
occurrence wins (the prior pass measured 2.48M/5.3M exact duplicates),
40-char window decontam (stride 20, whitespace-collapsed letter normal
forms both sides) vs the human-verified eval set, contiguous
source-order shards + `manifest.json` (every count) + `SHA256SUMS.txt`
sidecar. Provenance-preserving: source order kept, per-shard rows and
sha256 recorded.

Channel: artifact stages at `hf://datasets/Interscript/he-knesset-v6-weak`
(private, created for this WO), mounted ro via HfFileSystem in the
trainer job; `SHA256SUMS.txt` pins every file. The public distribution
copy (GitHub Release + sha256 sidecar on interscript-models, the
golden-v2 pattern) is an **owner-gated publish step** — this repo never
reads data over raw.githubusercontent.com.

## Recipe (run-093, crown recipe verbatim)

- byt5-base **encoder** + plane embedding + per-char head (the
  run-022 architecture); mask-predict training with random keep-rate q.
- Corpus: deduped knesset weak units (cap 1,500,000) **combined with the
  full gold train (50,433)** — the combined-corpus lesson; seed-42
  shuffle; 2,000 held-out val rows.
- AdamW lr 1e-4 wd 0.01, cosine, warmup 500, clip 1.0, bf16 autocast
  with **fp32 CE over bf16 logits** (the crown stability contract),
  micro-bs 8 × accum 2, 1 epoch (s45 stage-1 proportion).
- Norm discipline: ByT5's internal T5-norm stays AS-PRETRAINED — the
  crown recipe is proven stable at run-021/022/026 on this stack. No
  new RMSNorm modules; custom modules are plain fp32; the LayerNorm
  fix targets custom norm modules (none exist here). If the s-era loss
  spike appears: one fallback run with autocast off (fp32) — the
  known-good custom-stack fallback — then kill.
- ByT5 byte-table law: ids from `AutoTokenizer` only (`input_ids[:-1]`
  strips trailing EOS id 1); raw `text.bytes` never enters the pipeline.
- Decode/eval: single-row **greedy** K=3 mask-predict only — beam is
  counterproductive on flat byte students and is never used, matching
  the shipped crown protocol.
- Checkpoints: step-1000 cadence → `hf://buckets/Interscript/isx-training/run-093-heb-weak-pretrain/`,
  `labels.sha` (sha256[:12] of inventory bytes) resume contract. The
  weak-pretrain inventory is the stage-2 vocabulary — **vocab path
  consistency** enforced by the labels.sha gate (crown pattern).

## Gates

- **Prep gate (before GPU spend):** unique yield ≥ 1,000,000 rows
  (prior estimate 1.5–2M); decontam drops ≤ 0.1% of kept (a higher rate
  means the corpus overlaps the eval set harder than s45 found — stop
  and diagnose). Counts recorded in manifest.json.
- **Stage-1 eval is INFORMATIONAL:** weak-pretrain DER on the
  human-verified test set is reported, never gated — machine labels
  never gate quality.
- **Stage 2 (gold SFT) is OWNER-GATED**, launched only after:
  (a) the eval-set decision below, and (b) an owner go. Stage 2 = the
  exact crown recipe resumed from the run-093 best checkpoint, gate =
  the crown protocol (greedy, single-row windows, seq2seq_der) against
  the shipped 8.18; ship decision then follows the standard gates
  (parity ≥ 500 samples single-row greedy, license, conformance).

## Eval set — census and status

`hf://datasets/Interscript/hebrew-v4` `test.jsonl` = **1,864 held-out
HUMAN-VERIFIED rows** (Nakdimon-derived; the exact set that gated the
crown 8.18 and the whole plane family). Status: **adequate** for the
crown-protocol gate (apples-to-apples with every shipped Hebrew
number), but small — a DER delta under ~0.5pp on it is within seed
noise. Per the owner instruction: weak-pretrain runs NOW; **stage-2 SFT
is gated on the eval-set decision** — options for the owner:
(a) proceed on the 1,864-row set (comparable, small), (b) add a fresh
human-verified dev slice (ReNikud test is external and readable; any
addition must stay held-out from ALL training), (c) both (gate on the
crown set, report the second set as evidence).

## Kill criteria

- Prep gate miss → no GPU spend; report counts, one data-side iteration.
- Loss spike / non-finite loss signature → abort, one fp32-autocast-off
  fallback, then kill the arm (the RMSNorm+bf16 lesson: do not retry
  the unstable config).
- Checkpoint stall (no new step dir for > 2h) → investigate logs before
  any relaunch; one relaunch max (resume contract makes it cheap).
- Fleet discipline: ≤ 2 concurrent big-GPU runs from this campaign;
  never launch stage 2 while stage 1 is alive.

## Naming (WO87 law)

Successor candidate id: `heb-vocalized-plane-{major.minor}` — target
`vocalized` (native script + diacritics), tier `plane` rides along;
**version = owner decision at release, never picked here**. Note: the
zoo and `docs/naming/naming-reference.md` use the `heb-` prefix for
Hebrew (all seven shipped rows); any `he-` shorthand elsewhere defers
to the reference. Renames/aliases per the WO87 map when publishing.

## Deliverables

1. Prep artifact + manifest counts in RESULTS.md (this launch).
2. run-093 verdict.json (informational DER) + ETAActual in RESULTS.md.
3. Stage-2 SFT: owner-gated follow-up WO entry once the eval-set
   decision lands.
4. Negative results recorded with the same care (the ledger's law).

## Stage 2 — LAUNCHED (owner go, 2026-11-19)

Owner decisions recorded: stage-2 gold SFT approved; **eval-set =
option (a)** — the 1,864-row human-verified crown set as-is.

- Run: **run-094-heb-gold-sft** (a100-large, `--detach`, 6h timeout —
  above the 4h floor; ≈12.1K steps expected at crown-recipe scale).
- Init: run-093-heb-weak-pretrain `best/model.pt`; inventory READ from
  the run-093 dir and copied byte-identical (labels.sha digest
  unchanged — the vocab path consistency law); the trainer refuses to
  init if the checkpoint's saved classes diverge from the inventory.
- Recipe: crown gold recipe VERBATIM — gold-only hebrew-v4 train,
  4 epochs, AdamW lr 1e-4 wd 0.01, cosine warmup 500, clip 1.0,
  micro-bs 8 × accum 2, bf16 autocast + fp32 CE, mask-predict q.
- Gate (pre-registered): crown protocol, single-row greedy K=3,
  seq2seq_der on the crown test — **DER < 8.18 clears the crown gate**
  (`heb-vocalized-plane-2.0`); ≥ 8.18 is a recorded negative, the
  crown stays shipped. Stage-1 informational reference: 9.1316.
- Checkpoints: step-1000 cadence with the labels.sha contract →
  `isx-training:/run-094-heb-gold-sft/`.
- Fleet: 0 concurrent big-GPU runs from this campaign at launch
  (run-093 COMPLETED 6h 0m).
- Trainer: interscript-train branch `feat/he-gold-sft` (PR on merge;
  the WO92 branches were merged, so stage-2 rides fresh branches per
  the stranded-commits lesson).
- Ship chain after a cleared gate (owner-gated at each step): parity
  ≥ 500 samples single-row greedy, export/int8 per the standard chain,
  explicit owner-stated version, index entry + aliases, HF mirror.
  NO version numbers are picked by the campaign.

## Ship-gate round (owner standing directive; STOP at publish) — 2026-11-21

Job `heb-wo92-shipgate` (id `6b0120f04fdc5ab3c55c6204`, a100-large,
COMPLETED; trainer code interscript-train PR #149): one in-job pass on
the run-094 best checkpoint against the committed 600-row eval600 heb
slice (sha-verified in-job), single-row greedy K=3 (shipped decode
mode), reference = the fp32 ONNX artifact under ORT CPU x86 (the
published round's definition; torch bf16 decode kept as a sanity lane,
66/600 flips informational).

| gate | result |
|---|---|
| export (fp32 plane ONNX opset 17, input_ids+plane_ids) | **PASS** — 1661.3MB |
| int8-static export (house run-070 recipe: MatMul/Gemm-only QDQ, QUInt8 acts) | **PASS** — 418.8MB |
| int8-dynamic export (crown lineage's shipped mode) | **PASS** — 416.0MB |
| parity int8-static vs fp32 (CER ≤ 2.0pp, flips ≤ 1%, ≥ 500 samples) | **FAIL** — 0.94pp OK, flips 288/600 = 48.0% |
| parity int8-dynamic vs fp32 (same gates) | **FAIL** — 0.36pp OK, flips 203/600 = 33.8% |

Informational slice DER vs gold (seq2seq_der, 600 rows): fp32 9.8276 ·
int8-static 11.0422 (**+1.21pp DER cost**) · int8-dynamic 9.8825
(**+0.05pp — quality-neutral**). Full-set reference: 6.6078
(verdict.json).

**Finding:** the ≤1% flip gate — written for generation-based seq2seq
artifacts — cannot pass for per-char plane classification under ANY
int8 recipe; quantization flips single low-margin characters in a
third to half of rows. The quality truth is the DER delta: dynamic
int8 is neutral, static int8 costs +1.21pp. Consistent with the WO20u
scope note ("static recipe is KV-only") — the plane encoder sits
outside that verdict's scope.

Fixtures landed: `golden/heb-vocalized-plane-wo92rc-int8static-golden.jsonl`
+ `...-int8dynamic-golden.jsonl` (600 rows each, {"input","output"},
plane-family golden shape) + `conformance/wo92/manifest.json` (full
round record; sha-pinned; references the committed eval600 slice, no
duplication). All RC artifacts + SHA256SUMS on
`isx-training:/wo92-rc/` (verified on fetch).

**Owner decision queue (publish stays CLOSED until then):**
1. Gate semantics for plane artifacts: the flip gate predates the
   plane family; a DER-delta gate (e.g. ≤ 0.25pp on the slice) is the
   quality-faithful alternative. Redefinition = owner call.
2. Quantization arm: int8-dynamic (quality-neutral, the crown's
   shipped mode) vs fp32/fp16 vs a redefined static recipe.
3. Version word for `heb-vocalized-plane-{major.minor}` — the rename
   of the wo92rc lane fixtures + the chosen arm's zip is mechanical
   once spoken.
