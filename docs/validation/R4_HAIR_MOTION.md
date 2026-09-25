# R4 Hair Motion v1

Status: implementation and self-review complete; pending human visual acceptance. R3 and its accepted Sky edge result are frozen. The small top-leaf Sky residual remains accepted and deferred to R5/R7 polish.

## Design

The [Kumeng scene shader](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts) uses small layered frequencies and material/face protection, with one motion clock in its [scene component](https://github.com/buger404/KumengScreen/blob/main/components/dream-scene.tsx). DB borrows those design ideas, not its short-hair geometry, coordinates, or amplitudes. The online reference page was unavailable in this run, so the comparison used source code.

The [1672×941 two-channel mask](../../public/assets/hero/motion/hair-motion-mask.png) is authored by [paint_hair_motion_mask.py](../../scripts/paint_hair_motion_mask.py). Red covers the image-left lower fall; green covers the longer image-right fall. Polygon cores, a vertical root-to-tip ramp, a 12-source-pixel feather, and a light sleeve guard keep the face, eyes, hat, rose, ribbon, shirt, vest, and scene outside the moving region. [Region overlay](r4-hair-motion/final/region-overlay.png) shows both lobes. No new UV region affects the top hair or fringe.

One WebGL2 fragment UV displacement follows the existing Breathing displacement and precedes both Albedo and Normal sampling. The Blink patch uses that same UV but lies outside the hair mask. Sky and the registered edge tone continue sampling original UV. Right and left lobes have different phases, spatial phase gradients, and strengths (right 1.0, left 0.83). A 6.4-second primary sway and 9.1-second secondary drift produce predominantly horizontal motion with a small vertical arc. Maximum configured normal strength is 5.2 source pixels; actual weighted tip motion is lower. The ×2 stress control can reach 10.4 source pixels for inspection only. Hair and Leaves are not mechanically linked; their independent phases suggest one environment without matching every leaf.

Hair shares the existing capped 30-draw/s WebGL motion driver with Breathing. Its clock wraps only after 582.4 seconds, the common whole-cycle boundary of both frequencies, so long sessions have no phase jump. When both motions are off, rendering returns to on demand. Hidden tabs pause without accumulating elapsed time; reduced motion and Static quality disable Hair. Blink and Leaves keep their independent existing behavior.

## Three visual rounds

| Round | Problem → change → result |
| --- | --- |
| 1 | Started at ×2 stress to expose mask errors. Motion was visible, with stable face/ribbon/rose, but outer right and left feather reached too far toward scenery. [Overlay](r4-hair-motion/round1/region-overlay.png), [three-frame comparison](r4-hair-motion/round1/motion-contact.png). |
| 2 | Pulled both distal polygons inward and tried ×1.4. Motion remained visible and the protected face was pixel-stable; less right-tree and sleeve overlap. [Overlay](r4-hair-motion/round2/region-overlay.png), [comparison](r4-hair-motion/round2/motion-contact.png). |
| 3 | Set normal maximum to 5.2 source pixels, between the weak starting amplitude and the exploration previews. Captured isolated motion and full combination. [Normal motion GIF](r4-hair-motion/final/normal-preview.gif), [full Night composition GIF](r4-hair-motion/final/full-composition.gif), [sampled contact](r4-hair-motion/final/normal-contact.png). |

## Regression

Lit + Sky + Lighting + Breathing + Hair + Blink + Leaves ran for at least 22 seconds at each preset: [Dawn](r4-hair-motion/round3/dawn.png), [Noon](r4-hair-motion/round3/noon.png), [Dusk](r4-hair-motion/round3/dusk.png), [Night](r4-hair-motion/round3/night.png). Night remained readable; no global lighting or sky parameter changed. [Blink with Hair](r4-hair-motion/round3/blink-hair.png) shows closed eyes without a shifted patch; [Breathing with Hair](r4-hair-motion/round3/breathing-hair.png) keeps the garment edge registered. The two motion phases do not share a period.

The focused browser check confirms hair-only movement in the hair bounds, pixel-stable face and background, Normal motion from the same UV, hidden-tab pause/resume, reduced-motion disablement, and Static fallback. The current browser run reported 0.3 ms median / 0.6 ms maximum for 24 sampled WebGL draw times with Hair active, using the 30-draw/s cap; these CPU timings do not include all GPU work. `pnpm build`, `pnpm typecheck`, `python scripts/validate_time_controller.py`, `python scripts/validate_blink_normal.py`, `python scripts/validate_breathing.py ...`, and `python scripts/validate_hair_motion.py` passed. The time and breathing image comparisons now use the accepted R3.2c baseline with Hair explicitly disabled.

The motion is deliberately strongest in interior long strands; the thinnest outer wisps remain partly static to avoid pulling the distant trees or sky. Recommend freezing Character Motion Core after human acceptance. No R5 work is included.
