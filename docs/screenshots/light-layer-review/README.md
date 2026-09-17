# Light layers — visual review

Baseline: `1741b31`. Final frames use the unchanged artwork, default lighting and
bloom, with steam/motion frozen for repeatability. Left is before in comparisons.

| Time | Final | Before / after | Equal-mean lighting | Contacts | Face / straps | Sill |
| --- | --- | --- | --- | --- | --- | --- |
| 06:00 | [Final](after/shadow/0600-final.png) | [Compare](0600-compare.png) | [Form](0600-equal-mean-lighting.png) | [Detail](0600-contacts.png) | [Detail](0600-face-straps.png) | [Detail](0600-sill.png) |
| 12:00 | [Final](after/shadow/1200-final.png) | [Compare](1200-compare.png) | [Form](1200-equal-mean-lighting.png) | [Detail](1200-contacts.png) | [Detail](1200-face-straps.png) | [Detail](1200-sill.png) |
| 17:30 | [Final](after/shadow/1730-final.png) | [Compare](1730-compare.png) | [Form](1730-equal-mean-lighting.png) | [Detail](1730-contacts.png) | [Detail](1730-face-straps.png) | [Detail](1730-sill.png) |
| 23:00 | [Final](after/shadow/2300-final.png) | [Compare](2300-compare.png) | [Form](2300-equal-mean-lighting.png) | [Detail](2300-contacts.png) | [Detail](2300-face-straps.png) | [Detail](2300-sill.png) |

Neutral comparisons normalize mean luminance to 100; they show structure without
the artwork's painted shading. They are diagnostic images, not final appearance.
`after/layers/` contains separate ambient/form/contact/directional/lamp/shadow
captures. [Metrics](structure-metrics.json) and [performance](isolated-performance.json)
are local evidence; see [decisions and limitations](../../logs/light-layer-review.md).

Reproduce final captures in PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/light-layer-review/after'
npx playwright test --workers=2
python scripts/summarize-light-layers.py
```

The comparison script requires `before/shadow/` from baseline capture as well.
PNG/JSON files are ignored by Git under the existing local QA artifact policy.
