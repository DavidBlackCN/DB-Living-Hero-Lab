# Living Hero architecture

## Current review update — 2026-09-16

The historical baseline below is retained for context. Current glass/receiver
semantics, projected-light algorithm, validation and constraints are documented
in [spatial-light-review.md](logs/spatial-light-review.md).

- `lighting.ts` exports `projectedLightAt` for continuous artwork-directed daylight.
- `renderer.ts` uploads its geometry/shape/energy; `shaders.ts` evaluates two soft
  aperture lobes in aspect-correct image coordinates and gates them by receivers.
- Scene R is source-edge glass coverage with native raster antialiasing, no erosion. Scene G
  is indoor receiver weight, including book/cup/stacked books/chair as well as desk.
  Scene B remains lamp emission.
- Optional `lightShapingUrl` supplies a 1200×675 RGB map: window access, softened
  raised-object silhouettes, and contact occlusion. It occupies texture unit 5;
  bloom remains on unit 4. Total source texture storage is nominally 97.24 MiB.
  No rendering pass was added. Aspect ratio is validated; registration still
  requires source inspection. Existing consumers can omit this optional map.
- Projection includes a mullion gap, reduced light outside the aperture and
  translated silhouette shadows on receivers. Night separately combines quiet
  room ambient, window-side cool spill and a warm desk/subject lamp pool.
- Flower occlusion is generated offline by Python/Pillow/NumPy within the source
  JSON ROI and embedded in the scene SVG; there is no new runtime texture/pass.
- Neutral is fixed-scale grayscale luminance (×0.6); Projected is raw projection.
- Exterior Mask shows exact scene R; Shadow / Occlusion shows the combined
  authored darkening fields, not a physical visibility or depth buffer.
- Blink remains a dormant contract; [the registered-asset workflow](logs/blink-registered-plan.md)
  describes the future pre-relighting composition seam without a current branch.

The baseline sections below describe Phase 1, retained for the comparison path. **The current app loads the Phase 2 maps and uses the refinements documented at the end of this file by default.**

## Boundaries

- `src/app/`: app bootstrap, error/status reporting, viewport and panel styles.
- `src/debug-ui/panel.ts`: plain DOM controls. Calls the public engine API; contains no rendering logic.
- `src/engine/renderer.ts`: WebGL2 setup, texture loading/binding, uniforms, frame scheduling, lifecycle.
- `src/engine/timeline.ts`: local clock, 24h wrapping, shortest-path exponential time interpolation.
- `src/engine/lighting.ts`: periodic smoothstep keyframes for linear RGB ambient, window light, warm lamp; window-side light direction varies with time.
- `src/engine/shaders.ts`: full-screen triangle, registered analytic normals/masks, relighting and highlight shoulder.
- `src/engine/assets.ts`: base and optional normal/mask loading plus dimension validation.
- `src/engine/animation.ts`: contracts and validation for future registered micro-animation assets; blink is intentionally disabled until an exact closed-eye asset exists.
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

`prefers-reduced-motion` is read at initialization and observed for changes. Reduced motion or disabling the animation master skips interpolation. The master also controls the first micro-animation, procedural coffee steam. Steam is Final-view-only, independently toggleable, and disabled by reduced motion or a hidden tab. Blink has a registered-asset contract in `animation.ts`, but remains disabled until an exact closed-eye asset exists. Breathing, hair motion and bloom are not implemented yet.

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
