# Face finishing review

Before: `65e3fe8`. Same viewport1920×1080, DPR1, default normal v2/light/exposure,
bloom .22, correction0, frozen motion and steam. Left=before, right=after.

| Time | Final | Face before/after | Whole-frame before/after |
| --- | --- | --- | --- |
| 06:00 | [Final](after/layers/0600-final.png) | [Face](0600-face.png) | [Whole](0600-compare.png) |
| 12:00 | [Final](after/layers/1200-final.png) | [Face](1200-face.png) | [Whole](1200-compare.png) |
| 17:30 | [Final](after/layers/1730-final.png) | [Face](1730-face.png) | [Whole](1730-compare.png) |
| 23:00 | [Final](after/layers/2300-final.png) | [Face](2300-face.png) | [Whole](2300-compare.png) |

[Implementation and checks](../../logs/face-finish.md), [pixel metrics](metrics.json),
[skin/hair safety probes](after/face/probes.json). Local PNG/JSON are ignored by
Git under the existing QA policy. Source art and all runtime assets are unchanged.

Recreate current captures in PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/face-finish/after'
npx playwright test --workers=2
```

Face comparison crops use pixel bounds(1040,176)–(1296,416) on final1920×1080
captures, resized equally for viewing. Metrics exclude a larger rectangle to
account for feather/bloom. Before images require the baseline code capture.
