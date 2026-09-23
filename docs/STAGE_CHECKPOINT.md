# Living Hero 2.0 阶段交接

当前分支：`v2`。Artwork Space 为 **1672×941**，源像素与 UV 均以左上为原点。后续所有注册型资产必须与冻结的 Base 严格同尺寸、同构图、逐像素对齐；除非发现明确问题，不要随意重做已冻结美术资产。

| 项目 | 当前状态 |
| --- | --- |
| Base Albedo | **Frozen**；`public/assets/hero/base/base-albedo.png` 是注册基准。 |
| Local Blink v1 | **Accepted / Integrated**；Base 常驻，只叠加左右眼局部素材。整图 Blink 路线已废弃。 |
| Normal v3 | **Frozen for current Normal stage**；当前页面加载 `base-normal-v3.png`，v1/v2 留作历史对照。Normal view 用于原始法线对照，Lit view 接入 Runtime Lighting Foundation v1。 |
| Leaves v1 | **Accepted / Integrated**；四张透明素材和轻量 Canvas 2D 动画已接入。尺寸与轨迹可在后续独立调优。 |
| Runtime Lighting Foundation v1 | **Implemented**；独立 lighting state、单方向光、弱 ambient fill 和 Normal-driven stylized diffuse 已接入，支持 Base / Normal / Lit 手动对照。桌面与窄屏页面检查已完成。 |
| Half Blink | **Optional / Later**；不是当前 Blink 验收前提。 |
| Masks / Regions | **TBD**；只在 Runtime Lighting 或动效实现确有需要时补充，并沿用 Artwork Space。 |

**Runtime Lighting Foundation v1 已实现；正式 24h Time-of-Day 尚未开始。** 当前 Foundation 仅提供可手动调整的单方向光与极弱 ambient fill，不含时间线、自动时段或额外光照系统。下一阶段候选为 Dawn / Day / Dusk / Night 的 24h Time-of-Day；须先完成人工验收，再独立启动。之后才考虑 Breathing、Hair Motion、Blink 节奏微调与可选 Half、Leaves v2、Post Processing、Mobile / Performance。最终迁移至 VuePress 2 / `vuepress-theme-plume`。保持 Vue 页面层轻薄，`src/engine/` 可迁移。

Foundation v1 的实现和页面检查见 [`validation/LIGHTING_FOUNDATION_V1.md`](validation/LIGHTING_FOUNDATION_V1.md)。

继续开发前先读 [`ASSET_PLAN.md`](ASSET_PLAN.md)、[`ANIMATION_PLAN.md`](ANIMATION_PLAN.md) 和相关 [`validation/`](validation/) 记录。改动后至少运行 `pnpm build`；涉及 Blink / Normal 时运行 `python scripts/validate_blink_normal.py`。
