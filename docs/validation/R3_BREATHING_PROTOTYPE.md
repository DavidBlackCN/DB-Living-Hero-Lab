# R3 Breathing v1 prototype and region calibration

Status: prototype implemented and measured; **not recommended for freeze yet**. The R2A/R2B curves and assets are unchanged. Full Lit + Sky + Blink + Leaves simultaneous acceptance remains unavailable because the previously accepted Blink/Leaves overlays are restricted to Base view. This limitation requires a separately authorized integration decision; this R3 task did not refactor those modules.

Historical R3 prototype record: the remaining composition item was resolved in [R3.1 Final Lit composition](R3_1_FINAL_COMPOSITION.md), after human acceptance of the breathing motion.

## Reference and design

The [KumengScreen scene loop](https://github.com/buger404/KumengScreen/blob/main/components/dream-scene.tsx) advances a motion phase only while enabled and resets its timestamp on visibility changes. Its [scene shader](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts) applies broad UV region weights before sampling albedo and normal. DB adopts the UV sampling order and visibility principle, with its own source-pixel region. Unlike KumengScreen, DB v1 leaves the head stationary to preserve the separate local-eye Blink registration.

The shader defines ellipses in the frozen 1672×941 Artwork Space (center x/y, radius x/y):

| Region | Source pixels | Role |
| --- | --- | --- |
| Core | (1152, 461), (103, 137) | Vest and upper shirt; weight 1.0 at center. |
| Shoulder | (1151, 385), (145, 93) | Softer 0.42-weight follow. |
| Head/eyes | (1154, 229), (177, 135) | Protected. |
| Left/right arms | (987, 501), (87, 194); (1318, 520), (79, 207) | Protect hands, sleeves and book side. |
| Left/right hair | (1050, 433), (44, 160); (1282, 444), (50, 169) | Suppress hanging-hair displacement. |

All ellipses use a smooth falloff from normalized radius 0.30 to 1.0. The green/cyan [region overlay](r3-final/region.png) shows core/transition; red shows protection. The sky, architecture, cup, stone rail, skirt and face are outside the moving region. No mask PNG was added.

The 5.2-second cosine inhale/return cycle moves the core up by at most **4.8 source px** and expands it horizontally by at most about **1.4 source px**; shoulder contribution is at most 42% of core. Albedo and Normal sample the **same deformed UV**. The sky samples the original UV. At zero strength or when disabled, the original UV is used exactly. The debug slider exposes 0–2× strength; 2× is for stress inspection only.

## Iteration and checks

1. Initial wider region, 7.2 source px: motion was measurable, but hanging hair and outer shoulder were too close to the influence boundary. [Initial overlay](r3-round1/region.png).
2. Reduced to 4.8 source px: the torso remained visibly responsive over a cycle, while the stronger setting was less restrained. [Second overlay](r3-round2/region.png).
3. Added two soft hair protection zones and retained 4.8 source px. The center vest motion remains, with less influence at hair/shoulder edges. [Final 18-second torso clip](r3-final/torso-18s.gif) and [final overlay](r3-final/region.png).
4. At 2× stress, maximum vertical displacement is 9.6 source px. [Stress frame](r3-stress/phase-10.png) was used only to reveal region leakage.

Edge/WebGL2 validation sampled 20 frames over 18 seconds at final strength. Relative to Breathing OFF, the torso's mean RGB difference reached 4.35; the face sample remained at 0.000 rounded mean (only isolated 1-level RGB differences), and the stone sample remained exactly 0. Breathing OFF was pixel-identical to the frozen R2B Noon artwork outside the Debug Panel. [Dawn](r3-final/dawn.png), [Noon](r3-final/noon.png), [Dusk](r3-final/dusk.png), and [Night](r3-final/night.png) all rendered in Lit with the same region. Normal view used the same warped UV. Base view retained registered [Blink/Leaves operation](r3-final/base-with-blink-leaves.png) because the head and eye patch are stationary.

The component runs a breathing render driver only while enabled and visible, capped to 30 draws per second; otherwise rendering returns to on-demand. Hidden tabs stop the driver and retain the phase. On return, the phase continues without adding hidden elapsed time. Reduced motion disables breathing while keeping realtime Lit/Sky. Browser checks passed these transitions. The synchronous CPU draw time shown by the Debug Panel was typically around 0.3 ms in the Edge software WebGL run; this is not a GPU timing claim.

`pnpm build`, `pnpm typecheck`, `python scripts/validate_breathing.py docs/validation/r3-final --strength 1.0`, `python scripts/validate_time_controller.py`, and `python scripts/validate_blink_normal.py` passed. Existing R2A/R2B capture scripts explicitly disable Breathing before checking their frozen static baselines.

## Remaining acceptance item

The accepted `LivingHero.vue` composition mounts Blink and Leaves only when `renderView === 'base'`. Lit mode provides Runtime Lighting and Sky but does not mount those overlays. Therefore a single Dawn/Noon/Dusk/Night scene with Breathing + Blink + Leaves + Lit + Sky has **not** been verified. Breathing v1 is ready for human motion review, but freeze should wait for a decision about that existing view restriction and a simultaneous integration check. No Hair Motion or later effect was started.
