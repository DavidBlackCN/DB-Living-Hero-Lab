# R2A.5d Dawn / Night closeout and Sky Timeline

Status: Noon and Dusk accepted by human review; Dawn, Night, and the corrected 24H Sky Timeline are ready for final human acceptance. No later phase or animation work was started.

## Scope and changes

The accepted Noon and Dusk lighting parameters were preserved. The 12:00 screenshot is pixel-identical to R2A.5c; the 17:30 artwork differs by no more than one 8-bit channel level after the linked Dawn changes. The Sky assets, artwork, Normal, Blink, Leaves, and UI layout were not edited.

At 06:30, Dawn ambient rose from `0.368` to `0.411`, exposure from `-0.023` to `+0.025 EV`, and the key color became slightly more neutral/warm against the same cool gray-blue ambient. The key strength remains `0.528` and relight `0.967`. The scene is lighter without losing the cool early-morning atmosphere.

At 22:00, a deep-night-only solar-elevation weight reduces key strength from `0.200` to `0.175`, lifts ambient from `0.140` to `0.165`, and shifts ambient RGB from `(0.28, 0.36, 0.62)` to `(0.36, 0.47, 0.72)`. Exposure remains `-0.220 EV` and relight `0.970`. This adds stable blue-gray fill to the face, white sleeves, dark vest, and stone without turning the scene back into dusk. The adjustment fades out before the accepted Noon and Dusk anchors.

The old `skyFor()` interpolated directly from the 22:00 Night preview shortcut to the next 06:30 Dawn shortcut. It therefore began brightening immediately after 22:00. The shortcuts remain 06:30 / 12:00 / 17:30 / 22:00, but sky phase changes now use separate hold and transition windows:

| Time | Sky behavior |
| --- | --- |
| 00:00–05:00 | Night hold |
| 05:00–06:30 | Night → Dawn, smoothstep |
| 06:30–08:00 | Dawn → Noon, smoothstep |
| 08:00–16:00 | Noon hold |
| 16:00–17:30 | Noon → Dusk, smoothstep |
| 17:30–20:00 | Dusk → Night, smoothstep |
| 20:00–24:00 | Night hold |

The 24H Lighting model was checked separately. It still derives daylight and twilight continuously from solar elevation; the four preview shortcuts do not act as its phase boundaries. Deep-night exposure, key and ambient are stable at 22:00, 00:00, 02:00 and 04:30. Only the existing low-energy light direction continues its smooth nocturnal arc.

## Visual and runtime checks

The running Edge/WebGL2 Lit/Sky-on page was captured at 1440×900 at all requested times: 00:00, 02:00, 04:30, 05:30, 06:30, 08:00, 12:00, 16:00, 17:30, 20:00, 22:00, and 24:00. The full [timeline contact sheet](r2a5d-final/timeline.png) shows no sky hard cut. `skyFor()` returns the same Night/Night hold state at 22:00, 00:00, 02:00, 04:30 and 24:00. Both `skyFor()` and `lightingFor()` return identical states at 00:00 and 24:00.

- Final anchors: [Dawn 06:30](r2a5d-final/dawn.png) · [Noon 12:00](r2a5d-final/noon.png) · [Dusk 17:30](r2a5d-final/dusk.png) · [Night 22:00](r2a5d-final/night.png) · [four-phase sheet](r2a5d-final/contact.png)
- Night continuity: [22:00 / 00:00 / 02:00 / 04:30 sheet](r2a5d-final/night-continuity.png)
- The diagnostic artwork mean luminance across those four night captures is `0.01673 / 0.01674 / 0.01682 / 0.01692` in linear light. There is no post-22:00 sky brightening; the small image variation comes from the existing light-direction arc.

`pnpm build` and `pnpm typecheck` passed. Await human acceptance before freezing the combined visual baseline or entering R2B.
