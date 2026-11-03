# WO60 — A4: IS-1 v2 — denotational semantics

Status: IN_PROGRESS (9 rulings frozen #818/#820/#821; remaining: metadata/tests, item algebra, charset, funcall — see WO80 inventory)
Goal: complete the ISC specification with a semantics section so every
runtime behavior is derivable from the document; zero open rulings.
Method:
1. Collect every behavior where runtimes might diverge: boundary
   semantics, parallel rule priority, maybe composition, capture/ref,
   funcall typing, casing interactions, dependency staging order.
2. Write the denotational (or operational) semantics for the ISC
   fragment in IS-1; give each ruling a test vector.
3. Property-test all three runtimes against the semantics.
Acceptance: IS-1 v2 released with the semantics section; the rulings
list emptied; each ruling has vectors in all runtimes' suites.
Depends: nothing; feeds A5.
