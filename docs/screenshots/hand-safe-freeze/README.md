# Hand-safe lighting freeze review

Actual 1920×1080 browser captures. Animation and steam are disabled. Before is
commit `f80e79f`; after uses the local hand-safe implementation. PNG and JSON
outputs are ignored validation artifacts generated beside this tracked index.

## 23:00 acceptance

- [Before / After hand crop](2300-hand-before-after.png) — identical
  x1280–1550/y680–860 crop, enlarged equally.
- [Final](after/hand-safe/2300-final.png)
- [Effective normal](after/hand-safe/2300-normal.png)
- [Form shadow](after/hand-safe/2300-form.png)
- [Shadow / occlusion](after/hand-safe/2300-shadow.png)
- [Contact](after/hand-safe/2300-contact.png)
- [Lamp contribution](after/hand-safe/2300-lamp.png)
- [Hand semantic mask](after/hand-safe/2300-masks.png)
- [Combined diagnostic before / after](diagnostics-before-after.png)

## Regression

- [12:00 identical-crop comparison](1200-hand-before-after.png)
- [17:30 identical-crop comparison](1730-hand-before-after.png)
- [12:00 after crop](after/hand-safe/1200-hand.png)
- [17:30 after crop](after/hand-safe/1730-hand.png)

Reproduce the dedicated captures:

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/hand-safe-freeze/after'
npx playwright test tests/visual/hand-safe.visual.spec.ts
```

Technical finding and freeze decision:
[hand-safe lighting log](../../logs/hand-safe-freeze.md).
