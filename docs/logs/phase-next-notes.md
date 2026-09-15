# Phase Next Notes

Date: 2026-09-15

## Blink status

Blink renderer implementation: blocked by missing registered closed-eye asset.

The Pillow/NumPy/OpenCV experiment remains documented in `docs/logs/blink-tool-only-evaluation.md`. Its candidate was rejected visually and was not promoted to a runtime asset or renderer path.

## Bloom architecture

Bloom is implemented as a minimal WebGL2 post-processing path. The existing relit scene is rendered through a bright-pass into quarter-resolution targets, followed by two separable Gaussian blur passes and a final composite. The scene remains framework-independent and does not use Three.js or Babylon.js. The bloom buffers are resized only when the viewport changes and are destroyed with the renderer.

Bloom eligibility is intentionally conservative: the bright pass uses the current relit luminance, a high threshold, and protection terms for face and broad clothing. Hair, exterior/window highlights, lamp emitter contribution and a small scene contribution are allowed to receive the effect. Debug views expose Bright Pass and Bloom Only without replacing the existing views.

## Default parameters

- Bloom enabled: yes
- Intensity: `0.22`
- Threshold: `0.82`
- Radius: `1.0`
- Buffer scale: quarter resolution, capped by the current canvas render size

## Visual review

Playwright captured matched Dusk and Night Bloom OFF/ON screenshots. Dusk ON adds a restrained soft response around the brightest window/hair/lamp areas. Night ON adds only a small amount of lamp and local highlight separation; the cool exterior remains clean. Face structure, skin and white clothing do not become broad glowing regions. Noon remains effectively unchanged at the default settings.

## Performance notes

The bloom target is quarter-resolution and uses two lightweight fullscreen blur passes. The main relighting pass remains one draw, and bloom adds three draws only when enabled or when a bloom debug view is selected. DPR 1.0 and 1.5 use the same scaled quarter-resolution target strategy; a cross-GPU benchmark is still future work.

## Follow-up validation

The Bloom controls were corrected so intensity, threshold and radius update separate engine settings. Toggling Bloom off and on preserves the selected intensity instead of restoring the default. Playwright now asserts those values through `getSettings()`, checks for page errors and WebGL errors, and validates 1440x900 canvas dimensions at DPR 1.0 and 1.5. The full browser suite completed 16 tests successfully.

## Local performance baseline

`npm run test:perf` records Bloom OFF/ON samples at DPR 1.0 and 1.5 in `docs/performance/`. On the current Chromium machine, DPR 1.0 measured a 16.7ms median frame interval and roughly 33.3ms p95 with or without Bloom. DPR 1.5 measured a 50ms median and 66.7ms p95 with or without Bloom. This suggests the high-DPR cost is dominated by the scene/render target workload rather than the quarter-resolution Bloom pass, but it is only a single-machine headless Chromium baseline. All samples reported WebGL error 0 and no page errors.

## Next candidate

The next low-risk task should be texture/GPU memory optimization or browser performance measurement. Breathing and hair motion remain higher visual-risk because they require registered geometry or carefully bounded local deformation. Blink must remain blocked until an official registered asset exists.

## Texture memory optimization

The four full-resolution source/map textures are now uploaded as RGB8/RGB instead of RGBA8/RGBA because alpha is unused. This reduces the nominal main texture allocation from about 126.6 MiB to about 94.9 MiB at 3840×2160. Bloom render targets remain RGBA8 because they are framebuffer attachments. The visual pipeline and registration are unchanged. Performance JSON now reports canvas memory and source-texture memory separately.

## Context loss recovery

Added a safe `webglcontextrestored` handler. Since WebGL programs, textures and Bloom framebuffers are invalid after context loss, the current implementation reloads the page after the browser reports restoration rather than attempting an incomplete in-place reconstruction. Rendering remains paused during loss. A reusable GPU resource factory can later replace this reload path.

## Verification

After the context event lifecycle change: `npm run typecheck`, `npm test`, `npm run build`, and the full Playwright suite all pass. The browser suite remains at 18 passing tests, including DPR checks, Bloom comparisons, performance samples, and the four time-of-day baselines.
