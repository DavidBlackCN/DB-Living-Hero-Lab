# Lighting Convergence 2 — review gallery

[Decisions, measurements and validation](../../logs/lighting-convergence-2.md).
Before is `4a93a00`; after is this round. Fixed default exposure 0, Normal v2,
correction off, reduced motion, animation/steam off, debug UI hidden.
Main PNGs are 1920×1080 at DPR 1. No per-image normalization or auto exposure.
Images/measurement JSON are generated local artifacts, not tracked by Git.

- [Four times before/after](review/four-times-before-after.jpg).
- Room Participation: [06:00](review/room-0600.jpg), [12:00](review/room-1200.jpg), [17:30](review/room-1730.jpg), each Final and Projected.
- [Night Lamp Direction before/after](review/night-before-after.jpg): Final, Neutral and Lamp, matching crop/scale.
- [06:00 recheck](review/morning-review.jpg).
- [Region comparison data](review/comparison.json): raw display RGB means and differences; not normalized artistic scores.

| Time | Required full-resolution views |
| --- | --- |
| 06:00 | [Final](after/convergence/0600-final.png), [Neutral](after/convergence/0600-neutral.png), [Projected](after/convergence/0600-projected.png) |
| 12:00 | [Final](after/convergence/1200-final.png), [Neutral](after/convergence/1200-neutral.png), [Projected](after/convergence/1200-projected.png) |
| 17:30 | [Final](after/convergence/1730-final.png), [Neutral](after/convergence/1730-neutral.png), [Projected](after/convergence/1730-projected.png) |
| 23:00 | [Final](after/convergence/2300-final.png), [Neutral](after/convergence/2300-neutral.png), [Lamp](after/convergence/2300-lamp.png), [Exterior](after/convergence/2300-exterior.png) |

Fixed grayscale: [06:00](review/0600-grayscale.png), [12:00](review/1200-grayscale.png),
[17:30](review/1730-grayscale.png), [23:00](review/2300-grayscale.png).
These use `.2126 R + .7152 G + .0722 B` on displayed RGB, without contrast scaling.

Native 4K before/after crops (100% pixel scale):
[hair/sleeve](review/detail-hair-sleeve.jpg), [hands/book](review/detail-hands-book.jpg),
[cup/coaster/pen](review/detail-cup-coaster-pen.jpg), [left window/tools](review/detail-window-left.jpg),
[right window/vase/frame](review/detail-window-right.jpg).
Full native [Final](after/convergence/native-final.png),
[Lamp](after/convergence/native-lamp.png), [Exterior](after/convergence/native-exterior.png)
were captured at 2560×1440 CSS with DPR 1.5. JPEG sheets aid browsing; original PNGs
are the lossless evidence. Fit-to-window display may shrink the native crops.

Reproduce after captures and tests in PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/lighting-convergence-2/after'
node node_modules/@playwright/test/cli.js test --workers=2
python scripts/summarize-room-lighting.py
```

To recreate `before`, run the existing `convergence.visual.spec.ts` at `4a93a00`
with `VISUAL_OUTPUT_ROOT=docs/screenshots/lighting-convergence-2/before` before
applying this round. The summarizer requires both directories. Do not enable
`CONVERGENCE_BASELINE`: that optional switch freezes all Noon/Dusk/Night pixels
for the earlier 1.5 task; this round intentionally changes them. Existing test
logic and thresholds remain intact. Performance samples are in `after/performance/`;
new room/lamp probe data is in `after/room-lamp/`. Windows test-owned Vite may need
termination after all test results to complete the known teardown wait.
