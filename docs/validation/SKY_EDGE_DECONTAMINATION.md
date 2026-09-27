# Sky edge decontamination / reconstruction

The previous local Night repair multiplied the final display color by a dark/cool edge tone. It hid some seams but also dulled the foliage and stone. This revision removes that display-space path from both direct Lit and R6 Post.

## Registered assets and composition

- `sky-edge-reconstruction.png` (1672×941 RGBA) replaces only selected old-sky-contaminated foreground Albedo at the left vine opening, central pillar edge, ribbon-side tree, right roof/treeline, and upper-right leaves. The RGB comes from nearby interior leaf/stone pigment; alpha limits its reach to the fixed repair areas and boundary band. It enters before the existing scene lighting.
- `sky-edge-skyfill.png` (1672×941 RGBA) pairs recovered distant foliage RGB with estimated original-sky mixture alpha in hand-located tree gaps. Night weights this pair continuously into the ordinary Sky compositing path. Open Sky RGB, the four Sky plates, and the main Sky mask are unchanged.
- The generation recipe is `scripts/generate_sky_edge_reconstruction.py`. Its fixed polygons are localization bounds, not opaque painted patches. The script enforces Artwork Space registration.

Broad auto dilation and unrestricted foreground propagation were rejected during visual iteration: one ate a tower tip, and another left geometric patches on architecture. The final candidate uses a shorter foreground boundary band and separate, bounded distant foliage reconstruction. No final-color darkening, blur, Bloom, or new scene light is applied.

## Visual review

Final WebGL2 Lit frames: [Dawn](sky-edge-reconstruction/final/dawn-full.png), [Noon](sky-edge-reconstruction/final/noon-full.png), [Dusk](sky-edge-reconstruction/final/dusk-full.png), [Night](sky-edge-reconstruction/final/night-full.png).

Night before/after: [full frame](sky-edge-reconstruction/final/night-before-after.png), [roof and spires](sky-edge-reconstruction/final/roof-before-after.png), [left vine](sky-edge-reconstruction/final/vine-before-after.png), [ribbon-side tree](sky-edge-reconstruction/final/ribbon-before-after.png). The *before* side is the previous display-tone result. The *after* foliage is visibly warmer and less muddy because foreground material is restored rather than shaded over. The blue old-sky fringe is reduced most clearly at the right roof treeline and ribbon-side tree. Tower tips, roof line, hat, and ribbon remain intact. Dawn, Noon, and Dusk were inspected at full frame with no new holes or dark patches.

Some faint blue-gray original-air pigment remains in the most blurred distant branches, particularly at the lower left vine opening. It is a residual from the frozen Base painting, not a new Sky alpha discontinuity. Further suppression would require a wider semantic rebuild of those trees and risks flattening their depth; the current candidate preserves the painted distant-air softness.

No character lighting, 24H curves, motion, Normal, Base, or Sky RGB was changed. `pnpm build` and `pnpm typecheck` pass. The old `validate_time_controller.py` pixel baseline is intentionally stale for this visual change and fails its frozen Dawn image assertion; the time controller itself was not modified.

## Two marked Night regions: final local correction

User review then identified a pale old-sky patch behind the black ribbon and repair spill on the large tower to its right. The ribbon-side polygon was moved left to include the actual sky opening, and its nearly pure old-sky pixels receive full Night Sky replacement. A fixed tower protect matte now zeros both repair alpha channels across the tower wall, roofline, and side spires. The protect region follows the tower's left edge at approximately source x=1325, leaving the ribbon opening available for repair.

[Night ribbon before/after](sky-edge-reconstruction/two-box-final/ribbon-before-after-2x.png) and [Night tower before/after](sky-edge-reconstruction/two-box-final/tower-before-after-2x.png) show the two targeted changes. [Dawn](sky-edge-reconstruction/two-box-final/dawn-full.png), [Noon](sky-edge-reconstruction/two-box-final/noon-full.png), [Dusk](sky-edge-reconstruction/two-box-final/dusk-full.png), and [Night](sky-edge-reconstruction/two-box-final/night-full.png) were recaptured. The ribbon-side pale patch is reduced, and tower windows, wall planes, and spires no longer receive the correction. Faint soft sky pigment remains within some distant painted branches; no broad suppression was reintroduced.
