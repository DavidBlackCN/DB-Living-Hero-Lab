# Living Hero 2.0 阶段交接

当前分支：`v2`。Artwork Space 为 **1672×941**，源像素与 UV 均以左上为原点。后续所有注册型资产必须与冻结的 Base 严格同尺寸、同构图、逐像素对齐；除非发现明确问题，不要随意重做已冻结美术资产。

| 项目 | 当前状态 |
| --- | --- |
| Base Albedo | **Frozen**；`public/assets/hero/base/base-albedo.png` 是注册基准。 |
| Local Blink v1 | **Accepted / Integrated**；Base 常驻，只叠加左右眼局部素材。整图 Blink 路线已废弃。 |
| Normal v3 | **Frozen for current Normal stage**；当前页面加载 `base-normal-v3.png`，v1/v2 留作历史对照。Normal view 用于原始法线对照，Lit view 接入 Runtime Lighting Foundation v1。 |
| Leaves v1 | **Accepted / Integrated**；四张透明素材和轻量 Canvas 2D 动画已接入。尺寸与轨迹可在后续独立调优。 |
| Runtime Lighting Foundation v1 | **Implemented**；独立 lighting state、单方向光、弱 ambient fill 和 Normal-driven stylized diffuse 已接入，支持 Base / Normal / Lit 手动对照。桌面与窄屏页面检查已完成。 |
| R2A Time-of-Day Keyframe Calibration | **Engineering passed, visual calibration failed**；四个静态 preset 已被 R2A.1 连续模型取代，原验收结论见 validation 文档。 |
| R2A.1 Runtime Lighting Model v2 | **工程实现完成，视觉校准待验收**；连续 `lightingFor(minutes)`、linear-space Normal-driven relighting、宽尺度 stylized light band 与 24H Debug slider 已接入；关键时段结构差异与晨昏明暗仍未达到目标。 |
| R2A.2 Lighting Visual Calibration | **Superseded by R2A.3**；工程实现和连续时间轨迹保持不变。 |
| R2A.3 Four-Anchor Luminance & Color Calibration | **工程与诊断完成，等待人工视觉验收**；Dawn / Noon / Dusk / Night 光能、曝光、色温与宽尺度 band 已联合校准。四张核心截图和亮度诊断已归档；验收前不得进入 R2B。 |
| R2A.4 Reference-Guided Visual Calibration | **两轮自检校准完成，等待人工视觉验收**；基于 KumengScreen 在线预览微调晨昏曝光、环境填充及色温。最终截图和排除 Debug Panel 的诊断已归档；视觉基线尚未冻结，不得进入 R2B。 |
| Half Blink | **Optional / Later**；不是当前 Blink 验收前提。 |
| Masks / Regions | **TBD**；只在 Runtime Lighting 或动效实现确有需要时补充，并沿用 Artwork Space。 |

**Runtime Lighting Foundation v1 工程实现已通过。R2A 工程实现通过，但静态时段视觉校准未通过。R2A.1 工程实现完成但视觉校准未通过。R2A.3 已完成本轮四锚点校准和诊断，等待人工视觉验收；验收前不得进入 R2B。** Debug 24H Slider 当前仅供人工拉条校准，不跟随系统时间、不播放，也没有自动 timeline 驱动。当前不进入系统时间同步、自动播放、Bloom、Breathing、Hair Motion、Leaves v2 或其他动效。最终迁移至 VuePress 2 / `vuepress-theme-plume`。保持 Vue 页面层轻薄，`src/engine/` 可迁移。

Foundation v1 的实现和页面检查见 [`validation/LIGHTING_FOUNDATION_V1.md`](validation/LIGHTING_FOUNDATION_V1.md)。
R2A 工程实现与未通过的初始视觉校准记录见 [`validation/TIME_OF_DAY_KEYFRAMES_R2A.md`](validation/TIME_OF_DAY_KEYFRAMES_R2A.md)。R2A.1 参考研究见 [`reference/KUMENG_LIGHTING_NOTES.md`](reference/KUMENG_LIGHTING_NOTES.md)，连续模型及拉条检查见 [`validation/R2A1_LIGHTING_MODEL_V2.md`](validation/R2A1_LIGHTING_MODEL_V2.md)。
R2A.2 曝光 / tone mapping 记录见 [`validation/R2A2_LIGHTING_VISUAL_CALIBRATION.md`](validation/R2A2_LIGHTING_VISUAL_CALIBRATION.md)。R2A.3 四锚点参数、截图、亮度诊断和不变量检查见 [`validation/R2A3_FOUR_ANCHOR_CALIBRATION.md`](validation/R2A3_FOUR_ANCHOR_CALIBRATION.md)。

当前最新阶段为 R2A.4，详见 [`validation/R2A4_REFERENCE_GUIDED_CALIBRATION.md`](validation/R2A4_REFERENCE_GUIDED_CALIBRATION.md)。两轮自检后建议交由人工验收，尚未冻结视觉基线；上文 R2A.3 等待验收的描述为历史状态。不得自行进入 R2B。

