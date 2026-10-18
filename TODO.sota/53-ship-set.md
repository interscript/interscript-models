# WO53 — The ship set (assembled 2026-10-18; publish owner-gated)

Every lane, every gate, every artifact — the complete release picture.
The publish guard (`pipeline/publish.py`) makes an incomplete release
structurally impossible; this file is the human-readable counterpart.

## Lane-by-lane

| lane | candidate artifact | quality (verified) | parity | conformance | license | status |
|---|---|---|---|---|---|---|
| urd-diac | urd-diac-base-1.0-fp16.zip (1.35GB) | gate CER 0.0357 row-mean | ≡ torch, 300/300 rows (WO51) | runtime 12/12 byte-exact | **GATED-1** | ready pending license |
| urd-g2p | run-059/best export | 0.16 CER row-mean | cleared by WO51 contract | fixtures pending ship | **GATED-1** | ready pending license |
| ara-diac | r6/r7 canonical (shipped 1.1) | WER 2.58 / DER 1.53 (r6 verified) | int8 zipcheck GOOD | plane family | **GATED-2** | stage-2 may improve; relabel resume9 consolidating (C-lev fix) |
| fas-diac | run-077/best | 0.603% row-mean / 0.777% corpus, word-acc 82.33% | pending export | fixtures pending ship | CLEAR (CC0) | **GATED-4** (gate value) |
| he-* | — | — | — | — | no-license sources | **GATED-3** (data supply) |
| tha-* | shipped small tier | per WO08 contract | plane family | existing | clear | closed |

## The owner-gated queue (exactly what blocks shipping)

1. **urd-g2p weights** — training data verified **non-commercial**
   (humair025/urdu-g2p-dictionary, HF card). Options: ship
   research-only, or retrain on an open dictionary first.
2. **ara-diac (qcri-wiki)** — QCRI's Qatara repo carries **no license**
   (default copyright). Options: contact QCRI for explicit terms, or
   rebuild the ara lane on Tashkeela-derived data (GPLv2 — weights
   redistribution implications then apply).
3. **urd-dia sources** — the paper's corpus mixes `mahwizzzz` +
   `humairmunirawn`; **no licenses found on either**. Options: contact
   the paper authors, or rebuild from licensed sources.
4. **fas-diac gate value** — the docs' 0.52% is **proven
   unreproducible** (5-arm elimination; WO47). Accept the verified
   ceiling (run-077/best, 0.603%/0.777%) and re-anchor the recipe gate,
   or commission the corpus-rebuild arm (~18% of raw rows were dropped
   by the derivation) before shipping.
5. **Versions + final go** — per standing law, version numbers are the
   owner's decision. Name them (e.g. `urd-diac-base-1.0`,
   `fas-diac-base-1.0`) when saying go; the publish guard enforces the
   rest (explicit semver, green gates, conformance fixtures).
6. (HE supply asks — micsell no-license and QCRI-contact drafts sit in
   TODO.sota/43/17, ready to send whenever you choose.)

## Machine-gated (not owner)

- **stage-2 (ara oracle distill)**: resume9 running — all three arms
  complete; consolidation now uses the C levenshtein (the pure-python
  one needed ~56h vs the 23h timeout — the loop that killed resume6/8).
  `RELABEL_DONE` → stage-2 launch through the spine runner.

## Non-blocking backlog (recorded, not holes)

Housekeeper (ckpt pruning / dead-repo inventory) · exporter
attention-mask option for batched serving (WO51 remedy (b)) ·
conformance coverage grows with each shipped artifact ·
src/gpu/modal_* deprecation (owner-flagged; nothing deleted) ·
runtime default index URL re-point at next runtime release.

## OWNER DECISIONS APPLIED (2026-10-18)

1. urd-g2p → **ship RESEARCH-ONLY** (non-commercial upstream noted on
   the card). Waiver recorded in corpora/urd-g2p-dict.yaml.
2. ara-diac → **ship with dependency note** (weights depend on the
   QCRI upstream license). Waiver in corpora/qcri-wiki.yaml.
3. urd-dia → **ship with dependency note** (weights depend on the
   original data license). Waiver in corpora/urd-dia.yaml.
   → encoded as schema-level `license_review` records (#304): the
   license string is never loosened; unwaived restricted sources fail
   schema validation. Registry validates 0 problems / 0 blocked.
4. fas-diac → **improvement arm launched**: run-080-fas-oracle (the
   WO39 multi-arm oracle on fas — arms 076/077/079, 120K subset,
   ~22h). If stage-2 continue-train beats 0.603% row-mean, that
   becomes fas-diac-base-1.0; otherwise the RC ships as-is.
5. Versions delegated ("reasonable numbers"): urd-diac-base-1.0 ·
   urd-g2p-base-1.0 (research-only) · ara 1.1 line (dependency note)
   · fas-diac-base-1.0 on improvement-arm verdict.

Ship flow next: repack → GH Release + sha256 → models.yaml entry →
index-vN bump → HF mirror → cards with the dependency/research notes.
