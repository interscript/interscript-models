# WO94 — Persian poetry vocalization: acquisition + curriculum (SOTA-2027 R1)

**Priority:** P1 · **Cost:** ~2–4 CPU-h acquisition + 40–80 GPU-h phase 2
(`a100-large`) · **Owner go:** 2026-11-24 (interscript-models#488, owner
sources approved) · **Runs:** run-098 (acquisition), run-099+ (phase 2)

## Position in the campaign

The largest measured headroom in the org: `fas-vocalized-base-1.0`
(news/docs register) holds **CER 0.603%** (greedy, 9,288-row docs split,
row-mean) but scores **33.67%** on the pinned Ganjoor vocalized-poetry
eval (3,497 verses, 79 poets; sha256 94f318f688b556be…) — a **56×
register gap** (WO66-measured, full run 2026-10-26). The proven register
arm (fine-tune on the 446k CC0 corpus + the 3,497-verse seed ×10) HALVED
poetry CER to **16.55%** while holding the docs gate (0.69% —
run-089-fas-register). Neither validated 2026 template has been applied
at scale: this WO applies the Hebrew `heb-vocalized-plane-3.0` curriculum
(run-093 weak-pretrain → run-094 gold SFT; −1.57pp crown effect) mapped
to Persian, on license-clean owner-approved sources.

## Phase 1 — acquisition (owner sources, WO66 dossier pre-staged)

The dossier's three sources, with the license records and the acquisition
decisions actually made (2026-11-25):

### 1. Ganjoor (poetry register) — CC BY-SA 3.0, site-stated

- Canonical channel: the ganjoor.net public REST API
  (`https://api.ganjoor.net/api/ganjoor`) — **the live API is the only
  current bulk channel**: the official `ganjoor/ganjoor-db` MySQL dump is
  from 2017 (stale; probe sha256 4623701c5ff54a4f… recorded here, job
  rejected). License string recorded per the WO66 dossier (owner-reviewed
  2026-10-25); the site is client-rendered so no static license page
  exists to cite — the dossier IS the org license record. Share-alike
  consequence: the derived corpus inherits CC BY-SA 3.0; the weights
  carry the copyleft dependency note (the tashkeela lane).
- The API exposes, per poem, `plainText` (site-stripped) AND
  `verses[].text` — the **vocalized** text (erab/haraqat present), the
  exact src/tgt structure of the pinned eval.
- The pinned-eval src convention was REVERSE-ENGINEERED from the pinned
  rows and verified reproducing them (3,497/3,497 at character level):
  strip = the vocalic marks **U+064B–U+0652 + U+0670**, KEEPING the
  hamza/maddah carriers U+0653–U+0655 (the eval src retains U+0654
  hamza-above ×130 and U+0656 ×1) and all punctuation/ZWNJ. One pinned
  row carries a trailing space the acquisition's `.strip()` hygiene
  removes (the only 3497th-row delta; the CHARACTER convention is exact).
- Per-row attribution: `poet_url`, `poet_name`, `cat_path`, `poem_id`,
  `poem_title`. Job: `wo94-ganjoor-crawl`
  (`rhtse/6b06780e1460ffe1d5e9e4c2`, cpu-upgrade, detached, 12 h,
  per-poet `.done` resume markers in the bucket). Script:
  `interscript-train prep_fas_ganjoor.py`.

### 2. fa-Wikisource (poetry + classical prose) — CC BY-SA 4.0

- Canonical channel: `dumps.wikimedia.org/fawikisource/latest/
  fawikisource-latest-pages-articles.xml.bz2` (probed 47,719,980 B,
  Last-Modified 2026-11-01; the manifest pins exactly what was fetched).
- Wikitext extraction flattens templates to their argument VALUES —
  fa-wikisource poetry lives inside `{{شعر|بیت|بیت}}`-style templates;
  dropping templates whole would delete the poem bodies. Refs/tables/
  comments dropped; `[[a|b]]` → b; headers unmarked; line structure
  preserved. Per-row attribution: title + pageid (page history).
