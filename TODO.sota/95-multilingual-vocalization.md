# WO95 — multilingual joint vocalization: one ByT5, Hebrew + Urdu, language-prefix conditioning

**Priority:** P1 · **Cost:** ~1 CPU-h prep + smoke (~10 GPU-min) + full run ≈ 9–10
GPU-h (`a100-large`) · **Owner go:** standing delegation (execution per the
work-order instruction; ship stays owner-gated) · **Run:** run-098

## Position in the campaign

The per-language vocalization champions are shipped and gated:
**heb-vocalized-plane-3.0** (crown protocol corpus-level DER **6.6078**,
run-094) and **urd-vocalized-2.0 / 2.1** (WO37 full-split raw CER
**0.03641** / **0.03632**, run-096 clean-room distill / run-097
direct-gold). Every prior model in the zoo is monolingual. Cross-abjad
short-vowel restoration — one model vocalizing two unrelated scripts
(Hebrew niqqud, Urdu haraqat) that share the abjad property (vowels
elided in the source orthography, restored by the model) — is genuinely
unpublished territory: no cross-abjad joint vocalization model exists in
the literature we survey (ReNikud, DictaBERT, Sadeed are all
monolingual; multilingual T5 work covers translation/summarization, not
diacritic restoration). This WO builds the first joint model and
measures the only two questions that matter: (a) does each language hold
its per-language champion bar (parity-or-better), and (b) is there
transfer or interference between the abjad siblings.

## Research claim (pre-registered)

1. **Parity-or-better per language** vs that language's shipped
   champion: heb DER ≤ **6.6078**, urd CER ≤ **0.03641** (and the 3.632
   run-097 bar for the SOTA wording).
2. **Transfer evidence:** a joint model matching a monolingual
   specialist on the low-resource sibling (Hebrew, 50K gold vs Urdu's
   573K) is itself evidence of shared abjad structure; the interference
   measurement below quantifies the other direction.
3. **Interference gate (pre-registered, disclosed either way):** a
   language degrading **> 2% relative** vs its per-language champion
   (urd CER > 3.7046; heb DER > 6.74) is the interference signal —
   documented in the ledger, never hidden. The verdict vocabulary is
   PASS (both parity-or-better) / MIXED (one holds) / INTERFERENCE (the
   >2% signal fired on either language).

**Architecture caveat (recorded up front):** the Hebrew champion
6.6078 is the plane CLASSIFIER lineage (byt5-base encoder + plane head +
mask-predict) trained with the WO92 weak-pretrain curriculum (1.5M
machine-labeled units + gold SFT). The joint model is generative
seq2seq, gold-only. The DER protocol — test set, metric function,
windowing, separator stitching, corpus-level aggregation — is identical;
the architecture and curriculum are not. The champion number is the
pre-registered reference signal, not an architecture-controlled
comparison; the WO92 curriculum (weak-pretrain stage-1) remains the
known Hebrew quality lever and is explicitly out of scope here.

## Design

### One architecture: generative ByT5 seq2seq for both languages

