# WO87 — target-accurate model naming: document, then rename

Status: DONE (2026-10-24) — Phase 1 (tha-phonemic-1.0, models#357);
Phase 2 executed: all 33 legacy ids decoded for evidence
(docs/naming/target-documentation.json), the final MECE taxonomy
adopted (vocalized/ipa/phonemic/latn), 31 renames applied zoo-wide
with the authoritative renames: map (models#362); the reference
generated (docs/naming/naming-reference.{md,json}); the naming law in
CLAUDE.md. Three defects found by the sweep recorded below. Index
aliases land at the next index tag (owner).

Owner decision (2026-10-24): model names target the output convention.
Phase 1 renamed the release candidate (tha-g2p-lex-1.0 ->
tha-phonemic-1.0) — its target is exhaustively verified.

Phase 2 CANNOT blanket-rename today: the 2026-10-24 audit found ZERO
entries documenting their output target convention (source/target
scripts empty zoo-wide). Renaming undocumented models fabricates.

Method (per model, mechanical):
1. Decode 3 representative rows through the reference loader
   (one batch job over all 33).
2. Record the target convention in models.yaml
   (target_script/target_convention fields — a contracts.py extension).
3. Rename only on evidence: {lang}-{target}[-{tier}]-{version};
   old ids become aliases in the next index tag (zero breakage —
   index-v12 consumers keep resolving forever).
4. Quantization/architecture/register tiers (int8/int4/fp16,
   layerdrop/plane/news) are accurate orthogonal dimensions — they
   ride along unchanged.

Acceptance: every models.yaml entry carries a documented target
convention; every rename is evidence-backed; index-vN aliases keep
every historical id resolvable; docs + catalogue regenerate.
