# R4.1b Head motion gain

Status: self-reviewed, ready for human visual acceptance. This round changes only the two existing head-motion gain constants.

| Channel | R4.1 | Final | Change |
| --- | ---: | ---: | ---: |
| Whole-head mass | 0.9 source px | 1.8 source px | +100% |
| Nearby hair | 2.1 source px | 3.0 source px | +42.9% |
| Lower long hair | 5.2 source px | 5.2 source px | unchanged |

The 6.4 s and 9.1 s phases, Breathing coupling, four-channel registered mask, shader UV path, and Blink/Leaves/Lighting/Sky behavior are unchanged.

## Tuning

1. Tried 1.5 / 3.2 px. The head was more visible but still reserved in the full composition.
2. Tried 1.8 / 3.6 px. The head and side strands became easier to perceive. The image-left upper clothing/hair junction pulled a little too visibly.
3. Kept the whole-head gain at 1.8 px and reduced nearby hair to 3.0 px. The head remains perceptible without an apparent nod or shake; the upper clothing junction is calmer. A very slight junction pull remains inherent to the current registered warp.

In sampled Noon head clips, face translation span increased from roughly 0.95 to 1.75 screen px horizontally. This is a visual cross-check from two live captures, not a deterministic benchmark. [Final head animation](r4-1b-head-gain/final/normal-preview.gif) and [Night combined animation](r4-1b-head-gain/final/full-composition.gif) are available for review.

## Regression

The combined composition was held and captured at [Dawn](r4-1b-head-gain/final/dawn.png), [Noon](r4-1b-head-gain/final/noon.png), [Dusk](r4-1b-head-gain/final/dusk.png), and [Night](r4-1b-head-gain/final/night.png). [Lit Blink](r4-1b-head-gain/final/blink-hair.png), [Base Blink](r4-1b-head-gain/final/base-blink-hair.png), and [Breathing + Hair](r4-1b-head-gain/final/breathing-hair.png) were also captured. The Hair browser regression passed registered masks, rigid face/hat relation, static architecture, Albedo/Normal shared UV, Base/Lit Blink, and visibility/reduced/static behavior. `pnpm build` and `pnpm typecheck` passed.

No R5 work was started. Await human review before freezing Hair Motion.
