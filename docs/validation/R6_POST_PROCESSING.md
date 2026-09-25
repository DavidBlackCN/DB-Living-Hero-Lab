# R6 HDR / Bloom / Tone Mapping / Display Grading

## Frozen boundary and reference

Human review froze R5 before this stage. R6 changes no Base/Normal/Blink assets, Breathing/Hair/Leaves code, Sky RGB/matte, `lightingFor` or `skyFor`, or R5 material response. The accepted small Sky top-edge residual and image-left clothing pull remain outside scope.

Reference inspection covered Kumeng's [post settings](https://github.com/buger404/KumengScreen/blob/main/lib/post-settings.ts), [post shaders](https://github.com/buger404/KumengScreen/blob/main/lib/post-shaders.ts), [daylight](https://github.com/buger404/KumengScreen/blob/main/lib/daylight.ts), [scene shader](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts), [stylized lighting](https://github.com/buger404/KumengScreen/blob/main/lib/stylized-lighting.ts), and [composition](https://github.com/buger404/KumengScreen/blob/main/components/dream-scene.tsx), plus the live four-phase Lit preview. The adopted ideas are portable RGBM storage, soft-knee bright-pass, 2/4/8/16-scale bloom, and final display treatment. DB-specific thresholds and grading are calibrated to this artwork; Kumeng's values are not copied. Its Noon keeps cloth folds, Dusk has the strongest soft warmth, and Night remains blue-gray rather than glowing.

## Color-space and pass ownership

| Stage | Space and responsibility |
| --- | --- |
| Scene fragment | sRGB Base/Blink sampled at shared motion UV, decoded to linear; frozen Normal/R5 lighting produces linear scene radiance. No final tone mapping when Post is enabled. |
| Sky placement | Frozen Sky PNGs are display-referred sRGB. Their RGB is decoded and inverse-mapped through the existing ACES fit and scene exposure, then blended into linear Scene. The original Sky RGB and alpha remain untouched. |
| Scene FBO | Portable RGBM RGBA8 stores 0–16 linear HDR without a float-FBO extension. A second R8 attachment stores bloom eligibility. Open Sky has zero eligibility; the brightest shirt pixels are attenuated. |
| Bright-pass/pyramid | Post applies the frozen scene exposure plus its small independent 24H exposure offset for threshold selection, extracts highlights with a continuous soft knee, downsamples at 2/4/8/16, and blurs each level. Four differently weighted scales form local-to-broad glow. |
| Final Post | Adds bloom to exposed linear Scene, applies **one** ACES fit, converts linear to sRGB, then applies restrained display saturation/contrast/tint. The existing registered Night edge-tone correction stays in display space. |
| Bypass | Post OFF takes the original R5 Lit path and is pixel-identical at all four anchors. Base and Normal inspection views bypass Post. Lighting Detail OFF or ON can enter Post independently. |

`src/config/post.ts` uses complementary smooth transition weights with a stable 20:00–05:00 Night hold. Dawn favors slightly softer contrast and cool air, Noon has the highest threshold and smallest day bloom, Dusk has the most bloom and gentle warmth, and Night uses minimal bloom with blue-gray display unity. The `Post Processing on/off`, `Bloom on/off`, and `Post preview` controls separate old Lit, Scene plus Post without bloom, bright-pass, bloom-only, before-grade, and final views. No four-state switch or discontinuity is used for the 24H post curve.

## Five visual/curve iterations

1. Split Scene linear output and Post ownership, then captured four Post OFF / no-Bloom / final comparisons. The no-Bloom scene handoff differed from the old Lit by about 0.5–1.5/255 on average; first highlight thresholds were too high and bloom was essentially absent.
2. Lowered thresholds and exposed a true bright-pass debug view. Only tiny Noon/Dusk highlights were selected; Dawn/Night remained almost black.
3. Added source-space white-shirt bloom attenuation and lowered thresholds again. Bright-pass now found hair/face and local high areas without an open-Sky veil. Bloom remained too faint at full-frame scale.
4. Raised the restrained bloom contribution and completed the four-phase display grade. Compared all four A/B frames and inspected character/cloth crops. Dawn is lighter in feel without Dusk warmth; Noon keeps white folds; Dusk gains coherent warm softness; Night stays blue-gray and readable.
5. The 24H review found that an initial `1 - max(phase weights)` expression reintroduced a Night contribution in the middle of the Dawn→Day blend. Changed to complementary weights and repeated the four anchors, 24H scan, and full-composition captures. This is the final candidate.

