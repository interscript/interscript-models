# ALA-LC Batch 1 — Brahmic/SE-Asian (14)

Sources: alalc/{burmese,khmer,lao,thai,shan,javanese,balinese,batak,
lepcha,limbu,santali,manipuri,cham,tibetan}.pdf (2012-era tables).
Recipe per system: read the table (text layers are thin — read pages
visually at 3-5x); if glyphs are Latin lookalikes (batak.pdf), establish
glyph→Unicode visually against the script's block; encode
alalc-<lang>-<script>-Latn-<year>.isc with tests from the doc's own
examples; one PR for the batch; cross-run each map's tests before push.
Systems: Burmese mya-Mymr, Khmer khm-Khmr, Lao lao-Laoo, Thai tha-Thai,
Shan shn, Javanese jav, Balinese ban, Batak btk-Batk, Lepcha lep,
Limbu lif, Santali sat-Olck, Manipuri mni-Mtei, Cham cja/cjm, Tibetan
bod-Tibt.
