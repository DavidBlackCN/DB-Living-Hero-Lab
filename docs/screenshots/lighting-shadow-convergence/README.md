# Lighting / Shadow Convergence review

Before: `add7696`. [Decision log](../../logs/lighting-shadow-convergence.md).
Screenshots use default Normal v2, exposure 0, correction off, reduced motion,
animation/steam off and hidden UI, at 1920×1080 DPR 1. No per-image exposure or
contrast normalization. Images/JSON are generated local artifacts, ignored by Git.

- [Four-time comparison](review/four-times.jpg).
- [17:30 Before/After](review/1730-before-after.jpg), [23:00 Before/After](review/2300-before-after.jpg).
- [Lamp underside / sill objects](review/lamp-sill.jpg).
- [Face / blouse protection](review/face-cloth.jpg), [reading-area detail](review/reading-area.jpg).
- [17:30 shadow off/on](review/1730-shadow-control.jpg), [23:00 shadow off/on](review/2300-shadow-control.jpg).
- [06:00 recheck](review/0600-before-after.jpg), [raw comparison measurements](review/comparison.json).

| Time | Required lossless PNGs |
| --- | --- |
| 06:00 | [Final](after/shadow/0600-final.png), [Neutral](after/shadow/0600-neutral.png), [Shadow](after/shadow/0600-shadow.png) |
| 12:00 | [Final](after/shadow/1200-final.png), [Neutral](after/shadow/1200-neutral.png) |
| 17:30 | [Final](after/shadow/1730-final.png), [Neutral](after/shadow/1730-neutral.png), [Shadow](after/shadow/1730-shadow.png) |
| 23:00 | [Final](after/shadow/2300-final.png), [Lamp](after/shadow/2300-lamp.png), [Shadow](after/shadow/2300-shadow.png), [Exterior](after/shadow/2300-exterior.png) |

Shadow shows attenuation (brighter means darker contribution), not a physical
shadow map. Lamp is the raw lamp coefficient before composite corrections;
Neutral is the resulting total light. Additional 4K night output from the existing
convergence suite is in `after/convergence/native-*.png`. JPEG contact sheets aid
browsing; use individual PNGs for lossless inspection.

Reproduce final tests and gallery in PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/lighting-shadow-convergence/after'
node node_modules/@playwright/test/cli.js test --workers=2
python scripts/summarize-lighting-shadow.py
```

Before was captured at `add7696` using the new capture test alone, before runtime
edits, with output root `docs/screenshots/lighting-shadow-convergence/before`:
`node node_modules/@playwright/test/cli.js test tests/visual/lighting-shadow.visual.spec.ts --grep "shadow convergence captures" --workers=1`.
Do not regenerate before from the final revision. Leave the older
`CONVERGENCE_BASELINE` option unset; this task authorizes changes to the protected
times while requiring visual regression review. Windows Vite teardown can wait
after all tests finish; stop only the test-owned Vite PID to complete teardown.
