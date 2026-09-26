# R6.5D — Moon direction, Dawn eye, Night key

This pass changes only Scene Lighting response and a small Moon Direction debug readout. No R7 lamp, Sky RGB/timeline, Base, Normal, motion, R5 material asset, or R6 Post change was made.

## Independent Moon Direction

`moonDirectionFor(minutes)` supplies a separate continuous vector to the shader. From 20:00 to 05:00, its azimuth eases from **35° to 145°** and elevation rises from **12° to 55°** near midnight, then falls. The vector is periodic at 00:00/24:00. The existing Sky Night weight fades the key through twilight; the Sun Direction and frozen lighting time curve are unchanged.

| Time | Moon azimuth | Elevation |
| --- | ---: | ---: |
| 20:00 | 35° | 12° |
| 22:00 | 49° | 40° |
| 00:00 | 81° | 54° |
| 02:00 | 116° | 49° |
| 04:30 | 144° | 19° |

The Dusk sun azimuth is about 144°; early Moon is 35°, placing their horizontal receiving sides opposite one another. The debug panel shows Moon azimuth/elevation, and `scripts/capture_moon_direction.py` asserts opposite early sides, ordered Moon angles, the midnight height peak, and exact 00:00/24:00 direction equality. See the [five-time Moon contact](r6-5d-moon/final/moon-direction-contact.jpg) and [Dusk versus Night](r6-5d-moon/final/dusk-vs-night.jpg).

## Dawn screen-left eye

The screen-left eye (character's right eye) now has a feathered protection ellipse centered on its registered iris. It limits the low-sun contrast on skin/iris, moves the local bang-contact reduction toward the upper lid/forehead, and adds a small pigment-preserving iris lift only while the eye is open. The dark lash and painted hair remain. In the fixed screenshot iris sample, mean RGB rises from `78.3` to `98.0/255`; the other iris remains `107.3/255`. The [4× before/after](r6-5d-moon/final/dawn-eye-before-after-4x.jpg) is the primary Dawn review image.

## Night Moon Key

The previous moon modulation is replaced by a separate cool directional key. Broad Normal and a soft painted side gradient concentrate it on the receiving side. White cloth and masonry take the stronger response; the face has a softer keyed fill; registered hair receives a wider cool highlight. The back side retains the existing Night ambient. Moon height tapers scene/hair energy at low elevation, while the face keeps steady gentle fill so the early-night transition does not dip and rebound. No exposure, global ambient, Bloom, or grading adjustment is used.

At 22:00, the artwork mean rises by `5.0/255` relative to R6.5C, but the screen-left scene changes by `8.73/255` and the screen-right scene by only `1.17/255`. This is a directional separation rather than uniform lifting. Night remains far below Dawn/Noon luminance. Review [Night full frame](r6-5d-moon/final/22h.png), [Night before/after](r6-5d-moon/final/night-before-after.jpg), [character crop](r6-5d-moon/final/night-character-1-5x.jpg), and [stone crop](r6-5d-moon/final/night-stone.jpg).

## Continuity and regression

Noon and Dusk artwork screenshots are pixel-identical to R6.5C. Final 00:00 and 24:00 artwork pixels are identical (the UI time labels differ). The 24H scan keeps Noon artwork luminance `0.21972`, with daylight peak `0.21975` at 12:45; the evening face minimum remains within the accepted Night level tolerance. Night artwork means at 20:00 / 22:00 / 00:00 / 02:00 / 04:30 are `33.77 / 35.37 / 35.18 / 37.10 / 36.29` out of 255, with no false-dawn climb. See the [hourly scan](r6-5d-moon/final/24h-audit/hourly-contact.png).

`pnpm build`, `pnpm typecheck`, the 24H audit, Post, R5 Detail, Time Controller, Hair, Blink/Normal, and Breathing regressions all pass. The shading is intentionally broad and illustration-led; the frozen 2D artwork does not provide geometric cast shadows. Await human review. Do not begin R7.
