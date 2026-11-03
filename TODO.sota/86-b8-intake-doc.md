# WO86 — B8 intake: the community language path, documented

Status: PLANNED · Plane B

B8's proof is three outside languages through the 2-YAML path — but
there is no published onboarding document; the path exists only in
maintainer heads and CLAUDE.md notes.

Goal: a contributor can onboard a new language without reading the
pipeline: what to bring (authority reference or corpus + license), the
two YAML shapes, the eval-set expectation, the gates their PR must
pass, and how a learned component slots in if the table
underdetermines.

Method:
- `docs/contributing-language.md` in interscript-models: the 2-YAML
  contract (`recipes/`, `corpora/`), provenance law, gate walkthrough
  (quality/parity/license/conformance/regression), worked example
  end-to-end (smallest shipped map as the template).
- Mirror a short pointer from the maps repo README.
- The path itself needs no code change — if it does, that is a
  framework bug: record it, do not patch around it.

Acceptance: doc merged; one dry-run onboard of a trivial language
through the gates using only the doc.
