# R2A.5 Registered Sky Runtime Integration

Status: runtime integration complete; pending final human visual acceptance. R2B has not started.

## Scope

This round connected the accepted 1672x941 sky assets to the WebGL2 Runtime Lighting path. Base Albedo, Normal v3, Artwork Space, Blink, Leaves, the 24H slider structure, solar trajectory, sunrise/sunset, and the Vue/engine boundary were unchanged.

## Sky Layer

`src/config/sky.ts` owns the typed `SkyState`, registered asset URLs, four keyframes, and the continuous `skyFor(minutes)` function. The keyframes are Dawn at 06:30, Noon at 12:00, Dusk at 17:30, and Night at 22:00. Adjacent phases are interpolated with a smoothstep curve. The final Night -> Dawn segment wraps across midnight; 00:00 and 24:00 therefore resolve to the same state.

`HeroCanvas` loads and dimension-checks all four RGBA assets before creating `BaseRenderer`. The renderer binds them as four independent textures and passes the selected phase pair and mix amount to `hero.frag.glsl`. The current slider time drives both `lightingFor(minutes)` and `skyFor(minutes)`, so dragging the slider changes Runtime Lighting and the sky continuously rather than hard-cutting between buttons.

Each sky PNG already contains the alpha authored by `sky-mask.png`. The shader composites that alpha once and does not multiply the separate mask again. Sky compositing is limited to the Lit path after relighting, exposure, and tone mapping; Base view, Normal view, and Lighting-off Lit return before Sky is evaluated.

## Upper-scene A/B decision

The previous `upperSceneAttenuation` was an interim compensation for the open sky and upper background in the Base artwork. With the registered sky layer enabled, the default `duskUpperSceneAttenuation` and `nightUpperSceneAttenuation` are both `0`. This removes duplicate darkening from `dark sky asset + vertical attenuation`. The shader uniform remains available for controlled future calibration, but the current Sky-on result does not depend on it.

## Browser integration checks

The running page was inspected in Edge at `http://localhost:5173/` in WebGL2 Lit mode. No shader, console, or WebGL fallback errors were observed.

| Time | Runtime observation |
| --- | --- |
| 06:30 | Cool, readable dawn sky with restrained warm low-angle lighting. The character and architecture remain legible. |
| 12:00 | Pale gray-blue sky and stable neutral daylight. The face and white shirt remain controlled without obvious clipping. |
| 17:30 | Gray-blue upper sky transitions to muted warm gray/rose-apricot near the lower openings; the warm key does not wash the whole image orange. |
| 22:00 | Deep charcoal blue-gray sky replaces the Base's daytime blue. The face, white shirt, and stone foreground remain readable while the distant scene reads as night. |

Intermediate checks at 00:00, 09:00, 15:00, and 20:00 showed continuous phase changes without visible hard cuts. 00:00 and 24:00 displayed the same sky and lighting state. The Debug `Sky on/off` control restored the previous Base-sky result when disabled and re-enabled the registered layer correctly.

## Edge review

The Sky-on artwork was inspected around tower tips, roof lines, vines and thin leaves, the hat, hair silhouette, and antialiased architectural edges. No obvious halo, white fringe, daytime-blue residue, sky leakage onto the character/buildings, or mask seam was observed at normal page scale. The authored soft alpha remains the sole sky edge control; the separate grayscale mask is not multiplied at runtime.

## Invariants and exclusions

The shader still returns the sampled Base immediately for Base view and for Lit view with Lighting disabled, preserving the existing Base / Lighting-off invariant. No Base or Normal asset was edited. No system-time sync, playback, one-minute day, Bloom, Emission, Breathing, Hair Motion, Leaves v2, new runtime mask, or R2B behavior was added.

`pnpm build` passed after the integration. This round is ready for human visual acceptance; do not freeze the combined visual baseline or begin R2B until that acceptance is given.
