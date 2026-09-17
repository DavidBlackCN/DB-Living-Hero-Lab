# Lighting Convergence 1.5 review — 2026-09-17

[Decision log](../../logs/lighting-convergence.md). All images are local generated
QA artifacts, ignored by Git; this index and the generators are committed.

- [Morning before/after](after/convergence/morning-before-after.jpg): 06 / 07 / 08 / 12, Final and Neutral.
- [Morning with grayscale and isolated light](after/convergence/morning.jpg).
- [Four times at fixed exposure](after/convergence/four-times.jpg): Final, grayscale, Neutral, Projected and Lamp.
- [Exact protected-pixel report](after/convergence/protected-pixels.json): all six views at Noon/Dusk/Night unchanged.

| Time | Required captures |
| --- | --- |
| 06:00 | [Final](after/convergence/0600-final.png), [Neutral](after/convergence/0600-neutral.png), [Directional](after/convergence/0600-directional.png), [Projected](after/convergence/0600-projected.png), [Grayscale](after/convergence/0600-grayscale.png) |
| 08:00 | [Final](after/convergence/0800-final.png), [Neutral](after/convergence/0800-neutral.png), [Grayscale](after/convergence/0800-grayscale.png) |
| 12:00 | [Before](before/convergence/1200-final.png), [Final](after/convergence/1200-final.png), [Neutral](after/convergence/1200-neutral.png), [Grayscale](after/convergence/1200-grayscale.png) |
| 17:30 | [Before](before/convergence/1730-final.png), [Final](after/convergence/1730-final.png), [Neutral](after/convergence/1730-neutral.png), [Projected](after/convergence/1730-projected.png), [Grayscale](after/convergence/1730-grayscale.png) |
| 23:00 | [Final](after/convergence/2300-final.png), [Neutral](after/convergence/2300-neutral.png), [Lamp](after/convergence/2300-lamp.png), [Exterior](after/convergence/2300-exterior.png), [Grayscale](after/convergence/2300-grayscale.png) |

Native source-pixel-scale crops (Source / Normal v2 / 23:00 Final):
[bangs](after/convergence/detail-bangs.jpg), [front lock](after/convergence/detail-front-lock.jpg),
[tied/right long hair](after/convergence/detail-tied-long-hair.jpg),
[left sleeve](after/convergence/detail-left-sleeve.jpg), [right sleeve](after/convergence/detail-right-sleeve.jpg),
[torso](after/convergence/detail-torso.jpg), [left hand](after/convergence/detail-left-hand.jpg),
[right hand](after/convergence/detail-right-hand.jpg), [book](after/convergence/detail-book.jpg),
[cup](after/convergence/detail-cup.jpg), [chair](after/convergence/detail-chair.jpg),
[laptop](after/convergence/detail-laptop.jpg), [lamp shade](after/convergence/detail-lamp-shade.jpg),
[left glass/tools](after/convergence/detail-window-left.jpg),
[right glass/flowers/vase](after/convergence/detail-window-right.jpg).
Open at 100% rather than fit-to-window for detailed inspection. Lossless full
4K [Base](after/convergence/native-base.png), [Normal](after/convergence/native-normal.png),
[Final](after/convergence/native-final.png), [Lamp](after/convergence/native-lamp.png)
and [Exterior](after/convergence/native-exterior.png) are also available.

All color/grayscale panels share exposure 0 and scale. Grayscale is a fixed
weighted conversion of displayed RGB; no per-image normalization. JPEG contact
sheets are navigation aids; individual PNGs are the lossless comparison source.

Reproduce final captures in PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/lighting-convergence/after'
node node_modules/@playwright/test/cli.js test tests/visual/convergence.visual.spec.ts --workers=1
python scripts/summarize-convergence.py after
```

To reproduce the original before/after comparison, first capture `d253f56` with
the new QA spec (no lighting edits) into `.../before`, then summarize with
`python scripts/summarize-convergence.py before`. Preserve that directory. On
the final revision set
`$env:CONVERGENCE_BASELINE='docs/screenshots/lighting-convergence/before/convergence'`
before running the spec; this activates exact Noon/Dusk/Night comparisons.
Do not regenerate `before` from the final lighting revision. Identical browser,
host and capture settings are needed for exact PNG equality.

Full validation uses `node node_modules/@playwright/test/cli.js test --workers=2`
with the same output root. This includes both existing DPR performance tests;
results live in `after/performance/`. On this Windows host Vite teardown can
hang after all tests complete; terminate only the Vite PID owned by that test
run to let Playwright report its final exit status.