继续开发前先读 [`ASSET_PLAN.md`](ASSET_PLAN.md)、[`ANIMATION_PLAN.md`](ANIMATION_PLAN.md) 和相关 [`validation/`](validation/) 记录。改动后至少运行 `pnpm build`；涉及 Blink / Normal 时运行 `python scripts/validate_blink_normal.py`。
| R2A.4b Night Sky / Upper-Background Compensation | **Self-review complete, pending final human acceptance**；针对 DB artwork 的露天天空和上方远景加入通用、平滑的 `upperSceneAttenuation`，完成两轮有限校准，22:00 上部背景明显沉降且人物保持可读；不冻结视觉基线，不进入 R2B。详见 [`validation/R2A4B_NIGHT_SKY_COMPENSATION.md`](validation/R2A4B_NIGHT_SKY_COMPENSATION.md)。 |
| R2A.5 Registered Sky Runtime Integration | **Runtime integration complete, pending final human visual acceptance**；四张 1672×941 Sky 资产已接入 WebGL2 Lit 路径，`skyFor(minutes)` 与现有 0–1440 slider 联动，支持连续相邻时段插值和 Debug Sky on/off。Sky PNG 自带 alpha，运行时不重复乘 `sky-mask`；旧 `upperSceneAttenuation` 默认归零以避免重复压暗。边缘、四个锚点和中间时间已完成实机检查，详见 [`validation/R2A5_REGISTERED_SKY_RUNTIME.md`](validation/R2A5_REGISTERED_SKY_RUNTIME.md)。未完成人工 Freeze 前不得进入 R2B。 |
| R2A.5b Four-Phase Visual Separation Tuning | **Parameter calibration complete; pending human visual acceptance**. Dawn, Noon, Dusk, and Night were tuned on top of the registered Sky Layer. Sky assets, the 24H slider, solar trajectory, `upperSceneAttenuation=0`, and the Vue/engine boundary remain unchanged. WebGL2 Lit checks covered all four anchors plus 00:00, 09:00, 15:00, and 20:00. See [`validation/R2A5B_FOUR_PHASE_VISUAL_SEPARATION.md`](validation/R2A5B_FOUR_PHASE_VISUAL_SEPARATION.md). Do not enter R2B before human acceptance. |

## Latest calibration: R2A.5c

The Runtime Lighting four-phase visual calibration has completed three screenshot iterations and is ready for human visual acceptance. Dawn is cooler, Noon retains brighter-state detail, Dusk has stronger amber low-angle light, and Night is substantially deeper while the face and white sleeves remain legible. The time-varying relight strength, effective anchor parameters, baseline/iteration captures, and intermediate 24H checks are recorded in [`validation/R2A5C_RUNTIME_LIGHTING_FOUR_PHASE.md`](validation/R2A5C_RUNTIME_LIGHTING_FOUR_PHASE.md). Base, Normal, Blink, Leaves, and Sky assets remain unchanged. Do not enter R2B before human acceptance.

## Latest calibration: R2A.5d

Human review accepted Noon and Dusk. Dawn received a modest ambient/exposure lift, and Night received deeper blue-gray fill with a slightly weaker key. The Sky Timeline now holds Night from 20:00 through 05:00, with smooth transitions through Dawn and Dusk; preview shortcuts remain at 06:30 / 12:00 / 17:30 / 22:00. All 12 requested times and the 22:00–04:30 night continuity were captured in WebGL2 Lit mode. See [`validation/R2A5D_DAWN_NIGHT_SKY_TIMELINE.md`](validation/R2A5D_DAWN_NIGHT_SKY_TIMELINE.md). Dawn, Night, and the corrected timeline await final human acceptance. Do not enter R2B.

## Latest calibration: R2A.5e

Human review identified overbright intermediate frames near 07:32 and 16:30. The twilight warmth curve was boosting Key, Ambient, and exposure between the preview anchors. Runtime Lighting now smoothly balances those energy scalars from 06:30–10:00 and 15:00–17:30 while preserving solar direction, colors, Sky behavior, and all four anchor images exactly. A 15-minute WebGL2 day-arc sweep found no intermediate frame brighter than Noon. See [`validation/R2A5E_DAY_ARC_BRIGHTNESS.md`](validation/R2A5E_DAY_ARC_BRIGHTNESS.md). Await human review; do not enter R2B.

## Latest calibration: R2A.5f

Human review found a dark dip after Dusk: the face and white sleeves at 18:30 became darker than Night, then recovered. Runtime Lighting now balances Key, Ambient, and exposure from the existing 17:30 Dusk state to the existing 20:00 Night-hold state, aligned with the Sky transition. All four preview anchor images are unchanged. A 97-frame WebGL2 scan covered every 15 minutes across the full 24H; the evening face no longer falls below its Night level, Noon remains the brightest artwork frame, and midnight wraps consistently. See [`validation/R2A5F_DUSK_NIGHT_CONTINUITY.md`](validation/R2A5F_DUSK_NIGHT_CONTINUITY.md). Await human review; do not enter R2B.

## Current phase: R2B 24H Time Controller

