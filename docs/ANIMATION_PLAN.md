# Animation plan

| Module | Asset / input | Next validation |
| --- | --- | --- |
| Blink | v1 闭眼候选提取的左、右眼透明局部图；Base 始终常驻 | 最小 Open → Closed → Open 已接入并通过局部像素检查与桌面页面检查。后续继续实机调节眼睑造型、节奏，Half 可独立补充。 |
| Breathing | 安全区域、幅度和周期参数待定 | 先人工确认衣料和轮廓变形范围。 |
| Hair Motion | 独立发束区域或 Mask 待定 | 核对发梢、背景和遮挡关系。 |
| Leaves | 四张透明 master 已接入第一版 Canvas 2D 粒子覆层 | 已有缓慢下落、共享微风、个体轻摆／旋转、resize、后台暂停和 reduced motion 关闭；后续继续实机调密度与遮挡。 |

Artwork 显示区域由 `engine/coordinates/artwork.ts` 提供。Blink 的双眼区域在 `config/hero.ts` 用 Source Pixel 定义，随 Artwork 布局缩放；时间线位于 `engine/animation/BlinkTimeline.ts`，不依赖 Vue。自动间隔随机 4.2–7.6 秒，闭眼 115 ms，贴图淡入淡出 35 ms。Debug 可开关自动 Blink、触发一次 Preview Blink、显示双眼区域。后台暂停并恢复睁眼；reduced motion 和 Static quality 关闭自动 Blink。参数是首版可调值。

整图 Blink 路线已终止。v1 全图仅作离线提取来源，v2 失败候选继续归档；运行时不加载两张整图。局部静态验证见 [`validation/BLINK_LOCAL_V1.md`](validation/BLINK_LOCAL_V1.md)。Half 是后续可选状态。当前加载已冻结的 Normal v3；Debug 的 Base / Normal / Lit 用于基准、法线和手动光照对照。Runtime Lighting Foundation v1 已通过验收。R2A 已接入 Dawn / Noon / Dusk / Night 静态 preset 与手动参数；R2B 自动 24h 时间线尚未开始，详见 [`validation/TIME_OF_DAY_KEYFRAMES_R2A.md`](validation/TIME_OF_DAY_KEYFRAMES_R2A.md)。

Leaves 第一版用独立的 `engine/animation/LeafField.ts` 在 Canvas 2D 中逐片绘制，按可见 Artwork 区域裁剪；竖屏 contain 留边不会出现叶子。桌面 18 片、移动端（≤640 CSS px）10 片；主体约 14–32 CSS px，8% 概率为 38 px 前景叶。下落 10–22 CSS px/s；共同风向 2.5 CSS px/s，9 秒周期的 ±5 CSS px/s 微风，另有最多 2.5 CSS px/s 的个体轻摆。帧率上限 30、覆层 DPR 上限 1.5、透明度 0.58–0.84。以上均由 `src/config/hero.ts` 管理，属于可调的首版值，未视为最终视觉参数。

Debug Panel 已可开关 Leaves 并查看粒子数量。`prefers-reduced-motion` 或 Static quality 时默认关闭；页面后台停止 RAF，恢复时清零时间差以免跳帧；resize 更新画布和桌面／移动端数量。后续可按实际观感优化局部发射区、层次、遮挡与配色；若需要 atlas 再从四张 master 派生并保留透明 padding。

参考 [KumengScreen 的透明花瓣纹理粒子方案](https://github.com/buger404/KumengScreen#%E5%8A%A8%E6%95%88%E4%B8%8E%E8%8A%B1%E7%93%A3)：后续可用 Alpha Blend 绘制独立秋叶，并借鉴共同阵风与个体旋转、翻转、起落的分层思路；本项目的轨迹、密度和画面遮挡须按 Base 单独设计。
