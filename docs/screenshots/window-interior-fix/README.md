# Window lower interior correction

[Before / After: user's red-box area](comparison.png)

- [Before](final-before.png)
- [After](final-after.png)
- [Original artwork with source coordinates](source-grid.png)
- [Exterior diagnostic](exterior-after.png)
- [06:00](after/shadow/0600-final.png)
- [12:00](after/shadow/1200-final.png)
- [17:30](after/shadow/1730-final.png)
- [23:00](after/shadow/2300-final.png)

Baseline: spatial-convergence-3, fixed default exposure/settings. Current captures:
`VISUAL_OUTPUT_ROOT=docs/screenshots/window-interior-fix/after` with
`tests/visual/lighting-shadow.visual.spec.ts` and `tests/visual/window-light.visual.spec.ts`.
Comparison crop is (1312,384)…(1920,672) from the 1920×1080 screenshots, enlarged 2×.
Images remain local under the repository's existing ignore policy.

See [correction notes](../../logs/window-interior-fix.md).