Human review has accepted and frozen the R2A Runtime Lighting visual baseline. R2B now provides local Realtime by default, Manual slider/presets, Back to now, 60-second-per-day Play/Pause, midnight wrap, and visibility/reduced-motion behavior. Lighting and Sky receive one shared time value; their frozen visual curves are unchanged. Browser interaction tests, four pixel-identical anchor comparisons, and a repeated 97-frame 24H audit passed. See [`validation/R2B_TIME_CONTROLLER.md`](validation/R2B_TIME_CONTROLLER.md). R2B is ready for human acceptance; do not begin the next animation or post-processing stage yet.

## Current phase: R3 Breathing v1 prototype

Human review has accepted and frozen R2B. Torso-only Breathing v1 now has source-pixel soft regions, a 5.2-second cycle, shared Albedo/Normal UV deformation, a Region Overlay, a 0–2× strength control, and a visibility-aware 30-draw/s driver. Three calibration rounds plus stress and four-phase checks are recorded in [`validation/R3_BREATHING_PROTOTYPE.md`](validation/R3_BREATHING_PROTOTYPE.md). Breathing OFF is pixel-identical to R2B. The existing Blink/Leaves overlays are Base-view-only, so the requested simultaneous Lit/Sky/Blink/Leaves check remains open. Do not freeze R3 or start Hair Motion before human review and resolution of that integration item.

## Current phase: R3.1 Final Lit Composition

Human review accepted the R3 Breathing v1 motion. The remaining Lit integration is complete: approved local-eye Blink sprites now replace Albedo before Normal/Lighting/Sky, and existing Canvas2D Leaves overlay is enabled in Lit with a small time-of-day tone bridge. Four 18-second combined views, automatic Lit Blink closures, frozen-anchor comparisons, a repeated 97-frame 24H audit, visibility/reduced-motion checks, and build/typecheck validations passed. See [`validation/R3_1_FINAL_COMPOSITION.md`](validation/R3_1_FINAL_COMPOSITION.md). **R3 Breathing v1 is frozen.** Do not begin Hair Motion until the next stage is requested.

## R3.2 Sky edge matte cleanup (rejected)

The narrow, source-color-gated correction was rejected after human review found its before/after Night edge difference negligible. The earlier screenshots are archived in [`validation/R3_2_SKY_EDGE_CLEANUP.md`](validation/R3_2_SKY_EDGE_CLEANUP.md).

## R3.2b Edge-aware Sky Rematte (rejected)

A 3 to 5 source-pixel trimap, local soft-alpha estimate, and small registered override replaced the R3.2 edge-only result, but human review still found no sufficient Night improvement. The result and audit remain in [`validation/R3_2B_SKY_EDGE_REMATTE.md`](validation/R3_2B_SKY_EDGE_REMATTE.md).

## R3.2c Registered sky-edge material

The clarified upper-right target contains pale foreground canopy/building pixels next to sky that is already fully covered. A fixed 1672×941 local tone asset now corrects that foreground at Night without changing sky alpha/RGB or any time, lighting, or motion curve. Night before/after, 4× target, Neon, matte, four anchors, and late-night hold are documented in [`validation/R3_2C_MANUAL_SKY_EDGE_MATERIAL.md`](validation/R3_2C_MANUAL_SKY_EDGE_MATERIAL.md). Await human review before freezing R3; do not begin Hair Motion.

## R3 accepted and frozen; R4 Hair Motion

Human review accepted R3 Breathing, local Blink, Leaves, their Lit/Sky combination, the R2A/R2B lighting/time baseline, and the current Sky edge correction. A small top-leaf Sky residual is accepted and deferred to R5/R7 polish; R4 does not change Sky, Lighting, or Timeline. R4 now adds registered left/right lower-hair motion using one shared Albedo/Normal UV warp and the existing 30-draw/s WebGL motion driver. Three visual rounds, four 22-second full-composition checks, dynamic previews, lifecycle and pixel regressions are documented in [`validation/R4_HAIR_MOTION.md`](validation/R4_HAIR_MOTION.md). R4 awaits human visual acceptance before Character Motion Core is formally frozen. Do not begin R5 yet.

## R4.1 Head mass and nearby hair motion

Human review accepted R4 lower-hair motion and requested a more complete but still restrained head response. R4.1 adds near-rigid whole-head micro translation and protected secondary motion in bangs and side locks, while preserving lower-hair mask channels exactly. Base/Lit Blink, Breathing, four Lit phases, and lifecycle checks passed. See [`validation/R4_1_HEAD_MOTION.md`](validation/R4_1_HEAD_MOTION.md). Await human visual acceptance before formally freezing Hair Motion / Character Motion Core; no R5 work has begun.

## R4.1b Head motion gain

Whole-head gain is now 1.8 source px and nearby-hair gain 3.0 source px after three small tuning rounds. Lower hair, masks, rhythm, and all other systems remain unchanged. The stronger nearby-hair trial exposed mild image-left upper-clothing pull, so that gain was reduced for the final candidate. Four Lit phases, Blink/Breathing coexistence, Hair browser regression, build, and typecheck passed. See [`validation/R4_1B_HEAD_GAIN.md`](validation/R4_1B_HEAD_GAIN.md). Await human visual acceptance; do not start R5.

