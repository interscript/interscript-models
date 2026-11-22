# Release notes — SOTA round 2026-11 (interscript-models)

> **DRAFT — PRE-STAGED. Do not publish until the urd-diac-2.0 gates
> resolve.** The heb-vocalized-plane-3.0 section is factual and final
> (that artifact shipped 2026-11-21). The urd-diac-2.0 section is a
> placeholder: both of its release-blocking gates are PENDING, and no
> sentence here may be read as a pass that has not happened. Fill the
> urd section from the WO92 ledger verdicts at ship time; if a gate
> fails, urd-diac-2.0 does not ship and the section records the
> negative instead.

Round scope: the two model launches of the 2026-11 SOTA round —
`heb-vocalized-plane-3.0` (shipped) and `urd-diac-2.0` (pending gates).
Facts below come from the WO92 ledgers
(`TODO.sota/92-heb-weak-pretrain.md`,
`TODO.sota/92-urd-16e-recovery-distill.md`), `docs/RESULTS.md`, and
`models.yaml`. Numbers are reproduced as recorded; no claims beyond
them.

---

## heb-vocalized-plane-3.0 — SHIPPED (2026-11-21)

Hebrew nikud diacritization, plane-factorized: ByT5-base encoder +
per-character nikud-class head, K=3 mask-predict greedy decode,
int8-dynamic ONNX, 416 MB (416,041,780 B,
sha256 `d6833fc79751ad39ee6a6a7d45632038997ec060955e46f77d39c1fdb848959a`).

### Measured result

