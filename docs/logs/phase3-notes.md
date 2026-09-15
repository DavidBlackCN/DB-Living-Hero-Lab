# Phase 3 Notes

Date: 2026-09-15

## Handoff baseline

The repository was already a working Phase 2 WebGL2 prototype. Timeline, realtime mode, registered masks, low-frequency normals, region lighting, debug views, reduced motion, visibility pause, and the Phase 2 screenshots were present. The known limitations remain: hand-authored masks, low-frequency normals, baked daylight in the source illustration, no inverse lighting, and no automatic context restore.

## Browser validation

Playwright MCP was not available in the current agent tool list. The project now uses `@playwright/test` with a local Vite web server and a downloaded Chromium binary. `npm run test:visual` captures fixed 1440x900 screenshots for dawn (06:00), noon (12:00), dusk (17:30), night (23:00), and Normal/Masks/Scene/Overlay debug views. The suite disables animation and steam, enables reduced motion, and uses fixed time targets for repeatability.

## Visual baseline and review

The Phase 2 appearance remains intact in the new screenshots. Dusk keeps the warm window/lamp separation; night keeps the face readable while compressing the exterior window. Overlay and scene views make the approximate contours easy to inspect. No new shader or region asset adjustment was justified by the final screenshots, so `docs/scene-regions.json` and the generated SVGs were left unchanged.

## Coffee steam

Added a small procedural shader effect centered above the cup near the registered cup region. It uses two slow, low-opacity soft strands and is only emitted in Final view. It is controlled by a dedicated Coffee steam checkbox, the animation master toggle, `prefers-reduced-motion`, and the existing hidden-tab pause lifecycle. No new animation framework or raster asset was introduced.

## Remaining limitations

Fine curls, flyaway hairs, flower stems, transparent glass, pen cup and other thin boundaries remain approximate. The normal texture still represents broad orientation only. The source artwork's baked lighting cannot be removed by the shader. Blink, breathing, hair motion, bloom, GPU benchmarks, and automatic WebGL context restoration remain future work.

## Verification

`npm run assets:generate`, `npm run typecheck`, `npm test`, and `npm run build` pass. The Playwright run completed all 9 screenshot cases successfully, including the steam-enabled state. The generated `test-results/` directory is ignored and is not part of the source artifact.
