# R2A Time-of-Day Keyframe Calibration

## Scope

Adds four manually selectable static lighting configurations on top of Runtime Lighting Foundation v1. This is a calibration surface only: there is no clock, interpolation, auto progression, emission, new mask, motion module, bloom, or post processing. Frozen Base Albedo and Normal v3 are unchanged.

## Architecture

- `src/config/lighting.ts` owns the `LightingPreset` type, four named configurations, and `createLightingState`.
- `LightingState.exposure` is applied after Normal-driven diffuse, key light, and ambient fill are combined. It participates in the lighting result rather than replacing it with a color filter.
- `DebugPanel.vue` exposes Dawn / Noon / Dusk / Night buttons and keeps the existing manual lighting controls. Selecting a preset resets the lighting state to that preset; manual changes afterward do not mutate the preset source.
- Base view returns the Base sample before lighting. Lit with Lighting disabled also returns the Base sample before exposure or any other lighting operation.

## Preset Parameters

Direction components are normalized in the shader; azimuth / elevation are shown for readability.

| Preset | Direction (azimuth / elevation) | Exposure | Key intensity / color | Ambient intensity / color | Wrap / threshold / softness |
| --- | --- | ---: | --- | --- | --- |
| Dawn | 175° / 51° | 0.98 | 0.32 / `#ffc79c` | 0.055 / `#dbc7d4` | 0.22 / 0.85 / 0.10 |
| Noon | 301° / 76° | 1.00 | 0.28 / `#fff5e6` | 0.040 / `#dbe8ff` | 0.24 / 0.86 / 0.12 |
| Dusk | 10° / 46° | 0.94 | 0.34 / `#ffa36e` | 0.050 / `#a8b8f0` | 0.20 / 0.84 / 0.10 |
| Night | 174° / 67° | 0.78 | 0.20 / `#b8ccff` | 0.070 / `#a3baff` | 0.28 / 0.80 / 0.16 |

## Validation

- `pnpm build`: passed before the visual check; rerun after the validation note cleanup.
- Desktop page check: passed at 1440 x 900. All four preset controls were present and selectable.
- Captures are available at `%LOCALAPPDATA%\Temp\r2a-dawn.png`, `%LOCALAPPDATA%\Temp\r2a-noon.png`, `%LOCALAPPDATA%\Temp\r2a-dusk.png`, and `%LOCALAPPDATA%\Temp\r2a-night.png`.
- The Lit capture means were Dawn `(128.8, 111.9, 105.4)`, Noon `(129.3, 113.1, 106.7)`, Dusk `(122.4, 107.0, 101.6)`, and Night `(103.3, 90.8, 86.9)` RGB. These are full-frame measurements, including the artwork background.
- Lighting-off Lit versus Base had a mean absolute RGB delta of `0.045` per channel at 1440 x 900. The two shader paths both return the Base sample before lighting or exposure; the small capture delta is consistent with frame/capture timing, not an intentional image treatment.
- Visual spot check: Night is visibly darker while face details remain readable; Dawn and Noon stay close, with Dusk warmer. No conspicuous embossed-face or plastic-highlight effect was observed. These are implementation observations, not final art-direction approval.

## Acceptance Boundary

These values are initial static calibration candidates, not approved art direction. Night uses reduced exposure together with a distinct Normal-driven key direction and diffuse response; exposure is not intended as a standalone darken/blue treatment. Review face readability, hair grouping, clothing volume, architecture, and overall restraint in the four page captures. Do not begin R2B 24-hour interpolation until the user approves these keyframes.
