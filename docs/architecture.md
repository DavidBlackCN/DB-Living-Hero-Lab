# Living Hero architecture

## Current phase: Micro Animation / Living Scene Convergence

Lighting is FROZEN / ACCEPTED. Bloom and Coffee Steam are IMPLEMENTED.
Blink is IMPLEMENTED / ACCEPTED / FROZEN, including human desktop acceptance.
Code-only Breathing is the current default-OFF experiment, EXPERIMENTAL / awaiting
human acceptance. Hair Motion, Complex Parallax and Advanced particles remain
optional/deferred. Migrate into DB-Blog-Plume only after Living Hero Engine freeze.
The dated lighting calibration sections below retain historical design context;
they do not authorize changes to the accepted light fields or technical maps.

## Experimental Breathing

`breathing.ts` contains a timer-free phase accumulator and a compact GLSL influence
function. `setBreathing` defaults to false. `setSettings` accepts
`breathingStrength` (0-2 original-art pixels, default 1.8) and `breathingCycle`
(5-6 seconds, default 5.4). `getState` reports the requested switch and phase.
The existing renderer tick drives a cosine-eased neutral -> peak -> neutral lift.
Steam keeps its original wall-clock `uMotionTime`; Breathing uses a separate
phase uniform fed by the same scheduler so hidden elapsed time is never consumed.
Motion gates reset deformation to neutral; visibility/context loss pauses it.

Support is an ellipse centered at (681,380), radii (72,60), in 1200 x 675 artwork
coordinates, multiplied by squared radial falloff, inset cloth-only semantics and
a smooth x=645..662 exclusion for the dangling front lock. It lies entirely in
the garment interior, below neck/shoulders and above waist/hands/book. Missing
character masks or disabled refinement make Breathing neutral rather than guessing.

Pigment, normal, character semantics, optional correction and garment contact
(light-shaping B only) sample the same deformed material UV. Scene geometry,
light-shaping R/G, lamp/window positions and all frozen coefficients remain in
screen UV. The small warp transports existing normals rather than reconstructing
3D surface orientation. Original Base remains static; Breathing Weight shows
the spatial envelope independently of animation phase. No texture/pass/framebuffer
or GPU asset memory is added. [Prototype record](logs/breathing-prototype.md).

## Current: registered Blink (2026-09-20)

`animation.ts` owns the timer-free BlinkController and metadata validation.
`blinkMetadataUrl` is optional for portable engine consumers; the demo supplies
the approved 700 x 470 overlays. RGBA8 textures occupy units 7/8 (2.51 MiB total).
Metadata defines canvas dimensions, top-left crop registration, straight alpha,
sRGB and relative state paths. Loading rejects incompatible dimensions/bounds.

The fragment shader replaces base pigment within that crop before correction,
linearization, relighting and bloom extraction. Pigment-dependent light
classification (forehead protection and baked highlight suppression) deliberately
keeps reading the original source, preserving the frozen normal/light fields.
Original Base bypasses Blink. No light coefficients, masks, normals or passes change.

The renderer advances the controller on its existing clock: Half 40 ms, Closed
70 ms, Half 50 ms, Open; idle waits are randomized to 2800-5500 ms. Only active
blinks request animation frames; idle scheduling shares the existing timeout with
steam/realtime. `setBlink` and `triggerBlink` are the only new operations;
`blinkAvailable`, `getState().blink` and `blinkPhase` expose status. Animation-off
or reduced motion resets Open, visibility loss pauses the controller's clock,
and destroy cancels the shared scheduler and deletes both textures.
See [asset/validation notes](logs/blink-runtime.md). Older dormant-contract
descriptions below are historical.

## Current: code-only salvage (2026-09-18)

`lamp-fields.ts` owns compact near/desk/character receiving fields; Scene B remains
the emitter. Near illumination has a broad underside/bounce response, independent
of directional desk/character response. Contact, normal form and semantic scene
visibility are distinct levels in the same scene pass. `sceneVisibility` excludes
part of the rear beam from front torso and shelf recesses without shifting masks.
Projected debug now reports the visible contribution. Lamp Fields maps R/G/B to
near/desk/character with white emission. No render target or texture is added.
See [salvage decisions and measurements](logs/code-only-lighting-salvage.md).

## Current: incident light layers (2026-09-18)

`light-layers.ts` contains the logical ambient/window/projection/lamp/emission
composition used by the existing scene shader. It supersedes aggregate final
attenuation described below. Each incident source has its own contact visibility;
emission stays independent. Whole-room fill and soft normal bands share time and
direction. No new framebuffer, runtime texture or dependency is introduced.
Shadow debug measures removed incident energy; ambient, form and contact views
isolate the new structure. The Shadow slider controls occlusion; Stylized,
softness and normals control form. [Implementation, checks and performance limits](logs/light-layer-review.md).
All calibration sections below describe earlier revisions.

