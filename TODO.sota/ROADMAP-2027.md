# SOTA-2027 language roadmap — survey-grounded ranked plan

Status: **PLAN** (survey round 2026-11-25) — every language below gets its
own WO before execution; the owner gates each launch, version, and license
waiver. This file is the survey record: what the org holds, what the
public record shows, and the ranked order that falls out of both.

Inputs: `corpora/` + `corpora/PROVENANCE.md` (full corpus census,
2026-11-25), `models.yaml` (index-v17), WO89 Track B matrix,
WO56 Plane B targets, WO66 Persian registers, WO92/93 method ledgers,
`cards/`, `docs/RESULTS.md`, urdu-dev clause-16(e) records, and a
bounded public-record scan for the candidate languages.

## 0. The two validated method templates (both shipped)

Every candidate below is scored against these — they are the house
recipes, each with shipped evidence:

1. **CURRICULUM** — large weak-pretrain on machine-labeled data, then
   gold SFT fine-tune. Evidence: `heb-vocalized-plane-3.0` (shipped
   2026-11-21): 1.5M deduped knesset-v6 units (Dicta machine labels,
   MIT) weak-pretrain → gold SFT on hebrew-v4; Nakdimon DER 8.18 →
   **6.6078** (−1.57pp), 2× the earlier s45 curriculum effect. Law:
   machine labels are **weak supervision only** — they never gate
   quality and never enter eval (WO92).
