# R4.1 Head mass and nearby hair motion

Status: self-reviewed and ready for human visual acceptance. R4 lower-hair motion is retained; this round does not change Lighting, Sky, Timeline, Leaves, or Breathing parameters.

## Structure

The existing [registered 1672×941 mask](../../public/assets/hero/motion/hair-motion-mask.png) now uses blue for one whole-head mass and alpha for secondary nearby strands. Red/green lower-hair weights are pixel-identical to `e521bb6`. The [mask generator](../../scripts/paint_hair_motion_mask.py) keeps the face, hat, rose, and ribbon in one softly bounded head region. Secondary regions cover the bangs above the eye patches, both face-side locks, and hair between head and shoulder. Blink rectangles and the ribbon are protected from the secondary warp. [Final region overlay](r4-1-head-motion/round3/region-overlay.png) distinguishes all four channels.

The head translates by up to **0.9 source px** horizontally with a smaller vertical component, using a weak Breathing-phase link plus the existing 6.4 s and 9.1 s Hair phases. This is an almost rigid translation, without separate hat/flower/ribbon transforms or visible head rotation. The nearby hair adds up to **2.1 source px** with left/right phase difference; the existing lower hair stays at **5.2 source px** configured maximum. All three channels share one deformed UV for Albedo and Normal before lighting. Sky and edge tone still sample original UV.

Blink in Lit continues to use its registered shader patch. With Hair enabled, Base view also uses that shader patch instead of the stationary DOM eye images, so closed eyes move with the head. Hair off restores the original Base DOM path.

## Iterations and review

| Round | Change and observation |
| --- | --- |
| 1 | Added the two channels at head 0.75 px / nearby hair 1.8 px, then inspected ×2 stress. Face, hat, rose, and ribbon moved together; the tower remained fixed. The blue falloff extended a little far beyond the hat. [Stress overlay](r4-1-head-motion/round1/region-overlay.png), [head contact](r4-1-head-motion/round1/head-contact.png). |
| 2 | Narrowed the head-edge feather from 10 to 7 source px at normal strength. The contour remained smooth, with less sky/architecture in the transition. [Head motion GIF](r4-1-head-motion/round2/normal-preview.gif), [sampled contact](r4-1-head-motion/round2/head-contact.png). |
| 3 | Raised only the new channels to 0.9 / 2.1 px for clearer micro motion. Lower hair remained unchanged. [Normal head GIF](r4-1-head-motion/round3/normal-preview.gif), [Night full-composition GIF](r4-1-head-motion/round3/full-composition.gif), [sampled contact](r4-1-head-motion/round3/head-contact.png). |

The full Lit + Sky + Lighting + Breathing + Hair + Blink + Leaves composition ran about 22 seconds per preset: [Dawn](r4-1-head-motion/round3/dawn.png), [Noon](r4-1-head-motion/round3/noon.png), [Dusk](r4-1-head-motion/round3/dusk.png), [Night](r4-1-head-motion/round3/night.png). [Lit Blink](r4-1-head-motion/round3/blink-hair.png) and [Base Blink](r4-1-head-motion/round3/base-blink-hair.png) both close cleanly; [Breathing + Hair](r4-1-head-motion/round3/breathing-hair.png) keeps the neckline continuous. The browser regression checks head movement, near-rigid face/hat relation, static architecture, Normal UV movement, Base/Lit Blink, hidden-tab pause, reduced motion, and Static fallback. A sample of 24 active draws had 0.3 ms median CPU submission time (8.7 ms maximum); GPU duration is not measured.

`pnpm build`, `pnpm typecheck`, `python scripts/validate_hair_motion.py`, `python scripts/validate_time_controller.py`, `python scripts/validate_blink_normal.py`, and `python scripts/validate_breathing.py ...` passed. The latter two browser baselines disable Hair for frozen-frame comparisons.

At ×2 stress, a faint transition can be seen outside the head contour; at normal strength it is subdued. The accepted small upper Sky-edge residual remains deferred to R5/R7. Recommend freezing the Hair Motion stage after human review; do not start R5 in this round.