The urd lineage recipe (WO38 → run-059/066/094/096/097) is the family
being extended: encoder-decoder ByT5, bare src → vocalized tgt,
greedy decode, raw-char CER. Hebrew joins it in the generative
formulation: skeleton src → vocalized tgt. The Hebrew skeleton is
**derived** from the gold target with the crown's own decomposition
(`split_planes`, byte-exact inverse of the nikud plane) — the same
derivation the plane line trains and evals on — so Hebrew src/tgt are
perfectly skeleton-aligned by construction and the DER metric sees
exactly the crown conventions (its `_NIQQUD_MARKS` set, maqaf as a
spacing "consonant", teamim absent from v4). This is the only
formulation that shares one model across both languages without an
architecture split (the plane head cannot score Urdu's haraqat).

### Language conditioning: prefix sentinel tokens (the simpler proven pattern)

Standard multilingual-byt5 practice, chosen over per-language encoder
embeddings for being the minimal, well-proven mechanism: two atomic
prefix tokens `<he:` and `<ur:` added via `tok.add_tokens(...)` +
`model.resize_token_embeddings(len(tok))` (vocab 384 → 386), prepended
to every src (`f"<he:{src}"`). New embedding rows are explicit,
collision-free with T5's denoiser `<extra_id_*>` sentinels, and ride
every checkpoint (tokenizer saved with the model). Per-language encoder
embeddings would fork the backbone and break every downstream export
path for zero measured benefit — rejected.

### Data inventory (all verified from source, 2026-11-25)

| language | corpus | rows | integrity | channel |
|---|---|---|---|---|
| heb train | `hf://datasets/Interscript/hebrew-v4` `train.jsonl` | 50,433 `{"src","tgt"}` | crown-lineage SFT corpus of record (WO92); ~30% of tgt carry `\|` syllable pipes — stripped per the WO92 prep law (PREFIX_CHAR, printable-band, dropped explicitly) | dataset mount ro |
| heb eval | same dataset `test.jsonl` | 1,864 human-verified, **zero pipes**, crown test set | the exact set that gated 8.18 → 6.6078 | dataset mount ro |
| urd train | `rhtse/jobs-artifacts/rababa-urdu-cc174b96` `data-diacrit/train.jsonl` | 573,130 | sha256 `95736b0d19e57ada3ce435f28300b8a72a3fec6c761dfce34770ed9549331ee2` (36,589,714 B); re-verified from bucket 2026-11-25 (WO93 record); owner license review 2026-10-18; NOT CLE; zero CLE 8-word-shingle overlap (#477 discriminator) | bucket mount ro |
| urd eval | same bucket `data-diacrit/test.jsonl` | 11,940 | sha256 `6d822ae70a383e5547ee82e841a65e83fac81ae47ff320999b8e6b101b1790bb` (WO37 protocol split, never trained on) | bucket mount ro |

License: both gold corpora carry owner-approved license review records
(heb: the crown-lineage review; urd: the 2026-10-18 review with the
weights-dependency note). Zero CLE overlap is proven for the urd corpus
(#477); the heb lineage contains no restricted corpus at all.

**Per-language load-time invariants (the run-093 lesson is law):**
- urd: parsed src/tgt that still look like JSON abort at load; median
  len(tgt)/len(src) within [0.5, 3.0]; degenerate share (ratio < 0.35)
  under 1% — violations abort BEFORE any GPU spend (the family
  thresholds verbatim).
- heb: pipes stripped from tgt first; src derived via `split_planes`
  so the skeleton invariant holds by construction (asserted: no mark
  characters remain in src, non-empty both sides); windows with a
  leading-mark `\x00` artifact are dropped and counted; a nikud-density
  collapse (mean marks per letter < 0.5 vs the corpus's ≈1.9) aborts as
  data corruption. The crown eval remains the semantic check per the
  standing discipline.

### Mix (pre-registered)

Hebrew windows at the 230-tgt-byte budget: 50,433 rows → **93,429
windows** (computed over the actual corpus). Natural share would be
~14% of pairs — a guaranteed interference signature on the low-resource
sibling and a wasted arm. **HEB_OVERSAMPLE=3** (env-tunable) gives
280,287 heb windows vs 573,130 urd pairs ≈ **33% Hebrew presence**
while Urdu stays the majority language; 3 epochs then expose Hebrew
gold ~9 visits (the crown gold-SFT used 4 — the headroom is the price
of sharing capacity, and the interference gate watches it).

### Recipe (run-098; the family recipe verbatim + the multilingual deltas)

- Init **`google/byt5-base`** — the per-language base teacher tier
  (run-066 urd-diac-base, WO41 GATE PASS 0.0357; the plane crown is
  also byt5-base). Raw Google checkpoint: no interscript ancestry, no
  restricted exposure, single hop for both languages.
- 3 epochs, bs 16 × accum 2 (32 effective), lr 3e-4 cosine (200
  warmup) — the run-066-proven **base-tier** config of this exact task
  family — bf16 autocast, MAXLEN 256, grad clip 1.0, wd 0.01, seed 42,
  gradient checkpointing, NaN-skip + finiteness guard (family
  behavior), step checkpoints every 1000, cross-job resumable
  (step dirs + meta.json + optim.pt).
- Steps: ceil((573,130 + 3×93,429)/32) × 3 = **80,010**; ETA ≈ 8.2 h
  stepping at run-066's measured base-tier rate (~2.71 it/s, 53,733
  steps in 5.5 GPU-h) + ~30–45 min dual evals ≈ **9–10 h total** —
  inside the 24 h timeout with `--attempts 2`.
- Data: `DATA_SPECS=he:<root>:train.jsonl:<label>:3,ur:<root>:train.jsonl:<label>:1`
  (per-language prefix sentinel, glob, provenance label, oversample
  factor — single knob per language; both eval splits live in
  different files than the training globs and can never enter
  training).

### Eval: per-language routing to the crown protocols (terminal, full splits)

- **urd — WO37 protocol verbatim:** all 11,940 rows, greedy (beams 1)
  batched generation (bs 64, attention-masked in-job generate — the
  family decode path), **raw-char CER as the mean of per-row CERs**
  (the family metric of record; run-094/095/096/097 comparability),
  resumable per-row progress jsonl.
- **heb — crown protocol, generative decode:** every test row's gold
  windowed at the same 230-byte budget (word boundaries); per-window
  skeleton + `<he:` prefix → greedy generation → windows stitched back
  per row with the ORIGINAL separators (the crown's separator map);
  **corpus-level DER = Σ(wrong·positions)/Σ(positions)** via the
  crown's own `seq2seq_der` (copied verbatim from
  `interscript-train/src/rababa/evaluate.py`). K=3 mask-predict does
  not exist in the generative formulation — greedy single pass is the
  family decode mode (beam is counterproductive on flat byte models;
  standing law).
- Verdict carries both metrics + per-language verdicts + the
  interference flags; `chain_pass` semantics as the family defines
  them (smokes gate on chain, quality binds full runs only).

### Privacy / Clause 16(e) disposition

- **urd side:** the calibrated matched-split suite per the amended
  methodology (urdu-dev#23–#26) runs on the joint candidate with the
  **domain-matched clean reference** (`/ckpt/run-066-urd-diac-base/best`
  via `GATE_REFERENCE_PATH`; run-066 verified CLE-clean per the #471
  STEP-0 trace). same_population split, length parity enforced,
  self-control exactly 0.5, AUC ±0.05, success-rate 0.6. Note the
  known reading rule from WO92: the candidate is now
  **bilingual**, so a domain-mismatch residual against an urd-only
  reference is possible in either direction — the matched-split
  instrument controls for exactly this; a NOT-near-chance result on it
  is genuine incremental signal → STOP + report verbatim + escalate.
- **heb side: N/A with recorded reason** — the Hebrew lineage (raw
  `google/byt5-base` + hebrew-v4 public gold) contains **no restricted
  corpus**, so there is no held-in plane for a membership instrument to
  probe; a calibrated MIA without a restricted plane is undefined. The
  disclosure record (lineage table above + license review references)
  is the heb-side equivalent of the 16(e) disposition. Flagged here
  explicitly rather than silently dropped.

### Naming (WO87 law)

The naming law defines `{lang}-{target}[-{tier}]-{major.minor}` with
the target from the MECE set; the reference contains **no
multi-language precedent** (verified: zero `multi` rows in
`docs/naming/naming-reference.md` — this WO creates the first).
Candidate id per the standing delegation pattern (propose + record;
owner states the version at ship):

- **Candidate: `multi-vocalized-base-1.0`** — lang slot `multi` (the
  first multi-language family; per-language fallback aliases are an
  owner decision at ship), target `vocalized` (decode evidence: the
  output is native script + diacritics for both languages), tier
  `base` (the ByT5-base init, `urd-vocalized-base-1.0` precedent).
- Run id: **run-098** (next free number; smoke = run-098a).

## Gates (all pre-registered)

| gate | bar | meaning |
|---|---|---|
| urd quality gate | CER ≤ 0.0377 | shipped-champion floor (urd-vocalized-1.0, WO37) |
| urd champion bar | 0.03641 / 0.03632 | urd-vocalized-2.0 / 2.1 — parity-or-better |
| heb parity bar | DER ≤ 6.6078 | heb-vocalized-plane-3.0 — parity-or-better |
| interference signal | urd CER > 3.7046 or heb DER > 6.74 | >2% relative degradation vs champion — document, don't hide |
| smoke gate | chain_pass true, both eval routes produce metrics | chain validation only (WO92 ruling: quality binds full runs) |
| 16(e) urd | calibrated matched-split near chance | amended methodology, run-066 clean reference |

Verdict matrix: PASS (both parity bars met) → ship recommendation to
owner (candidate `multi-vocalized-base-1.0`) + the SOTA claim "first
cross-abjad joint vocalization model at per-language champion parity".
MIXED (one language holds) → the holding language carries transfer
evidence; the degraded language documents the interference signal; owner
decides next arm (pre-registered candidates: HEB_OVERSAMPLE sweep, heb
weak-pretrain stage-1 join per WO92, two-stage curriculum). INTERFERENCE
(>2% on either) → documented negative, no ship consideration, owner
decides.

## Kill criteria

- Load-time invariant violation on either corpus → abort before GPU
  spend; one data-side iteration max, then stop + report.
- Loss spike / non-finite signature → family NaN-skip applies; >1% of
  steps skipped → abort (the RMSNorm+bf16 lesson does not retry
  unstable configs; this stack is the run-066-proven one).
- Checkpoint stall (no new step dir > 2 h) → investigate logs before
  any relaunch; one relaunch max (resume contract makes it cheap).
- Fleet discipline: this campaign holds THE one big-GPU job (a100);
  verified free at launch (all running jobs a10g-large/cpu); never
  launch a second big job while run-098 is alive.
- Window/timeout: 24 h timeout, `--attempts 2`, checkpoint cadence
  1000 — a timeout mid-eval resumes from the eval progress jsonl
  without re-stepping (family contract).

## Jobs (HF Jobs only; one big-GPU job; env-file launches — the
process-substitution lesson is law)

| job | purpose | config |
|---|---|---|
| `run-098a-multiling-smoke` | 2×200-row joint smoke: both corpora load through DATA_SPECS, per-language invariants, prefix tokens + resize, train steps, both eval routes emit metrics | a100-large, 2 h timeout, `--attempts 2`, `multiling-smoke.env` |
| `run-098-multi-vocalized` | full joint run + dual terminal evals | a100-large, 24 h timeout, `--attempts 2`, `multilingual.env`, CKPT_EVERY 1000 |

Launcher: `training/teacher_distill/launch.sh train_multiling_vocalize_hf.py
<env> a100-large -v hf://datasets/Interscript/hebrew-v4:/data-heb:ro`
(the extra heb mount rides the launcher's extra-mount passthrough;
default mounts give `/ckpt` rw + `/data-replay` ro). Aggregate-only
logging (Clause 19): corpus text never printed.

## Deliverables

1. This WO (design + inventory + gates + kill criteria + version
   candidate) — merged before any GPU spend.
2. Trainer PR on urdu-dev (`train_multiling_vocalize_hf.py` + env
   files + regression pins), merged on green before launch.
3. Smoke verdict (chain evidence) recorded here verbatim.
4. Full-run launch record (job id, ETA) and, on terminal, both
   per-language verdicts verbatim in this ledger.
5. Negative results recorded with the same care (the ledger's law).

## Execution records

### Trainer + smoke (2026-11-25)

- Trainer landed: urdu-dev#31 (`train_multiling_vocalize_hf.py` +
  `multilingual.env` + `multiling-smoke.env` + 22 regression pins,
  suite 30 passed; no-corpus guard clean; Urdu fixtures romanized per
  the split-parity precedent). Real-data pre-check through the actual
  loaders on actual bytes: heb 50,433 rows → 93,429 windows at the
  230-byte budget, nikud density 0.6487 (the abort floor set to 0.4
  against the measured norm); urd train 573,130 pairs sha256
  `95736b0d…` verified from the bucket (ratio_median 1.7, degenerate
  0.0); urd test 11,940 rows sha256 `6d822ae7…`; ByT5 prefix tokens
  verified atomic (ids 384/385, vocab 384 → 386).
- Smoke `run-098a` (job `rhtse/6b06a4ed1460ffe1d5ea4814`, a100-large,
  COMPLETED 2m54s): **CHAIN PASS** — `{"chain_pass": true, "pairs":
  1286, "steps_completed": 41, "steps_expected": 41,
  "final_checkpoint_usable": true, "nan_skips": 0, "eval_langs":
  ["he","ur"], "eval_rows_scored": 617}` — both per-language eval
  routes emitted metrics (he corpus-level seq2seq_der over 417
  windows; ur WO37 CER over 200 rows). Quality fields MISS as
  expected at 41 steps from raw init (WO92 ruling: smokes gate on
  chain only).

### Full run launch (2026-11-25)

- `run-098-multi-vocalized`: job `rhtse/6b06d122d91f621b93079037`,
  a100-large, detached, 24 h timeout, `--attempts 2`, CKPT_EVERY
  1000, mounts = launcher defaults (`isx-training:/ckpt` rw,
  `rababa-urdu-cc174b96:/data-replay` ro) + `hebrew-v4:/data-heb` ro.
- Fleet at dispatch: this campaign held THE big-GPU job (others:
  4× ivrb cpu-basic, 3× foreign a10g-large). Early-stepping sanity:
  step 900/80,010, loss 0.107 falling, 2.28 it/s, zero NaN skips.

### run-098 verdict (2026-11-26) — **PASS: both parity bars beaten, zero interference**

Job COMPLETED in 10 h 07 m (80,010/80,010 steps at ~2.2 it/s;
verdict.json + SHA sidecar at `isx-training:/run-098-multi-vocalized/`).
Gated fields, verbatim:

```json
{
  "run": "run-098-multi-vocalized",
  "init": "google/byt5-base",
  "steps": 80010, "epochs": 3, "pairs": 853417,
  "ur_cer": 0.03604,
  "he_der_pct": 5.3075,
  "ur_pass": true, "he_pass": true,
  "ur_interference": false, "he_interference": false,
  "chain_pass": true,
  "verdict": "PASS"
}
```

Gate table (WO95 pre-registered bars):

| language | metric (protocol) | joint run-098 | gate | champion | verdict |
|---|---|---|---|---|---|
| urd | raw-char CER, row-mean (WO37, 11,940 rows) | **0.03604 (3.604%)** | ≤ 0.0377 | 0.03641 (urd-vocalized-2.0) · 0.03632 (urd-vocalized-2.1) | **PASS — beats BOTH champions** |
| heb | corpus-level seq2seq_der, generative crown protocol (1,864 rows / 4,094 windows) | **5.3075%** | ≤ 6.6078 | 6.6078 (heb-vocalized-plane-3.0) | **PASS — beats the crown by 1.30pp** |
| urd interference | >2% relative degradation (bar 0.0370464) | flag **false** | — | — | no interference |
| heb interference | >2% relative degradation (bar 6.74) | flag **false** | — | — | no interference |
| chain | steps 80,010/80,010, final ckpt usable, 0 NaN skips, 16,034 eval rows scored (4,094 + 11,940) | chain_pass **true** | — | — | PASS |

Reading: the first cross-abjad joint vocalization model is
parity-or-better on BOTH language champions — the SOTA-claim condition
of this WO holds. The low-resource sibling (Hebrew, 50K gold vs Urdu's
573K) shows the largest margin: one gold-only generative ByT5-base
beats the plane-classifier crown that trained with the WO92
weak-pretrain curriculum, with zero >2% degradation on either language
— no interference signal fired. Architecture caveat unchanged: the heb
comparison is the pre-registered reference signal (metric/test/stitch/
aggregation identical), not an architecture-controlled trial.

Release status: **NOT SHIPPED — nothing ships from this record.** The
urd-side calibrated Clause 16(e) matched-split gate (run-066 clean
reference), the standard ship chain (parity ≥ 500 shipped-mode samples,
conformance fixtures, license strings, Schedule D, certificate), and
the owner-stated version (candidate `multi-vocalized-base-1.0`, never
picked here) all remain ahead of any release consideration.

## Status

RUN COMPLETE — verdict PASS recorded 2026-11-26; ship chain owner-gated.
