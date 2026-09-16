# Window registration and spatial light / shadow review

2026-09-16. Based on `bef0321`; continues the existing engine and approved artwork.
Review images: [local gallery](../screenshots/spatial-light-review/README.md).

## Phase A — diagnosis

- Morning's former axis `[-.13,.99]` ran almost vertically down the far right of the image. It missed the sampled book and shoulder. Broad ambient and positive-only projection further hid the difference.
- Night retained directional energy, high ambient and a broad lamp ellipse. It lacked distinct window access, local receivers and occlusion, so the result looked like a global grade.
- The glass source polygons were still approximate at the vertical mullion and lower edge. The frame exclusion was oversized. A .65-reference-pixel erosion plus .45 blur then introduced an uncovered seam. Earlier tests sampled too far from the edge to detect it; passing them did not establish precise registration.

Read the existing requirements, architecture/assets, engine, shaders, generated-map code, visual tests and recent window/directional/projection history before editing. The source illustration remains the visual truth; no character pixels or composition were changed.

## Phase B — source glass correction

`docs/scene-regions.json` remains the sole editable contour definition. It already had separate `windowGlassLeft` and `windowGlassRight`, so another mask hierarchy was unnecessary.

- Re-measured the native-source metal/glass transition, then authored a piecewise contour following the slightly leaning right mullion and rising lower edge. Recalibrated the left pane's lower edge and the picture-frame exclusion.
- Removed the entire glass erosion/blur filter. The path now gets native raster antialiasing only. Final, Scene, Overlay, exterior exclusion and Exterior Mask all consume exactly scene R. No UV threshold or boundary workaround was introduced in the shader.
- Restricted petal extraction to source-colored bright seeds and nearby coverage, plus one explicitly registered shaded-petal seed. This removes false opaque background islands made by the broad search ROI; it is still an approximate fine-foreground extraction.
- Added independent native-pixel edge probes: 6 vertical and 4 lower-edge pairs sampled 3 pixels on either side. Glass coverage is 247–255; frame coverage is 0. Existing checks also scan the lower strip and exclude frame, sill and indoor objects.
- Added `Exterior Mask` view and full-height right-pane / lower-window screenshots. These isolate actual glass coverage from the scene RGB display and from general night ambient.

Phase B checks passed: typecheck, build, 7 unit tests and 26 visual tests. Its screenshots remain in `mask/acceptance/`.

Conclusion: the reported broad frame seam and below-frame exterior spill are corrected at source level in the inspected areas. Pixel probes and closeups support that conclusion; they do **not** prove every translucent petal, fine stem or hair is perfectly segmented.

## Phase C — receiving light and shadow

### Day

Retained the two soft aperture lobes, aspect-correct coordinates and existing material/scene receivers. Added a soft mullion energy gap. Outside the aperture, receiving areas lose part of the ambient/directional contribution; raised-object coverage translated along the light direction adds a soft cast shadow on indoor receivers. Direct beam energy also falls in those shadows. This makes the projection toggle change both light and dark structure.

| Time | Structure |
| --- | --- |
| 08:00 | Narrow diagonal path `[-.70,.714]`, from the window-side hair/shoulder toward book and desk; perceptible morning energy |
| 12:00 | Higher origin, steeper axis `[-.42,.907]`, broader and more neutral aperture, strongest region further right on the desk |
| 17:30 | Shallower axis `[-.90,.435]`, longer reach across upper body/book/table and the strongest beam; accompanying backlit-side darkening |
| 23:00 | Projection energy and solar RGB are zero; no daytime beam |

### Night

Reduced night ambient. Interior darkness follows source-authored window access, with subdued cool spill near the window. The warm lamp has a desk pool and a smaller window-side subject pool; both are gated by receivers, exterior exclusion and a lamp-directed cast-shadow field. Book/cup contact occlusion anchors these objects to the desk. The lamp emitter gets a separate local response. Face safety keeps expression readable without restoring daytime brightness.

### Data / cost

`light-shaping.svg` is a 1200×675 RGB data texture generated from the same regions:

- R: broad window access, authored gradient rather than full-scene tint.
- G: existing raised-object contours with a 4.5-reference-pixel penumbra. One shifted sample avoids the stepped duplicate outlines seen in the initial three-sample trial.
- B: book/cup contact bands with a 2.2-pixel blur.

No new render pass. One optional texture on unit 5, two additional samples in the spatial path; unit 4 remains Bloom. Nominal source texture storage increases by 2.32 MiB to 97.24 MiB. This is an art-directed two-dimensional shadow approximation; there is no recovered depth or true shadow map.

