# WO58 — A2: invertibility ledger + reverse maps

Status: IN_PROGRESS (phase 1 DONE 2026-10-21: docs/invertibility ledger — 10 pairs probed, 1 lossless, 39/278 collisions + probe tool; phase 2 = reverse-map generation)
Goal: for every system, determine whether forward∘reverse = identity;
publish the loss conditions (homophone mergers, digraph ambiguity,
case conventions, vowel elision).
Method:
1. Script against the installed gem runtime: for each map with a
   reverse variant (or a generated one), round-trip the map's embedded
   tests + a synthetic Unicode sample per source script.
2. Classify: lossless / lossy-with-convention / not-invertible; attach
   minimal distinguishing examples.
3. Where an authority publishes a reverse system: encode it (whole-
   document law). Where the forward map is provably bijective:
   generate the reverse from the grammar and validate.
Acceptance: docs/invertibility/LEDGER.md covering all systems; reverse
maps shipped for every losslessly invertible one; losses cited.
