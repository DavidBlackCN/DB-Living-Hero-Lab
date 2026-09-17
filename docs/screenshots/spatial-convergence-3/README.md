# Hero light / shadow review

Actual Chromium/WebGL captures, 1920×1080, DPR1, exposure 0, default Shadow .65,
normal v2, correction off, animation/steam disabled. [Implementation and validation](../../logs/spatial-convergence-3.md).

| Time | Final | Before / After |
|---|---|---|
| 06:00 | [Dawn](after/shadow/0600-final.png) | [Compare](0600-comparison.png) |
| 12:00 | [Noon](after/shadow/1200-final.png) | [Compare](1200-comparison.png) |
| 17:30 | [Dusk](after/shadow/1730-final.png) | [Compare](1730-comparison.png) |
| 23:00 | [Night](after/shadow/2300-final.png) | [Compare](2300-comparison.png) |

Inspect [night lamp/sill](2300-lamp-sill.png), [night book/contacts](2300-contacts.png),
[dusk face/straps](1730-face-straps.png), [night exterior](after/shadow/2300-exterior.png),
[night lamp coefficient](after/shadow/2300-lamp.png), [dusk shadows](after/shadow/1730-shadow.png),
[night shadow off](after/shadow/2300-shadow-off-final.png) and
[native 4K night](after/convergence/native-final.png).

`after/shadow/` includes Final / Neutral / Shadow / Lamp / Exterior / Projected /
Base / Normal for all four times. QA raster/JSON files stay local by repository policy.