- Job: `wo94-fawikisource-dump` (`rhtse/6b067816d0582cfbbefdbef5`,
  cpu-upgrade, detached, 4 h). Script: `prep_fas_fawikisource.py`.

### 3. OSCAR-fa → **NOT ACQUIREABLE upstream; substitute = cc-fa-web**

- **The canonical OSCAR releases are suspended upstream** (2026-11-25
  probe): `oscar-corpus/oscar` (CC0-1.0), `OSCAR-2109/2201/2301` — all
  gated manual, and the gate text states VERBATIM: *"We are forced to
  temporarily suspend access to OSCAR … we will not grant any access
  until the situation has been clarified."* No archive.org snapshot of
  the old OSCAR host; no Zenodo mirror; `allenai/mc4` removed from HF;
  the third-party mirrors (`nthngdy/oscar-mini` et al.) are truncations
  with unverifiable lineage (fa.gz = 15.7 MB — a sample, not the mass).
  The rhtse token is not granted; a gate request is futile while the
  suspension stands, so none was filed.
- **Decision (recorded): reconstruct the dossier row's register intent
  from its own framing** — "colloquial/web; Common-Crawl-derived;
  register = modern web; quality filters needed" — directly from Common
  Crawl WET, crawl **CC-MAIN-2026-47** (Nov 2026; 100,000 WET segments,
  ~66 MB gz each at probe), deterministic stride sample (NSEG=120,
  reproducible from the crawl id alone). Language = WET
  `WARC-Identified-Content-Language` header (fas/pes/fa/pbu) **and** a
  Persian-letter floor (≥ 0.6) **and** script-exclusive rejection of the
  Kurdish (ڕڵۏێە) / Urdu (ٹڈڑںے) letters and ta-marbuta-heavy docs
  (neighbor-script bleed verified in the smoke probe and fixed).
- Registry treatment: license `LicenseRef-CommonCrawl-Terms` +
  `license_review:` record citing the owner's dossier framing (the same
  construction the dossier put on OSCAR-fa). **Weak-pretrain mass ONLY —
  never the quality or eval signal** (no-teacher-poison law; machine
  mass never gates quality).
- Job: `wo94-ccfa-web-n500` (`rhtse/6b0678a31460ffe1d5e9e5ec`,
  cpu-upgrade, detached, 12 h, per-segment `.done` resume; supersedes the
  NSEG=120 first launch `rhtse/6b06781b1460ffe1d5e9e4cc` — cancelled at 2
  segments after the observed fa yield (~135 docs/segment) showed 120
  segments would land only ~16k docs; NSEG=500 targets ~67k).
  Script: `prep_fas_ccfa_web.py`.

### Packaging (the run-096b conventions, mirrored per source)

Bucket: `isx-training:/run-098-fas-acquisition/{ganjoor,fawikisource,
cc-fa-web}/`. Per source: contiguous source-order shards
(`{source}-NNNNN-of-NNNNN.jsonl`), `manifest.json` (every count, the
policy block, the license/provenance block, per-poet shares where
applicable), `SHA256SUMS.txt` sidecar pinning every shard + the
manifest, and a `DONE` marker. Per-poet/segment raw files + `.done`
markers make both crawls resumable across job restarts. The
`corpora/*.yaml` records pin the manifest sha256 (the heb-knesset-weak
pattern).

### Corpus gates — PRE-REGISTERED before acquisition (the run-093 law)

The evals must stay held-out: both crawls decontaminate (40-char windows,
stride 20, Arabic-letter normal forms, BOTH sides) against BOTH pinned
evals — the Ganjoor crawl shares its upstream source site with the poetry
eval, making this the load-bearing gate.

Semantic invariants (enforced by the separate
`gate_fas_acquisition.py` job, which re-hashes every artifact from the
bucket and recomputes stats from the shards):

