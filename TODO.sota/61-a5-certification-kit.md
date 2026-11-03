# WO61 — A5: third-party conformance certification kit

Status: PLANNED · Plane A
Goal: an implementable certification path so ANY runtime can
self-certify against Interscript.
Method:
1. Levels: L0 parse (ISC grammar conformance), L1 embedded tests, L2
   frozen conformance vectors (maps + models), L3 full cross-runtime
   parity on the distinguishing corpora (WO59).
2. Ship the kit as a package: vector bundles from GitHub Releases +
   a runner spec + a self-certification report format (machine-
   checkable).
3. Certify our three runtimes at L3 as the reference demonstration.
Acceptance: kit published; report format validated; ruby/ts/py at L3.
Depends: WO58/WO59/WO60 for L3 content.
