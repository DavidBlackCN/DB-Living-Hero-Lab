# Lighting / Shadow Convergence — 2026-09-17

Starting HEAD: `add7696`, clean tree. This round addresses the user's confirmed
remaining lamp-placement and shadow-depth issues. Fresh before captures were
made before runtime edits. [Gallery and commands](../screenshots/lighting-shadow-convergence/README.md).

## Lamp root cause and change

Convergence 2 corrected the lamp's signed direction, but its broad desk pool
still centered too far forward. Sill objects were absent from the main receiver
channel and received only a weak fallback tail. Fixing direction alone therefore
could not light the lamp's actual nearby surroundings.

Keep Normal v2, the lamp position (.797,.327), rear Z offset −.08, diffuse wrap,
emission, global lamp strength and face visibility floor. Recalibrate only pools
and source receivers:

- Desk: center (.825,.735), radius (.20,.115), coefficient 1.45. This moves the
  reading pool right/back and reduces its forward reach.
- Subject: center (.78,.49), radius (.085,.20), coefficient 1.55. Right-side hair
  and shoulder get local warm light without widening it onto the face/chest.
- Sill: center (.82,.49), radius (.13,.105), coefficient 1.0, gated by Scene G.
- Broad fallback tail: .10 → .06.
- Source `lampSill` and existing tools/frame/vase contours supply receiving
  coverage. Scene R/exterior and all normal data remain untouched.

Measured 23:00 raw Lamp R means, encoded ×255 (same fixed rectangles/exposure):

| Region | Before | After |
| --- | ---: | ---: |
| Face | 2.35 | 1.45 |
| Chest | 6.66 | 3.63 |
| Right hair | 54.42 | 57.76 |
| Left page | 59.21 | 32.31 |
| Right page | 183.96 | 150.20 |
| Cup | 107.31 | 126.82 |
| Front desk | 91.35 | 27.39 |
| Right desk | 165.54 | 196.79 |
| Tools | 3.37 | 35.36 |
| Directly under lamp | 4.63 | 68.60 |
| Picture frame | 4.45 | 31.52 |

This redistributes rather than globally increases lamp energy. The right page
stays substantially brighter than the left; nearby sill objects respond while
the front desk loses its former dominance. Lamp debug is before aggregate
shadow/face corrections; Final and Neutral are reviewed separately.

## Lightweight shadow / occlusion stage

Implemented inside the existing fragment pass, without a new render target,
texture, depth map or physical shadow map. One `shadow` strength slider/API
setting (0–1, default .65) controls the enhancement. Existing Shadow/Occlusion,
Lamp and Neutral views are sufficient; no debug UI restructuring.

### Contact and AO-like attachment

Reuse light-shaping B. Retain existing book/coaster contacts and add eleven
narrow, source-authored detail bands: fringe/face, side lock/face, chin/neck,
both straps, both hand/page contacts, tools/frame/vase roots and chair/drape.
Strokes use a 2.2-reference-pixel blur and named receiver clipping. Filter bounds
are in user space so thin horizontal paths do not disappear or truncate their
blur. No entire silhouette is offset. Contact coefficient is B×.18×strength;
at default, existing full-value contacts are near the old .12 coefficient.

Face contacts are capped at .025 before strength and softened further by the
existing face-safe light handling. Nose and eye sockets have no added contact
data. User-supplied artwork is never repainted.

### Directional occlusion and volume dark sides

Existing broad day/night occlusion remains. The new layer uses wide smoothstep
normal/light transitions for hair, cloth and prop/chair receivers, excludes face
volume, and lightly attenuates regions outside the corresponding projected/lamp
field. Volume coefficient .10 and off-field coefficient .045 are scaled by
material coverage and the shadow control. Total added attenuation is capped at
.22, including contacts. This gives soft dark-side relationships, not hard cel
bands, nose shadows or specular/metallic highlights.

Shadow debug combines existing broad occlusion with the actual added attenuation;
brighter debug values mean more darkening. `shadow=0` disables this contact/volume
stage, while retaining the older broad day/night structure. On/off Final captures
at 17:30 and 23:00 isolate the enhancement from the lamp redistribution.

## Visual review and corrections

The first narrower desk candidate reduced the center-book probe below the
existing minimum (.233 versus >.25). Slightly widening its X radius from .185
to .20 restores readable pages while retaining reduced forward reach. The
existing book-light threshold was not reduced.