| gate | ganjoor | fawikisource | cc-fa-web |
|---|---|---|---|
| src/tgt ratio | len(tgt)/len(src) ∈ [1.0, 2.0] EVERY row (vocalization only adds marks; eval calibration: median 1.1724, max 1.8571) | — | — |
| vocalized share | tgt ≠ src on ≥ 0.30 of rows; per-poet share recorded | — | — |
| harakat density | marks-per-letter median ≥ 0.05 on vocalized rows (eval median 0.2222, p5 0.037) | — | — |
| degenerate share | < 1% (empty src/tgt) | < 1% | < 1% |
| rows floor | — | ≥ 500 pages | ≥ 10,000 docs |
| script sanity | Arabic-letter fraction median ≥ 0.5 (eval p5 0.6); Persian-specific letters پ چ ژ گ ALL present; ZWNJ present | same floor | Arabic-letter fraction median ≥ 0.6 (the acquisition floor itself) |
| integrity | SHA256SUMS re-hash clean | same | same |

Persian script/range law (documented): Arabic block U+0600–U+06FF
(includes the Persian letters پ U+067E چ U+0686 ژ U+0698 گ U+06AF
ک U+06A9 ی U+06CC), Arabic Supplement U+0750–U+077F, Extended-A
U+08A0–U+08FF; haraqat strip set U+064B–U+0652 + dagger alif U+0670;
hamza/maddah carriers U+0653–U+0655 retained (letter-changing); ZWNJ
U+200C counted (Persian orthography); presentation forms U+FB50–U+FEFF
flagged as normalization artifacts (none expected post-NFC inputs).

### Phase 1 records

Acquisition numbers, gate verdicts, and artifact sha256s are appended in
the Phase 1 RESULT section below once the three jobs and the gate land
(the records are written from the bucket artifacts, not from job logs).

## Phase 2 — the curriculum (Hebrew template mapped to Persian)

