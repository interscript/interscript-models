# ICAO + UNGEGN source diffs

Obtain current ICAO 9303 + UNGEGN romanization documents; diff each vs
the registry's icao-*/un-* maps; encode genuine gaps, note reissues.
The registry has icao-{rus,bel,bul,mkd,srp,ukr}-9303 + icao-mul-2015.

SOURCE STATUS (2026-11-03, updated same day):

- ICAO — ACQUIRED + DIFFED. Doc 9303 Part 3 Amd 1 (16/09/16) was found
  in interscript-references/icao/; the diff ran as WO09 (maps PR
  #247): 8 maps aligned to Section 6 (rus/bel/bul/mkd/srp/ukr/fas
  fixed, heb notes-only, mul verified on the icao-9303 branch and
  adoption left open); 141 embedded tests added; the 04BA -> C
  source-side erratum documented in all six Cyrillic maps. Ukrainian
  word-initial rules and teh-marbuta XAH remain documented-not-encoded
  (boundary-constraint encodings, follow-up).
- UNGEGN — ACQUIRED, DIFF PENDING. 47 unstats PDFs + 92 EKI WGRS
  edition files (rom1/rom2, pdf+htm, all editions per language)
  downloaded into interscript-references/ungegn/ on branch
  ungegn-romanization-library (pushed). Encoding the un-* diffs waits
  on the branch landing in the library + owner go-ahead per system.
- The older .imp-era icao-9303-2 multi-language content was already
  split per-language in the registry per the #168 analysis.
