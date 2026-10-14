# WO44 — release plan: naming + publication for the staged wave

Status: PROPOSAL — every numbered decision below is the owner's;
I execute verbatim once stated. Nothing ships without those numbers.

## Publish-state audit (verified 2026-10-14)

| artifact | state | blocker |
|---|---|---|
| run-047/055 e6 export | staged zip 821,320,781 B, sha 12cb294d… (as "ara-diac-news-1.2") | name decision D1 |
| run-040 base-strip export | exists in bucket export/ (4.00/2.84) | name decision D1 |
| run-059 urd-g2p-base | staged zip 399,894,914 B, sha b1d9a319… (as "urd-g2p-base-staged"); parity re-running | parity + D2 |
| py decode contract (py#35) | on origin/main, version 0.2.0 NEVER published (PyPI interscript = 0.1.0) | D3 |
| npm decode contract (ts#108) | on origin/main; npm 5.7.0 published 10-09, PR merged 10-11 → UNPUBLISHED | D3 |
| gem decode contract (ruby#805) | on origin/main, VERSION 3.0.1 unpublished (rubygems `interscript` at 3.0.1? — verify at release) | D3 |
| models.yaml | corrected metrics + staged rows | D1/D2 names |
| index | v10 published | D4 |

## The naming law (derived from the 29 existing HF mirrors)

1. **Tier/domain/architecture is a NAME SEGMENT with its own version
   lineage**: `-small-` `-base-` `-large-` `-plane-` `-plane-large-`
   `-layerdrop-` `-news-`. tha-g2p-small-1.0 and tha-g2p-base-1.0 are
   siblings, not a sequence.
2. **In-lineage improvement bumps the version**: heb-diac 1.0 → 1.1.
3. **New artifacts carry precision in METADATA, not the name**
   (ara-diac-news-1.0, heb-diac-plane-2.0 pattern).
4. Artifacts ship via GitHub Releases + sha256 sidecar (2 GiB part
   cap — all three staged zips fit single-part); HF mirrors canonical;
   runtimes pin an index version.

## Decisions for the owner

**D1 — Arabic staged artifacts.**
(a) RECOMMENDED: `ara-diac-news-1.1` = base-strip retrain (4.00/2.84
first-alt; contract-clean — it does not emit alternates, so old
runtimes score it correctly too) AND `ara-diac-news-large-1.0` =
large-strip e6 (3.5607/1.4588 NEW BEST; the `-large-1.0` pattern is
our own established precedent via ara-diac-plane-large-1.0).
(b) Minimal-churn: ship only ara-diac-news-large-1.0, drop 1.1.

**D2 — Urdu base tier name.** `urd-g2p-base-1.0` (tha-g2p-base-1.0
precedent). Requires a 10-min re-export with the final IMF_ID (the
staged zip's metadata.yaml id literally reads "urd-g2p-base-staged")
→ fresh sha replaces b1d9a319.

**D3 — Runtime versions.** The wave carries BOTH a behavior fix
(decode returns primary choice) AND a new public method
(first_alternates/firstAlternates) → semver MINOR applies:
- npm `interscript` **5.8.0** (owner floated 5.7.1 — that understates:
  new API surface can't be a patch)
- gem `interscript` **3.1.0** (same reasoning; 3.0.2 floated)
- py `interscript` **0.2.0** — already declared on main, never
  published; publish as-is, no new number.

**D4 — Index.** index-v11: adds the D1/D2 entries, carries the
corrected-protocol metrics. Released via GitHub Releases + sha256;
runtime release PRs pin v11.

**D5 — Card text** for ara-diac-news-1.0 mirror: add the
decode-contract note (bytes unchanged, sha valid, pre-#108 runtimes
need first_alternates or score raw).

## Order of operations (dependency-true)

1. Parity verdict (RUNNING) → D2 re-export (final id) → fresh sha.
2. Owner states D1/D2/D3 → GH Releases ×3 + sha256 sidecars.
3. models.yaml published entries → index-v11 build + release.
4. HF mirrors ×3 + cards (existing pipeline); D5 card note.
5. Runtime releases: py 0.2.0 → npm 5.8.0 (OIDC trusted publishing
   ONLY — never tokens) → gem 3.1.0 (release-gem@v1 flow); each pins
   index-v11. Verify loaders fetch v11 + new artifacts before tagging
   complete.
6. /ml page rows + WO05 DER derivation for release notes (DER
   comparisons only within same benchmark+protocol — WikiNews
   multiref DER 1.4588 vs published frontier DERs only where the
   benchmark is identical).
7. Release-notes drafts → owner reviews wording (external-comm law)
   → post.
```

## Post-release verification

- Loader smoke in all three runtimes: list → fetch → sha-verify →
  translate golden (incl. alternates contract).
- HF mirror download + ORT decode parity spot-check per new artifact.
- Golden parity suite re-run (WO18/23 chain).


## Execution log (2026-10-14, decisions D1-D5 APPROVED by owner)

- npm interscript@5.8.0 PUBLISHED (dispatch; provenance).
- py 0.2.0: blocked on red CI (yaml dep) → PR #36 open; re-dispatch
  after merge.
- gem 3.1.0: PR #806 open (version bump); blocked on pre-existing
  main spec failures (golden/imf fixtures, Isc ParseError) and the
  broken v3 CI release path — ships hand-rolled after green.
- PARITY GATE: int8 zip FAILED (0.44 vs 0.14 CER) → fp32 shipping
  decision; 4-job fp32 re-export wave in flight; GH Releases gated
  on green zip parity.

## Release-notes drafts (owner reviews wording before posting)

**Runtime wave (shipped: npm 5.8.0 ✓, gem 3.1.0 ✓; py 0.2.0 pending
the PyPI trusted-publisher entry):**
> Seq2seq models trained on multi-reference corpora emit
> slash-separated alternates; the decode contract now returns the
> primary choice by default and exposes `first_alternates` /
> `firstAlternates` for callers who want the full set. Fixes the
> WikiNews-style scoring artifact (raw-protocol numbers were
> inflated); models.yaml metrics are stated under the corrected
> first-alternate protocol.

**Model wave (gated on parity/releases):**
> urd-g2p-base-1.0: base-tier Urdu G2P, full-split CER 15.65 (beats
> the small tier's 15.78 gate); fp32, shipped-bytes parity verified.
> ara-diac-news-1.1: alternate-free base-tier news specialist
> (no decode-contract dependency). ara-diac-news-large-1.0: NEW BEST
> 3.5607/1.4588 first-alt on WikiNews-2024 multiref (ship pending
> WO45 static-int8 — the fp32/fp16 graphs exceed the 2GB ONNX cap).