## R5 Lighting Detail / Material Response

Human review has accepted and frozen the R4/R4.1b Character Motion Core. R5 adds a registered face, crown-hair, and iris material mask and a separately switchable Lit-only shader detail layer. Six visual rounds were compared at Dawn, Noon, Dusk, and Night. The final candidate keeps the frozen 24H lighting and Sky curves and all animation systems unchanged; Detail OFF restores the previous Lit image. Four 22-second full-composition previews, closed Blink, 24H audit, regressions, build, and typecheck are recorded in [`validation/R5_LIGHTING_DETAIL.md`](validation/R5_LIGHTING_DETAIL.md). R5 awaits human visual acceptance before freeze.

## R6 HDR / Bloom / Display Post

Human review accepted and froze R5. R6 moves the Lit output through an RGBM linear-HDR Scene target, four-level bloom pyramid, one final ACES/display conversion, and continuous 24H display grading. Post OFF retains the exact R5 Lit baseline. Base/Normal inspection, frozen artwork and animation assets, Lighting/Sky curves, and R5 material logic remain unchanged. Five visual/curve iterations and the final 24H/full-composition validation are documented in [`validation/R6_POST_PROCESSING.md`](validation/R6_POST_PROCESSING.md). R6 awaits human visual acceptance; do not begin R7.

## R6.5 Directional Solar Shading

R6 remains intact. R6.5 adds a switchable, low-sun Scene Lighting response from the existing broad Normal and sun vector, with a light painted side cue for flat architecture. Dawn and Dusk show different receiving sides; Noon response softens and Night fades out. The frozen lighting and Sky curves, R5 material assets, R6 Post, and motion paths are unchanged. Four tuning iterations, static A/B and full-composition screenshots, 24H audit, build/typecheck, and critical regressions are documented in [`validation/R6_5_DIRECTIONAL_SOLAR_SHADING.md`](validation/R6_5_DIRECTIONAL_SOLAR_SHADING.md). Await human acceptance; do not begin R7.

## R6 character shadow cleanup

Human feedback found that R6.5's broad directional response still tinted and flattened the main character's Dawn/Dusk shadows. The character now uses softer face/garment directional gains and subtle registered bang/chin contact plus Base-guided shirt folds. Architecture direction, frozen curves and R6 Post are unchanged. Dawn/Dusk character crops, Noon/Night regression, 24H scan and validation are recorded in [`validation/R6_5B_CHARACTER_SHADOW_CLEANUP.md`](validation/R6_5B_CHARACTER_SHADOW_CLEANUP.md). Await human review; do not begin R7 or left-lamp lighting.

## R6.5C Dawn polish and directional moonlight

Dawn's character shadow band now receives a softer cool fill on the left hair, face, and upper clothing, while the receiving side and architecture retain their morning direction. Night gains low-contrast cold moon shaping driven by the existing continuously rotating nighttime Direction vector, with stable Night-hold energy. Noon and Dusk static output remain unchanged. Four visual rounds, final 24H and combined captures, and validation are recorded in [`validation/R6_5C_DAWN_MOONLIGHT.md`](validation/R6_5C_DAWN_MOONLIGHT.md). Await human review; do not begin R7 or left-lamp lighting.

## R6.5D Moon direction and Dawn eye

The Moon now has an independent 20:00–05:00 direction arc that rises opposite the Dusk sun, crosses high near midnight, and fades through twilight. Dawn's screen-left eye has a feathered iris/upper-lid protection, while Night receives a stronger cool directional key on hair, face, cloth, stone, and architecture. Noon/Dusk images remain unchanged, and the 24H continuity scan passes. Review images and regressions are recorded in [`validation/R6_5D_MOON_DIRECTION_EYE_NIGHT.md`](validation/R6_5D_MOON_DIRECTION_EYE_NIGHT.md). Await human review; do not begin R7.

## R6.5E Dawn face and twilight continuity

The Dawn face/eyes have a broader local soft fill and lighter directional shadow. The Moon direction now joins continuously at 05:00 and 20:00, with a small ambient overlap after 05:00 to prevent a pre-sunrise brightness dip. Night hair moon sheen follows selected outer locks instead of a broad glossy mask. Noon and Dusk images are unchanged. Review images and validation are in [`validation/R6_5E_DAWN_TRANSITION_NIGHT_HAIR.md`](validation/R6_5E_DAWN_TRANSITION_NIGHT_HAIR.md). Await human review; do not begin R7.

## R6 Final head lighting polish

Dawn's head receives softer face-plane shading and under-eye skin fill. Dusk's bright eye highlight is locally compressed without changing its sunset environment. Night's face and eyes gain a gentler directional Moon fill, while nearby hair sheen is narrowed. Noon remains pixel-identical, and changed artwork pixels are confined to the head. Four head phases, before/after crops, time-boundary captures and validation are recorded in [`validation/R6_FINAL_HEAD_LIGHTING_POLISH.md`](validation/R6_FINAL_HEAD_LIGHTING_POLISH.md). Await human acceptance; do not begin R7.

