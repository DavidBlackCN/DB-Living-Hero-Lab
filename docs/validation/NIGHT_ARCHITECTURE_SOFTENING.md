# Night tower shadow / foreground isolation follow-up

Baseline: `a9abc73`, branch `v2`. User screenshot time: **03:54**, Moon azimuth 140?, elevation 28?. Await human review.

## Confirmed defects

1. The registered tower rectangle ends at artwork y=350 and the stone pigment selector also accepts pale shirt pixels. Architecture ownership was subtracted from the character mask without consulting the existing character material / garment receive. The white shoulder consequently received a horizontal strip of architecture shadow.
2. The tower plane interpolation spanned only 4 source pixels. Together with a receive band starting at -0.12, the late-night right-facing plane fell nearly to ambient-only illumination, exaggerating the split between the two visible sides.

This is a shader receiving / coverage error. No new local brightening or darkening patch is used.

## Correction

- `architectureReceiver` now receives the existing Face, Hair and Clothing coverage. Foreground coverage takes priority over stone classification: its 0.03?0.20 soft exclusion clears architectural receiving from the shirt, including its edge. All masks use the displaced artwork coordinates; the motion deformation is unchanged.
- Tower corner normals interpolate across 4?14 source pixels according to the tower's width, rather than a fixed 4 pixels. This softens illumination across the painted corner without blurring the artwork texture.
- Architecture Moon broad receive changes from `smoothstep(-0.12, 0.90, facing)` to `smoothstep(-0.75, 1.10, facing)`. The wider wrapped response reduces the abrupt back-plane falloff. Moon direction, elevation gain, key intensity, ambient, exposure and Post remain unchanged.
- Left-facing and right-facing planes remain distinct and follow the same Moon vector. Early-night image-right receiving and late-night image-left receiving are retained.

Only `src/shaders/hero.frag.glsl` changes production behavior. No artwork, Normal, material asset, Motion, Leaves or Lamp logic changes; no new texture, pass or RAF.

## Actual-render checks

`scripts/audit_architecture_softening.py` captures the frozen shader and current shader with the same assets, time and renderer state. The reference for the affected shirt is `55d995c`, before architecture ownership was introduced.

- 180 independently selected shoulder pixels: architecture receive maximum **0** after correction. Mean display RGB error against the earlier character receive decreases from **41.38 to 6.76**. The remaining difference includes the existing partial garment blend with the changed broad architecture response; it is not claimed pixel-identical to the earlier character frame.
- At 03:54, the sampled right plane's mean RGB rises from **34.36 to 38.62**. The left plane remains the primary Moon-facing side; the backing plane is readable rather than a deep strip.
- Left/front to right/side display RGB ratios: **0.866 at 20:00**, **1.059 at midnight**, **1.300 at 03:54**, **1.283 at 04:30**. Ratios include frozen painted albedo and Post; they are comparative display values, not physical irradiance.
- Dawn 06:30, Noon 12:00, Dusk 17:30: exact baseline equality, maximum RGB delta **0**.
- Face material core: maximum Night RGB delta **1** with the existing Post chain.
- 00:00 / 24:00: exact equality.

## Review images

- [03:54 tower + shoulder before / after](night-architecture-softening/03h54-tower-shirt-ab.jpg)
- [03:54 full frame before / after](night-architecture-softening/03h54-full-ab.jpg)
- [Architecture receiving coverage before / after](night-architecture-softening/receiver-coverage-ab.jpg): white = building receiving, black = excluded foreground. The visible shirt must be black.
- [Night times, full scenes with Moon readout](night-architecture-softening/night-times.jpg)
- [Night tower sequence](night-architecture-softening/night-tower-times.jpg)

## Verification and limits

`pnpm typecheck`, `pnpm build`, the targeted actual-render audit and existing atmosphere/character lifecycle regression pass. Context restore, reduced motion, static quality, hidden tab, 1080p/1440p/4K/mobile resize, Blink, Breath/Head/Hair, Lamps, Leaves and Post smoke checks pass. See [targeted results](night-architecture-softening/audit-stats.json) and [regression results](night-architecture-softening/regression-stats.json).

The Base's painted masonry corner and original contrast remain. The correction softens the lighting transition, not the architectural shape or painted texture. Night architecture remains an artistic broad-normal model without cast shadows. Stop for human visual review; no next stage begins.
