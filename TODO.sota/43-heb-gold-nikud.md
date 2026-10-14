# WO43 — HE gold-nikud speech arm: the second contender path for g2p

## The insight

Our SHIPPED Hebrew g2p chain is nikud-model → nikud→IPA rules
(py#29/#30) at **0.2393** nCER. Its ceiling is the NIKUD model, not
the rules. The audio chain (WO36) attacks g2p directly; this arm
attacks the OTHER end: better nikud → the shipped chain improves with
NO new runtime artifact. The frontier reference: ReNikud 0.0244 grade
nikud would put our chain near-frontier without winning the audio
contest.

## Resource (availability VERIFIED 2026-10-14)

`micsell/hebrew_speech_campus_nikud` — public, non-gated, 28.6 GB,
117 train parquets, **GOLD nikud annotations** over campus-radio
speech (WO36 "alternative noted", never pulled). Also
`micsell/hebrew_speech_kan_nikud` (same family). License check
against the dataset README REQUIRED before any training run
(third-party data → owner visibility per the no-unauthorized-use
instinct; note in RESULTS before launch).

## Arms

1. **run-068-nikud-gold-ft** — fine-tune the shipped nikud champion
   lineage (plane-2.0 architecture, WO04 trainer) on campus-nikud
   pairs (unpointed→pointed derived from gold). Mix with the original
   training corpus (replay to avoid register forgetting — the
   r9-yallamorph convention-drift lesson). Gate: nikud DER ≤ 8.18 on
   the crown benchmark AND g2p-chain nCER (nikud+rules on the
   phonikud gt) < 0.2393.
2. If plane-arch retraining is too heavy for the queue: byt5-base
   nikud arm as a MEASUREMENT (is gold speech data worth anything to
   the chain?) before committing the plane retrain.

## License check (2026-10-14): FAILED — arm BLOCKED

The dataset README carries NO license field (default all-rights-
reserved). Training on it without permission is off-limits. Unblock
path: owner-to-owner ask to micsell for a research license; until
granted, the gold-nikud arm stays parked and the HE g2p path rides on
WO36/42 only.

## Queue position

After WO41 (urd-diac-base) and only if WO36/42 haven't closed the
audio path — the two paths are complements; whichever converges
first ships. NOT launched this wave (fleet full: e12 a100, WO39 l4,
parity l4, 500h cpu).

## Cost

Fine-tune ≈ 8-14 GPU-h; byt5 measurement arm ≈ 6 GPU-h.
