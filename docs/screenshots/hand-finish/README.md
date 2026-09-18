# Left-hand finishing review

Actual browser renders. Comparisons: before left, after right.
PNG/JSON outputs are local ignored validation artifacts.

| Time | Hand comparison | Full final |
|---|---|---|
| 06:00 | [comparison](0600-hand.png) | [scene](after/layers/0600-final.png) |
| 12:00 | [comparison](1200-hand.png) | [scene](after/layers/1200-final.png) |
| 17:30 | [comparison](1730-hand.png) | [scene](after/layers/1730-final.png) |
| 23:00 | [comparison](2300-hand.png) | [scene](after/layers/2300-final.png) |

Capture using PowerShell:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/hand-finish/after'
npx playwright test tests/visual/light-layers.visual.spec.ts -g 'capture incident'
```

Before captures use baseline `4b3cf9d`. Closeups crop x1280–1550/y680–860
from 1920×1080 screenshots and enlarge both sides equally.
See [implementation and limitations](../../logs/hand-finish.md).
