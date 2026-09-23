# Animation plan

| Module | Asset / input | Next validation |
| --- | --- | --- |
| Blink | 闭眼候选、未来半闭眼与眼部区域 | 检查背景跳变和像素注册，再决定整图或局部方案。 |
| Breathing | 安全区域、幅度和周期参数待定 | 先人工确认衣料和轮廓变形范围。 |
| Hair Motion | 独立发束区域或 Mask 待定 | 核对发梢、背景和遮挡关系。 |
| Leaves | `leaf-01.png`～`leaf-04.png` 四张透明候选 master 已制作；发射区、路径、速度和密度待定 | 下一步先在 Base 场景中人工检查缩小后的辨识度、边缘与遮挡，再定轻量粒子行为。 |

所有坐标由 `engine/coordinates/artwork.ts` 提供。未冻结任何最终动画参数；Debug 面板的控件目前为禁用占位。

Leaves 目前只完成素材制作与独立透明图验收，没有实现粒子系统、时间线或 Debug 开关。运行时应以 Artwork Space 定义发射与消失区域，并遵守 reduced motion、后台停帧及移动端降级；具体参数等场景预览后决定。以后若需要 atlas，再从这四张 master 派生并保留透明 padding，master 本身不合图。

参考 [KumengScreen 的透明花瓣纹理粒子方案](https://github.com/buger404/KumengScreen#%E5%8A%A8%E6%95%88%E4%B8%8E%E8%8A%B1%E7%93%A3)：后续可用 Alpha Blend 绘制独立秋叶，并借鉴共同阵风与个体旋转、翻转、起落的分层思路；本项目的轨迹、密度和画面遮挡须按 Base 单独设计。