| metric | value | protocol |
|---|---|---|
| Nakdimon test DER | **6.6078** | crown protocol — greedy, single-row, K=3 mask-predict, seq2seq_der, full 1,864 human-verified rows |
| previous shipped crown (`heb-vocalized-plane-2.0`) | 8.18 | same protocol |
| delta | **−1.57pp** | — |
| parity vs fp32 ONNX reference | +0.0549pp DER (gate ≤ 0.25pp), 600 samples | classification gate law (#459) |

### Training chain (the curriculum arc)

- **Stage 1 — run-093 weak-pretrain** (informational only, never
  gated): 1.5M deduped knesset-v6 weak units (Dicta machine labels —
  weak supervision only) COMBINED with the full gold train, 1 epoch.
  Stage-1 DER 9.1316, reported not gated (machine labels never gate
  quality).
- **Stage 2 — run-094 gold SFT** (owner-gated, launched on owner go):
  exact crown recipe resumed from the run-093 best, gold-only
  hebrew-v4 train, 4 epochs. DER 6.6078 — crown gate CLEARED
  (< 8.18). The s45 curriculum verdict reproduces on the plane
  lineage at ~2x its earlier effect (−0.88 DER on the custom stack).

### Quantization arm

int8-dynamic — the crown lineage's shipped mode — measured DER-neutral
(+0.0549pp vs fp32 on the 600-row eval600 slice). int8-static measured
+1.21pp DER on the same slice and is not shipped. Parity gates per the
classification law adopted in #459 (DER-delta ≤ 0.25pp); the
generation-artifact flip gate is untouched.

### Ship gates (all PASS, publish guard verdict PUBLISH READY, version 3.0.0)

export PASS (fp32 / int8-dynamic / int8-static); parity PASS under the
amended classification gate; conformance PASS (600 frozen vectors,
`conformance/heb-vocalized-plane-3.0-vectors.json`); regression PASS
(6.6078 improves on the registry best 8.18); license BSD-3-Clause.

### Published

- GitHub release: `releases/tag/heb-vocalized-plane-3.0`
  (`heb-vocalized-plane-3.0-int8-dynamic.zip` + `.sha256` sidecar)
- Index: **index-v16** (`models.yaml` entry serves the artifact;
  metrics anchored to `docs/RESULTS.md`)
- HF mirror: `Interscript/heb-vocalized-plane-3.0` (public, zip + card)
- Model card: `cards/heb-vocalized-plane-3.0.md` — data attribution
  per the Schedule D convention (knesset-v6 MIT weak-pretrain corpus;
  hebrew-v4 gold). The card records that the CLE schedule does not
  apply to this lineage (no CLE material in the Hebrew corpora).

---

## urd-diac-2.0 — PENDING GATES (not shipped)

> **Placeholder section — to be completed at ship time from the WO92
> ledger verdicts. Both release-blocking gates below are PENDING. This
> section must not be published, and no gate in it may be marked
> passed, until the gate records exist in the ledger.**

### Candidate (as recorded in the ledger)

ByT5-small distillation student (init `google/byt5-small`, lineage
recipe: 3 epochs, bs 16 x accum 2, lr 3e-4 cosine 200 warmup, bf16
autocast, MAXLEN 256) trained on teacher relabels of the public-lineage
`data-diacrit` train sources (573,130 rows in; 483,289 pairs after
dedupe in the run-093-class relabel). The CLE-adapted internal teacher
is INTERNAL ONLY and is never a release artifact; the student never
sees CLE text as input or target (8-word regurgitation guard, MUST
drop 0).

### Release-blocking gates — all PENDING

1. **Quality gate — PENDING.** Full-split raw CER ≤ 0.0377 on the
   11,940-row `data-diacrit` test split (WO37 protocol; the
   `urd-vocalized-1.0` champion bar).
2. **Clause 16(e) privacy gate — PENDING; runs after training.**
   Calibrated suite: reference-calibrated membership-inference
   (reference `google/byt5-small`; reference self-control exactly 0.5
   required or the probe is invalid; AUC tolerance ±0.05; success-rate
   tolerance 0.6), zero verbatim reproductions of >= 25 consecutive
   words (agreement Clause 18(d) threshold), extraction-by-prompting
   probe, WordNet vocab scan.
3. **Standard ship gates — PENDING.** Parity >= 500 samples in shipped
   decode mode, conformance fixtures, license strings, Schedule D
   attribution in card / NOTICE / release notes, compliance-certificate
   coverage, owner-stated version.

### Chain status (as of 2026-11-22, merged ledger records only)

Corrected relabel chain in flight: the first distillation corpus was
invalidated by a relabel input bug (recorded negative — run-094
QUALITY MISS, CER 3.2066 vs bar 0.0377, on a corpus whose targets were
degenerate from the input bug; the 16(e) spend was withheld, nothing
published); the corrected chain (semantic-invariant relabel smoke, then
full regeneration, then the corpus review gate, then the student
retrain) is recorded in
`TODO.sota/92-urd-16e-recovery-distill.md`. Latest merged record:
semantic-invariant smoke launched, run-095 unit plan recorded
(2026-11-21). Fill this section from the verdict records when the gates
run.

### Version

`urd-diac-2.0` — the version word is stated by the owner at ship time
per the ship-gate law; no version is picked by the campaign.

### Schedule D attribution (ships with urd-diac-2.0 when it ships)

Per Clause 4 and Schedule D of the CLE-Ribose license agreement — full
resource citation (model card, README, documentation):

> CLE Urdu Digest Corpus 1M (International Package), Catalogue No.
> CLE12T003; CLE Urdu WordNet (International Package), Catalogue No.
> CLE12L001. Center for Language Engineering, Al-Khawarizmi Institute
> of Computer Science, University of Engineering and Technology,
> Lahore, Pakistan.

Standard credit line (NOTICE / credits / release notes):

> Linguistic resources provided by the Center for Language Engineering
> (CLE), Al-Khawarizmi Institute of Computer Science (KICS), University
> of Engineering and Technology (UET), Lahore, Pakistan.

Compliance records (16(e) testing records, compliance certificate,
retention per Clause 17(d) — 2 years post-expiry) are maintained in the
access-controlled licensed repository (`interscript/pk-cle-urdu`,
PRIVATE). The 16(e) verdict is PENDING; the certificate covers this
release only if the artifact ships.

---

## Channel notes

- Index state at drafting: index-v16 serves `heb-vocalized-plane-3.0`.
  The round's runtime index bump (index-v17) exists only as staged
  branches on the four runtime repositories
  (`pin/index-v17` in interscript-rs / interscript-ruby / interscript-ts
  / interscript-py) and is merged only when urd-diac-2.0 ships.
- Distribution channels unchanged: GitHub Releases primary (zip +
  sha256 sidecars), HF mirror; raw.githubusercontent.com is never a
  data channel.