A native source-grid check located the tools' true foot around y=358–360. The
first contact band was too high, based on an exterior-occluder contour rather
than the actual base. It was moved to the foot and the frame contact aligned
to its lower edge. A new probe rejects contact darkening across the tools body
at y=340. This visual correction was made even though the first full suite passed.

Before/After review covers four times; 17:30 and 23:00 include all diagnostic
views. Face/cloth and reading-area crops retain the original expression, soft
fabric, paper curvature and ceramic cup. Sill roots have a restrained attachment
shadow; the left side keeps its prior room participation. Normal v2 has no edits.

The 06:00 direction remains lower and softer than Noon, with a neutral/cool room.
It needed no further time-key change. Noon remains broad and natural. Dusk keeps
its warm reading-area target with slightly stronger dark-side relationships.
Noon/Dusk whole-image Final mean absolute changes are approximately .4/.9 of
255 display levels; these quantify scope, not artistic acceptance.

Exterior debug remains pixel-identical at all four times. Only Scene G receiving
coverage changes; the accepted window/exterior contours and flower extraction
are preserved. Source Base is also pixel-identical in all comparisons.

## Validation and test interpretation

The old night-page guard assumed a constant shadow field over the entire probe.
It reported range 2 versus ≤1 when the new smooth volume layer was enabled.
The original ≤1 range assertion is retained with that layer off; a new ≤1
per-pixel step assertion checks the enabled layer. Existing source probes still
reject page-interior contact and the former floating stripe. This is an explicit
update for the requested volume shading, not a looser threshold hiding a band.

New tests check registered contact locations, zero nose/interior/body stripes,
restrained face response, volume attenuation, the actual strength control,
sill/tools illumination, front-desk falloff and right/left page balance.

- `npm run typecheck`: PASS.
- `npm run build`: PASS.
- `npm test`: 7/7 PASS.
- Full Playwright suite, including visual and performance tests: 43/43 PASS.
  Final screenshots use `VISUAL_OUTPUT_ROOT=docs/screenshots/lighting-shadow-convergence/after`.
  Windows Vite teardown stalled after all results; stopping only the test-owned
  Vite process allowed the runner to finish with exit code 0.
- `git diff --check`: PASS. Both original image SHA-256 hashes are unchanged.
- Performance captures have no WebGL or page errors. Median frame times on this
  test host were 33.3 ms at DPR 1 and 66.6–66.7 ms at DPR 1.5; these do not establish
  a 60 fps desktop guarantee.
- Required four-time diagnostics, 17:30/23:00 Before/After and shadow-off/on
  comparisons are linked in the gallery. Raster QA outputs remain local under
  the repository's existing ignore policy; the gallery and capture scripts are tracked.

## Modified files

- Runtime: `src/engine/shaders.ts`, `src/engine/renderer.ts`, `src/debug-ui/panel.ts`.
- Receiver/contact source and generator: `docs/scene-regions.json`,
  `scripts/generate-scene-assets.mjs`.
- Generated assets: `public/assets/generated/scene-masks.svg`,
  `public/assets/generated/light-shaping.svg`.
- QA: `tests/visual/lighting-shadow.visual.spec.ts`,
  `tests/visual/desk-light.visual.spec.ts`, `scripts/summarize-lighting-shadow.py`.
- Documentation: `README.md`, `docs/architecture.md`,
  `public/assets/generated/README.md`, this log, and
  `docs/screenshots/lighting-shadow-convergence/README.md`.

## Decision and known limits

Browser visual review: lamp placement **ACCEPT**, local contact/volume shading
**ACCEPT**, Noon **ACCEPT**, Dusk **ACCEPT**, morning **ACCEPT**, window coverage
**ACCEPTED APPROXIMATION**. The face remains soft and naturally readable.
These are this session's review judgments; final human acceptance is pending.

The source contains baked sunlight, shadows and highlights. Contact bands and
receiver geometry are hand-authored approximations, not reconstructed depth;
the lamp's wrapped diffuse includes a deliberate stylized bounce allowance.
There are no cast-shadow rays or light blockers inferred from displacement.
Fine transparent objects remain approximate. Stronger physical light reversal
would require better base/geometry data; this change does not claim that result.

Stop here for human review. No Blink, breathing, hair animation, particles,
parallax, Blog integration or renderer refactor was started.