2. **CLEAN-ROOM DIRECT-GOLD** — train directly on license-clean,
   verified-lineage gold pairs; calibrated Clause 16(e) matched-split
   gate (amended methodology, urdu-dev#23–#26) as the memorization
   gate. Evidence: `urd-vocalized-2.0` (shipped 2026-11-24): ByT5-small
   on 573,130 sha-pinned public-lineage gold rows, full-split CER
   **3.641**, beating the 3.74 champion. The CLE-DAPT path was
   **falsified and retired** — the MIA measured domain specialization,
   not memorization (#474/#475/#477).

Templates that are **banked negatives** (never retry as written):
noisy-student relabel on correlated teachers, self-silver as an ID
lever (moves OOD, pays ID — WO17), LLM teachers (registry law), RL
distillation, beam decode on flat byte students.

## 1. What the templates do NOT change — the Arabic carry-over

The Arabic line (`ara-vocalized-*`, the rababa lineage) predates both
templates and already holds a shipped champion: `ara-vocalized-2.0`
(ByT5-large-class 580M; SadeedDiac-25 full-set DER **2.29**, #1
dedicated model vs the 1.39 frontier LLM; trained on human-vocalized
classical running text (Tashkeela lineage, GPLv2 training-clear) plus a
news-domain adaptation stage over a morphology-auxiliary curriculum).
The curriculum template's Arabic analog — machine-labeling undiacritized
mass with our own shipped model — is exactly the self-silver/noisy-
student family already measured **negative** for ID (WO06, WO17, WO26);
the oracle-relabel capture path (WO39) remains the one live arm. So no
new-language inference: Arabic keeps its WO89 row (DER < 2.0 / WikiNews
WER < 8, VRR) and its existing doctrine. Urdu keeps WO65 (CER < 3; the
run-097 direct-gold arm is the live continuation).

## 2. Ranking axes (readiness = all five, weighted)

1. **Need** — a script that omits short vowels in running text (abjad
   behavior) or an unvocalized-input convention with a shipped/Track-A
   companion map.
2. **In-org data** — corpus entries already in `corpora/` or staged in
   the training bucket.
3. **Acquisition path** — identifiable, licenseable public sources
   (verified, not assumed).
4. **Eval availability** — a held-out human-vocalized gold eval, or a
   concrete plan to build one (never machine-labeled).
5. **Method fit** — which template runs, and what is missing to run it.

## 3. The ranked plan

| rank | language (line) | need | in-org data | acquire | eval | method fit | effort (GPU-h class) |
|---|---|---|---|---|---|---|---|
| R1 | Persian — register expansion (`fas-vocalized`) | measured | CC0 446k | dossier ready | both evals pinned | direct-gold (+ seed-oversample) | 40–80 |
| R2 | Ottoman Turkish (`ota-vocalized`, new line) | extreme | none | public corpora exist, licenses UNVERIFIED | build | hybrid (curriculum + direct-gold) | 100–200 |
| R3 | Jawi / Malay (`jawi-vocalized`, new line) | heavy | none | Quranic-Jawi mining, UNVERIFIED | build | clean-room direct-gold | 60–120 |
| R4 | Pashto (`pus-vocalized`, new line) | real | none | undiacritized mass only | build (annotated) | direct-gold after annotation | 50–100 (+ human lead time) |
| R5 | Sindhi / Punjabi Shahmukhi (parked pair) | moderate | none | none identified | none | blocked on gold | — |

### R1 — Persian register expansion (`fas-vocalized` line)

- **Need:** measured, not assumed. `fas-vocalized-base-1.0` holds
  **CER 0.603** (greedy, 9,288-row docs split, row-mean) but scores
  **33.67%** on the pinned Ganjoor vocalized-poetry eval (3,497 verses,
  79 poets) — a ~56× register gap. The proven register arm
  (fine-tune + 3,497-verse seed ×10) halved poetry CER to **16.55%**
  while holding the gate (0.69%) — WO66.
- **Data inventory:** in-org — `fas-dia` 445,869 train / 9,288 test,
  **CC0-1.0 verified** (the only diacritization corpus that clears the
  license gate outright). To acquire — the WO66 dossier is already on
  the table: Ganjoor (CC BY-SA 3.0 site-stated), fa-Wikisource
  (CC BY-SA 4.0), OSCAR-fa (cc-shaded tooling; filters needed).
- **Eval:** two pinned evals already exist (docs split CC0; Ganjoor
  eval sha 94f318f688b556be). Scale-up adds a fa-Wikisource
  classical-prose slice and a colloquial register slice, all
  held-out-from-training.
- **Method fit:** clean-room direct-gold — every vocalized Persian
  source is human-authored text, so no weak-pretrain stage is wanted.
  The seed-oversample recipe is proven; scale it with the acquired
  vocalized mass (10× seed → mass oversample).
- **Risks:** attribution/share-alike on the weights (CC BY-SA derived
  corpus → weights-dependency note, same lane as the tashkeela
  copyleft note); OSCAR-fa quality filtering (machine noise — keep it
  out of eval, treat as weak-pretrain mass only if used); the Arabic-
  loan vocalization scar (WO66 probe).
- **Effort:** ~40–80 GPU-h (a100-class): corpus build + 2–3 fine-tune
  arms + register-stratified eval + ship chain. The highest-readiness
  item on the board; owner source picks are the only gate.
- **Target:** WO66/B5 — hold **CER < 0.7 across registers**, published
  register-stratified numbers.

### R2 — Ottoman Turkish (`ota-vocalized`, new line)

- **Need:** the extreme case — Ottoman orthography omits short vowels
  entirely and layers Arabi-i Osmani letter ambiguity on top; the
  vocalization model is also the composition base for the shipped
  Ottoman romanization track (WO89 names ottoman a future D+M
  companion line; the DIN 31635 Ottoman section is references-only).
- **Data inventory:** nothing in-org. Public record: an active
  research line exists (OttomanNLP GitHub org and HF datasets; SIGTURK
  2024 clean-text-corpus work; OttoBench; arXiv 2501.04828
  foundations; OTA-BOUN treebank) — but **no license state is
  verified** for any of it. Every candidate source enters the survey
  as `UNVERIFIED` and stays out of training until read.
- **Eval:** must be built — a small human-vocalized gold eval
  (vocalized editions of public-domain Ottoman prose) is the
  prerequisite for any gate.
- **Method fit:** **hybrid** — this is the natural second deployment of
  the curriculum template: a machine-labeled weak pass over large
  undiacritized Ottoman mass (weak supervision only, knesset law) →
  gold SFT on the verified vocalized pairs. If no licensed machine
  labeler exists, clean-room direct-gold on the gold set alone is the
  fallback (small-data regime, ByT5-small class per the Urdu
  precedent).
- **Risks:** license negotiation is the wall (third-party datasets may
  be research-only); orthographic-era variance (classical vs late
  Ottoman conventions) — eval must be register-stratified from the
  start; do not let transliteration-era romanization tables masquerade
  as vocalization gold (bibliographic vs phonological — the ISC
  two-families lesson).
- **Effort:** ~100–200 GPU-h class including weak-pretrain arms;
  dominated by non-GPU acquisition + eval construction.
- **First WO:** a license-and-availability census of the OttomanNLP /
  OttoBench corpora (zero-GPU), then the gold-eval build.

### R3 — Jawi / Malay (`jawi-vocalized`, new line)

- **Need:** heavy — Jawi running text omits vowels aggressively; the
  Track A side is already paved (WO89 lists Malay (Jawi) D+M and
  Jawi-Pegon in ALA-2; the WO17-round jawi pilot landed the
  transliteration map), so the vocalization-as-composition pair has
  its deterministic half.
- **Data inventory:** nothing in-org. Public record: **no dedicated
  diacritized-Jawi corpus surfaced** in the survey; the plausible
  path is mining fully-vocalized Jawi Quran editions (public-domain
  religious text — the Tashkeela pattern for Arabic), which must be
  verified before anything is staged.
- **Eval:** build from the mined source with strict held-out rules;
  a second, non-Quranic eval slice is mandatory before any SOTA claim
  (register coverage).
- **Method fit:** clean-room direct-gold once mining verifies.
  Curriculum has no licensed weak source here yet.
- **Risks:** Quranic register dominance (a Quran-only model is not a
  Jawi model — single-gold DER undercounts; VRR tracking applies);
  regional orthographic conventions; mining provenance discipline
  (sha256 pins from fetch, the heb-knesset pattern).
- **Effort:** ~60–120 GPU-h after the mining gate passes.
- **First WO:** mining-verification probe (zero-GPU): does a public,
  redistributable, fully-vocalized Jawi Quran text exist, and how many
  unique vocalized units does it yield after dedupe?

### R4 — Pashto (`pus-vocalized`, new line)

- **Need:** real — Pashto writes long vowels as letters and omits
  short vowels as diacritics in running text; the ALA-2 Pushto table
  plus BGN/PCGN Pushto give the deterministic companions.
- **Data inventory:** nothing in-org. Public record: large
  **undiacritized** monolingual mass exists (e.g., a 1.5B-word
  community corpus on HF), but **no diacritized gold corpus
  surfaced** — the clean-room template has no seed. This is the
  binding constraint.
- **Eval:** none exists; a human-annotated gold eval is the
  prerequisite (annotators are the lead-time item).
- **Method fit:** direct-gold **after** annotation; the undiacritized
  mass is only useful as curriculum weak-pretrain if a licensed
  machine labeler appears — never self-labeled for eval.
- **Risks:** the annotation campaign itself (quality control, the
  urdu relabel-input lesson: semantic invariants at load time);
  dialect split (Southern/Northern) must be declared per split.
- **Effort:** GPU modest (~50–100 GPU-h once data exists); human
  annotation lead time dominates — **start the eval-slice track in
  parallel with R1** even though training ranks fourth.
- **First WO:** eval-slice design + annotator sourcing (zero-GPU).

### R5 — Sindhi / Punjabi Shahmukhi (parked pair)

Both are ALA-2 rows with a real but moderate omission need. Parked
pending a licensed gold source: no diacritized corpus surfaced for
either in the survey; Shahmukhi's vocalization conventions are loose
enough in running text that "gold" is unstable (the conventions
problem, not the data problem). Revisit on any of: a community
corpus offer (the 2-YAML intake path, B8), a licensed source, or a
Track A batch that surfaces companion demand.

## 4. In-org corpus census (2026-11-25) — every entry

| corpus | lang / task | train rows | eval rows | license state |
|---|---|---|---|---|
| `heb-knesset-weak` | Hebrew diac, machine-labeled | 2,667,695 (2.67M survive dedupe) | — (weak never gates) | MIT verified |
| `hebrew-v4` | Hebrew diac gold | 50,433 | 1,864 human-verified | mixed-internal, owner-reviewed |
| `urd-dia` | Urdu diac gold (public-lineage) | 573,130 | 11,940 | unresolved → ship-with-note (owner review 2026-10-18) |
| `urd-g2p-dict` | Urdu g2p | 609,580 | 12,699 | non-commercial — BLOCKED (owner decision #1) |
| `qcri-wiki` | Arabic diac | 32,834 articles (~5M words) | — | no license found — BLOCKED (owner decision #2) |
| tashkeela (r8-mined) | Arabic classical | (r8-mined chain, not registry-pinned) | — | GPLv2 — clear for training; copyleft note on weights |
| `fas-dia` | Persian diac | 445,869 | 9,288 | **CC0-1.0 VERIFIED CLEAR** |
| `khm-dict` | Khmer translit | 74,983 | 326 | LGPL-2.1 |
| `khm-latn` | Khmer Latin | 16,120 | 895 | UNVERIFIED — owner-gated |
| `tha-phonemic-v3` | Thai g2p | 130,906 | 1,223 dev / 11,119 | Apache-2.0 |

Reading: the org's only license-clean diacritization corpus is Persian
— which is one reason R1 ranks first. Everything else on the board
starts from acquisition.

## 5. Rejected / deferred candidates

| candidate | reason |
|---|---|
| Uyghur (Arabic script) | vowels written as letters — no omission need |
| Kazakh (Arabic script) | same — vowel letters in standard orthography |
| Kurdish Sorani (ckb) | most vowels written as letters; residual omission need low |
| Yiddish | standard orthography is largely phonemic; no vocalization gap |
| Modern Syriac (aii/syc) | WO89 defers the M companion; corpus base too thin today |
| Judeo-Arabic | real need, no identified licensed source; revisit with R2's census method |
| Ottoman as *map-only* | the D table ships, but unvocalized real-world input is the norm — map alone is the known D+M gap, hence the R2 line |

## 6. Recommended order and dependency graph

```
R1 fas registers ──► (proves register-stratified eval doctrine)
R2 ota census ──► ota gold eval ──► ota weak-pretrain ──► ota gold SFT
R3 jawi mining probe ──► (gate: verified public source?) ──► jawi direct-gold
R4 pus eval-slice track (HUMAN lead time — start with R1) ──► pus direct-gold
```

- **Launch order:** R1 first (only owner gate is the source picks);
  R2 and R4 first-WOs are zero-GPU censuses/eval-design and start in
  parallel; R3's mining probe likewise. Training GPUs follow the
  census results, ≤ 2 concurrent big-GPU jobs (fleet law).
- **Promotion rule:** if R3's mining probe verifies a source while R2's
  license negotiation is still open, R3 promotes ahead of R2 — data in
  hand beats data in negotiation (the Urdu lesson: clean-room shipped
  where the licensed path stalled).
- **2027 scoreboard:** fas register-stratified numbers published; ota
  gold eval + first gated model; jawi/pus gated on their probes.
  All under the standing laws: no LLM teachers, UNVERIFIED blocks
  publish, single-row greedy decode contract, ByT5 byte-table law,
  data channel = GitHub Releases + sha256, versions owner-stated.

## 7. Acceptance

- Each ranked line opens its own WO before any GPU spend.
- Every acquisition claim in this file carries its verification status;
  nothing UNVERIFIED enters training or eval.
- Negatives recorded with the same care (the ledger's law).
