# Code-only lighting salvage

Baseline `f941549`; four times share 1920×1080, DPR 1, normal v2, default lighting,
exposure 0, bloom .22, correction 0, frozen motion/steam. Left is before in strips.

| Time | Before Final | After Final | Comparison | After Shadow | After Lamp |
| --- | --- | --- | --- | --- | --- |
| 06:00 | [Before](before/layers/0600-final.png) | [After](after/layers/0600-final.png) | [Pair](0600-compare.png) | [Shadow](after/layers/0600-shadow.png) | [Lamp](after/layers/0600-lamp.png) |
| 12:00 | [Before](before/layers/1200-final.png) | [After](after/layers/1200-final.png) | [Pair](1200-compare.png) | [Shadow](after/layers/1200-shadow.png) | [Lamp](after/layers/1200-lamp.png) |
| 17:30 | [Before](before/layers/1730-final.png) | [After](after/layers/1730-final.png) | [Pair](1730-compare.png) | [Shadow](after/layers/1730-shadow.png) | [Lamp](after/layers/1730-lamp.png) |
| 23:00 | [Before](before/layers/2300-final.png) | [After](after/layers/2300-final.png) | [Pair](2300-compare.png) | [Shadow](after/layers/2300-shadow.png) | [Lamp](after/layers/2300-lamp.png) |

- [23:00 near-lamp objects](2300-near-lamp.png), [desk/contact](2300-desk.png), [character](2300-character.png).
- [17:30 equal-mean Neutral](1730-equal-mean.png), [23:00 equal-mean Neutral](2300-equal-mean.png). Diagnostics normalize mean to100; they are not final appearance.
- [Lamp Fields](after/salvage/2300-fields.png): R near, G desk, B character, white emitter.
- Optional correction: [off](after/salvage/2300-correction-0.png), [.25](after/salvage/2300-correction-0.25.png). Default remains off.
- [Probe results](after/salvage/probes.json), [comparison metrics](comparison-metrics.json).
- [Hardware browser screenshot](edge-d3d11-browser-night.png), [software screenshot](software-browser-night.png).
- [Forced-redraw performance](performance.json), [default steam/bloom performance](performance-animated.json).
- [Full decisions, validation and remaining limitations](../../logs/code-only-lighting-salvage.md).

Reproduce after captures with `$env:VISUAL_OUTPUT_ROOT='docs/screenshots/code-only-salvage/after'`
then `npx playwright test --workers=2`. Run `python scripts/summarize-salvage.py`
after both `before/layers/` and `after/layers/` captures exist.
Run `node scripts/compare-lighting-performance.mjs f941549` separately from tests;
append `--animated` for existing steam/bloom RAF timings. Baseline server shares
current public assets only for runtime comparison, not the visual before images.
PNG/JSON remain local, untracked artifacts under the repository's existing policy.
