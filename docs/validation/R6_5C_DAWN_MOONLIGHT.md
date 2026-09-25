# R6.5C — Dawn polish and directional moonlight

Scope: Scene Lighting shader only. The frozen lighting energy/time curve, Sky RGB and timeline, Base/Normal assets, motion, Blink, Leaves, R5 material response, and R6 Post remain unchanged. No lamp or R7 work.

## Dawn

At low morning sun, a registered character response now softens the darkest directional band on the screen-left hair, face, white sleeves, and vest. The shadow contrast floor is `-0.12` only within these regions, with a small cool gray-blue ambient fill on the back-facing side. Bang/chin contacts and Base-guided shirt folds retain their structure at 70% and 65% of the previous Dawn strength. The light-facing planes and architecture still respond to the original solar direction. This response fades continuously as the sun rises and is controlled by the existing Directional Shading switch.

The left-hair fill combines existing hair/material masks, a soft local contour, and the painted hair pigment. An earlier broader head mask revealed speckling beside the eye; the final contour excludes that area. Dusk and Noon shader output are pixel-identical to the previous committed R6.5B static captures.

## Night

Moon shaping uses the **existing continuously rotating nighttime Direction vector**, broad Normal, and a soft painted side gradient. It no longer uses a fixed angle: as the vector turns from 22:00 through midnight toward dawn, the receiving and shadow sides shift with it. The response is a low-contrast cool modulation with a small blue fill and registered hair sheen. The negative contrast is floored at `-0.08` so dark clothing and stone do not collapse. Night sky weight and low key intensity gate it out continuously through twilight; the existing 20:00–05:00 Night hold keeps the energy restrained. The Directional Shading switch gates both new Dawn and Moon responses; R5 Detail OFF does not remove the moon crown mask.

## Visual iterations and review

Four shader rounds preceded the final direction correction: initial weak shaping; stronger Dawn fill and Night contrast; redistributed Night highlights; then exclusion of an eye-adjacent hair-mask artifact. The final moon pass replaced the fixed angle with the rotating vector. [Full four-phase sheet](r6-5c-dawn-moon/final/four-phase.jpg), [Dawn face/hair comparison](r6-5c-dawn-moon/final/face-hair-zoom.jpg), [Night 22:00](r6-5c-dawn-moon/final/night.png), [22:00 / 00:00 / 02:00 / 04:30 contact](r6-5c-dawn-moon/final/night-hold.jpg), and [larger moon-direction crops](r6-5c-dawn-moon/final/moon-direction-detail.jpg) are the main manual review targets. [Combined animation captures](r6-5c-dawn-moon/final/combined-contact.jpg) cover Blink, Breathing, Hair, and Leaves.

The static 24H scan reports Noon artwork luminance `0.21972`, daylight peak `0.21975` at 12:45, and an evening face minimum above the 22:00 Night value. The Night artwork mean remains near 31/255 at the four reviewed hold times; 00:00 and 24:00 are pixel-identical. The rotating moon changes local light placement, with no late-night global brightening trend.

## Validation

`pnpm build`, `pnpm typecheck`, `scripts/audit_lighting_24h.py`, and `scripts/validate_post.py`, `validate_lighting_detail.py`, `validate_time_controller.py`, `validate_hair_motion.py`, `validate_blink_normal.py`, and `validate_breathing.py` pass. The Post OFF baseline verifies that Directional Shading OFF restores the frozen scene. The remaining limitation is the fixed 2D artwork/Normal: the moon response provides broad receiving planes and painted side structure, not geometric cast shadows. Await human visual review before freezing R6.5C; do not begin R7.
