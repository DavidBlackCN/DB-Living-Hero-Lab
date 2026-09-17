# Lighting Convergence 2 — Room Participation + Lamp Direction Fix

2026-09-17. Starting HEAD `4a93a00`, working tree clean. This round responds to
new human feedback after 1.5; its earlier acceptance is historical, not a reason
to dismiss the room/lamp issues. Reviewed current requirements, agent rules,
renderer, shaders, lighting, region generator, prior convergence log and tests.
Fresh before captures were made before changing production code.

[Fixed-exposure comparison gallery](../screenshots/lighting-convergence-2/README.md).
The reference [KumengScreen README](https://github.com/buger404/KumengScreen#readme)
describes full-image normal-based lighting with soft stylized transitions. The
relevant direction here is room-wide participation and restrained form response;
no reference artwork, effects or rendering pipeline was copied.

## 1. Room Participation diagnosis

The projection receiver was the maximum of desk/prop coverage and hair/clothing
weights. Wall, shelf and foreground coverage was zero. Its reach and axis were
also calibrated primarily to the reading area. Left-side directional light
existed but could not make the room visibly respond to the window aperture.
Raising ambient would brighten everything without fixing that spatial omission.

## 2. Room Participation strategy and result

Reuse G in the existing 1200×675 `light-shaping.svg`, formerly an unused exposed
desktop diagnostic. `roomParticipation` in `docs/scene-regions.json` contains five
coarse weights: wall .80, shelf/books .40, shelf edge .72, left foreground .43,
chair surroundings .58. A 10-reference-pixel feather softens their transitions;
existing character/desk contours exclude foreground subject surfaces. These
are receiving weights, not depth, material normals or a new segmentation system.
R remains window access; B remains desktop-clipped contact occlusion.

The existing two-lobe window aperture is also evaluated for the upright room
plane. Its screen-space axis `normalize(-1, axis.y*.40)` preserves the changing
time direction while foreshortening the floor-to-wall relationship. Width grows
with distance; the soft reach ends at 2.30 image-height units. Room weighting is
scaled by .65 and the same projection energy, intensity, sun control and sampled
normal response as the original projection. It is visible in Projected debug,
independent of ambient, and disappears when projected/sun/refinement is disabled
or after sunset. The main subject aperture is unchanged.

This is a two-plane artistic approximation, not recovered 3D visibility or
volumetric scattering. No luminous layer was put over the left-middle air.
The new falloff illuminates surfaces through the existing linear-light multiply.
The left side remains subordinate: wall is stronger than shelving, foreground
is quieter, and the reading area remains the main receiver. No exposure,
ambient, saturation, time key or global projected-intensity default changed.

Fixed-rectangle Final R means (0–255 display encoding; no normalization):

| Time | Wall before → after | Shelf before → after | Foreground before → after |
| --- | --- | --- | --- |
| 06:00 | 132.67 → 138.67 | 94.23 → 96.30 | 103.20 → 104.22 |
| 12:00 | 163.58 → 168.23 | 116.68 → 117.95 | 127.71 → 129.75 |
| 17:30 | 136.14 → 146.51 | 97.07 → 100.59 | 106.13 → 109.07 |

These document the restrained local change, not an artistic score. At Noon,
the sampled face, chest, hair, sleeve and book Final patches remain identical;
at Dusk the unchanged daylight aperture combines with the revised, weaker
front-facing lamp contribution. Dusk's reading-area balance remains coherent.

## 3. 23:00 lamp direction diagnosis

Normals encode +Z toward the viewer, but the lamp vector used a fixed **+.28**
forward offset. This made camera-facing surfaces receive direct warm light.
The wide subject pool centered at (.755,.54) further spread that contribution
onto the blouse front. The warm reading pool was useful; its spatial direction
and front/side balance were the problem, not the global lamp-strength setting.

## 4. Lamp strategy and local review

In the spatial lighting path the lamp offset is now **−.08**. Its XY source stays
at the registered lamp location (.797,.327). The subject pool moves toward the
lamp to (.78,.53), narrows to (.09,.22), and receives a 1.25 local coefficient.
The desk pool coefficient becomes 1.35 to preserve upward-facing paper/desktop
illumination; the broad fallback tail decreases from .16 to .10. Lamp strength,
emitter and night ambient/readability floor stay unchanged.

Lamp reflection uses `.08 + .92 * clamp((N.L + .70) / 1.70, 0, 1)` to preserve
soft turning surfaces under the rear-side source. This wide diffuse wrap is a
deliberate stylized visibility allowance, not a physical area-light solution.
Face-safe orientation mixing and the separate emitter are retained. The older
non-spatial comparison path still uses its original forward-light response.

The first candidate simply changed the direction with the old clamped N.L.
Hair, sleeve and cup collapsed to the same response floor, visibly flattening
them and failing the existing normal-response test (hair delta 0, required
>.004). It was rejected. The soft wrap restores those material differences;
no thresholds or probe locations were changed. The first room candidate also
under-covered Noon; the final upright-plane axis corrects that coverage.

23:00 isolated Lamp R coefficients, encoded ×255 for measurement:

| Region | Before | After |
| --- | ---: | ---: |
| Face | 9.20 | 2.41 |
| Chest | 16.74 | 6.66 |
| Right hair | 127.30 | 54.42 |
| Right sleeve | 115.77 | 65.29 |
| Left hand | 32.85 | 32.87 |
| Right hand | 172.31 | 131.11 |
| Book | 105.12 | 100.12 |
| Cup | 148.68 | 107.31 |
| Coaster | 233.71 | 232.34 |
| Pen/desktop | 159.25 | 161.96 |

Face/chest lamp contribution falls about 74%/60%. Right-side absolute brightness
also decreases; the goal is a more credible balance, not stronger light on every
object. Sleeve/chest lamp ratio rises from 6.9 to 9.8. The face remains readable
in Final (mean R 113.37 → 109.72), supported primarily by the unchanged ambient
and face-safe floor. Native 4K before/after crops show restrained warm outer
hair and sleeve folds, readable hands, distinct paper planes and ceramic cup
volume. No new hard terminator, plastic highlight, full rim glow, emitting page
edge or whole-blouse glow was observed. Coaster, pen and desk retain the local
warm pool; the cup still responds more toward its lamp-side surface.

## 5. 06:00 recheck

**ACCEPT for this round's browser review.** The existing morning keyframes are
unchanged. Final remains slightly cool/neutral with a soft shallow window path;
Neutral and Projected distinguish its shoulder/book relationship from the
broader, higher Noon path. Room participation extends the effect into the wall
and shelf without tinting everything orange. The lamp correction also affects
its small residual lamp contribution. No extra morning-only adjustment needed.

## 6. Window mask recheck

**ACCEPTED APPROXIMATION.** Checked glass/frame edges, lower edges, tool holder,
flowers, vase and picture frame in native before/after crops and Exterior.
Exterior debug is pixel-identical at all four times. Scene SVG, flower occlusion
and glass source data did not change. The room-only addition to the source JSON
does not redraw windows. Foreground glass objects now receive less broad lamp
spill, but preserve their silhouettes. Fine stems/transparency remain the
accepted approximate coverage; no UV cutoff or additional mask hack was added.

## 7. Final judgment and limits

| Item | Browser review decision |
| --- | --- |
| Room Participation, especially Noon/Dusk | ACCEPT: nonuniform weak room response; subject remains dominant |
| 23:00 Lamp Direction | ACCEPT: reduced front fill, rear/right local response and preserved reading pool |
| 06:00 | ACCEPT: low-angle identity retained |
| Window mask | ACCEPTED APPROXIMATION |
| Normal v2 / approved Hero | Preserved; no asset redesign |

**Lighting Convergence 2: READY FOR HUMAN REVIEW.** Stop here. The user's final
artistic acceptance is still pending; automated passes do not substitute for it.
No Blink, animation, particle, UI/Blog integration or correction expansion.

The painted Hero still contains fixed highlights and shadows. Room surfaces
mostly retain flat authored normals, and the lamp uses a fixed signed offset
rather than true depth/occlusion. Thus this is a more coherent local lighting
approximation, not independent physical relighting. Correction remains optional
and disabled by default. No new texture, pass or renderer architecture was added.

## Validation and files

- `npm run assets:generate`: PASS; only `light-shaping.svg` content changes.
- `npm run typecheck`, `npm test` (7/7), `npm run build`: PASS.
- `node node_modules/@playwright/test/cli.js test --workers=2`: **40/40 PASS**,
  including two new room/lamp tests and both existing DPR performance tests.
- Earlier corrected targeted run: 14/14 PASS. Initial 13/14 failure is recorded
  above and resolved in shader behavior. All pre-existing test files, probes and
  thresholds are unchanged.
- `python scripts/summarize-room-lighting.py`: fixed-exposure galleries, native
  local crops, grayscale images and before/after region measurements generated.
- `git diff --check`: PASS. Approved Hero/reference SHA-256 hashes match prior
  records. Normal v2 and all other generated technical map contents are unchanged.

Performance during the full suite: DPR 1 RAF median 33.3 ms, p95 33.4/50 ms
(bloom off/on); DPR 1.5 median 66.7 ms, p95 83.3/83.4 ms. All WebGL/page error
counts are zero; nominal source memory remains 97.24 MiB. These are headless RAF
scheduling samples, not GPU timings or proof of 60 FPS. Existing performance
tests assert sizes and error-free execution, not frame-time targets. Windows
Vite teardown waited after all tests; terminating only that test-owned Vite PID
let Playwright finish with exit 0.

Changed files: `src/engine/shaders.ts`, `docs/scene-regions.json`,
`scripts/generate-scene-assets.mjs`, `public/assets/generated/light-shaping.svg`,
`tests/visual/room-lamp.visual.spec.ts`, `scripts/summarize-room-lighting.py`,
`README.md`, `docs/architecture.md`, `public/assets/generated/README.md`, this log
and `docs/screenshots/lighting-convergence-2/README.md`. QA images/JSON stay local
under the repository's existing ignore policy. Only related files are committed.
