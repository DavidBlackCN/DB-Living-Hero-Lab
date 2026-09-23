# Runtime Lighting Foundation v1 Validation

## Scope

This phase upgrades the Normal/Test Light renderer path into a manually controlled Runtime Lighting foundation. It does not implement a 24-hour timeline, time-of-day presets, masks, multiple lights, shadows, PBR, depth, bloom, or post processing. Base Albedo, Normal v3, Local Blink v1, and Leaves v1 assets were not modified.

## Architecture

- `src/engine/types.ts` defines `LightingState`, RGB colors, and the `base | normal | lit` render views without a Vue dependency.
- `src/config/hero.ts` owns the default lighting parameters and the Normal v3 URL.
- `BaseRenderer` maps the state to WebGL uniforms. `hero.frag.glsl` samples the registered Base and Normal textures, computes a single wrapped diffuse response relative to a neutral-facing baseline, and adds a very weak ambient fill. It does not use specular response or a physically based material model.
- `LivingHero.vue` owns the interactive state. `HeroCanvas.vue` forwards it to the renderer, while `DebugPanel.vue` edits it. Blink and Leaves are suppressed outside Base view so diagnostic comparisons stay clean.

## Default Parameters

| Parameter | Default |
| --- | ---: |
| Direction azimuth / elevation | 312° / 55° |
| Key intensity | 0.35 |
| Key color | `#ffe8cf` |
| Ambient intensity | 0.045 |
| Ambient color | `#c7d6ff` |
| Diffuse wrap / threshold / softness | 0.22 / 0.85 / 0.08 |

All lighting defaults are centralized in `heroConfig.lighting`; the shader contains no scene-tuning constants for these controls.

## Debug Coverage

- Switch between Base, Normal, and Lit.
- Enable or disable lighting; disabled Lit returns the unlit Base.
- Adjust azimuth, elevation, key intensity, ambient intensity, and key / ambient colors.
- Blink and Leaves remain available in Base and do not overlay Normal or Lit.

## Visual Check

- Desktop Chromium / WebGL2 at 1440×900: Base, Normal, and Lit were exercised through the Debug Panel. With Blink and Leaves disabled, the canvas-only Lit capture differed from Base by mean absolute RGB 5.08/255; 44.4% of pixels had grayscale delta above 4. Lighting-off Lit matched Base exactly (0 delta). Normal differed clearly from Base as expected.
- Manual direction/intensity check: changing azimuth to 0° and key intensity to 0.60 changed 29.0% of pixels by more than 4 grayscale levels compared with default Lit. The default shading reads as restrained tonal modeling in the existing painted style; it does not create a strong standalone light-direction cue. No specular highlight is present. This is a foundation for review, not final art direction.
- Narrow viewport 390×844: the Debug Panel measured 290×270 px, is capped at 32vh, and scrolls internally. The artwork remains visible above it; this browser viewport check does not certify device performance.

## Known Limits

- Normal v3 is frozen for its current stage, not a physically authored material normal. Some source-painted edges can still drive shading, while near-neutral regions intentionally respond weakly.
- Foundation lighting is deliberately subtle and manually controlled. The ambient fill and neutral-facing diffuse baseline can keep the scene close to its painted Base; direction changes are visible but remain restrained. No temporal continuity, dawn/day/dusk/night palettes, responsive auto exposure, semantic light masks, or final art-direction pass is included.
- Mobile verification used a 390×844 browser viewport override; it is a layout check, not a device/GPU performance certification.

## Result

Foundation v1 is implemented and suitable for review as the prerequisite renderer layer. The architecture and controls support a separate timeline phase, but its restrained default appearance should be reviewed before proceeding. The project is **not yet ready to claim 24-hour Time-of-Day acceptance**; that phase should begin only after this checkpoint is reviewed.
