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
