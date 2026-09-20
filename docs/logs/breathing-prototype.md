# Code-only Breathing Prototype

Status: **EXPERIMENTAL / awaiting human acceptance**. Default OFF.
Lighting is FROZEN / ACCEPTED; Blink is IMPLEMENTED / ACCEPTED / FROZEN,
including the user's desktop acceptance. No Hair Motion is developed here.

## Scope and phase synchronization

README, REQUIREMENTS, AGENTS and architecture now identify Micro Animation /
Living Scene Convergence as the current phase. Technical Art / Lighting design
requirements remain as completed/frozen constraints rather than upcoming work.
Blink is no longer deferred; Breathing is experimental, Hair Motion / Complex
Parallax / Advanced particles optional/deferred. DB-Blog-Plume migration waits
for full Living Hero Engine freeze. Historical logs and capture records remain
untouched. Neither WORK.md nor work/ changes belong in this session's commit.

## Implementation

One local material-UV deformation inside the existing fragment pass. Default
cycle 5.4 s, default amplitude 1.8 original-art pixels, hard cap 2 px; strength
0-2 px and cycle 5-6 s are exposed in the existing Settings API and debug panel.
Cosine `(1-cos(2*pi*phase))/2` starts/ends neutral with zero velocity. Sampling
downward produces a tiny upward garment lift, not whole-character movement.
The displacement is divided by actual artwork height, not viewport height.
At 1200 x 675 the default peak travel is only 0.5625 display pixels.

Influence uses the existing 1200 x 675 coordinate convention:
center (681,380), radii (72,60), quadratic `(1-r^2)^2` inside the ellipse,
zero outside. Original 4K bounding box is x=1948.8..2409.6,
y=1024..1408. The left edge is additionally suppressed through x=645..662
(4K x=2064..2118.4) to exclude the dangling front hair lock, which the existing
coarse cloth mask does not separate. Existing cloth semantic samples are inset
by 10 source pixels; face/hair/white-hand channels suppress coverage. These are
runtime safety bounds, not modifications of masks or source region assets.

Actual movement is central front knit / inner suspender-adjacent garment only.
The conservative support deliberately does not animate shoulders or outer straps.
Neck/head, Blink crop, front-lock tip, long-hair silhouette, hands, book, cup,
desk, environment and character silhouette remain outside support. The weight
and its radial derivative tend to zero before garment boundaries. No clean plate,
new image, whole-character scale, puppet rig, parallax or generated art is used.

Base pigment, normal, character mask, optional intrinsic correction and local
garment contact (light-shaping B) move together. Light-shaping R/G, scene masks,
lamp fields and projected aperture use original screen UV; their sources and
coefficients are untouched. Original Base always remains the original image.
Breathing Weight is a debug-only view of spatial support, independent of phase.
No new texture, framebuffer, draw pass or runtime asset memory. Extra cost is
small shader arithmetic plus up to five existing-mask samples inside the ellipse
and a contact sample while enabled; continuous redraw also costs time/power.

## API and lifecycle

```ts
hero.setBreathing(true);
hero.setSettings({ breathingStrength: 1.8, breathingCycle: 5.4 });
hero.setDebugView('breathingWeight'); // envelope inspection
hero.setDebugView('final');
hero.setBreathing(false); // exact neutral on next render
```

UI: Breathing / Experimental checkbox, Strength (source px), Cycle (s).
The animation master must be enabled and reduced motion disabled. The feature
also safely disables when masks are absent or refinement is off. Changes to
strength/cycle reset phase. `breathingPhase` in state aids deterministic QA.
There is no independent RAF, interval or timeout. The renderer's existing tick
advances the phase and schedules frames while enabled; disabled scheduling is
unchanged. Visibility/context loss excludes elapsed hidden time, and the first
resumed frame retains phase. Master-off/reduced-motion reset neutral; destroy
clears phase and the existing scheduler/resources. Steam's clock and visual
formula, and Blink's controller/assets/registration/timing, are unchanged.

## Validation

The visual suite loads the immutable accepted shader from Git commit `e29c635`
via a Playwright route (requires that commit in local history), then compares
canvas SHA-256 values against the current OFF shader at all four times and all
21 pre-existing views. It also compares fixed-time Steam plus Half/Closed Blink.
Tests capture synchronously after draws because drawing buffers are not preserved.
ON tests isolate Steam/Blink/Bloom for exact outside-region comparisons, then
separately inspect Bloom-enabled protected regions and unchanged GPU memory.
Unit tests exercise curve/cycle/pause/reset. Browser tests cover motion gates,
hidden/resume, destroy, parameter caps, UI changes and Blink crop compatibility.

QA captures and hashes: `docs/screenshots/breathing-regression/breathing/`.
See [capture index](../screenshots/breathing/README.md). PNG/JSON review outputs
remain local and are not new runtime artwork.

Final validation (2026-09-20):
- `npm run typecheck`: passed.
- `npm test`: 14/14 passed (existing Blink/timeline plus breathing clock).
- `npm run build`: passed.
- `npm run test:visual -- --workers=1`: 68/68 passed in 4.5 minutes, including
  7 unchanged Blink tests, 8 Breathing tests and all existing lighting/Steam/Bloom QA.
- `git diff --check`: passed.
- 84 OFF time/view hash pairs are identical to the accepted shader; fixed-time
  Steam and Half/Closed Blink comparisons also match.
- ON changed-pixel counts at 1200 x 675: dawn 3611, noon 3703, dusk 3536, night
  2413 inside support; **0 outside** at all four times. Bloom-enabled 1920 x 1080
  face/neck/hands/book/left-hair/right-hair closeups contain 0 changed pixels.
- Source texture memory remains 99.75 MiB, or 107.66 MiB with correction loaded.
  No WebGL errors occurred. Existing default-OFF performance probes measured
  50 ms median at DPR 1 and 116.7-133.3 ms at DPR 1.5 in this browser environment;
  this is not a hardware frame-rate acceptance or a Breathing-ON benchmark.
- Visual inspection of full scenes, weight and garment closeups found no visible
  seams, silhouette movement or additional night lighting. Recommend manual A/B
  review at 1.8 px / 5.4 s; keep OFF until that review is complete.

## Limits and decision

This is a tiny 2D garment-interior warp, not physical breathing or reconstructed
3D shape. It transports existing normal texels, without Jacobian normal rotation;
the 2 px cap and wide falloff keep that approximation small. The coarse semantic
mask cannot isolate every painted strand, so explicit conservative bounds are
necessary. It is intentionally hard to notice and may contribute too little at
small viewports. Enabling it requires ongoing redraws even with Steam off; true
hardware pacing and subjective calmness require desktop A/B review. Background
tests simulate visibility events, not OS compositor occlusion. Do not mark this
feature ACCEPTED/FROZEN or enable it by default before human review.