## Character Lighting Core rebuild — current review candidate

Human review rejected the accumulated R6.5 face and eye patches. The Lit shader now gives the character one continuous Sun/Moon key and ambient field, then varies the response of face, hair, clothing, and head accessories with the existing registered masks. The Dawn eye/under-eye spot fills, left-hair fill, face-only Moon fills, bang/chin multipliers, and one-eye sunset white correction have been removed. The previous R6 Final note remains historical. Four clean full frames, four head crops, before/after pairs, seven visual/continuity rounds, and regressions are in [`validation/CHARACTER_LIGHTING_CORE.md`](validation/CHARACTER_LIGHTING_CORE.md). Base/Normal, R5 assets, lighting and sky curves, Post, and motion remain unchanged. Await human acceptance; do not begin R7.

## Local Sky seam repair after character lighting review

The current review prioritizes Night Sky/foreground junctions before further
character lighting. Registered local repairs now darken and cool only the
marked left vine opening, right roof canopy/spires, ribbon-side background,
and top leaves at Night; open Sky and all three daylight anchors are unchanged.
Before/after crops, four-phase captures, and limitations are recorded in
[`validation/SKY_SEAM_LOCAL_REPAIR.md`](validation/SKY_SEAM_LOCAL_REPAIR.md).
Await human acceptance; do not resume character lighting or start R7 yet.

## Sky edge decontamination review candidate

Human review rejected the preceding Night display-tone seam suppression. That final-color multiplier is now disabled in both Lit and Post. Two registered 1672×941 reconstruction assets recover local foreground pigment and replace the old-sky mixture in selected distant foliage openings before/within normal Sky composition. The strongest visible improvement is at the right roof treeline and ribbon-side tree; a faint soft-air residual remains in the lower left distant branches. Dawn, Noon, Dusk, and Night review images and limitations are in [`validation/SKY_EDGE_DECONTAMINATION.md`](validation/SKY_EDGE_DECONTAMINATION.md). Await human review; do not resume character lighting or begin R7.

The final two-box correction extends the ribbon-side Sky replacement into the actual pale opening and protects the adjacent large tower from both reconstruction assets. Night before/after crops and four-phase recaptures are linked from the same validation note. Await human review before resuming character lighting.

## Character Moon direction follow-up — current review candidate

On the existing Character Lighting Core, Night now separates the Moon-facing and back-facing sides of the full figure more clearly; face/eyes use the same direction with softer contrast. Dawn, Noon, and Dusk fixed-time output remain pixel-identical. The pale image-left background near the head was checked with Sky, Post, and directional shading independently disabled and identified as painted architecture/ambient reception rather than a new halo, so no local darkening was added. Four-phase images, Night figure before/after, diagnostic crops, and a 24H audit are in [`validation/CHARACTER_NIGHT_DIRECTION.md`](validation/CHARACTER_NIGHT_DIRECTION.md). Await human review; do not begin R7.

## Unified Normal-driven character shading — current review candidate

The previous Night character receiving plane leaned too heavily on screen X. It now follows the broad painted Normal and the same independent Moon vector used throughout the figure; a small positional bias remains only as a secondary cue. Face softens this shared response without local eye/cheek patches, while hair and clothing keep stronger fold/lock direction. Low-Sun hair and clothing gains were modestly raised; Noon is visually stable. The pale building beside the rose was verified as a directional architecture response and its global Night key restrained. Four full and head captures, Night before/after, diagnostics, and 24H validation are in [`validation/CHARACTER_UNIFIED_NORMAL_SHADING.md`](validation/CHARACTER_UNIFIED_NORMAL_SHADING.md). Await human review; do not begin R7.

## Twilight Sun/Moon handoff continuity

The 24H preview's morning shadow swap and evening brightness rebound were traced to separate character Sun/Moon thresholds, a morning energy-curve join, and Dusk colors cooling ahead of the Sky. The character key now crossfades through the existing Sky twilight weight, Dawn energy eases into its accepted 06:30 anchor, and Dusk colors stay aligned with the 17:30–20:00 Sky transition. Fixed Noon/Dusk/Night frames are unchanged and Dawn differs by at most one RGB level. Five-minute before/after captures, the full-day audit, and checks are in [`validation/TWILIGHT_HANDOFF_CONTINUITY.md`](validation/TWILIGHT_HANDOFF_CONTINUITY.md). Await human review; do not begin R7.

## R6 final lighting closure — review candidate

The Night architectural Moon contribution is quieter, removing the overlit impression beside the black rose without a local darkening patch. The existing broad-Normal character Moon response is slightly stronger on hair and clothing, with a softer face share. Dawn's face-wide morning response is marginally softer; Noon and Dusk fixed frames are unchanged. Four-phase screenshots, A/B crops, 24H continuity and checks are recorded in [`validation/R6_FINAL_LIGHTING_CLOSURE.md`](validation/R6_FINAL_LIGHTING_CLOSURE.md). Recommend freezing R6 after human review; R7 has not begun.

