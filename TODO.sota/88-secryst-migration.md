# WO88 — full migration of the secryst-lineage models into the framework

Status: IN_PROGRESS (2026-10-24, owner-directed: "fully migrate them
to interscript in our new framework")

The secryst-era models (khm-latn-1.0, the legacy tha-g2p line) predate
the contract: no recipes, no corpora pins, no documented targets
(WO87's audit), thin provenance. Migration = bring each into the
2-YAML + gates world so every future retrain/release runs the same
lawful path.

## Step 1 — metadata migration (this WO, now)
- `corpora/khm-latn.yaml`: the secryst lineage documented with honest
  UNVERIFIED markers where provenance is not yet pinned (the training
  corpus predates pinning; the decode evidence + khmer-dict-spice
  source are documented).
- `recipes/khm-latn.yaml`: the retrain contract for the
  framework-native khm-latn (the WO68/82 path).

## Step 2 — retrain under gates (the real migration)
Each legacy line retrains through recipes+gates; the legacy artifact
stays resolvable via index aliases until its successor passes.
Order: khm-latn (B7 owner data pending → blocked), tha-phonemic
legacy line (superseded by tha-phonemic-1.0 — retire, don't retrain),
urd/fas lines (gates already apply to their successors).

## Acceptance
Every id in models.yaml carries recipe+corpus or an explicit
retire note; nothing remains outside the contract.
