# R2A.2 Lighting Visual Calibration

## Scope

R2A.2 calibrates the existing manual `lightingFor(minutes)` model and 0-1440 Debug Slider. Solar elevation, azimuth trajectory, and shortcut times are unchanged. No clock synchronization, automatic playback, Bloom, post-processing beyond a minimal display transform, or animation module is included. Base Albedo and Normal v3 remain frozen.

## Lighting and Display Pipeline

- `src/config/lighting.ts` keeps physical key / ambient illumination, twilight energy, exposure stops, diffuse response, and broad-band values centralized.
- The shader decodes Base sRGB to linear reflectance, applies Normal v3-driven diffuse plus low-frequency painted-band response, then blends Base and relit scene in linear space using `relightStrength`.
- Display exposure is applied downstream as `exp2(exposureStops)`, followed by a compact ACES-fit tone map and sRGB encoding.
- Base and Normal diagnostic views, and Lit with Lighting disabled, return their original samples before the display transform. This preserves exact diagnostic comparisons.
- Night reduces physical key and ambient energy, uses cool sky fill and a low directional key, and compensates with bounded display exposure. Dawn / Dusk receive additional warm key and ambient energy for readable forms.
- Debug includes manual controls for display exposure in EV and band strength / threshold / softness.

## Calibrated Parameters

Shared values in `lightingModelConfig`:

| Parameter | Value |
| --- | ---: |
| Night / day key intensity | 0.28 / 0.92 |
| Twilight key boost | 0.58 |
| Night / day ambient intensity | 0.25 / 0.58 |
| Twilight ambient boost | 0.20 |
| Night / dawn / day / dusk display exposure | +0.48 / +0.02 / 0.00 / +0.02 EV |
| Diffuse wrap / threshold / softness | 0.08 / 0.52 / 0.24 |
| Band strength / threshold / softness | 0.48 / 0.68 / 0.24 |
| Relight strength | 0.90 |

The time model derives twilight contribution continuously from its existing warmth and daylight curves. The direction curve, azimuth, elevation model, and 24:00 wrap behavior are unchanged.

## Page Check

Desktop Chromium / WebGL2 at 1440 x 900 was captured at 00:00, 06:30, 09:00, 12:00, 15:00, 17:30, 20:00, and 22:00. PNGs are under `%TEMP%` as `r2a2-0000.png`, `r2a2-0630.png`, `r2a2-0900.png`, `r2a2-1200.png`, `r2a2-1500.png`, `r2a2-1730.png`, `r2a2-2000.png`, and `r2a2-2200.png`. WebGL2 initialized and Playwright reported no page errors.

Spot checks show Noon remains close to the authored Base. Dawn / Dusk retain warm directional color with stronger energy than R2A.1; Normal-driven face and clothing structure is visible without a conspicuous specular or embossed effect. Night is cooler, its physical key and fill remain below daytime levels, and the face and clothing stay readable at +0.48 EV. These are implementation checks only; visual acceptance remains with the user.

Base versus Lit with Lighting disabled must remain pixel-identical: both shader paths return the sampled Base before exposure, tone mapping, or any lighting operation. This invariant is kept in the shader; no frozen artwork assets were modified.

## Acceptance Boundary

R2A.2 is submitted for manual visual review. Do not start R2B system-time synchronization or playback, Bloom, Breathing, Hair Motion, Leaves v2, or other follow-on work until explicitly accepted.
