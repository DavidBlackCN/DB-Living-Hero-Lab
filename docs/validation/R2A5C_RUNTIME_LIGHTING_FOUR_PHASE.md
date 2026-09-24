# R2A.5c Runtime Lighting four-phase calibration

Status: three visual iterations complete; ready for human visual acceptance. This does not freeze the art baseline or start R2B.

## Comparison before editing

The current project's WebGL2 Lit/Sky-on baseline was captured at 1440×900 at the four fixed anchor times. It was compared with the four Kumeng screenshots supplied for this round. The references show a cool, quiet dawn; a bright but textured noon; an amber/rose low-angle dusk with cooler shadow; and a deep blue-gray night with a readable face. The projects use different characters, architecture, palettes, and authored skies, so the target is comparable phase separation rather than identical color or exposure.

In the project baseline, Dawn and Dusk had nearly the same lightness and rose/gray balance. Noon was the brightest but its white shirt, face, and pale stone looked somewhat lifted. Night had a dark sky but the lit figure and railing remained comparatively bright. The baseline contact sheet is [here](r2a5c-baseline/contact.png).

## Iteration log

All captures used the running Vite page in Edge headless at 1440×900, with `Mode: WebGL2`, `Render view: Lit`, Lighting on, and Sky on. Each iteration contains individual captures for 06:30, 12:00, 17:30, and 22:00.

| Round | Adjustment | Visual finding |
| --- | --- | --- |
| [1](r2a5c-round-1/contact.png) | Strongly reduced dawn/noon/night energy, raised dusk key, strengthened cold/warm colors, and made relight vary with time. | Deliberately overshot: dawn looked like a dark overcast scene, night lost the face and shirt. Dusk still leaned pink. |
| [2](r2a5c-round-2/contact.png) | Restored dawn fill/key and night fill; shifted dusk key toward amber and kept a cooler fill. | Dawn and night became readable, Noon stayed controlled, but Dusk was still too similar to ordinary warm daylight. |
| [3](r2a5c-round-3/contact.png) | Increased the existing twilight color curve's contribution, strengthened the dusk key and warm fill, and added a little night ambient. | Dawn is cool gray-blue, Dusk shows clear amber low-angle light, Noon remains brightest with clothing/stone detail, and Night is deep while the face, sleeves, and silhouette remain readable. |

## Final effective anchor states

These are the actual `lightingFor(minutes)` outputs at each anchor, rounded for reporting. Colors are linear light multipliers in RGB order. The config values can differ because the model blends day, night, and twilight curves.

| Time | Exposure | Relight | Key intensity / RGB | Ambient intensity / RGB | Band |
| --- | ---: | ---: | --- | --- | ---: |
| Dawn 06:30 | -0.023 EV | 0.967 | 0.528 / (0.822, 0.887, 0.999) | 0.368 / (0.283, 0.456, 0.770) | 0.277 |
| Noon 12:00 | -0.420 EV | 0.950 | 0.640 / (1.000, 0.980, 0.940) | 0.380 / (0.600, 0.700, 0.880) | 0.300 |
| Dusk 17:30 | -0.052 EV | 0.984 | 1.005 / (0.959, 0.623, 0.335) | 0.379 / (0.556, 0.430, 0.514) | 0.277 |
| Night 22:00 | -0.220 EV | 0.970 | 0.200 / (0.560, 0.700, 1.000) | 0.140 / (0.280, 0.360, 0.620) | 0.165 |

`relightStrength` now follows daylight from 0.97 at night to 0.95 at noon, with a smooth dusk boost peaking near the low sun. The final 17:30 value is 0.984. No new mask, region, shader pass, or sky asset was introduced. The existing Normal-driven shader, ACES display transform, registered Sky Layer, solar direction, and 24H slider remain in use.

## Final captures and checks

- [Dawn 06:30](r2a5c-round-3/dawn.png) · [Noon 12:00](r2a5c-round-3/noon.png) · [Dusk 17:30](r2a5c-round-3/dusk.png) · [Night 22:00](r2a5c-round-3/night.png)
- [Four-phase contact sheet](r2a5c-round-3/contact.png) and [intermediate-time contact sheet](r2a5c-round-3/intermediate.png) covering 00:00, 09:00, 15:00, 20:00, and 24:00.
- `lightingFor(0)` and `lightingFor(1440)` return identical state values. Intermediate states transition smoothly from dawn to noon and from dusk to night. The screenshot capture also confirmed WebGL2 Lit/Sky-on operation at each anchor and intermediate time.
- Using the existing luminance diagnostic regions, Noon shirt p95 fell from 0.646 to 0.593 linear luminance with no near-white pixels; Night background architecture mean fell from 0.0317 to 0.0112. These figures support the visible reduction in lifted highlights and the deeper night, but visual review remains the acceptance measure.

The final scene does not exactly match the Kumeng reference: the frozen autumn school artwork keeps warm leaves and a different sky silhouette, and its night lighting is darker on the uniform. The face, white sleeves, and character outline still read at full size. The four phases are distinct without relying on the debug labels, so this is ready for human acceptance. Do not begin R2B until that acceptance.
