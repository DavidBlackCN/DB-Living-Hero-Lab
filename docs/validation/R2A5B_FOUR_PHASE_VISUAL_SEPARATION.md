# R2A.5b Four-Phase Visual Separation Tuning

Status: parameter calibration complete; pending human visual acceptance. No R2B work was started.

## Scope

This round tuned the existing Runtime Lighting model after the registered Sky Layer integration. Base Albedo, Normal v3, Artwork Space, Sky assets, Blink, Leaves, the 24H slider structure, solar trajectory, sunrise/sunset, shader architecture, and the Vue/engine boundary were unchanged. No system-time sync, playback, Bloom, Emission, Breathing, Hair Motion, Leaves v2, or new mask was added.

## Parameter iterations

Two small parameter iterations were checked in the running WebGL2 page.

| Iteration | Problem | Change | Result |
| --- | --- | --- | --- |
| 1 | Dawn and Dusk were too close in atmosphere; Noon still needed restrained highlights; Night needed to remain clearly separated. | Split the shared twilight boosts into `dawnKeyBoost` / `duskKeyBoost` and `dawnAmbientBoost` / `duskAmbientBoost`. Calibrated Noon to `-0.46 EV`, Night to `-0.04 EV`, kept `upperSceneAttenuation` at `0`, reduced the shared band ceiling to `0.30`, and kept Dusk warmer than Dawn. | Noon highlights remained controlled, Dusk retained warm key plus cool fill, and Night remained distinctly darker with the registered dark sky. |
| 2 | Dawn was readable but still slightly too warm and heavy compared with the desired cool, clear morning reference. | Dawn key boost `0.42 -> 0.36`; Dawn ambient boost `0.24 -> 0.26`; Dawn key color `[1, 0.88, 0.78] -> [0.98, 0.86, 0.78]`; Dawn ambient color `[0.48, 0.60, 0.84] -> [0.42, 0.56, 0.84]`. | Dawn became cooler and lighter in character without losing the soft warm morning key. Noon, Dusk, and Night were not materially changed. |

## Final configuration

The final values are in [`src/config/lighting.ts`](../../src/config/lighting.ts). The four anchor states are:

| Anchor | Exposure | Key / ambient | Band | Visual intent |
| --- | ---: | ---: | ---: | --- |
| Dawn 06:30 | `+0.20 EV` | `0.51 / 0.34` | `0.28` | Cool ambient with restrained warm morning light |
| Noon 12:00 | `-0.46 EV` | `0.78 / 0.47` | `0.30` | Bright, neutral daylight with protected highlights |
| Dusk 17:30 | `-0.02 EV` | `0.70 / 0.39` | `0.28` | Warm low-angle key with cool ambient separation |
| Night 22:00 | `-0.04 EV` | `0.22 / 0.14` | `0.17` | Dark, cool, readable night scene |

`relightStrength` remains `0.90`; diffuse wrap, threshold, softness, and band threshold/softness were not changed in iteration 2. `duskUpperSceneAttenuation` and `nightUpperSceneAttenuation` remain `0`, because the registered Sky Layer already supplies the authored upper-background treatment.

## Browser checks

The local page at `http://127.0.0.1:5173/` was checked in Edge with the renderer confirmed as `WebGL2`, Render view `Lit`, and `Sky on/off` enabled. The four final anchor frames were captured and visually inspected in sequence:

- **06:30 Dawn:** cool gray-blue environment, readable face and shirt, with a restrained warm key. It reads lighter and clearer than Dusk.
- **12:00 Noon:** brightest and most neutral state. The white shirt, face, stone, and sky retain visible midtone detail without an obvious washed-out highlight.
- **17:30 Dusk:** warmer low-angle direction and rose/apricot sky remain distinct from Dawn; cool ambient fill prevents a whole-frame orange wash.
- **22:00 Night:** registered deep sky plus low physical light produce a clearly darker night state. Face, white shirt, stone rail, and character silhouette remain readable.

Intermediate checks at 00:00, 09:00, 15:00, and 20:00 were also performed with the same Lit/Sky-on state. The slider updated lighting and sky continuously, with no visible hard phase jump. The 00:00 and 24:00 endpoint behavior remains governed by the existing wrapped time model.

The browser page was accidentally returned to Base during one intermediate capture; that capture was discarded. The final check was repeated after WebGL2 recovered, and the final anchor observations above are from Lit mode.

## Decision

The four-phase separation is substantially improved and is ready for human visual acceptance. The implementation remains a calibration candidate rather than a frozen visual baseline until that acceptance is given. Do not begin R2B.