Latest region correction: `lampSill` now follows the physical shelf rather than
crossing the window apron; `penHolderReceiver` covers the tool holder body.
This fixes an indoor receiver stripe which exterior-only tests missed. Glass
coverage and shader behavior are unchanged. See [window interior fix](logs/window-interior-fix.md).

## Spatial convergence 3 — historical calibration

Glass anchors now live in `docs/window-glass.json`; the asset generator applies
an outer polygon clip and an inward-only edge transition. The normal/correction
generator derives glass exclusions from the same anchors.

Contact softness is authored per path. The existing Shadow control now also
attenuates direct lamp energy at contacts and controls room access/form shading.
Total aggregate attenuation is capped at .30; face contact remains capped at .025.
The rear-right lamp pool and sill receiver have been recalibrated. No passes,
textures, dependencies or public API were added. Full current coefficients,
validation and limits: [spatial convergence 3](logs/spatial-convergence-3.md).
The calibration sections below are historical and superseded where noted here.

## Lighting / Shadow Convergence — latest calibration

The current spatial lamp uses a reading pool at (.825,.735), radius (.20,.115),
a rear/right subject pool at (.78,.49), radius (.085,.20), and a local sill pool
at (.82,.49), radius (.13,.105). Source-authored Scene G now includes the sill,
tools, picture frame and vase at restrained receiving weights. Exterior Scene R
and the normal maps are unchanged. The signed rear offset and soft lamp wrap
from Convergence 2 remain; the wider foreground tail is reduced.

`Settings.shadow` (0–1, default .65) controls a lightweight shading stage inside
the existing fragment pass. It combines B-channel registered contact strokes,
wide normal-based dark sides and soft attenuation outside the daylight/lamp
fields. Existing book/coaster contacts are retained in B; new detail strokes are
clipped to their source-authored receiving surfaces. Face volume is excluded,
face contact is capped at .025 before the strength multiplier, and total added
attenuation is capped at .22. No extra texture or framebuffer pass is introduced.

Shadow debug composes the new attenuation with existing broad daylight/night
occlusion. It is a fixed-scale darkening amount (bright means more attenuation),
not a shadow map. Setting shadow=0 disables the contact/volume enhancement;
existing day/night spatial illumination remains. Lamp debug still shows the raw
lamp coefficient before aggregate shadow/face/highlight corrections; Neutral
shows the resulting combined lighting. See [current review](logs/lighting-shadow-convergence.md).

## Technical Art Alignment — current implementation

This section supersedes historical defaults below. The app now uses registered
normal v2 by default; `?normal=registered`/`v1` selects v1 and `?normal=low-frequency`
selects the earlier SVG. Engine structure, artwork UVs and pass count are retained.

Directional sunlight, projected aperture and lamp reflection all use the decoded
normal. Projection multiplies its existing access/receiver field by N·L. Lamp
reflection uses an aspect-correct direction toward the source lamp. Lighting
Convergence 2 changes its Z offset to -.08 (behind the figure), uses a wide soft
diffuse wrap, and keeps emission separate. The smaller subject pool favors the
right side while the upward-facing desk retains a broad local pool. See
[current calibration](logs/lighting-convergence-2.md); the earlier
[integration details](logs/normal-light-integration.md) describe the first version.

Room participation reuses light-shaping G for five soft source-authored receiving
weights (wall, books/shelf edge, chair surroundings, foreground). The existing
window aperture is evaluated on a foreshortened upright receiving plane, using
the same time-driven origin, axis, width and energy. It adds weak normal-aware
window light only where G permits, with longer reach than the tabletop aperture.
This is not global ambient, atmospheric scattering or physical ray tracing.
Scene-mask/exterior coverage, main subject projection and normal assets are unchanged.

Optional `correctionUrl` must match base dimensions. It is a grayscale signed EV
gain map: `EV=(R*255-128)/254`, applied as `linearBase*exp2(EV*correction)` before
lighting. The scalar gain does not displace, resample or repaint the base. Unit 6
uses R8; absent maps use a neutral one-pixel placeholder. Opt-in texture memory
is 105.15 MiB versus the normal 97.24 MiB. There is no added pass. `correction`
defaults to 0 in the engine; the demo enables it only at `?correction=1` and
provides a debug checkbox. `correctionAvailable` identifies availability.

Debug `lamp` displays the raw linear lamp coefficient (before global corrections),
`directional` displays directional luminance ×0.6, `correction` displays .5+EV,
`correctedBase` shows the active corrected base. Original `base` bypasses all
correction; zero correction is tested pixel-identical to an absent map.

