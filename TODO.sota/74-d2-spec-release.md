# WO74 — D2: IS-1/ISC as a citable standard

Status: BLOCKED-ON-A4 (2026-10-21 finding): the IS-1 spec DOCUMENT
does not exist in any repo — TODOs across interscript-ruby reference
`spec/isc/document.adoc` but only `spec/isc/parser_spec.rb` and the
grammar sources (`spec/isc/grammar*`) are committed. The A4 semantics
work is therefore the AUTHORING of the spec document from the grammar,
not an edit of an existing one; D2 releases its output.
Goal: versioned spec releases with a citation block; the spec becomes
an artifact others implement against.
Method: IS-1 v2 (WO60) tagged as spec release v2.0 on the canonical
repo; spec PDF/HTML artifacts attached; citation block (BibTeX) in the
README + site spec page. D1 (PyPI publisher) remains tracked in
WO53-ship-set; do not nag.
Acceptance: spec release tagged; citation renders on the site.
