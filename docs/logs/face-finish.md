# Face transition finishing pass — 2026-09-18

Baseline: `65e3fe8`. User scope: only soften the over-dark upper-face/fringe
transition and close the lighting phase. No global or lamp/projection redesign.

## Finding and minimal fix

Read the existing face-safe blend, face/hair masks, contact caps and the local
Kumeng lighting analysis. Face-normal protection is the relevant reference idea;
no reference shader or scene-specific geometry was transplanted.

The coarse face contour starts at the fringe's lower edge. Exposed peach skin
above it inherits hair normals and hair occlusion, while the cheek receives face
protection. Neutral diagnostics show the resulting boundary. Contact darkening
on the existing face is already capped; reducing global shadow strength would
not address the misclassified forehead and would damage other contacts.

Only `src/engine/shaders.ts` runtime code changes (20 added lines):
- `foreheadSafety` uses soft artwork bounds x661–800/y110–190 on the 1200×675
  reference plus source-pigment G and B/G transitions to identify exposed skin.
- Soft-union that weight into existing face protection, transferring the same
  coverage out of hair. This avoids double material weights or a feather seam.
- Blend 75% of the newly protected skin's erroneous hair normal toward the
  frontal face normal, scaled by the existing face control. Retain local form.

No texture samples, passes, assets or settings are added. Eyes/brows/dark brown
bangs fail the pigment gate. The original illustration's linework and painted
shadows remain intact. The existing night face floor is unchanged. Normal debug
shows the effective lighting normal; the registered normal asset is unchanged.

This is deliberately artwork-specific. It must be rechecked if the artwork is
ever replaced; it is not a general face segmentation algorithm.

## Four-time review

Same 1920×1080/DPR1, default settings, motion/steam off and bloom .22 before/after.
See [gallery](../screenshots/face-finish/README.md).

| Time | Inspection |
| --- | --- |
| 06:00 | Exposed forehead loses the cold gray hair-shading patch; fringe shade remains |
| 12:00 | Skin above the eyes joins cheek lighting without a heavy band; brows preserved |
| 17:30 | Warm direction and hair volume remain; only upper skin transition softens |
| 23:00 | Forehead correction is restrained; cheek and low night ambience unchanged |

Lower-cheek comparison patch max difference is 0 at every time. Outside a
conservative face-local rectangle (1020,150)–(1315,335), max final difference is
1/255 for daytime and 0 at night (existing bloom can spread sub-level changes).
At one exposed-forehead patch, mean RGB before→after is dawn138→174, noon176→205,
dusk128→163, night84→92. These are 8-bit image values, not physical illumination.
The narrower night change is consistent with keeping a dark room rather than
introducing an emissive face. Window masks and lamp/projected core remain intact.

## Validation and freeze decision

`npm run typecheck`, `npm run build`, 7 unit tests and all 52 Playwright checks
passed. New test checks both exposed forehead regions, preserved brown bangs,
unchanged cheek/hat/desk classification, softened local normal, and a fully dark
result when all sources are off at every review time. The first provisional
probe was on a brown strand; source inspection corrected it to exposed skin.
Existing face/window/lamp/hand-page guards were retained without relaxed limits.

Ready to freeze this local finishing version from implementation/self-review.
Retain the source artwork's painted fringe shadow; do not try to erase it with
additional brightness. Previous software-renderer high-DPR limits remain outside
this local change. No new animation or next-stage work is started.