## R7.1 local lamp lighting — review candidate

Human review froze the R6 visual baseline at `3241d76`. R7.1 adds two fixed registered corridor lamp source/influence masks and one continuous dusk-to-dawn weight. Emissive glass enters the existing HDR/Bloom path; nearby stone and vine surfaces receive a separate broad-Normal warm key that remains visible with Bloom OFF. The figure and distant Sky stay pixel identical at Night, while Lamps OFF restores the frozen R6 frame exactly. Twelve timeline captures, A/B and Bloom comparisons, 24H continuity, current-stage motion smoke checks, build and typecheck are in [`validation/R7_1_LOCAL_LAMP_LIGHTING.md`](validation/R7_1_LOCAL_LAMP_LIGHTING.md). Await human acceptance; do not begin R7.2.

## R7.1 source registration correction

The R7.1 lamp source mask now covers three individually registered glass faces on each existing corridor lantern (near R, far G). The local influence asset and all lighting/time/Post/motion parameters remain unchanged. A local Debug Panel Hide/Debug button permits unobstructed preview without changing renderer state or interrupting Play. The mask close-ups, 22:00 images, and verification results are in [`validation/R7_1_LOCAL_LAMP_LIGHTING.md`](validation/R7_1_LOCAL_LAMP_LIGHTING.md). Await human acceptance; do not enter R7.2.

### R7.1 glass-edge follow-up

Near lamp right glass coverage and far lamp left metal-rim spill were corrected in the same fixed source mask; all influence, lighting, timing, and Post behavior remains frozen. Enlarged before/after crops and the 22:00 frame are linked from [`validation/R7_1_LOCAL_LAMP_LIGHTING.md`](validation/R7_1_LOCAL_LAMP_LIGHTING.md). Build, typecheck, and the R7.1 validator pass. Await human acceptance; do not enter R7.2.

The far lamp's left/front metal separator was then restored after review found the two glass faces too close. The R7.1 validation record includes the corrected 22:00 close-up and explicit source-alpha separator check.

## R7.2 Leaves v2 — review candidate

The accepted four leaf masters and Canvas2D overlay now use three restrained depth layers without increasing the desktop/mobile counts (18/10). Per-leaf motion rhythms and deterministic respawns reduce repeated paths; a soft artwork-space face guard protects the eyes; a slight Night warm response follows the existing left-corridor lamp weight. Time-of-day leaf grading, R6/R7.1 lighting, and other motion systems remain unchanged. Four static phases, three 25-second videos, debug/A-B views, lifecycle and performance checks are in [`validation/R7_2_LEAVES_V2.md`](validation/R7_2_LEAVES_V2.md). Await human visual acceptance; do not begin R7.3.

Follow-up size calibration raised the dynamic leaf sizes to match the distinct painted single leaves more closely: midground 26–46 CSS px, background 18–27 CSS px, and rare foreground 52–60 CSS px. Density, paths, face guard, and lighting remain unchanged. The four frames and three 25-second videos were recaptured; the updated size A/B and checks are in the same R7.2 record.

## R7.3A Character Coherence — awaiting human review

Head mass now follows the 5.2s master breathing phase with a small lag; its independent drift is reduced, while upper/lower secondary hair retains its accepted path and strength. Night character Moon receive uses a steadier filtered broad Normal, softer shared-direction Face shaping and compressed material gains. The screen-X character Moon bias and separate side-lock lunar ribbons were removed; a narrow crown sheen remains optional. No frozen artwork, sky, lamp, leaf, Post or time curve changed. Four fixed phases, 20s before/after Noon/Night motion, sheen A/B, twilight continuity, and critical regressions are in [`validation/R7_3A_CHARACTER_COHERENCE.md`](validation/R7_3A_CHARACTER_COHERENCE.md). Await human acceptance before freezing Character Motion + Lighting. Do not begin R7.3B.
## R7.3A.1 Final Character Calibration — awaiting human review

On top of `c97b2c4`, the existing Breath → Head → Hair motion was raised modestly to 5.2 / 2.5 / 3.6 / 5.8 source-px caps (torso / whole head / upper hair / lower hair), with slightly broader shoulder participation. Character solar and moon receive now share a wider broad-Normal sample; Night's Hair, Clothing and Vest gains and receive contrast are compressed slightly. Face, time paths, frozen art, lamps, leaves and Post are unchanged. The 2560×1440 four-phase images, 20s motion comparisons, sheen A/B and regressions are in [R7.3A validation](validation/R7_3A_CHARACTER_COHERENCE.md#r73a1-final-calibration). Recommend freezing Character Motion + Character Lighting after human review. Do not begin R7.3B.

## R7.3A.2 Long-hair light balance — awaiting human review

