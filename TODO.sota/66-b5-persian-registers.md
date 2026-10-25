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