Owner plan (#488): **weak-pretrain on the web mass → gold SFT on Ganjoor
poetry** — the run-093 → run-094 recipe that delivered −1.57pp DER on the
Hebrew crown, plus the proven WO66 register arm (checkpoint fine-tune +
seed oversample). Note the ROADMAP's earlier "no weak-pretrain wanted"
line is superseded by the owner's explicit #488 plan; the ROADMAP's
method-fit note applies to its direct-gold arm, which remains a fallback
arm below.

- **Stage 1 (weak-pretrain / DAPT-mass):** byt5-base + the Persian
  corpus mass — the cc-fa-web slice (cap 1,500,000 units, the run-093
  proportion) combined with the full fas-dia gold train (445,869) — the
  combined-corpus lesson; seed-42 shuffle; 2,000 held-out val rows.
  Stage-1 eval is INFORMATIONAL (machine/web mass never gates quality).
- **Stage 2 (gold SFT):** resumed from stage-1 best, the crown recipe
  verbatim on Ganjoor gold (acquired vocalized verses; the 3,497-verse
  pinned eval ×10 seed oversample — the proven register recipe, now
  scaled by the acquired mass). Gate pre-registered:
  - **news-classic hold:** full 9,288-row docs split, row-mean CER
    **< 0.70%** (the WO66/B5 register-hold law; current 0.603% — the
    model must HOLD the news register while gaining poetry).
  - **poetry gain:** the pinned 3,497-verse Ganjoor eval, same protocol
    as run-089 (harakat-stripped src vs vocalized gold; row-mean raw CER)
    — report against the 33.67% baseline and the 16.55% register-arm
    precedent; the SOTA line is register-gap reduction.
  - A fa-Wikisource classical-prose slice (held-out-from-training) and a
    colloquial register slice join the eval battery as informational
    register probes (WO66's register-stratified acceptance).
- **License gate:** corpora ganjoor (CC BY-SA 3.0) + fas-dia (CC0) +
  fawikisource (CC BY-SA 4.0) + cc-fa-web (LicenseRef + review record);
  publish path needs the owner's read on the share-alike
  weights-dependency note (the tashkeela lane) — surfaced at ship, not
  now.
- **Calibrated 16(e), amended methodology (urdu-dev#23–#26):**
  matched-split construction (same_population mode; length-parity
  enforced as a hard property) with a **Persian-domain-matched
  reference** — the fas lineage's own base checkpoint
  (fas-vocalized-base-1.0 lineage), NOT a generic multilingual reference
  (the urdu finding: a generic reference conflates domain specialization
  with memorization). Expected near chance (clean sources); NOT near
  chance on a matched split = real signal → STOP + escalate.
- **Naming (WO87):** successor candidate id **fas-vocalized-1.0**
  (target `vocalized` per decode evidence; separate id from the shipped
  tier model fas-vocalized-base-1.0, which stays). Version = OWNER
  decision at ship; the candidate number is recorded here per the
  standing delegation pattern ("owner approves the recommendation;
  version delegation to my stated recommendation" — the WO92 ship
  precedent) and becomes real ONLY on the owner's ship approval.
- **Fleet discipline:** ≤ 2 concurrent big-GPU runs; never stage 2 while
  stage 1 is alive; `--detach`, `--timeout ≥ 4h`, step-1000 checkpoints
  with the labels.sha resume contract, bucket I/O via HfFileSystem mount.

### Phase 2 GPU plan (ETA at crown-recipe scale)

| arc | job | flavor | est. |
|---|---|---|---|
| P2-0 | corpus prep (shards, seed build, decontam verify) | cpu | ~1–2 h |
| P2-1 | run-099 stage-1 weak-pretrain (1.5M mass + 446k gold, 1 epoch, bs 8 × accum 2) | a100-large | ~10–14 h |
| P2-2 | run-100 stage-2 gold SFT from run-099 best (Ganjoor gold + seed ×10, 3–4 epochs) | a100-large | ~6–10 h |
| P2-3 | register-stratified eval battery + calibrated 16(e) matched-split vs the fas-domain reference | l4x1 | ~2–4 h |
| P2-4 | owner report + ship chain (parity ≥ 500 single-row greedy, export, conformance) — owner-gated | cpu/l4x1 | owner |

Total ≈ 20–30 GPU-h core (inside the 40–80 h envelope with retries and
the fallback direct-gold arm).

### Phase 2 launch authority (agent judgment, recorded per #488's report gate)

- The **direct-gold arm** (Ganjoor gold SFT + the fas-dia CC0 corpus —
  no CC-derived input) is squarely covered by the owner's #488 approval
  and the standing delegation ("Fully approve all, use reasonable
  recommendations" / "Continue all and make SOTA 2027 … finally
  launch"): launchable once the corpus gates are green.
- The **weak-pretrain arm on cc-fa-web is owner-visible first**: the
  OSCAR→Common-Crawl substitution is a material deviation from the
  dossier's named source, and any ship path through it carries
  `LicenseRef-CommonCrawl-Terms`, which the registry blocks without an
  explicit owner review (a publish-guard law, never an agent call).
  Training on it (weak mass, never quality-gating) is defensible under
  standing delegation; SHIPPING anything derived from it is not. The
  acquisition report therefore precedes that arc's launch, per #488's
  own "acquisition run → owner view" reading.

### Kill criteria

- Corpus gate FAIL → no GPU spend; one data-side iteration max, then
  report (the run-093 lesson: never launch on a failed stats gate).
- Stage-1 loss spike / non-finite loss → abort; one fp32-autocast-off
  fallback, then kill the arm (the RMSNorm+bf16 lesson).
- Docs-hold gate FAIL at stage 2 (register gain that costs the news
  register) → the model is a poetry specialist, NOT the successor:
  record, try the seed-oversample proportion next, then stop.
- Poetry eval ≤ the 16.55% register-arm precedent with the full mass
  acquired → the curriculum adds nothing over the proven arm; record the
  negative with the same care, keep the register arm as the line.
- 16(e) matched-split NOT near chance → STOP + escalate (never
  parameterize the gate toward PASS).

## Deliverables

1. Three acquired corpora + manifests + sha256 pins (bucket
   run-098-fas-acquisition) + `corpora/*.yaml` records.
2. Gate verdicts (gate-verdict.json) + this ledger's Phase 1 RESULT.
3. Phase 2 training branches + runs per the plan above.
4. Negative results recorded with the same care (the ledger's law).

## Phase 1 RESULT (2026-11-25 — acquisition, gate, owner decision, subset)

### Acquisition numbers (jobs: ganjoor 6b06780e1460ffe1d5e9e4c2 1h25m ·
### fawikisource 6b067816d0582cfbbefdbef5 105s · cc-fa-web 6b0678a31460ffe1d5e9e5ec 3h44m)

| source | rows in | kept | volume | register |
|---|---|---|---|---|
| ganjoor (API crawl, 246 poets) | 3,155,942 verses | **3,078,058** (dedupe 42,036; decontam 3,831; filtered 32,017) | ~1.1 GB shards | poetry (mostly unvocalized — see gate FAIL) |
| fawikisource (dump 5fb9ad73…, 47,719,980 B) | 84,176 pages | **35,692** (extract 37,143; redirects 482; short 1,425; script 26) | 8 shards | poetry + classical prose |
| cc-fa-web (CC-MAIN-2026-47, 500-segment stride) | 55,989 docs | **55,296** (dedupe 693) | 344 MB chars, 8 shards | modern web (OSCAR-fa SUBSTITUTE) |

The parent-gate layout mismatch (packaging under `ganjoor/raw/`) was fixed
by the staging job `wo94-ganjoor-stage` (6b06d2fdd91f621b93079334) —
package files copied up one level inside the bucket; the frozen gate and
the factory reference twin untouched (the fail-tree equivalence test in
`interscript-train tests/acquisition/test_gate.py` exercises the same
shape).

### Parent corpus gate — FAIL (falsification record, verbatim)

Job `wo94-acquisition-gate` (6b06d326d91f621b93079392), verdict.json
sha256 b20776e319e88011bb1d08c78c1eaeaeecba23b7e59c0d38ded2e3fc5973e7a5:

```
[gate] ganjoor: FAIL checks={"ratio_band_all_rows": true, "vocalized_share_min_0.30": false, "harakat_density_median_min_0.05": true, "degenerate_lt_1pct": true, "script_median_min_0.5": true, "persian_specific_all_present": true, "zwnj_present": true}
[gate] fawikisource: PASS checks={"rows_min_500": true, "degenerate_lt_1pct": true, "script_median_min": true, "persian_specific_all_present": true}
[gate] cc-fa-web: PASS checks={"rows_min_10000": true, "degenerate_lt_1pct": true, "script_median_min": true, "persian_specific_all_present": true}
[gate] VERDICT FAIL
```

The single failing check: ganjoor vocalized_share 0.054141 (166,649 of
3,078,058 rows, tgt≠src) vs the pre-registered 0.30 floor — the acquired
Ganjoor text is overwhelmingly unvocalized plain verse. No thresholds
were changed; the verdict stays recorded verbatim.

### Owner decision (2026-11-25): the vocalized-subset route

Carve the vocalized rows as the fas-poetry corpus; the plain verses stay
in the bucket as an UNSUPERVISED REGISTER (never deleted).

- **Extraction** (`prep_fas_ganjoor_subset.py`, job
  6b0701f4b6a90bbe997dd45e): membership = FAS_GATE_LAW haraqat
  U+064B–U+065F + U+0670 (the frozen gate's counting set — membership and
  gate density must measure one population; the narrower strip set
  U+064B–U+0652+U+0670 stays the src-derivation convention only).
  3,078,058 parent rows → **245,791 vocalized rows, 234 poets** (larger
  than the parent gate's tgt≠src count because law-set membership also
  counts hamza-carrier rows; the ratio band still holds per-row). All
  parent-invariant re-asserts dropped 0. Packaging contract mirrored;
  provenance = parent manifest sha 8d2aab248a03aca9… + the FAIL verdict
  sha + license CC BY-SA 3.0 carried over.
- **Fresh gate def** (`gate_fas_ganjoor_vocalized.py`, PRE-REGISTERED
  before the run; NOT an amendment): share == 1.0 by construction; ratio
  [1.0, 2.0] every row; true-median density ≥ 0.05 (law set); degenerate
  < 1%; Arabic-letter median ≥ 0.5; Persian-specific present; ZWNJ
  present; rows ≥ 100,000; sums re-hash clean.

### Subset gate — PASS (verbatim)

Job `wo94-ganjoor-vocalized-gate` (6b07023dd91f621b930847ea),
gate-verdict.json sha256 9e3395c14ea340dab6a0ec85da8082f99afa5e9145f53325d0a522cb4387d470:

```
[gate] {"vocalized_share_eq_1.0": true, "ratio_band_all_rows": true, "harakat_density_median_min_0.05": true, "degenerate_lt_1pct": true, "script_median_min_0.5": true, "persian_specific_all_present": true, "zwnj_present": true, "rows_min_100000": true, "sha256sums_clean": true}
[gate] stats={"rows": 245791, "vocalized": 245791, "degenerate": 0, "zwnj": 60057, "ratio_min": 1.0, "ratio_max": 2.0, "harakat_density_median_lawset": 0.05, "arabic_letter_fraction_median": 0.962963, "persian_specific_letters": {"پ": 46866, "چ": 61641, "ژ": 2277, "گ": 116211}}
[gate] VERDICT PASS
```

Corpus record: `corpora/fas-ganjoor.yaml` (train 215,067 = shards 0–6 /
held-out test 30,724 = shard 7; pins: SHA256SUMS cb42588ce2764766…,
manifest 81a25fe02e058fdc…, test shard 256c2349dc07b56a…). The campaign
quality evals stay the two pinned external sets.

### Phase 2 status

Training does NOT launch from this ledger update — the owner relays the
gate PASS before any GPU dispatch. The curriculum plan and the GPU table
above are the standing draft.

## Phase 2 — run-099 RECORD (2026-11-26): poetry HALVED+ on a clean eval;
## docs gate FAIL + a docs-gate INSTRUMENT finding — successor claim OPEN

Owner relayed the subset-gate PASS (2026-11-25); phase-2 authorized per
the plan. Dispatched the DIRECT-GOLD arm (the cc-fa-web weak-pretrain arc
stays parked per the launch-authority note): **run-099-fas-vocalized-sft**
(google/byt5-base; combined curriculum fas-ganjoor 215,067 + fas-dia
register, seed-42 shuffle; crown recipe verbatim — bs 16×2, MAXLEN 256,
3 epochs, 61,092 steps, lr 1e-4 cosine, bf16; step-1000 ckpts + resume;
greedy decode only; nan_skips 0). Job `rhtse/6b070d99b6a90bbe997df9e9`
(a100-large, detached, 16h; attempt-1 aborted pre-step at the eval-leak
kill — 5 register rows matched pinned eval sources; the fix enforces the
holdout law constructively: drop + record to dropped-rows.jsonl, hard
residual assertion).

### Verdict VERBATIM (verdict.json sha256 f3c48d1695eab43c1dc0e72063ca9061c8b87da8480c0fed0da0376a34a9b13b)

```
{"run": "run-099-fas-vocalized-sft", "backbone": "google/byt5-base",
 "curriculum": {"ganjoor": 215067, "docs": 436599},
 "epochs": 3, "steps": 61092, "nan_skips": 0,
 "docs_gate": {"rows": 9288, "cer_row_mean": 0.009334, "word_acc": 0.770457,
               "gate_row_mean_max": 0.007, "gate_pass": false},
 "poetry_eval": {"rows": 3497, "cer_row_mean": 0.151375, "word_acc": 0.078353,
                 "baseline": 0.3367, "register_arm_precedent": 0.1655},
 "ganjoor_val": {"tag": "ganjoor-val5k", "rows": 5000,
                 "cer_row_mean": 0.042028, "word_acc": 0.4724},
 "verdict": "FAIL"}
```

- **Poetry (the SOTA surface): 15.1375%** on the fully held-out pinned
  eval — vs the 33.67% baseline (2.2× better) AND below the 16.55%
  register-arm precedent, with NO eval exposure (the acquisition
  decontam + the run's holdout exclusion; ganjoor drops 0). The
  acquired-mass curriculum delivers more poetry than the seed-oversample
  arm did.
- **Docs hold: FAIL** — 0.9334% vs the 0.70% gate. Per the pre-registered
  kill criterion this run is a poetry specialist, NOT the successor; the
  crown `fas-vocalized-base-1.0` stays shipped.

### INSTRUMENT FINDING — the docs gate's comparability is broken

The r2 holdout dropped **9,270 docs rows**, and the decomposition probe
(`interscript-train holdout_decompose.py`, job
`rhtse/6b0750ded91f621b9308fe30`,
holdout-decomposition.json on the run dir):

```
{"total_dropped": 9270, "reason_counts": {"docs_test_src": 9264,
 "docs_test_tgt": 7911, "poetry_eval_src": 5}, "src_side_drops": 9264,
 "tgt_side_drops": 6, "docs_test_srcs_total": 9205,
 "docs_test_srcs_also_in_train": 1587,
 "docs_test_srcs_also_in_train_fraction": 0.172406}
```

**9,264 register-TRAIN rows carry INPUTS verbatim-identical to the
9,288-row docs test**; 1,587 of 9,205 unique test inputs (17.24%) appear
in the train split (many-to-one, ~5.8 train rows per test input). Every
lineage docs number (the 0.52% docs line, the 0.603% champion, the 0.70%
gate) was measured while a chunk of the gate set was visible in training;
run-099 trained WITHOUT those rows. The 0.9334% and the 0.603% are NOT
same-instrument numbers — the register cost of this run is overstated by
an unquantified memorization subsidy the prior champions enjoyed. The
poetry number carries no such confound.

### Disposition (owner queue — no further GPU until ruled)

1. **Re-baseline the docs instrument**: measure the shipped 0.603%
   champion (and run-099) on the contamination-controlled test (drop the
   1,587 exposed test inputs, or dedupe test-vs-train) — restores
   comparability; then re-read the 0.70% gate.
2. **The pre-registered proportion iteration** (the kill criterion's
   "seed-oversample proportion next"): re-run with the ganjoor share
   reduced (e.g. 0.330 → ~0.15) — same 40–80 GPU-h envelope, ~13 h.
3. **Successor naming stays unpicked** (fas-vocalized-1.0 remains the
   candidate id; nothing ships from run-099).

run artifacts: `isx-training:/run-099-fas-vocalized-sft/` (best/, 3 epoch
ckpts, step-* ckpts, verdict.json, dropped-rows.jsonl sha256
2b1c29fe9992ad52cc062d985f72e0be9f623fabfa52439970180c2000beb00c,
holdout-decomposition.json). Trainer + fix on `interscript-train`
`feat/fas-vocalized-sft` (c6f1523, 3a93274; f528d6f probe).

## Docs-instrument RE-BASELINE — the triangle (2026-11-26, disposition 1
## executed and approved-now; disposition 2 HELD for owner relay)

Instrument construction (owner-approved law, pre-registered before any
eval): the pinned 9,288-row docs test minus every row whose `src.strip()`
appears in the stripped-src set of the ORIGINAL pinned register train
split (445,869 rows, 383,923 unique stripped srcs) — src-side ONLY (the
memorization vector is the visible input), rows verbatim, no re-split.
**Clean instrument: 7,621 rows** (1,667 colliding rows removed; the
probe's 1,587 was the unique-input count — multi-row collisions account
for the difference). Built by `interscript-train build_docs_test_clean.py`
(job `rhtse/6b07529fb6a90bbe997e8057`; input pins verified in-job):
`isx-training:/wo94-docs-instrument/docs-test-clean/`,
docs-test-clean.jsonl sha256 61f2b760d5fc5b89569998cc8a2627588495cbdd00d1521d916d61bcc8341dc9.

### The triangle (identical greedy crown protocol on the SAME 7,621 rows)

| model | instrument | rows | cer row-mean | word acc |
|---|---|---|---|---|
| crown lineage champion (`run-078-fas-diac-base/best`, the shipped fas-vocalized-base-1.0 tier's torch source) | contaminated (historical, RESULTS/models.yaml) | 9,288 | **0.603%** | — |
| crown, clean | `wo94-docs-instrument/docs-test-clean` | 7,621 | **0.6527%** (0.006527) | 0.805537 |
| run-099-r2 best, clean | `wo94-docs-instrument/docs-test-clean` | 7,621 | **0.8526%** (0.008526) | 0.777457 |

eval-verdict.json sha256s: crown e4e6b3d08cc56423fb1391f799291f9850bb7f5bcf4b397f8112fde1a4b863b3;
run-099 35f9affd712b873b40aa6b26af66ecbc5574e6b255cfd5bb871742852b301863
(`run-078-fas-diac-base-best-clean-eval/` and
`run-099-fas-vocalized-sft-best-clean-eval/` on the bucket; jobs
`rhtse/6b075300b6a90bbe997e8129` 20m5s and `rhtse/6b075306b6a90bbe997e8141`
19m54s, l4x1, identical protocol/code).

### Reading (the triangle decides)

- **The contamination subsidy on the crown is +0.0497pp** (0.603 →
  0.6527 clean). Real, but small — the crown still clears the 0.70% gate
  on the clean instrument.
- **The run-099 docs regression is REAL on the clean instrument**:
  +0.1999pp clean-to-clean (0.8526 vs 0.6527). Contamination explains
  only ~0.05pp of the apparent gap; the remaining ~0.20pp is genuine
  register cost from the curriculum's poetry share (0.330).
- **Disposition 2 is therefore JUSTIFIED per the owner's rule**
  ("proportion iteration only if the regression is real on the clean
  instrument"): launch a proportion-iteration run — recommendation:
  ganjoor share 0.330 → **0.15** (between the register arm's ~0.073
  effective share and run-099's 0.330), same recipe otherwise, ~13 h
  a100 — **HELD for owner relay before dispatch** (per instruction; no
  training GPU until the triangle is seen). The clean instrument is the
  eval for that iteration, and the gate re-read on it: crown clean 0.6527%
  clears 0.70% — the gate stands as-is on the clean instrument for now;
  any redefinition stays an owner call.
- Successor naming stays unpicked; nothing ships.

## run-100 PRE-DISPATCH record (2026-11-26 — disposition 2 RELAYED)

The owner relayed the triangle and authorized the proportion iteration.
Pair numbers, derived BEFORE dispatch (trainer knob
`FAS_GANJOOR_SHARE`, interscript-train `feat/fas-vocalized-prop-iter`
9b82a48 off main 01a1b4b):

- **docs side stays COMPLETE**: 436,599 post-exclusion rows (the
  register anchor is never subsampled — same as run-099-r2).
- **ganjoor capped**: floor(436,599 × 0.15 / 0.85) = **77,046** rows,
  seed-42 sample over the SAME post-exclusion pool run-099 used —
  so PROPORTION is the only experimental delta (exclusions, recipe,
  holdout law identical).
- **combined: 513,645 pairs; ganjoor share 0.149999 (~0.15 by
  construction)**. vs run-099-r2: ganjoor 215,067 → 77,046 (−64%),
  poetry exposure per epoch ~77k verses.
- **The docs gate now measures on the CLEAN instrument**:
  `wo94-docs-instrument/docs-test-clean` (7,621 rows, docs-test-clean
  sha256 61f2b760d5fc5b89569998cc8a2627588495cbdd00d1521d916d61bcc8341dc9,
  pin-verified in-job), threshold UNCHANGED at 0.0070 row-mean; crown
  clean reference on the same instrument: 0.6527% (under gate).
- Gates for the completion report: docs clean-instrument row-mean
  < 0.70% (gate), pinned poetry 3,497 reported INFORMATIONALLY against
  run-099's 15.1375%, corpus val (ganjoor shard-7 5k) reported.
- Run: **run-100-fas-vocalized-sft** (new run dir; a100-large, detached,
  16 h, attempts 2, step-1000 ckpts + resume; fleet at dispatch: 0
  big-GPU jobs). ETA ~8–10 h (513,645/32 × 3 ≈ 48,154 steps at the
  measured ~4.1 it/s + evals).
