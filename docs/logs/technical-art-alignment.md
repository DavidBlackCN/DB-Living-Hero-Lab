# Technical Art Alignment — 2026-09-16

## Handoff and baseline

Starting commit: `4e5502c`. The existing uncommitted `REQUIREMENTS.md` is user work
and is preserved. Read the requirements, architecture, generated-asset notes,
phase/review logs, region/surface sources, renderer, shaders, lighting, generators
and current visual tests. No engine reinitialization or Blog integration.

Fresh baseline: `docs/screenshots/technical-art-alignment/before/`.
`before/audit/` captures registered v1 at **06:00**, 12:00, 17:30, 23:00, including
Final, Neutral, Normal, Projected, Exterior and Overlay, plus directional-only.
The older normal suite starts at 08:00; it is insufficient for the dawn gate.

Baseline typecheck/build pass, unit tests 7/7, browser tests 31/31. On this Windows
host Playwright's Vite teardown hangs after all results; terminating only the
test-owned Vite PID completes teardown with exit 0. Historical screenshots stay
untouched and new output uses a separate `VISUAL_OUTPUT_ROOT`.

Diagnosis: v1's Gaussian curve heights make some locks/folds read as overlapping
mounds. Hand normals have no finger cross-sections, several scene planes are
missing, and the table normal continues through the laptop. Projection and lamp
do not read normals at all. Dawn projection ramps so slowly that 06:00 is mostly
ambient; night depends on a smooth pool. The source's painted sunlight remains
a separate limit. Existing glass corrections and independent probes are retained.

## Sequence

1. Refine and inspect deterministic v2 at unchanged lighting.
2. Integrate normals into directional, projected and local lamp contributions.
3. Recalibrate dawn/noon/dusk/night; inspect window source coverage.
4. Try optional registered gain correction, preserving the approved Hero.
5. Capture four-time/color/grayscale evidence and run all validation.

No Blink, breathing, hair movement, new particles or displaced silhouette shadows.

## Delivered implementation

- [Normal v2](normal-v2-review.md): deterministic native 4K curves and surfaces;
  v1 source/PNG retained, old low-frequency SVG retained. v2 is the demo default,
  not a claim of ground-truth reconstructed geometry.
- [Normal-aware lights](normal-light-integration.md): directional, projection and
  lamp share the normal; lamp emission remains independent. New isolated views.
- Calibration: explicit 06:00 projection energy .85 instead of an almost-zero
  tail of the 05:30–08:00 ramp; fresh lower ambient and window-side low-angle
  daylight. Noon key stays unchanged. Dusk lowers ambient and increases the
  proportion of soft direct light. Normal 1, stylized .50, softness .18, face
  .85, hair .95, cloth .94. Night keeps its quiet room/cool exterior structure.
- Window review: inspected original/Final/Exterior closeups and passed the
  existing frame, lower-edge, pen and flower probes. **No scene-region/mask
  change was needed**; no cutoff or extra region compensation was introduced.
- [Intrinsic experiment](delight-experiment.md): optional R8 gain texture,
  exact off behavior, default disabled. The benefit is small; not clean albedo.
- [Review gallery](../screenshots/technical-art-alignment/README.md): four times,
  seven views, actual Final grayscale, before/after, night volume and correction.

## Validation and interpretation

Final typecheck, build, 7/7 unit tests and 36/36 browser tests pass. The browser suite adds v2 unit-vector and
surface probes, isolated-light normal response, mean-normalized Final grayscale,
and correction identity/range/registration checks. Baseline 31 tests grows to 36.
Existing mask/hand/contact/projection thresholds were not reduced.

The existing hand/contact and normal-disable comparisons were then extended to
all three maps, including v2; all four targeted tests pass with the original
continuity/equality thresholds. v2's sampled maximum unit-vector error is .00566,
minimum Z .639. `git diff --check` passes. Final 23:00 Exterior versus the
starting registered-v1 Exterior has **zero changed pixels**.

Initial integration probes at the center of a sleeve cylinder and almost outside
the dusk aperture produced only one 8-bit level of change. They were relocated
to the visible turning sleeve surface and exposed desktop inside the beam;
thresholds stayed unchanged. Tests additionally compare the cup's two sides
after dividing out the lamp field, so a mere brightness change cannot pass.

After normalizing away mean brightness in a fixed character/reading-area ROI:

| Final grayscale pair | Mean absolute spatial difference | Pixels differing >5% |
| --- | ---: | ---: |
| 06:00 / 12:00 | 4.40% | 24.1% |
| 12:00 / 17:30 | 8.03% | 58.1% |
| 06:00 / 17:30 | 6.23% | 44.7% |

These are relative pixel differences, **not an artistic-quality score**. The
same-exposure grayscale images show the morning diagonal, broad noon lighting
and lower dusk path; the actual painted image still carries its baked structure.

Nominal source texture memory remains 97.24 MiB by default, 105.15 MiB with the
optional correction loaded. Render pass count is unchanged. Headless RAF
measurements remain roughly 33 ms at DPR 1 and 50–67 ms at DPR 1.5 in this host;
they are scheduling measurements, not GPU timings or a demonstrated 60 FPS
guarantee. An early six-worker performance run timed out once; the unchanged
performance tests passed separately and in subsequent two-worker full runs.

Both approved source hashes match the Phase 1 record. v1 and all prior scene
maps are preserved. User `REQUIREMENTS.md` changes remain untouched.

## Answers to the phase decision questions

1. v2 improves coherent hair/sleeve cross-sections, adds restrained finger
   volumes, separates page tilts and fills missing scene planes; face stays soft.
2. Projected light now genuinely uses the sampled surface normal.
3. Lamp reflection now genuinely uses a local normal/light dot product.
4. At 23:00, sleeve/hair/page/cup response is more credible and isolated Lamp
   makes the change unambiguous. Final remains deliberately subtle.
5. Main window/glass/frame precision is acceptable at inspected source edges.
   Fine stems, flyaway hair and transparent coverage are still approximations.
6. The three daytime states differ in grayscale structure, not just tint/global
   brightness; dawn/noon difference is the smallest and remains restrained.
7. Correction is safe and measurable but only mildly useful. It is **not** a
   successful full de-light and stays opt-in.
8. The current Hero remains a viable artistic master for restrained relighting;
   this does not establish it as a clean final albedo for unrestricted lighting.
9. Baked light is still the main limit on larger directional changes. This
   experiment does not prove an unavoidable need to redraw the entire Hero;
   stronger reversals would require better intrinsic/artist-authored base data.
10. Stop here for review. Do not automatically proceed to Blink/breathing/hair.
    Blink is still asset-blocked, and final artistic approval of the lighting
    remains a separate gate from passing tests.

The technical-art and normal-light integration work is complete. The result is
closer to a relit scene, but the stronger claim of fully independent relighting
without baked-light interference remains unachieved and is not hidden by this
report. No new animation or Blog integration was started.
