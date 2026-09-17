# Intrinsic correction experiment — bounded registered gain

Route B was chosen: deterministic scalar gain, leaving the approved Hero intact.
No AI generation/editing, new illustration, geometry warp or source replacement.

## Method and contract

`npm run assets:correction` reads v2 normal and source region geometry. It assumes
a weak fixed broad key direction `(0.65,-0.45,0.60)` and approximately inverts
that *assumed* illumination. Gain is limited to -0.25…+0.15 EV before conservative
material weights. Face/eyes, hands, hat, exterior, laptop and untouched background
are excluded. There is no luminance-to-height extraction, denoising or texture
blur; linework is multiplied by a slowly varying scalar alongside its neighbors.

Actual encoded range is 83…160, about **-0.177…+0.126 EV** (linear gain roughly
0.884…1.091). `intrinsic-correction-v1.png` is native 3840×2160 grayscale data.
R=128 is neutral, `EV=(R-128)/254`. Runtime uses R8 on texture unit 6, adding
7.91 MiB only when the full map is loaded. No new rendering pass.

`/?correction=1` loads and enables it; the checkbox switches it off/on without
reloading. Default `/` does not load it. Original Base bypasses it; Corrected
Base displays the active gain before lighting. The engine also exposes optional
`correctionUrl`, `correctionAvailable`, and `setSettings({correction:0|1})`.

## Results and decision

See [same-light OFF/ON and amplified difference](../screenshots/technical-art-alignment/final/alignment/correction-comparison.jpg).
This comparison disables bloom on both sides. Full-frame mean absolute RGB
difference is 0.49/255 at dusk and 0.38/255 at night; maxima are 12 and 10/255.
It slightly softens the fixed brightness bias on a few hair/page/cup regions,
but its benefit is small and varies by material. It does **not** remove the
painted wall sunlight, window reflections, cast shadows or hand/page shadows.

Keep it as an **opt-in experiment**, not the new default and not a claimed clean
albedo. A larger inverse gain would risk mistaking reflectance for lighting and
exposing the approximate normals. That escalation was deliberately not made.
There is no evidence here to justify replacing or repainting the entire Hero.

## Validation and rejected behavior

- Native size, bounded gain and exact neutral samples on face/hands/glass/wall.
- Correction=0 Final is pixel-identical to the same rendering without a map.
- Original Base is pixel-identical with the setting on/off.
- Corrected Base at neutral gain is pixel-identical to Original Base. The first
  implementation unnecessarily round-tripped sRGB and failed exact equality;
  neutral-gain debug pixels now return original data directly. No tolerance was
  loosened to accept that failure.
- Fixed screenshots at 06:00, 12:00, 17:30 and 23:00, with no animation/steam.
- Shader compilation and WebGL error checks pass in Chromium.

This is a registration-preserving experiment, not an intrinsic decomposition
ground truth. Full separation of painted illumination and reflectance remains
unresolved; stronger relighting would need an artist-reviewed clean base or
better intrinsic evidence, not additional masks hiding the conflict.