Compact contacts for the first three rounds: [round 1](r6-post/iteration1.jpg), [round 2](r6-post/iteration2.jpg), [round 3](r6-post/iteration3.jpg).

## Evidence

| Phase | R5 baseline / Post OFF | R6 final | Isolated passes | Full composition |
| --- | --- | --- | --- | --- |
| Dawn 06:30 | [before](r6-post/final/dawn-before.png) | [final](r6-post/final/dawn-final.png) | [bright](r6-post/final/dawn-bright.png) · [bloom](r6-post/final/dawn-bloom.png) | [22 s](r6-post/final/dawn-combined.png) |
| Noon 12:00 | [before](r6-post/final/noon-before.png) | [final](r6-post/final/noon-final.png) | [bright](r6-post/final/noon-bright.png) · [bloom](r6-post/final/noon-bloom.png) | [22 s](r6-post/final/noon-combined.png) · [motion](r6-post/final/noon-motion.gif) |
| Dusk 17:30 | [before](r6-post/final/dusk-before.png) | [final](r6-post/final/dusk-final.png) | [bright](r6-post/final/dusk-bright.png) · [bloom](r6-post/final/dusk-bloom.png) | [22 s](r6-post/final/dusk-combined.png) · [motion](r6-post/final/dusk-motion.gif) |
| Night 22:00 | [before](r6-post/final/night-before.png) | [final](r6-post/final/night-final.png) | [bright](r6-post/final/night-bright.png) · [bloom](r6-post/final/night-bloom.png) | [22 s](r6-post/final/night-combined.png) · [motion](r6-post/final/night-motion.gif) · [closed Blink](r6-post/final/night-blink-closed.png) |

[Enlarged four-phase A/B](r6-post/final/comparison.jpg), [motion contact](r6-post/final/motion-contact.jpg), and [24H hourly contact](r6-post/24h-audit/hourly-contact.png) aid review. `*-scene-post.png` files show the no-Bloom handoff; the bright/bloom preview images intentionally show sparse sources on black, not a display-ready frame.

## Validation, performance, limits

- Four Post OFF artwork captures match the frozen R5 captures **exactly** (maximum RGB difference 0). `scripts/validate_post.py` checks this, the Scene/Post handoff, Noon shirt, Night bloom, and 22:00/00:00/02:00/04:30/24:00 hold.
- A 97-frame, 15-minute WebGL scan passed. Noon artwork luminance is 0.21978; 12:45 ties the daylight peak. Night artwork luminance is 0.01585 at 22:00, 0.01587 at 00:00, 0.01595 at 02:00 and 0.01604 at 04:30; 00:00 equals 24:00. Evening face minimum 0.01760 remains above 22:00 face 0.01728.
- Four 22-second combined Lit/Sky/Blink/Breathing/Hair/Leaves/Lighting Detail/Post views were captured. Noon, Dusk, Night motion samples and closed Blink were visually checked; no new seam or white-cloth glow was found.
- The final 72 sampled CPU render submissions during the combined previews had a 0.4 ms median (0.7 ms 95th percentile, 0.9 ms maximum) versus the archived R5 0.3 ms median. This measures CPU submission in headless software WebGL, not GPU execution or production-device FPS. The pyramid allocates full-frame RGBM plus R8 gate and four smaller ping-pong levels; resize re-creates and destroy releases them.
- `pnpm build`, `pnpm typecheck`, R5 Detail, R2B time controller, Hair, Breathing, and Blink/Normal regressions passed after baseline checks explicitly disabled Post.

Bloom is deliberately sparse: Night has no materially selected highlights, while Dawn, Noon, and Dusk use local highlights plus display grading for a gentle finished look. The inverse-ACES Sky registration and RGBA8 RGBM quantization cause a small difference in the Post-on/no-Bloom path; Post OFF is the exact baseline. The accepted Sky-edge residual remains. R6 is ready for human visual acceptance; R7 and Leaves v2 were not started.