### Measured behavior

Projected-light centroids in a 1200×675 view: morning `(843,496)`, noon `(960,515)`, dusk `(815,451)`. After normalizing away total intensity, mean spatial differences are .985 morning/noon and 1.096 noon/dusk. Morning sampled book and shoulder direct-light values are .040 and .045; both had effectively missed the old path. Night projected maximum is exactly zero.

In the sampled indoor rectangle, projection-on versus projection-off at fixed Neutral scale gives:

| Time | Pixels brightened > .015 | Pixels darkened > .02 |
| --- | --- | --- |
| 08:00 | 14.7% | 68.0% |
| 12:00 | 12.6% | 70.7% |
| 17:30 | 34.8% | 42.7% |

These are diagnostic sample fractions, not subjective quality scores. Night Lighting view confirms glass B>R, lamp pool R>B, pool brighter than room; disabling the lamp leaves glass samples identical with Bloom disabled. Final and same-weight grayscale captures are supplied for human assessment.

## Files and reasons

| Files | Change / reason |
| --- | --- |
| `docs/scene-regions.json` | Correct glass/frame contours and petal seed settings; author access/contact regions |
| `docs/window-edge-probes.json` | Independent original-art edge observations for regression checks |
| `scripts/generate-scene-assets.mjs` | Remove erosion, generate registered light-shaping channels |
| `scripts/generate-flower-occlusion.py` | Restrict petal coverage to source seeds; remove background-shaped islands |
| `public/assets/generated/scene-masks.svg`, `window-flower-occlusion.png`, `light-shaping.svg` | Regenerated runtime data, not QA images |
| `src/engine/lighting.ts` | Morning/noon/dusk geometry/energy, zero night solar energy and lower night ambient |
| `src/engine/shaders.ts` | Aperture shadows, cast/contact occlusion, separated night lighting and isolated diagnostics |
| `src/engine/assets.ts`, `renderer.ts`, `src/app/main.ts` | Optional shaping texture, ratio check, upload/binding and actual texture-size statistics |
| `src/debug-ui/panel.ts` | Two diagnostic choices; no new tuning sliders |
| `tests/timeline.test.mjs` | Night solar-energy regression |
| `tests/visual/window-light.visual.spec.ts` | Four-times/seven-views capture, close edge probes, spatial/receiver tests and paired light/shadow/night tests |
| `tests/visual/hero.visual.spec.ts`, `performance.spec.ts` | Updated texture budget and measurement from runtime statistics |
| `scripts/summarize-spatial-review.py` | Arrange real captures with identical grayscale conversion and source/mask closeups |
| README, architecture, generated-assets README, screenshot index/gallery and this log | Current contracts, reproducible capture, acceptance evidence and limitations |

## Final validation

- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm test`: 7/7 passed.
- `npm run test:visual`: 27/27 passed, including actual browser GLSL compilation and WebGL error checks.
- `git diff --check`: passed. Both approved original-image SHA-256 values match the starting version.
- Performance JSON is local under `final/performance/`; RAF timings are host/browser scheduling measurements, not a claim of GPU render time or guaranteed 60 fps.
- This run measured median RAF intervals of about 33.3 ms at DPR 1 and 66.7 ms at DPR 1.5 (Bloom on). The earlier local DPR 1.5 sample was about 50 ms, so this host shows a performance cost despite no added pass. Desktop hardware/browser profiling remains necessary before integration; the current result does not meet a demonstrated 60 fps target.
- Test-owned Vite process required explicit termination after tests on this Windows host to complete Playwright teardown. Only the PID launched by that test invocation was stopped.

Screenshots/metrics remain ignored by existing `.gitignore`. Keep before, mask and final evidence locally; transient failed test output and exploratory inspection crops can be deleted. Runtime textures remain versioned.

## Remaining limits / next step

The final grayscale captures show altered receiving/shadow structure, especially across shoulder, book and desk; night is substantially more separated. Normal fields are still broad. Fine hair, clothing folds, book curvature and cup volume cannot respond naturally with the current normals. The baked-in source illumination also remains and cannot be erased by multiplication.

After this human review, a carefully registered, higher-quality normal map is more useful than accumulating scalar shader controls. A modest height/receiver-depth field would later improve the cast-shadow approximation. Do not migrate to Blog or move to Blink before the core appearance is accepted. This round ends here; no Blink or other animation work was performed.
