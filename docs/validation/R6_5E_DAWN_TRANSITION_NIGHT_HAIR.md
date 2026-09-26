# R6.5E — Dawn face, 05:00 transition, Night hair

Status: implementation and local review complete; awaiting human visual acceptance. No R7 work.

## Root cause and changes

- `moonDirectionFor()` wrapped the visible 20:00–05:00 moon arc to its 20:00 start at exactly 05:00. The Night sky weight and moon key were still nonzero, so this caused a 145° → 35° direction jump. The moon now follows the same overnight arc and returns smoothly through the hidden daytime interval, joining at 05:00 and 20:00. Night direction and elevation at 20:00, 22:00, 00:00, 02:00 and 04:30 retain their previous values.
- As the Night sky/moon fades after 05:00, solar energy has not yet risen enough; at 05:30 ambient fell to 0.142 and the artwork briefly dipped below late Night. A small eased ambient overlap (peak +0.025 at 05:30, zero at 05:00 and 06:30) closes that gap. No global exposure, accepted Dawn anchor, Noon or Dusk parameter changes.
- Dawn face shading now uses a feathered registered face core and both eye regions to lift the darkest solar contrast band and add local neutral/cool fill. Bang contact stays on the upper forehead/lid, with reduced contact over both eyes. No face fill is added to Dusk.
- Night's additive hair sheen no longer applies across whole lower-hair, secondary-hair and crown masks. Narrow ribbons follow selected outer locks on the moon-facing side, with a smaller crown edge contribution; the cool sheen strength changes from `0.100` to `0.065` and is less white. The broader Moon key on face, clothes and architecture is retained.

## Visual review

- [Dawn face 2× before/after](r6-5e/review/dawn-face-2x.png) and [eye/face 4× before/after](r6-5e/review/dawn-face-4x.png): both eyes, nose bridge, mouth and face center are clearer. In the 4× crop, mean RGB rose approximately 7/7/6 code values; the painted eyelid and fringe remain.
- [04:30 / 05:00 / 05:30 / 06:00 contact sheet](r6-5e/review/dawn-transition-contact.png). Full frames and direction readouts are in [`r6-5e/after/`](r6-5e/after/). 04:59, 05:00 and 05:01 read 145° / 12°; their artwork mean absolute RGB differences are below 0.10 code values per minute. Artwork mean brightness at 04:30 / 05:00 / 05:30 / 06:00 is 35.90 / 35.32 / 35.05 / 48.03.
- [Night hair 2× before/after](r6-5e/review/night-hair-2x.png): the interior and central bangs no longer carry the same broad glossy sheet; selected outer locks retain cold moon pickup.
- Final [Dawn full frame](r6-5e/after/dawn.png) and [Night full frame](r6-5e/after/22h.png). The prior corresponding frames are in [`r6-5e/before/`](r6-5e/before/).
- Noon and Dusk artwork screenshots were pixel-identical to the previous commit in the static WebGL2 capture. Midnight and 24:00 remain pixel-identical. The Night atmosphere and 24H preview behavior are otherwise unchanged.

## Validation

- `pnpm build` and `pnpm typecheck`: passed.
- `python scripts/capture_moon_direction.py docs/validation/r6-5e/after`: passed, including the 04:59/05:00/05:01 artwork jump bound and exact 00:00/24:00 equality.
- `python scripts/validate_post.py`, `python scripts/validate_lighting_detail.py`, `python scripts/validate_hair_motion.py`: passed. The Hair regression exercises moving head, Normal UV and Blink coexistence.
- The older `validate_time_controller.py` was attempted twice. Its clock-driven Play/Pause assertion at line 88 failed once and the second run stalled in Playwright's fake clock; it also compares screenshots against a pre-R6.5 frozen visual baseline. The focused browser capture above verifies manual 24H preview, midnight equality and the repaired 05:00 continuity, but this legacy controller test remains an open test-harness issue.

Static review captures disabled Blink, Breathing, Hair Motion and Leaves to isolate lighting; runtime regressions exercise their integration separately.