The Dawn image-left long-hair shadow and Night image-right long-hair pale wash were rebalanced through the existing shared Character Lighting hair response and the existing soft lower-hair regions. No new mask, light direction, time curve or motion behavior was added. Four fixed views, 2× Dawn/Night before/after, build, typecheck and character/motion regressions are in [`validation/R7_3A_2_HAIR_LIGHT_BALANCE.md`](validation/R7_3A_2_HAIR_LIGHT_BALANCE.md). Await visual acceptance; do not begin R7.3B.

## R7.3A.3 Night edge and continuous Blink — awaiting review

Night Sky coverage now follows the same displaced artwork coordinates as Character Motion, and the tower Moon add-on is quieter. Blink uses a 320 ms continuous local-eye blend in the existing lit path. The reported Dawn sky block is deferred at the user's request; it is not marked fixed. Review captures, regression notes, and remaining limits are in [R7.3A.3 validation](validation/R7_3A_3_FINAL_VISUAL_BLINK.md). Do not begin R7.3B.

## R7.3B Final Atmosphere — visual polish frozen candidate

The latest user handoff accepted R7.3A and authorized R7.3B, superseding the earlier stop notices above. `eb3a488` is this round's frozen source/visual reference. A registered conservative background depth asset feeds the existing MRT metadata and final Post pass; very mild aerial perspective, continuous final grading, and tighter Bloom eligibility finish Dawn/Dusk/Night. Scene illumination, Character Core, all animation, lamp logic, frozen Sky/Base/Normal and time curves remain unchanged. Atmosphere OFF exactly matches the frozen commit in all four phases; Noon ON is also pixel-identical. Four-phase A/B, three 25s combined previews, 4K GPU timing, 610.8s continuous Play, context restore and key regressions are recorded in [R7.3B validation](validation/R7_3B_FINAL_ATMOSPHERE.md). Await human acceptance before freezing. Do not begin R7.4 Final Integration.

## R7.3B final fix — awaiting human review

The latest request supersedes the prior Noon identity requirement: all four phases now have perceptible, depth-limited background atmosphere. Bloom/global exposure and the lighting model remain unchanged. Dawn/Night nose and chin contamination was traced to pale painted skin dropping out of the existing pigment-gated Face material coverage; the same geometric Face region now receives the unified softened character lighting consistently. No local face patch was added; Hair/Iris channels, frozen artwork and all animation/lamp/leaf logic are unchanged. Four-phase OFF/ON, head close-ups, isolated coverage A/B and continuity/lifecycle checks are in [R7.3B final fix](validation/R7_3B_FINAL_FIX.md). Atmosphere OFF now includes the corrected Face asset and is not claimed pixel-identical to `f56cd9f`. Stop for human acceptance; do not enter the next phase.

### R7.3B chin / neck receive follow-up — awaiting review

User review found the remaining Dawn/Night jaw shadow. The existing Face coverage still ended at the chin and excluded the exposed neck, allowing architecture illumination to deepen the painted skin shadow. The same registered skin region now extends continuously to the collar; no local light patch or shader/light/time parameter was added. The original painted neck shadow remains. Actual A/B, all four head views, motion/lifecycle regression and midnight continuity are in [chin receive follow-up](validation/R7_3B_CHIN_RECEIVE_FOLLOWUP.md). Stop for human review.

### Night architecture Moon direction — awaiting review

The tower beside the black rose incorrectly reused background-containing Head Motion coverage as accessory light receiving. Registered pale masonry now receives the architecture Moon key instead, while the motion mask and character lighting model remain unchanged. Architecture's additive Moon-side bias and retained solar key at Night are replaced by a continuous Moon-direction/elevation response; four distant towers share coherent visible-plane orientations. The bright side changes from image-right early to image-left late. Dawn/Noon/Dusk anchors and midnight wrap are exact matches, and build/typecheck plus lifecycle regressions pass. Five annotated Night frames, before/after and direction-only isolation are in [Night architecture validation](validation/NIGHT_ARCHITECTURE_MOON_DIRECTION.md). Stop for human review.

### Night tower / shoulder spill follow-up ? awaiting review

User review at 03:54 found an overly dark right-facing tower plane, a harsh corner transition and architecture shadow spilling onto the white shoulder. The existing foreground material/garment receive now excludes architecture ownership; corner-normal transitions scale with tower width and Moon broad receive is softer. Direction/elevation, key/ambient values, character lighting model, animation, Leaves, Lamps and Post remain unchanged. Dawn/Noon/Dusk anchors and midnight wrap are exact matches. Actual 03:54 A/B, coverage debug, Night sequence and verification are in [tower softening validation](validation/NIGHT_ARCHITECTURE_SOFTENING.md). Stop for human review.


## Pre-Dawn Tower Lighting - awaiting human review

On top of `a0e34e5`, the visible tower behind the image-left hair/beret now has one fixed masonry registration. It fills the old receiving holes without including the foreground character; a continuous late-Moon normal response establishes the broad left-facing plane and replaces the two wrong bright fragments. The correction fades with the existing Dawn handoff. Character receiving metadata, Atmosphere, animation, Leaves, Lamps, Sun/Moon/time curves and frozen artwork remain unchanged. Build/typecheck, actual-render isolation, one-minute Dawn fade, midnight wrap and lifecycle regressions pass. Requested time frames, 04:36 before/after and limits are in [pre-Dawn tower validation](validation/PRE_DAWN_TOWER_LIGHTING.md). Stop for human review; do not expand the phase.

