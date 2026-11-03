# PARG v2 migration (per ~/src/parsanol/)

Parsanol is the org's PEG parser family: parsanol-rs (Rust, packrat +
arena, bytecode backend, crates.io), parsanol-python, parsanol-ruby,
parsanol-ts, parsanol-codegen, audit/ + docs/ + leptris gem.
MIGRATION: the ISC map compiler/runtime moves to parsanol v2 — the ISC
grammar re-expressed as a parsanol grammar; the compile pipeline emits
through parsanol-codegen; each runtime executes via its parsanol lib.
Keep ISC semantics frozen (IS-1 v2 normative page; the 22 frozen
rulings; conformance fixtures decide equivalence — byte-identical
outputs across runtimes before any runtime swaps in).
