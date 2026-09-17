# Technical Art Alignment — visual review

Default `/` now displays normal v2. Old alternatives remain at
`/?normal=registered` (v1) and `/?normal=low-frequency`. Optional correction:
`/?correction=1`, then toggle the experiment in the debug panel.

- [Four times before / after](final/alignment/before-after.jpg)
- [Final / actual grayscale / Neutral / Normal / Projected / Lamp / Exterior](final/alignment/four-times.jpg)
- [23:00 local volume before / after / isolated lamp](final/alignment/night-volume.jpg)
- [Correction OFF / ON / amplified difference](final/alignment/correction-comparison.jpg)
- [v2 source-registered guides](calibrated/v2-source-guides.png)
- [Normal v1 / Normal v2 / Original guides close review](normal-only/detail.jpg)
- [Window source](final/acceptance/night-window-base.png), [23:00 Final](final/acceptance/night-window-final.png), [Exterior](final/acceptance/night-window-exterior.png)

| Time | Final | Neutral | Directional | Normal | Projected | Lamp | Exterior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 06:00 | [view](final/alignment/v2-dawn-final.png) | [view](final/alignment/v2-dawn-neutral.png) | [view](final/alignment/v2-dawn-directional.png) | [view](final/alignment/v2-dawn-normal.png) | [view](final/alignment/v2-dawn-projected.png) | [view](final/alignment/v2-dawn-lamp.png) | [view](final/alignment/v2-dawn-exterior.png) |
| 12:00 | [view](final/alignment/v2-noon-final.png) | [view](final/alignment/v2-noon-neutral.png) | [view](final/alignment/v2-noon-directional.png) | [view](final/alignment/v2-noon-normal.png) | [view](final/alignment/v2-noon-projected.png) | [view](final/alignment/v2-noon-lamp.png) | [view](final/alignment/v2-noon-exterior.png) |
| 17:30 | [view](final/alignment/v2-dusk-final.png) | [view](final/alignment/v2-dusk-neutral.png) | [view](final/alignment/v2-dusk-directional.png) | [view](final/alignment/v2-dusk-normal.png) | [view](final/alignment/v2-dusk-projected.png) | [view](final/alignment/v2-dusk-lamp.png) | [view](final/alignment/v2-dusk-exterior.png) |
| 23:00 | [view](final/alignment/v2-night-final.png) | [view](final/alignment/v2-night-neutral.png) | [view](final/alignment/v2-night-directional.png) | [view](final/alignment/v2-night-normal.png) | [view](final/alignment/v2-night-projected.png) | [view](final/alignment/v2-night-lamp.png) | [view](final/alignment/v2-night-exterior.png) |

Captures: 1920×1080, DPR 1, hidden UI, reduced motion, no steam/animation. Four
times use identical default exposure; no per-image normalization. Neutral is
lighting coefficient luminance, while Grayscale is converted from actual Final.
GPU response tests use a 1200×675 viewport and same-frame readback.

Rebuild and validate in PowerShell:

```powershell
npm run assets:normal
npm run assets:correction
npm run typecheck
npm test
npm run build
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/technical-art-alignment/final'
node node_modules/@playwright/test/cli.js test --workers=2
python scripts/summarize-alignment.py
```

The standalone `scripts/capture-alignment.mjs <output> <normal> <port>` can also
capture guides and four-time evidence against an already running local app.
Historical before images need the starting renderer and are not recreated by
the final source. QA PNG/JPG/JSON remain local and ignored by existing Git rules.
The summary script tolerates missing historical captures in a fresh clone.

See [implementation and assessment](../../logs/technical-art-alignment.md),
[normal v2](../../logs/normal-v2-review.md), [light integration](../../logs/normal-light-integration.md),
and [correction limits](../../logs/delight-experiment.md).
