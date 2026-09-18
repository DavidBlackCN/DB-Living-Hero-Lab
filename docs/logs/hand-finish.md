# Left-hand local finish — 2026-09-18

Baseline: `4b3cf9d`. Scope: anatomical left hand (screen right), cuff and nearby
right page. Preserve the accepted face, glass, projection and whole-scene lighting.

## Diagnosis and change

Rendered final/form/contact/lamp/shadow/neutral at 06:00, 12:00, 17:30, 23:00
before editing. The contact diagnostic is already a narrow registered curve;
the large dark patch is primarily inferred rear-facing form response compounded
with shadows painted in the source. Globally reducing occlusion is inappropriate.

- `src/engine/shaders.ts`: compact reflected lamp contribution centered at
  (889,489), extent (76,57), in 1200×675 artwork coordinates. Peak coefficient
  .24, reduced on already lit orientations. Existing scene/cloth receivers gate
  it; hair, face and glass exclude it. It follows night weight and actual lamp
  strength, passes through existing contact/source visibility, and multiplies
  source pigment. No brightness floor, emission, new texture or render pass.
- `docs/scene-regions.json`: only `right-hand-page` (screen-coordinate naming)
  changes: width 3→1.8, blur 1.25→.85, weight .65→.48. The existing wider faint
  penumbra automatically becomes narrower/weaker with this contact path.
- `public/assets/generated/light-shaping.svg`: regenerated contact channel.
  Other regenerated assets have no content differences.

Contact stays at the page edge. The original illustration supplies cast-shadow
direction and broad silhouette; the weak reflected contribution alleviates its
double-darkening. No displaced synthetic hand silhouette or new dynamic cast
shadow is introduced: this pass cannot reconstruct missing depth or unpaint
the original cuff shadow. Those source-art shadows remain intentionally visible.

## Validation

- Build and typecheck passed; timeline tests 7/7 passed.
- Related Playwright tests 11/11 passed: light layers, desk light, face finish,
  salvage and spatial bounds. No full performance benchmark in this small pass.
- Actual 1920×1080 screenshots, bloom enabled, steam/animation disabled.
- Outside conservative hand ROI x1290–1550/y690–880: maximum RGB difference
  **0/255 for all four times**. Face, window, cup and distant tabletop unchanged.
- Hand sample x1380–1490/y740–825 mean absolute RGB differences:
  06:00 .41, 12:00 .26, 17:30 .46, 23:00 7.21 (8-bit values).
- 17:30: narrow contact cleanup, warm contrast retained.
- 23:00: less dead-dark cuff/hand, continuous weak warmth toward page, crease
  and finger contact still readable. No self-lit hand or broad desk relighting.

Local visual review supports freezing this version. The residual painted cuff
stripe and approximate normal geometry remain limits of code-only relighting.
Gallery: [before/after and full scenes](../screenshots/hand-finish/README.md).
