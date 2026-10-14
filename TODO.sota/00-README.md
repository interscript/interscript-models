# TODO.sota — 2026 SOTA campaign (client-usable quality)

Derived from the 2026-10-05 SOTA sweep (Arabic / Hebrew / Thai).
Goal: close the measured gaps to the 2026 frontier on all three
languages while keeping every artifact client-usable (int8, sha-verified,
multi-runtime, versioned).

## Substrate: HF (NOT Modal)

All training and eval jobs run on **Hugging Face Jobs** (`hf` CLI, v1.26+):

```bash
hf jobs run --flavor a100-large -d \
  -v hf://datasets/Interscript/hebrew-v4:/data:ro \
  -v hf://buckets/Interscript/isx-training:/ckpt:rw \
  python:3.12 python train.py
```

- Datasets: `hf://datasets/Interscript/<name>` (mounted read-only).
- Checkpoints/artifacts: `hf://buckets/Interscript/isx-training` (read-write).
- Detached always (`-d`); poll via `hf jobs ls` / `hf jobs logs`.
- Modal is retired for compute. It may be used ONLY to export corpora
  off Modal volumes during the one-time migration (#44).

## Standing rules that shape this campaign

- **NO LLM TEACHERS** (memory law, 2026-08): never use Claude/GPT/
  Gemini/any LLM as a label source for haraqat/niqqud/Thai IPA.
  WO06 is therefore noisy-student/self-ensemble — NOT the
  "LLM-ensemble teacher" phrasing used in the sweep notes.
- Versions/releases/cards/index are owner decisions at ship time;
  specs define gates, not version numbers.
- Data channel for shipped artifacts stays GitHub Releases + sha256;
  HF dataset repos here are TRAINING inputs, not the shipping channel.
- PRs only; no tags without explicit instruction.

## Work orders

| WO | File | Priority | Depends | Status |
|----|------|----------|---------|--------|
| 01 | 01-wikinews-multiref-reconciliation.md | P1 | — | DONE (RESULTS #257) |
| 02 | 02-user-diacritics-preservation.md | P1 | — | DONE (py#28, ruby#801) |
| 03 | 03-thai-hybrid-latency.md | P1 | — | DONE (py#31, RESULTS #258) |
| 04 | 04-hebrew-plane-scaleup.md | P2 | #44 | gate CLEARED — artifact DER 8.18 (int8, runtime protocol); release pending owner version |
| 05 | 05-external-benchmarks.md | P2 | 01, 07 | DONE (RESULTS #259; MILIM awaiting release) |
| 06 | 06-arabic-r8-noisy-student.md | P2 | #44 | CLOSED — dose-response mapped (RESULTS wave 2); teacher-quality lesson became the WO31 pattern |
| 07 | 07-nikud-ipa-rule-layer.md | P3 | — | DONE (py#29, py#30) |
| 08 | 08-thai-small-tier.md | P3 | #44 | CLOSED — see 12 (sub-10MB tier negative) |
| 09 | 09-hebrew-audio-pseudolabel-probe.md | P3 (parked probe) | — | DONE as parked probe (script only) |
| 10 | 10-heb-plane-2-release.md | P1 | 04 | DONE (release, index-v9, 3 pin bumps, card, golden, HF mirror #28) |
| 11 | 11-arabic-r8-chain.md | P1 | — | CLOSED — r8a/b/c/d verdicts in RESULTS waves 2-4; specialist shipped |
| 12 | 12-thai-tiny-contract.md | P2 | — | NEGATIVE (caveated) — PER 2038%; sub-10MB closed |
| 13 | 13-thai-lexicon-release.md | P2 | 03 | DONE (tha-lexicon-kaikki-1.0 + sha, CC BY-SA) |
| 14 | 14-ts-plane-port.md | P2 | — | DONE (ts#99/#100/#101, CI leg models#265) |
| 15 | 15-api-edge.md | P2 | 14 | DONE (api#29: edge-first /v1/infer, kind in index) |
| 16 | 16-parking-lot.md | — | — | parked (not now) |
| 17 | 17-arabic-register-closure.md | P1 | 11 | CLOSED — register-specialist doctrine; specialist shipped; numbers superseded by WO35 corrected protocol |
| 18 | 18-parity-runs.md | P1 | 10 | DONE via WO10+WO23 — golden attached, 3-leg parity GREEN |
| 19 | 19-lexicon-loader.md | P2 | 13 | DONE (py#33) |
| 20 | 20-hebrew-large-arm.md | P1 | 04 | NEGATIVE — 8.48 vs base 8.18; base stays shipped |
| 21 | 21-arabic-plane-transfer.md | P2 | 17 | VERDICT: OOD −3.14 WER, ID +1.66 (Pareto) — specialist candidate staged |
| 22 | 22-runtime-releases.md | P1 | 14 | PREPARED — owner-gated versions |
| 23 | 23-ort-alignment.md | P1 | 18 | CLOSED — characterization complete; 3-leg parity GREEN at documented bound |
| 24 | 24-verdict-wave.md | P1 | 17 | CLOSED — all verdict waves recorded in RESULTS |
| 25 | 25-ar-news-specialist.md | P1 | 17 | VERDICT: OOD 10.13/8.98 (crown), ID 5.50; export staged |
| 27 | 27-ar-large-id-arm.md | P1 | — | NEGATIVE — 2.5765 parity with r7; capacity closed on AR too |
| 28 | 28-oracle-complementarity.md | P2 | — | CLOSED — ceiling 96.78 real; naive voting catastrophic |
| 30 | 30-heb-learned-ipa-v0.md | P1 | 09 | NEGATIVE — CER 1.18; ASR teacher is the bottleneck |
| 31 | 31-heb-phoneme-asr-v1.md | P1 | 30 | stage 2 CLOSED at 0.546 nCER (capacity negative, metric/conventions fixed); rules 0.2393 stands; ivrit.ai $500 = owner decision |
| 32 | 32-matched-architecture-arms.md | P1 | 17 | BiLSTM 14.30 refuted; run-033 10.78/9.16 gate-MISS — specialist dominates; successor = word-channel class |
| 26 | 26-heb-noisy-student.md | P1 | 04 | NEGATIVE — 8.72 vs 8.18; all three text levers closed |
| 33 | 33-lexicon-disambiguator.md | P1 | 17/32 | NEGATIVE — 18.07/11.44; word-only can't diacritize OOV |
| 34 | 34-hybrid-word-char.md | P1 | 32/33 | CLOSED — hybrid 13.53, fastText 13.59, vcd ±0, oracle 0.71 (all old-protocol; see 35) |
| 35 | 35-alternate-protocol.md | P1 | 34 | arm 2 PASS — large-strip 3.5983/1.4715 NEW BEST (0.90 to frontier); 1.1+1.2 staged; 3-way oracle ceiling 2.9484 |
| 36 | 36-ivrit-scale.md | P1 | 31 | e12 CONVERGED 0.4462 (+8ep bought nothing) — undertraining refuted; residual structural; label-filter arm next, teacher v4 last resort |
| 37 | 37-portfolio-sota.md | P2 | — | REFERENCE NUMBERS PUBLISHED — fas 1.47 / urd-diac 3.86 / urd-g2p 15.78 CER (n=3000, protocol+artifacts sha'd); urd-g2p = the one future arm |
| 38 | 38-urd-g2p-base.md | P1 | 37 | GATE PASS 0.1565 < 0.1578 (12.7K full split); export+parity RUNNING; staged urd-g2p-base-staged |
| 40 | 40-heb-teacher-reeval.md | P1 | 36 | VERDICT 0.1382 TRUE (was 0.87 bug) — student-bottleneck; teacher v4 demoted to last resort |
| 39 | 39-ar-oracle-distill.md | P1 | 35 | RUNNING — stage-1 relabel on l4x1 (chunk-resume, 9 tests green); stage-2 continue-train queued on a100 |
| 41 | 41-urd-diac-base.md | P2 | 38 | STAGED — script in bucket; last in a100 queue (after WO39 stage 2) |
| 42 | 42-heb-label-filter.md | P2 | 40 | STAGED (conditional — fires if e12 misses; self-consistency filter, 10 GPU-h) |
| 43 | 43-heb-gold-nikud.md | P2 | 36/42 | BLOCKED — dataset has NO license (all-rights-reserved default); owner-to-owner ask to micsell required |
| 44 | 44-release-plan.md | P1 | owner | PROPOSAL — naming law + publication order + decisions D1-D5 (owner states, I execute) |
| 45 | 45-large-static-int8.md | P2 | 44 | PARKED — 3 toolchain walls (ORT-static, fp16-refuse, torch-dynamic trace); large tier = measurement; artifact needs external-data-in-zip (runtime-arch) |
| 46 | 46-int8-artifact-remediation.md | P1 | 44 | ACTIVE — zipcheck under test; 1.0 fp32 re-export queued; release-asset replacement path defined |
| 47 | 47-fas-diac-release.md | P1 | — | NEW GAP FOUND — fas-diac trained at 0.52% CER, NEVER released; checkpoint on a Modal volume; probe queued |
| 48b | (48 ext) | P2 | 48 | he-wiki DUD (1,244 pairs); pivot spec'd: he.wikisource CC BY-SA (10-50K gold pairs), queued behind fleet drain |
| 49 | 49-ur-lexicon-probe.md | P2 | 38 | probe RUNNING (cpu) — lexicon-oracle CER vs 0.1565 gate decides the runtime lexicon layer |

## Schedule

Wave 1 (local, days): WO01, WO02, WO03, WO07 + infra #44.
Wave 2 (HF training, launched together): WO04 (a100-large), WO06
(a100-large), WO08 (l4x1) — run concurrently, watch via `hf jobs ls`.
Wave 3: WO05 tables after 01+07 land; WO09 probe only.

## Path-to-success graph + SOTA matrix (2026-10-14, post-WO38/39)

```
ARABIC ── WikiNews-2024 multiref (OOD news, WER/DER, first-alt protocol)
  ladder: shipped 4.10 > base-strip 4.00 > large-strip e6 **3.5607/1.4588**
  frontier 2.70 → gap 0.86; 3-way oracle ceiling 2.9861 (routing closed <2)
  → WO39 ORACLE-DISTILL (the capture path): relabel 300K QCRI rows with
    per-row best arm → continue-train e6 → gate < 3.5607, stretch <= 2.70
  runtimes return primary choice (py#35 / ts#108 / ruby#805)

ARABIC ── SadeedDiac-25 (ID): r7 2.2864 [BEST dedicated]; specialist
  5.4814 first-alt rescored — ID was never inflated (artifact OOD-only)

HEBREW ── nikud DER: 8.18 crown (2x runner-up); all text levers closed
HEBREW ── g2p CER (the open frontier): rules 0.2393 · ReNikud 0.0244
  audio chain (WO36) now END-TO-END CONSISTENT: v3-teacher labels 200h
  → student 4ep nCER 0.4415 (first valid number; beat FLEURS-student 0.546)
  → e12 +8-epoch continuation RUNNING (undertrained hypothesis)
  → if miss: label filter, then 500h slice (building now) → teacher v4
URDU ── g2p: run-059 base GATE PASS 0.1565 < 0.1578 (1.0) on full 12.7K
  split; int8 export + torch/ORT parity in flight; staged
  urd-g2p-base-staged (owner names release)
THAI ── PER: hybrid 0.1478 @0.73ms [crown]
FAS ── g2p 1.47 full-split [anchor beaten 25x]
CLIENT SURFACE: 3-runtime parity ✓ · preserve ✓ · edge /v1/infer ✓
  index-v10 · 29+ HF mirrors
```

| axis | ours | 2026 frontier | status |
|---|---|---|---|
| AR in-domain DER | 2.2864 | 1.39 (LLM API) | #1 dedicated (LLM = no-teacher law) |
| AR OOD multiref WER | **3.5607** (DER 1.4588) | 2.70 | 0.86 gap → WO39 distill READY |
| HE nikud DER | **8.18** | — (we lead) | crown held |
| HE g2p CER | 0.4415 (audio, e12 running) | 0.0244 (ReNikud) | OPEN — undertrained→scale levers queued |
| UR g2p CER | **15.65** full-split (base) | — | GATE PASS; export+parity in flight |
| UR diac CER | 3.77 full-split | — | shipped |
| FAS g2p CER | 1.47 full-split | — | shipped |
| TH PER | **0.1478** | 26.9 (latency play) | crown held + latency tier |
| client surface | 3 runtimes + edge | none exists | moat maintained |
