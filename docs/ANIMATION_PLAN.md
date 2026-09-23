# Animation plan

| Module | Asset / input | Next validation |
| --- | --- | --- |
| Blink | v1 与新生成 v2 均未通过整图切换验收；双眼内容仅作为局部素材来源，Half 与正式局部范围待定 | 整图重试见 [`validation/BLINK_V2_FULL_FRAME_RETRY.md`](validation/BLINK_V2_FULL_FRAME_RETRY.md)。下一步正式转局部眼部方案，再做真实页面时间线验收。 |
| Breathing | 安全区域、幅度和周期参数待定 | 先人工确认衣料和轮廓变形范围。 |
| Hair Motion | 独立发束区域或 Mask 待定 | 核对发梢、背景和遮挡关系。 |
| Leaves | 四张透明 master 已接入第一版 Canvas 2D 粒子覆层 | 已有缓慢下落、共享微风、个体轻摆／旋转、resize、后台暂停和 reduced motion 关闭；后续继续实机调密度与遮挡。 |

Artwork 显示区域由 `engine/coordinates/artwork.ts` 提供。Blink、Breathing、Hair Motion 等最终动画参数仍未冻结；这些模块的 Debug 控件目前为禁用占位。

Blink v1 和整图重试 v2 均未启用运行时代码：两张整图都不能直接切换；双眼内容可留作局部闭眼方案的来源。差异图与新候选已归档。本轮失败后不制作 Half 整图，下一轮先解决局部素材、Half 状态和眨眼节奏。Normal 不与本轮合并。

Leaves 第一版用独立的 `engine/animation/LeafField.ts` 在 Canvas 2D 中逐片绘制，按可见 Artwork 区域裁剪；竖屏 contain 留边不会出现叶子。桌面 18 片、移动端（≤640 CSS px）10 片；主体约 14–32 CSS px，8% 概率为 38 px 前景叶。下落 10–22 CSS px/s；共同风向 2.5 CSS px/s，9 秒周期的 ±5 CSS px/s 微风，另有最多 2.5 CSS px/s 的个体轻摆。帧率上限 30、覆层 DPR 上限 1.5、透明度 0.58–0.84。以上均由 `src/config/hero.ts` 管理，属于可调的首版值，未视为最终视觉参数。

Debug Panel 已可开关 Leaves 并查看粒子数量。`prefers-reduced-motion` 或 Static quality 时默认关闭；页面后台停止 RAF，恢复时清零时间差以免跳帧；resize 更新画布和桌面／移动端数量。后续可按实际观感优化局部发射区、层次、遮挡与配色；若需要 atlas 再从四张 master 派生并保留透明 padding。

参考 [KumengScreen 的透明花瓣纹理粒子方案](https://github.com/buger404/KumengScreen#%E5%8A%A8%E6%95%88%E4%B8%8E%E8%8A%B1%E7%93%A3)：后续可用 Alpha Blend 绘制独立秋叶，并借鉴共同阵风与个体旋转、翻转、起落的分层思路；本项目的轨迹、密度和画面遮挡须按 Base 单独设计。
