# Animation plan

| Module | Asset / input | Next validation |
| --- | --- | --- |
| Blink | 闭眼候选、未来半闭眼与眼部区域 | 检查背景跳变和像素注册，再决定整图或局部方案。 |
| Breathing | 安全区域、幅度和周期参数待定 | 先人工确认衣料和轮廓变形范围。 |
| Hair Motion | 独立发束区域或 Mask 待定 | 核对发梢、背景和遮挡关系。 |
| Leaves | 透明叶片素材与发射区待定 | 先制作与验收素材，再实现轻量粒子。 |

所有坐标由 `engine/coordinates/artwork.ts` 提供。未冻结任何最终动画参数；Debug 面板的控件目前为禁用占位。
