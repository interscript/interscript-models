# WO87 — target-accurate model naming: document, then rename

Status: PLANNED · Phase 1 DONE (tha-phonemic-1.0, models#357); Phase 2
= the legacy 33

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
