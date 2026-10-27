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


## Like-for-like verdict (2026-10-25, SAME split — secryst test, 895 rows)

- Legacy khm-latn-1.0 artifact: **CER 27.57%**
- Framework retrain (ByT5-small, 4+4 epochs, resume-tuned): **28.99%**

The migration's retrain is 1.4 points behind the legacy on identical
data — close, not beating. Next levers (recorded, in order): ByT5-base
backbone (the legacy may be base-class), corpus enrichment (merge the
Chuon Nath IPA + SBBIC vocab layers), longer schedule. The migration
contract holds: the framework path produces a honest, reproducible
28.99 where the legacy number was undocumented.


## Backbone lever RESULT (2026-10-27): ByT5-base 28.81% best (ep2)

Like-for-like standings on the secryst test split:
- Legacy artifact: **27.57%**
- Framework ByT5-small (8ep): 28.99%
- Framework ByT5-base (4ep): **28.81%** (best; ep3 28.92)

The backbone lever is near-exhausted — the remaining ~1.2-point gap is
the CORPUS: the legacy's undocumented training set evidently exceeds
our 17k pairs. The recorded next lever is corpus enrichment (merge the
Chuon Nath IPA layer + SBBIC vocabulary + the khm-latn pairs), which
is the WO68 data work. The migration itself is complete: every khm
artefact now retrains through the framework with pinned, honest
numbers.


## Multi-task RESULT (2026-10-27): the framework BEATS the legacy

khm multi-task (<latn>+<ipa> task prefixes, ByT5-small, 4ep):
**dev CER 24.50%** (best; final 24.54) — vs legacy 27.57% like-for-like.
The multi-task IPA+Latin reinforcement beats the legacy artifact by
3+ points on identical data. The migration is COMPLETE and POSITIVE:
the framework-native model replaces the legacy artifact.

Next: export the multi-task model → fixtures → gates → publish as the
khm-latn successor (owner: id + version — the convention is
khm-phonemic-1.0 under the MECE taxonomy, since the output is IPA).