Current defaults: normal 1, face .85, hair .95, cloth .94, stylized .50, softness
.18. Dawn has an explicit 06:00 projection key and lower-angle direction; noon
keyframe is unchanged; dusk balances lower ambient with warm direct light.
All preceding window geometry and contact-shadow constraints remain in force.

## Current review update — 2026-09-16

The historical baseline below is retained for context. Current glass/receiver
semantics, projected-light algorithm, validation and constraints are documented
in [spatial-light-review.md](logs/spatial-light-review.md), superseded for desk
receivers and shadows by [desk-light-review.md](logs/desk-light-review.md).

- `lighting.ts` exports `projectedLightAt` for continuous artwork-directed daylight.
- `renderer.ts` uploads its geometry/shape/energy; `shaders.ts` evaluates two soft
  aperture lobes in aspect-correct image coordinates and gates them by receivers.
- Scene R is source-edge glass coverage with native raster antialiasing, no erosion. Scene G
  is indoor receiver coverage, including hands/book/cup/stacked books/chair as well as desk.
  Hair/clothing occlude the desktop; hands are included at full receiving coverage.
  Scene B remains lamp emission.
- Optional `lightShapingUrl` supplies a 1200×675 RGB map: R window access, G soft
  room receiving weights, B contact occlusion on desk, character and sill. G previously exported unused
  desktop coverage; custom maps must now use G=0 to disable room participation
  or author registered room weights. Book/coaster B remains clipped to exposed
  desktop; new B detail bands are clipped to their own receiving contours.
  It occupies texture unit 5;
  bloom remains on unit 4. Total source texture storage is nominally 97.24 MiB.
  No rendering pass was added. Aspect ratio is validated; registration still
  requires source inspection. Existing consumers can omit this optional map.
- Projection includes a mullion gap and reduced light outside the aperture.
  Translated silhouette shadows were removed: without receiver height they painted
  detached shadows across the hand/pages. Contact darkening is restrained and
  source-registered. Night separately combines quiet room ambient, window-side
  cool spill and a warm desk/subject lamp pool continuous over foreground sleeves.
- Flower occlusion is generated offline by Python/Pillow/NumPy within the source
  JSON ROI and embedded in the scene SVG; there is no new runtime texture/pass.
- Neutral is fixed-scale grayscale luminance (×0.6); Projected is raw projection.
- Exterior Mask shows exact scene R; Shadow / Occlusion shows the combined
  authored darkening fields, not a physical visibility or depth buffer.
- The former dormant Blink contract is now the accepted registered implementation
  documented above; its earlier [asset plan](logs/blink-registered-plan.md) is historical.

The baseline sections below describe Phase 1, retained for the comparison path. **The current app loads the Phase 2 maps and uses the refinements documented at the end of this file by default.**

## Boundaries

- `src/app/`: app bootstrap, error/status reporting, viewport and panel styles.
- `src/debug-ui/panel.ts`: plain DOM controls. Calls the public engine API; contains no rendering logic.
- `src/engine/renderer.ts`: WebGL2 setup, texture loading/binding, uniforms, frame scheduling, lifecycle.
- `src/engine/timeline.ts`: local clock, 24h wrapping, shortest-path exponential time interpolation.
- `src/engine/lighting.ts`: periodic smoothstep keyframes for linear RGB ambient, window light, warm lamp; window-side light direction varies with time.
- `src/engine/shaders.ts`: full-screen triangle, registered analytic normals/masks, relighting and highlight shoulder.
- `src/engine/assets.ts`: base and optional normal/mask loading plus dimension validation.
- `src/engine/animation.ts`: accepted Blink controller and registered metadata validation.
- `src/engine/postprocessing.ts`: quarter-resolution bloom targets and separable blur passes.

## Rendering

One WebGL2 draw per update, three texture slots, no scene graph or framework runtime. The canvas fills the viewport. A centered contain viewport preserves the full 16:9 artwork; other aspect ratios show dark margins rather than crop/distort the scene. DPR is capped at 1.5.

The original image is an already lit illustration, **not albedo**. Convert sRGB to linear, multiply by spatially varying ambient + directional response, add a warm lamp contribution in the lighting coefficient, then apply exposure, a mild highlight shoulder and sRGB encoding. This is a relighting approximation, not physically correct inverse rendering. The lamp contribution does not cast shadows or use geometry-based occlusion.

Top-left UV coordinates match the original image: face center (0.608, 0.292), hair mass (0.605, 0.37), body (0.551, 0.585), lamp pool (0.795, 0.51). Soft ellipses approximate face/hair/body. Curved normals approximate face/hair; table has a broad tilted normal. Window contribution grows toward image right. Face safety floors low lighting coefficients locally; hair limits bright coefficients. These fields deliberately avoid shifting any image pixels. Mask view exposes their approximate coverage; they must not be mistaken for segmentation.

