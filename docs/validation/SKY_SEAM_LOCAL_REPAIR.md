# Sky seam local repair

The Night seams marked at the left column/vine opening, right roof and spires,
ribbon-side background, and upper foliage were checked against Base, sky alpha,
and the existing edge-tone asset. The sky matte already covers the open sky and
most small leaf openings. The main discontinuity was the warm, pale Base color
retained by distant foliage and masonry immediately beside the dark Night sky.
The left opening and ribbon-side tree had no registered foreground correction;
the earlier upper-right correction was too weak for the larger marked area.

`scripts/paint_sky_edge_tone.py` now authors local, fixed Artwork-Space repair
patches in the existing 1672×941 `sky-edge-tone.png`. They follow the marked
canopy/roof, vine, ribbon-side tree, and top leaf clusters. The existing sky
alpha clips the patches out of open sky, preserving the fine leaf holes and
spire silhouettes. The asset's RGB stores a cool per-channel absorption and
alpha stores the local strength. Both Lit display paths use the same registered
sample, multiplied by the existing continuous Night weight. This is local
foreground material correction, not a new sky segmentation or global grade.

No new leaf occluder was added: the existing leaf and vine silhouettes already
cover the seams naturally once their Night material no longer glows warm.
Noon/Dawn/Dusk remain pixel-identical to their before captures (0 changed
pixels at 2048×1033). Night changed 145,517 pixels, confined to the authored
repair regions. The left warm tree is substantially quieter; the right roof
canopy and ribbon-side tree sit behind the subject; the spires, roof profile,
and individual top leaves remain legible. A small amount of source-painted
warmth and anti-aliased fringe remains at high zoom, especially around the
right roof tree, but no longer dominates the full Night composition.

Review images:

- [Four-phase contact](sky-seam-repair/final/four-phase-contact.png)
- [Dawn](sky-seam-repair/final/dawn-full.png) · [Noon](sky-seam-repair/final/noon-full.png) · [Dusk](sky-seam-repair/final/dusk-full.png) · [Night](sky-seam-repair/final/night-full.png)
- [Night before](sky-seam-repair/before/night-full.png) · [marked-region before/after](sky-seam-repair/night-before-after-crops.png)
- [Base / sky alpha / old tone audit](sky-seam-repair/before/source-matte-audit.png)

Sky RGB and alpha plates, Base, Normal, lighting, Post settings, time curves,
Blink, Breathing, Hair, and Leaves are unchanged. `pnpm build` and
`pnpm typecheck` passed. Await human review before resuming character lighting.
