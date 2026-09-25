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
