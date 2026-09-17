# Technical Art Alignment 1.5 — Lighting Convergence / Visual Polish

2026-09-17. Starting HEAD: `d253f56`; clean working tree. Re-read requirements,
AGENTS, the four Round 1 review logs, renderer/shaders/lighting and current tests.
Default asset: Registered Normal v2. The user's Round 1 approval is the baseline;
the decisions below are this session's browser/visual review, pending the user's
final review of 1.5. [Screenshots and reproduction](../screenshots/lighting-convergence/README.md).

## 1. Issue from manual acceptance

The user accepted v2 and all three normal-aware lighting paths, Noon and Dusk,
and the current window approximation. Morning still resembled cooler, darker
daylight. Night needed one final local material review. Correction was declared
finished with limited benefit; it remains optional and off. No new architecture,
normal asset, mask system, animation or Blog integration was requested.

Fresh browser baselines cover 06:00, 07:00, 08:00, 12:00, 17:30 and 23:00 before
editing. The old morning aperture had identical geometry from 06:00 to 08:00;
brightness changed more than its direction. This justified a time-key adjustment.

## 2. Morning change and review

Only production change: `src/engine/lighting.ts`. At 06:00 the daylight vector
changes from `[.76,-.44,.56]` to `[.90,-.28,.48]`. The 09:00 interpolation anchor
changes from `[.10,-.96,.72]` to `[.38,-.82,.66]`, retaining a lower morning angle
before the unchanged Noon key. The direction changes smoothly from 05:00 to
12:00; no global normal/material or shader change is involved.

The 06:00 projection enters higher in the window: origin `[.93,.14]`, axis
`[-.83,.558]`, width `.095`, spread `.04`, separation `.24`, reach `1.25`.
The 08:00 key uses `[.91,.14]`, `[-.77,.638]`, width `.10`, reach `1.19`.
The zero-energy 05:30 key shares the 06:00 geometry. Projected axis angles are
approximately 34° / 40° / 65° below image-left at 06 / 08 / 12, in equal-length
artwork units. These are art-directed screen-plane angles, not solar elevation.
Energy stays `.85` at 06:00 and `1.15` at 08:00. Exposure, ambient, RGB colors,
lamp strength, projection intensity and all material balances stay unchanged.

Review at equal exposure: the shallow band travels through window-side long
hair/shoulder, across the sleeve and toward the book/table. Noon keeps its
broader, steeper fall toward the cup/right desktop. The chair remains restrained
and mostly outside the direct aperture; its difference comes from the lower
directional light, not an invented beam through an occluded region. At 06:00
the Final is cool/neutral and soft. The grayscale Final and fixed-scale Neutral
retain a different shoulder-to-desk relationship from Noon without orange tint
or an exaggerated spotlight. 07:00 and 08:00 transition coherently.

One initial candidate put the 08:00 projection centroid only 27.34 reference
pixels from Dusk, failing the existing >35 test. Moving its entry upward and
slightly flattening its axis restores separation (37.13 pixels) while retaining
the book/shoulder coverage. No test threshold or probe was changed. That failure
was resolved in lighting data, then recaptured and rechecked visually.

## 3. 23:00 lamp art pass

No night adjustment is necessary. Native 3840×2160 browser output (2560×1440
CSS, DPR 1.5) was inspected against Base, Normal, Lamp and Final:

- Window-side hair has warm surface response; no new continuous rim, metallic
  band or clipped plastic highlight. Painted fine highlights remain in Base.
- Right sleeve has soft volume and visible folds. The torso stays quiet; neither
  a hard normal terminator nor a whole-shirt glow was introduced.
- Both hands retain skin tone and modest finger curvature without waxy knuckles
  or newly strengthened finger creases.
- Book pages have distinct tilts and a readable spine; the page edge does not
  read as an emitter. The cup stays ceramic, with coherent cylinder sides,
  rim and handle rather than a metallic lobe.

Cool exterior, dark room and the local warm reading pool remain balanced.
23:00 already meets the freeze standard; forcing an edit would add no benefit.

## 4. Normal v2 final local review

**ACCEPT.** Native-scale crops cover bangs, front lock, tied/right long hair,
both sleeves and cuffs, torso, both hands/fingers, spine and both page planes,
cup/rim/handle, chair, laptop and lamp shade. Approximate broad surface patches
are visible in Normal debug, but no clearly wrong light direction, spherical
cap, rounded mound or abrupt false-volume seam requires a source edit in Final.
Chair/laptop retain their planar reading; lamp shade remains curved metal with
a separate emitter. Neither `docs/normal-surfaces.json` nor its PNG changed.
This accepts the current art-directed approximation, not recovered 3D geometry.

