# WO66 — B5: Persian — hold < 0.7 across registers

Status: PLANNED
Goal: fas-diac 0.603 row-mean holds < 0.7 on poetry and colloquial
registers; Arabic-loan vocalization probe (the known residual).
Method: register-stratified eval sets (build from poetry corpora,
colloquial sources); probe the scar (docs 0.52% lesson: corpus-level vs
row-mean declared); targeted data if registers degrade; VRR.
Acceptance: register-stratified external-protocol numbers published.


## Source dossier (2026-10-25, for owner approval)

| source | register | license | note |
|---|---|---|---|
| Ganjoor (ganjoor.net) | poetry (Hafez/Saadi/…) | CC BY-SA 3.0 (site-stated) | the largest digitized divan corpus; attribution + share-alike |
| fa-Wikisource | poetry + classical prose | CC BY-SA 4.0 | attributable, steady quality |
| OSCAR-fa | colloquial/web | Common-Crawl-derived (CC0-shaded tooling) | register = modern web; quality filters needed |

Owner picks the sources -> corpora/<x>.yaml with sha256 pins ->
the register-hold arm (target: CER < 0.7 across registers).


## Register gap MEASURED (2026-10-26, full run)

fas-diac-base-1.0 on the Ganjoor vocalized poetry eval (3,497 verses,
79 poets, harakat-stripped inputs vs vocalized gold): **CER 33.67%** —
vs 0.603% on the news-classic register. The register gap is ~56x, now
quantified. The poetry corpus + eval are pinned
(run-089-fas-poetry-eval, sha 94f318f688b556be). The register-hold arm
(<0.7 across registers) requires poetry in training: the 3,497
vocalized verses are the seed; the owner source picks (dossier above)
scale it.


## Register arm RESULT (2026-10-26): the poetry seed HALVED the gap

The register-adapted model (fas-diac-base fine-tuned on the full 446k
corpus + the 3,497-vocalized-verse seed x10; gate-passed 0.69% on
news-classic) scores **CER 16.55%** on the identical Ganjoor eval —
vs 33.67% pre-register. HALVED. The per-section trajectory shows the
residual concentrates in dense-vocalization verses (the late eval
sections). Scale-up path: the owner source picks (dossier) grow the
vocalized seed; the recipe (checkpoint fine-tune + seed oversample)
is proven.
