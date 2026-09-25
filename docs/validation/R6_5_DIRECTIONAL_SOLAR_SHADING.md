# R6.5 Directional Solar Shading — human review candidate

R5 material detail and R6 Post remain in place. This change acts only on linear Scene Lighting, before the existing RGBM/Post handoff. Base/Normal assets, `lightingFor()`, `skyFor()`, R5 masks and material glints, R6 bloom/ACES/grading, and motion systems were not changed. It adds no cast-shadow system.

## Cause and response

The frozen Normal v3 is deliberately flat across many broad painted surfaces: typical face and sleeve X slopes are about ±0.05 and masonry is flatter. The previous broad Normal band mixed into diffuse with about 0.30 weight, so changing azimuth often altered color more visibly than surface illumination. The R5 face smoothing further reduced that cue.

The shader now samples the existing 5-source-pixel broad Normal and forms a **centered horizontal-facing band** from its XY slope and the existing sun vector. An 11× horizontal slope gain makes the low-amplitude broad normals visible without amplifying high-frequency bump. The face uses the filtered R5 normal at a 0.48 blend and 18% less added solar response, preserving eye and cheek stability. A weak, clamped horizontal painted falloff gives nearly flat stone and architecture a broad side-light cue. The band uses `smoothstep(-0.42, 0.42)` with no hard toon boundary.

The added response is continuous: daylight key intensity controls solar presence, light-direction Z controls the low-sun gain, and X determines which side receives light. Low Dawn/Dusk sun produces the strongest separation; overhead Noon retains only a small residue; Night's low key drops below the response window. A Debug `Directional Shading on/off` control plus `Directional Strength` (0–1.6, default 1) provides a direct A/B with R5 Detail and R6 Post still on. OFF restores the exact R6 render path, modulo the unchanged shader compilation.

This was calibrated in four shader iterations: (1) modest 2.5× broad-normal response was barely visible; (2) 10× slope response revealed planes but biased both twilight phases darker; (3) centering on the horizontal slope produced an actual morning/evening reversal; (4) raised the balanced band/falloff while softening the face. [Round 1](r6-5-directional/round1/comparison.jpg), [round 2](r6-5-directional/round2/comparison.jpg), [round 3](r6-5-directional/round3/comparison.jpg), and [final A/B plus intermediate times](r6-5-directional/final/contact.jpg) document the progression.

## Visual evidence

| Time | Directional ON | Same-time OFF |
| --- | --- | --- |
| Dawn 06:30 | [frame](r6-5-directional/final/06h30.png) | [baseline](r6-5-directional/final/06h30-off.png) |
| Noon 12:00 | [frame](r6-5-directional/final/12h.png) | [baseline](r6-5-directional/final/12h-off.png) |
| Dusk 17:30 | [frame](r6-5-directional/final/17h30.png) | [baseline](r6-5-directional/final/17h30-off.png) |
| Night 22:00 | [frame](r6-5-directional/final/22h.png) | [baseline](r6-5-directional/final/22h-off.png) |

[Dawn / Dusk side by side](r6-5-directional/final/dawn-vs-dusk.jpg), [enlarged portrait A/B](r6-5-directional/final/portrait-detail.jpg), and [06:30 → 09:00 → 12:00 → 15:00 → 17:30 contact](r6-5-directional/final/contact.jpg) show the fixed regions. The dawn-facing and dusk-facing planes change on face/hair, sleeves, vest folds, column, and stone rail; this is observable with color held fixed by the same-time toggle. Noon is substantially more even. Night ON/OFF is visually equivalent. [Four full-composition frames](r6-5-directional/combined-contact.jpg) retain Blink, Breathing, Hair and Leaves.

## 24H, regression and performance

[22:00 / 00:00 / 02:00 / 04:30](r6-5-directional/night-hold.jpg) remains stable. The four display-frame RGB means over the artwork crop are 30.220, 30.157, 30.188, 30.268 / 255. The artwork portion of 00:00 and 24:00 is pixel identical; the time label differs. The [97-frame 24H scan](r6-5-directional/24h-audit/hourly-contact.png) passed: Noon artwork luminance 0.21974, daily daylight maximum at 12:45 is 0.21978, and the evening face minimum 0.01760 remains above Night 22:00 at 0.01728. No new phase jump was observed. The frozen lighting curve was not modified.

`pnpm build`, `pnpm typecheck`, `validate_post.py`, `validate_lighting_detail.py`, `validate_time_controller.py`, `validate_blink_normal.py`, `validate_hair_motion.py`, `validate_breathing.py`, and `audit_lighting_24h.py` passed. Frozen pixel-baseline scripts turn the new directional layer OFF before comparing their respective old baselines. Four-phase full-composition preview remained stable. The implementation adds shader arithmetic only, with no pass or texture allocation. In headless software WebGL, sampled CPU render-submission medians were 0.4–0.5 ms across four phases; this is not a GPU or production-device FPS measurement.

The fixed artwork's very flat stone normal still limits local masonry relief. The broad side falloff supplies a directional cue but does not create physically correct occlusion or cast shadows. This R6.5 candidate is ready for human visual review; R7 has not started.
