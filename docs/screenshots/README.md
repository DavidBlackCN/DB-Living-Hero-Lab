# Visual validation artifacts

Screenshots and generated metrics are local QA artifacts, excluded from Git.
Only Markdown instructions in this directory are tracked. Runtime artwork and
technical textures under `public/assets/` remain tracked.

Current instructions: [spatial light / shadow / glass review](spatial-light-review/README.md).
Image links there work after local capture; images are not shipped in a fresh clone.

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/spatial-light-review/final'
npm run test:visual
python scripts/summarize-spatial-review.py
```

Old phase screenshots and rejected Blink preview images were removed during the
2026-09-16 cleanup. Historical observations remain in `docs/logs/`; this cleanup
does not rewrite earlier Git commits. Pre-change captures cannot be recreated
using the current renderer. The summary script skips unavailable earlier stages.
