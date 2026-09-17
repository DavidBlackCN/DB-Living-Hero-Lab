# Hero spatial lighting convergence — 2026-09-17

Scope: window bounds, contact/form shadows, rear-right lamp and whole-room cohesion.
Original artwork, normal v2, UI and runtime passes are retained. No new dependency.

## Baseline review

Ran the actual Chromium/WebGL app and inspected 06:00, 12:00, 17:30 and 23:00
before editing. Existing glass paths already bounded the window; the reported
large spill below the frame was **not reproduced in this checkout**. Do not claim
this iteration removed a demonstrated large leak. The prior contact field was
very diffuse, room dark sides did not use its room weights, and lamp illumination
under the shade was weaker than its desk pool.

## Changes and tuning

- `docs/window-glass.json` is now the single glass geometry source: ordered
  anchors in original 1200×675 coordinates, plus the inward-only left lower
  transition. Both generators read it. An outer polygon clip bounds all exterior
  filtering. Existing flower extraction only subtracts coverage; it cannot move
  the boundary. No inferred blur defines glass bounds. Edge antialiasing changes
  slightly (maximum 39/255 in the exterior diagnostic at subpixel edge pixels),
  with the original independent edge probes still passing.
- `contactDetails[].feather` is explicit per contact: .9 reference pixels for
  hair/face, 1.25 for neck, straps, hands/pages, sill objects and chair/drape;
  previously all used 2.2. Book/desk and coaster/desk keep broader 2.2 softness.
  Contact attenuation increases .18 → .30; face cap remains .025 before strength.
- Form darkening increases .10 → .22, using existing registered normals and
  time-dependent light directions. Unlit fill suppression .045 → .075. Total
  added attenuation is capped at .30 and controlled by existing Shadow (.65).
  No shifted silhouette shadows or new face-volume shading.
- Lamp subject pool is (.752,.49), radius (.092,.21), with smooth rear/right
  visibility between x=.62 and .74 and face exclusion. Sill pool is (.82,.515),
  radius (.13,.10), weight 1.65; desk geometry remains (.825,.735), (.20,.115).
  Wide fallback spill drops .06 → .025. Contact B also attenuates direct lamp
  light (up to .30), while the room ambient remains. Lamp diagnostic includes
  this direct occlusion, before subsequent aggregate shadow/face correction.
- Room G weights participate in form and access-based fill loss; chair weight
  .58 → .65. Night's distant room fill floor .42 → .38. Walls, foreground and
  chair respond softly to the same daylight/access system, with no lamp flood
  across the left side. No additional texture or framebuffer pass.

## Visual self-review

- Window: no visible blue layer below the frame, on the lamp base or tabletop.
  Lower room strip x=870…1200, y=300…550 is exactly zero exterior at reference,
  1920 and native 3840 raster sizes. Independent near-edge tests also pass.
- Lamp: sill objects and right desk pool read together with restrained falloff.
  Raw lamp red-channel coefficients: sill .436, front desk .102; right page
  .580 vs left page .122; face .0036, chest .0097, sleeve .225, hair .286, cup .499.
  These are diagnostic coefficients, not lux or final display luminance.
- Character: left sleeve/front torso and turned hair are quieter; right side
  stays warm at night. Face remains gentle and readable. Dusk has the strongest
  warm/shadow relationship; noon remains least dramatic and dawn cooler/lighter.
- Contacts: inspected fringe/face, neck, straps, both hands/pages, book/desk,
  coaster/desk, tools/frame/vase and chair/drape. Attachment is stronger without
  introducing a detached stripe across the book or face. Face contacts remain
  deliberately very subtle; the original painted linework carries much detail.
- Left room: participates in changing light and shadow. The effect remains
  secondary, particularly in blurred plants. Whole-image mean absolute changes
  vs baseline are 2.48 / 1.40 / 2.25 / 2.50 display levels of 255 at the four times;
  this is a restrained refinement, not a wholesale transformation.

## Validation

- Typecheck and build PASS; timeline/light continuity unit tests 7/7 PASS.
- Full visual/performance run: 44/45 initially passed. The new room test read
  after a second animation frame and saw a discarded buffer (the renderer uses
  preserveDrawingBuffer=false). It now reads in the draw frame and asserts a
  nonzero reference sample. Both new tests passed on targeted rerun. All 45
  distinct tests therefore have passing results; no thresholds were loosened.
- Native 4K screenshots and both normal variants inspected/tested; Base
  screenshots remain pixel-identical. No source illustration changes.
- GPU/page errors: zero. Source texture storage unchanged at 97.24 MiB.
- Concurrent test-host frame medians: DPR1 33.3ms bloom off/on; DPR1.5
  66.6ms off, 83.2ms on. Historical medians were 33.3ms and 66.6–76.7ms.
  These are noisy browser RAF samples, not isolated GPU benchmarks or evidence
  of a 60fps guarantee. High-DPR smoothness remains a limitation of this host.
- Windows Vite teardown again stalled after test results. Terminated only the
  Vite PID printed by each owned test run; runners then returned their summaries.

## Remaining limits

The base contains baked sunlight and contact shadows; its highlights cannot
fully reverse at night. Lamp visibility and contact paths are authored 2D
approximations, without depth-based cast shadows. Transparent flowers retain
approximate extraction. Extra hard clipping secures bounds but does not improve
fine foreground segmentation. Final artistic acceptance is still the user's.

## Reproduce

```powershell
npm run assets:generate
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/spatial-convergence-3/after'
npx playwright test --workers=2
python scripts/summarize-spatial-convergence.py
```

The comparison script needs this session's `before/shadow` captures. Images and
JSON remain local under the existing ignore policy. See the [gallery](../screenshots/spatial-convergence-3/README.md).