## 5. Window mask final review

**ACCEPTED APPROXIMATION.** Inspected both glass edges, lower frame, pen/tools,
flowers, transparent vase and thin branches in source/Final/native crops and
Exterior. Normal viewing does not show a new frame spill or visible boundary
seam. The vase and fine branches remain approximate transparent/foreground
coverage consistent with the original soft artwork. Existing edge, frame,
flower and object probes pass. No source polygon or shader UV cutoff changed.

## 6. Protected Noon / Dusk and validation

The new browser test compares the captured PNG bytes to fresh pre-edit files
for **12:00, 17:30 and 23:00**, in Final, Neutral, Directional, Projected, Lamp and
Exterior. All 18 comparisons are identical; the independent decoded-pixel
report gives **zero changed pixels** in every image. Noon stays clean and broad;
Dusk retains its accepted warm hair, diagonal light and book/table balance.

Validation uses the repository's existing thresholds. See the final validation
record below for commands and results. Screenshots use default v2, exposure 0,
correction 0, reduced motion, animation/steam disabled and hidden debug UI.
Color comparisons share 1920×1080/DPR 1; native local review uses DPR 1.5.
New grayscale images apply fixed `.2126 R + .7152 G + .0722 B` to displayed
8-bit RGB, without per-image normalization or contrast/exposure adjustment.
Existing normalized-shape numerical tests remain separate diagnostics; those
numbers are not substituted for fixed-scale visual evidence.

## 7. Final decisions and phase gate

| Item | Decision | Evidence |
| --- | --- | --- |
| Normal v2 | ACCEPT | Native local surfaces have no visible blocking artifact |
| 06:00 | ACCEPT | Soft low-angle diagonal remains distinguishable in grayscale |
| 12:00 | ACCEPT | Exact protected baseline, no regression |
| 17:30 | ACCEPT | Exact protected baseline, no regression |
| 23:00 | ACCEPT | Local materials natural; exact protected baseline |
| Window mask | ACCEPTED APPROXIMATION | Edges/foreground acceptable at normal viewing |

**Technical Art Alignment: ACCEPTED WITH BAKED-LIGHT LIMITATION**.
This records the current review decision, not a claim that the user has already
approved these new captures. Stop here for human review. Blink stays deferred.

## 8. Baked-light limitation

The approved Hero remains the artistic master. Its painted sunlight, fine hair
highlights, paper values and contact shadows persist under runtime lighting.
Consequently Final direction changes are quieter than Neutral/Projected, and
this system cannot independently reverse all illumination or reconstruct clean
albedo. That is the accepted scope of this freeze. The limited correction
experiment remains unchanged and disabled by default; no full-image de-light,
redraw, v3, depth or compensating shader mechanism was added.

## Validation record

- `npm run typecheck`: PASS.
- `npm test`: 7/7 PASS, including whole-day projection continuity.
- `npm run build`: PASS (Vite 7.3.6).
- `node node_modules/@playwright/test/cli.js test --workers=2`: **38/38 PASS**,
  including the two new convergence captures and the two existing DPR performance
  tests. Exact-baseline mode was enabled. Existing thresholds are unchanged.
- The corrected morning/window/convergence subset also passed 7/7 before the
  final full run. The initial 37/38 run and its resolved failure are described
  above; it is not counted as a pass.
- `python scripts/summarize-convergence.py before` / `after`: fixed-scale
  galleries, grayscale PNGs, native crops and decoded-pixel report generated.
- `git diff --check`: PASS. Both approved source-image SHA-256 hashes match
  the previous phase. Generated runtime maps and their sources are unchanged.

Performance samples on this host, measured concurrently with the full suite:

| DPR | Bloom | RAF median / p95 ms | Source textures MiB | WebGL/page errors |
| --- | --- | --- | --- | --- |
| 1 | off | 33.3 / 33.4 | 97.24 | 0 / 0 |
| 1 | on | 33.3 / 50.0 | 97.24 | 0 / 0 |
| 1.5 | off | 66.6 / 83.3 | 97.24 | 0 / 0 |
| 1.5 | on | 66.6 / 83.4 | 97.24 | 0 / 0 |

These are headless RAF scheduling samples, not GPU timings or proof of a 60 FPS
target. The existing performance tests assert valid canvas sizing and absence
of errors, not a frame-time threshold. No passes, texture allocations or per-pixel
shader operations were added. The Windows Vite teardown again waited after all
38 results; stopping only that run's Vite process allowed Playwright to finish
with exit 0. This is recorded separately from test execution.
