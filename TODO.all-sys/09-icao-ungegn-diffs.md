# ICAO + UNGEGN source diffs

Obtain current ICAO 9303 + UNGEGN romanization documents; diff each vs
the registry's icao-*/un-* maps; encode genuine gaps, note reissues.
The registry has icao-{rus,bel,bul,mkd,srp,ukr}-9303 + icao-mul-2015.

SOURCE STATUS (2026-11-03): neither the current ICAO 9303 part
documents nor the current UNGEGN romanization files are in
interscript-private-references/. OWNER-GATED acquisition (the
older .imp-era icao-9303-2 multi-language content was already split
per-language in the registry per the #168 analysis). Once acquired:
diff per language column vs the registry maps; encode genuine gaps;
note reissues as notes, never silently overwrite.