The subsequent 04:15 review found the tower back-plane shadow too prominent. A small height-dependent wrapped receive floor (0.06–0.10) and a 26px corner transition replace the harder separation; the registered coverage and all other systems remain frozen. The actual 04:15 display gap is reduced by 64%, while the left-facing plane stays slightly brighter through 05:30. Build/typecheck, targeted A/B and lifecycle regressions pass. Current captures and checks are in the [shadow-softening follow-up](validation/PRE_DAWN_TOWER_LIGHTING.md#人工反馈收口阴影过重--暗面柔化). Await human review.
### Tower Moon-center handoff — awaiting human review

User review identified that the left tower plane only started receiving at 02:30 while the Moon crosses the center at 00:30. The old direction gate (0.40–0.60) is replaced by a smooth center ownership join (−0.12–0.00). Near-center broad receiving uses the same tower normals/Moon vector with a neutral front-facing term and an elevation-controlled key; left receiving grows as right receiving declines immediately after 00:30. No new patches/assets or global Sun/Moon curve changes. The accepted 03:30 onward softening, four-phase anchors, character metadata and all pixels outside the tower remain unchanged; midnight wrap and one-minute center continuity pass. Build/typecheck and lifecycle regression pass. See the [Moon handoff follow-up](validation/PRE_DAWN_TOWER_LIGHTING.md#午夜月光交接延迟修复--等待人工验收). Stop for human review.
### Tower final coverage / 24H review — freeze recommended

On `0f1078d`, the hat-adjacent masonry outline is registered to the actual painted edge, closing the remaining pre-Dawn bright wedge. Only the existing receiver mask and its generator changed; all lighting curves, shader logic, character/animation/lamp/leaf systems remain frozen. A 98-time 24H render sweep, 21 selected frames, motion-on gap crops, 68.17s full-animation Play crossing midnight, build/typecheck and lifecycle regressions passed. Face/outside-repair pixels and four phase anchors are identical. Visual review finds the broad Moon handoff and twilight relationships coherent for this painted scene; the remaining subpixel softened contour is acceptable. Recommend freezing R7.3B visual closure, subject to human acceptance. Next is **R7.4 Final Integration**, not started. See [final coverage and 24H review](validation/TOWER_FINAL_24H_REVIEW.md).
### Dawn Sky/scene synchronization — awaiting review

Following `ecc955e`, user review found that Sky brightened before scene lighting. Morning energy previously began at 05:30 while Sky started at 05:00. Key/ambient energy, exposure and light colors now share the actual Night-to-Dawn Sky mix (05:00–06:30); the isolated predawn fill hump is removed. Solar/Moon direction, shaders, assets and all other phases remain unchanged. Actual 5-minute samples show monotonic morning brightness and a 64% smaller mean Sky/scene progress mismatch; four anchors and midnight wrap are exact. Build/typecheck and lifecycle regressions pass. See [Dawn synchronization](validation/DAWN_SKY_SCENE_SYNC.md). This supersedes the preceding freeze candidate pending human review; no next-stage work started.
## R7.4 Final Integration — awaiting final acceptance

Follow-up: the standalone demo now includes a responsive example homepage, native debug drawer and opt-in Base-to-Lit entrance. Plume integration is explicitly deferred. Frozen scene pixels remain unchanged outside the relocated Debug button; loading, drawer focus/state, mobile layout and reduced-motion checks pass. See [homepage example validation](validation/HOMEPAGE_EXAMPLE.md). Await visual acceptance of the page design.

R7.3A/B and all visual systems are frozen at `ad18ee5`. LivingHero now exposes a production API, SSR poster, host slots/events, configurable asset root, explicit optional debug, lazy renderer, cancellable registered asset loading and fallback/retry. High preserves the baseline; Medium/Low control pixel and animation budgets without changing frozen Post strengths. Auto may downgrade under sustained cadence pressure. Hidden/offscreen/paused and unmount lifecycles are validated. Seven fixed frames are pixel-identical; 24H Play, context restore, resize, accessibility preferences and key visual regressions pass. Public SSR entry and `/blog/` assets pass; the actual VuePress target is not present, so host-site build/deployment remains a later integration check. See [R7.4 validation](validation/R7_4_FINAL_INTEGRATION.md) and [VuePress guide](VUEPRESS_INTEGRATION.md). Stop for final human acceptance.

### Standalone scene page — awaiting acceptance

The scrolling homepage has been replaced at user request by a single-screen clock/scene layout with no navigation. A product lighting drawer exposes existing render parameters; time, motion, fullscreen, immersive and view controls stay local. Default four-phase rendering remains identical. Relative build assets were tested under /dist/ with all controls, auto reset, mobile and reduced-motion checks passing. No Plume integration or visual-engine changes. See [standalone validation](validation/STANDALONE_SCENE_PAGE.md).