## Asset replacement

```ts
import { createLivingHero } from './engine/renderer';
const hero = await createLivingHero(canvas, {
  baseUrl: '/assets/hero-4k-digital-art.png',
  // Optional exact-registration 3840×2160 maps:
  // normalUrl: '/assets/generated/normal.png',
  // maskUrl: '/assets/generated/masks.png',
  onUpdate: state => console.log(state.minutes),
});
hero.setTime(1050);
hero.setRealtime(true);
hero.setSettings({ exposure: 0, ambient: 1, sun: 1, lamp: 1 });
hero.setDebugView('normal');
hero.setReducedMotion(true);
hero.setAnimation(false);
// On unmount:
hero.destroy();
```

Normal RGB is data encoded from [-1,1] to [0,1], +X right, +Y down, +Z toward viewer. Mask RGB = face, hair, body. Maps must match base dimensions. The same-size check cannot detect semantic misregistration; inspect overlays manually before acceptance. See `public/assets/generated/README.md`.

## Scheduling and motion

Manual times settle over a short exponential transition; midnight takes the short path. Realtime reads `Date` in the local timezone, then uses the same interpolation. When settled, manual mode stops requesting frames; realtime polls at one second. Background visibility cancels frame and polling callbacks, and foreground resumes from the current local clock. ResizeObserver wakes a redraw.

`prefers-reduced-motion` is read at initialization and observed for changes. Reduced motion or disabling the animation master skips interpolation and disables micro-animation. Steam is Final-view-only and independently toggleable. Blink is accepted and implemented in `animation.ts`; Bloom is implemented in `postprocessing.ts`. Breathing is the default-OFF experimental candidate; Hair Motion remains deferred. Hidden tabs pause the shared scheduler.

`destroy()` removes observers/listeners, cancels callbacks and deletes GPU resources. On context loss, the app pauses rendering; when the browser reports restoration, the app performs a full page reload so no invalid WebGL objects are reused. This is a safe recovery path; no-refresh resource reconstruction remains a later improvement. On initialization failure, a static CSS image is shown with the error and without working lighting controls.

## Phase 2: registered regions and night separation

The app passes `normalUrl`, `maskUrl` and `sceneMaskUrl` to the engine. `assets.ts` loads and validates all four images including the base. The renderer binds one additional scene-mask texture; it remains a single render pass. The four source/map textures use RGB8 because alpha is unused, nominally using about 94.9 MiB at 3840×2160 before framebuffer/browser overhead. Bloom targets remain RGBA8 at quarter resolution; no texture compression or mipmaps are currently used.

`docs/scene-regions.json` stores hand-authored Bézier/polygon contours in a 1200×675 reference view. `scripts/generate-scene-assets.mjs` creates three 3840×2160 SVGs under `public/assets/generated/`; regenerate with `npm run assets:generate`. The browser rasterizes these during image loading. Flat normals remain the default outside specified surfaces. This gives predictable alignment without modifying the base art, but does not claim a geometrically recovered normal field.

- Character RGB: face / hair / clothing. Hand areas are excluded from clothing; fine curls are not fully separated.
- Scene RGB: exterior / tabletop / lamp emitter. Hat, hair, lamp shade, picture frame, vase and pen cup contours subtract interior objects from the exterior region.
- Normal RGB: broad hair, face, clothing and table orientations; the shader decodes and normalizes the vectors.
- New periodic `night` keyframe weight controls exterior-specific dimming and gentle suppression of existing bright interior highlights. It is independent of lamp intensity, so switching the lamp off does not change the time of day.
- The lamp pool is blocked by the exterior mask; desk receiving strength is separate. This remains a soft illumination model without actual shadow rays.
- Face safety blends toward restrained neutral light instead of using the large ellipse's warm coefficient floor; face normals stay nearly flat to preserve eyes and linework.
- Hair/cloth settings scale directional response in their own regions. `night` setting scales nighttime suppression from 0 to 1.
- `setSettings({ refinement: 0 })` restores the Phase 1 analytic masks, normals and lighting behavior for comparison. `refinement: 1` restores Phase 2. Other common settings and current time are retained.
- `setDebugView('scene')` shows the scene RGB map; `setDebugView('overlay')` blends registered region colors over the unlit base for alignment inspection.

Optional maps are still optional for consumers of the engine. Without map URLs it uses analytic fallbacks; the demo app explicitly supplies all three generated maps. Bloom defaults to intensity 0.22, threshold 0.82 and radius 1.0, with face and broad-cloth protection. All original time, reduced-motion, visibility and destroy APIs remain intact.
