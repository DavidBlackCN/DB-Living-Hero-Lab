# R2A.1 Runtime Lighting Model v2

## Scope

This phase replaces the Foundation v1 baseline-preserving directional delta with configurable linear-space relighting and adds a manual 0-1440 minute calibration slider. It does not add a clock, playback, post processing, emission, or new motion systems. Frozen Base Albedo and Normal v3 are unchanged.

## Architecture

- `src/config/lighting.ts` contains typed lighting-model parameters, the four calibration shortcut times, the pure `lightingFor(minutes)` function, and conversion to the engine `LightingState`.
- The model uses a sinusoidal solar elevation, independently shaped daylight and twilight-warmth curves, a daytime dawn-to-dusk azimuth arc, and a smooth dusk-to-next-dawn night arc. 00:00 and 24:00 resolve to the same state.
- Vue stores the manually selected minute and forwards the resulting state. Renderer and shader remain independent of Vue.
- The shader decodes Base sRGB to linear, applies Normal v3-driven wrapped diffuse, ambient/sky fill and a broad low-frequency Normal light band, blends against Base in linear space with `relightStrength`, then encodes to sRGB.
- Base view returns the untouched Base sample. Lit with lighting disabled also returns that sample before exposure or relighting.

## Calibration Model

Central parameters in `lightingModelConfig`:

| Parameter | Value |
| --- | ---: |
| Sunrise / sunset | 06:00 / 18:00 |
| Daylight start / full daylight | -0.12 / 0.98 solar elevation |
| Dawn / noon / dusk azimuth | 35 / 90 / 145 degrees |
| Night / day elevation | 18 / 64 degrees |
| Night / day exposure | 0.90 / 1.00 |
| Night / day key intensity | 0.52 / 0.92 |
| Night / day ambient intensity | 0.30 / 0.58 |
| Diffuse wrap / threshold / softness | 0.08 / 0.58 / 0.24 |
| Painted band strength / threshold / softness | 0.38 / 0.84 / 0.20 |
| Relight strength | 0.90 |

The night state still receives a low-elevation Normal-driven key and colored sky fill; exposure is only one part of the model. The encoded Normal v3 green channel is down-positive, so the shader flips Y when decoding it for lighting. No specular response, PBR, real shadows, or Bloom is used.

## Debug Coverage

- Slider range 0-1440, one-minute step, `HH:mm` readout, and 00:00 / 06:00 / 12:00 / 18:00 / 24:00 ticks.
- Dawn / Noon / Dusk / Night shortcuts select 06:30 / 12:00 / 17:30 / 22:00.
- Time changes update lighting immediately. Manual exposure, relight strength, direction, elevation, key / ambient intensity and colors remain available.
- Key intensity control spans 0-1.2 and ambient intensity 0-0.8 so the entire model output can be adjusted without an out-of-range thumb.
- No system time synchronization or playback is included.

## Visual Validation

Desktop Chromium / WebGL2 at 1440 x 900 was checked at 00:00, 06:30, 09:00, 12:00, 15:00, 17:30, 20:00 and 22:00. Captures are written to `%TEMP%\r2a1-HHMM.png`. The slider label and value were verified at every point, and the WebGL2 renderer initialized without page console errors. Base versus Lit with Lighting disabled was read directly from the WebGL canvas and matched exactly (maximum RGB delta 0).

The model directions at the requested sample times are: 00:00 (90, 18), 06:30 (36, 24), 09:00 (63, 57), 12:00 (90, 64), 15:00 (118, 57), 17:30 (144, 24), 20:00 (137, 18), and 22:00 (117, 18), as azimuth / elevation degrees. The model also reports daylight / warmth values of 0.000 / 0.000, 0.132 / 0.614, 0.846 / 0.062, 1.000 / 0.000, 0.846 / 0.062, 0.132 / 0.614, 0.000 / 0.000 and 0.000 / 0.000 at those respective points. The light parameter curve is continuous and 00:00 equals 24:00.

Visual review remains **not accepted**. Current captures keep facial features readable and show no plastic/specular effect, but Dawn / Dusk structure separation is still weak, Dawn / Dusk faces and clothing read too dark, and Night is still perceived predominantly as a darker/cooler scene rather than a clear Normal-driven structural lighting state. Measured mean RGB difference over the artwork area was 2.07 for 06:30 vs 17:30, 0.32 for 09:00 vs 15:00, and 54.22 for Noon vs 22:00; the last comparison is dominated by the overall night luminance shift. The frozen Normal v3 has very small XY deviation across large parts of the character, limiting global directional structure without stronger/stylized treatment. Do not describe R2A.1 as visually accepted or begin R2B based on this calibration.

## Result

R2A.1 implements the requested continuous manual calibration model, but the current visual calibration does **not** satisfy the user's structure-difference goals. The screenshots and values are ready for human review; do not add automatic time, interpolation playback, post processing, or other animation until the user accepts the lighting calibration.
