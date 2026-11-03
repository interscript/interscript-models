# WO80 — A4 stage 1: the ISC semantic rulings inventory

Status: **IN PROGRESS** — 14 of 10 points empirically ruled
(batches 1-4, ruby#818/#820/#821/#822; 18 vectors). Remaining open:
point 4's ML-adapter contract (secryst/rababa provisioning semantics),
point 8's local alias blocks, and the stray-identifier hazard
(ruby#822 pins it; stricter parse gated on a clean 293-map x
3-compiler parse).
The IS-1 spec document (A4's vehicle, WO74 dependency) is authored from
this inventory: every point gets (a) the grammar anchor, (b) the ruby
interpreter's actual behavior verified by a test, (c) a normative
ruling.

## The semantic surface (code anchors: interscript-ruby @ main)

| # | area | grammar anchor | interpreter anchor |
|---|------|----------------|--------------------|
| 1 | stage composition | grammar/concerns/stages.rb (sequence_block, parallel_block, run_rule, separate_directive) | interpreter.rb `execute_rule` / `call` |
| 2 | parallel rule priority + `separator` | stages.rb:45-53 | the parallel executor pass |
| 3 | run (stage composition across dependencies) | stages.rb:120 | dependency-aliased dispatch |
| 4 | funcall (`rababa` + kwargs passthrough) | stages.rb:70-77 | stdlib adapters (optional layer) |
| 5 | item algebra: any / character classes / ranges / alternation | grammar/concerns/primitives.rb (21 rules) | `build_item` |
| 6 | maybe + capture + ref composition | grammar/concerns/items.rb (21 rules) | `build_item`/capture frame |
| 7 | boundary / word guards + casing interaction | primitives.rb + interpreter case handling | `build_regexp` + case pass |
| 8 | aliases (local/remote/imported) + dependency resolution | grammar/concerns/aliases.rb, dependencies.rb | registry alias resolution |
| 9 | metadata contract + embedded tests | grammar/concerns/metadata.rb, tests.rb | test runner |
| 10 | charset/casing directives (`upcase`/`downcase`/`title` stdlib) | metadata/system concerns | stdlib functions |

## Method per point
1. Write the empirical test against the ruby interpreter (the reference
   runtime).
2. Run the same vector through ts + py (the C1 harness).
3. Divergence = an open ruling -> decide, encode the ruling as a
   normative spec section + a frozen vector.
4. IS-1 v2 text accumulates one section per ruled point; the document
   ships when all 10 close (then D2 releases it).
