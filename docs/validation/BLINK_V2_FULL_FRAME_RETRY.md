# Blink v2 · 整图闭眼重试

## 结论

**失败：不满足整图 Blink 可用标准。** 新候选闭眼表情自然、尺寸正确，但除双眼外仍有全画面细节重绘。它比 v1 的眼外差异略小，却仍会在直接切换整图时产生背景与人物纹理闪动。本轮不生成 Half，也不把新候选放入运行时素材目录。后续正式采用**局部眼部 Blink** 路线；Base 之外的像素必须保持原图，不应再用整图生成结果直接替换帧。

## 输入与生成

- 编辑目标：`public/assets/hero/base/base-albedo.png`，冻结的 1672×941 RGB 原图；未修改。
- 工具：内置 imagegen，使用 Base 作为唯一参考／编辑目标。
- 本轮原始输出：[blink-v2-generated-rejected.png](blink-v2-generated-rejected.png)，1672×941 RGB，未缩放、裁切或后处理；仅作为失败证据归档，不供运行时加载。
- 指令核心：`Edit Image 1 as the immutable base artwork; change only the girl's two eyes and immediately adjacent eyelid/eyelash pixels (approximately x=1093–1161,y=188–239 and x=1163–1233,y=207–261); preserve every other part of the 1672×941 scene and exact pixel registration; no redraw, shift, crop, relighting, smoothing or global filter outside those tiny regions.`

## 静态像素验证

两图均为 1672×941 RGB。为避免把眼周变化误计到眼外，排除比提示词指定范围更宽松的两个矩形：`[1085,180,1168,246)` 与 `[1155,199,1240,269)`，坐标以左上为原点，右下边界不包含。

| 指标 | v1 旧候选 | v2 本轮候选 |
| --- | ---: | ---: |
| 至少一个通道发生变化的全图像素 | 99.18% | 99.13% |
| 眼外平均 RGB 通道绝对差 | 4.125 | 3.643 |
| 眼外平均通道差 ≥10 的像素 | 118,743（7.60%） | 87,457（5.60%） |
| 眼外平均通道差 ≥20 的像素 | 约 1.46% | 12,532（0.80%） |

v2 中平均通道差 ≥10 的全图像素共 90,574 个，只有 3,117 个（3.44%）落在双眼排除框内。最高幅度的差异主要在眼部，但大量中小差异仍遍布眼外。差异主要是生成式重绘，而不是可以通过统一平移解决的注册问题。

另在左侧建筑区域 `x=70..779, y=120..739` 测试 ±3 px 平移，v2 对 Base 的最低平均 RGB 绝对误差为 3.027，出现在 `(dx=0, dy=0)`；邻近位移的误差更高。

## 可视证据

- [眼部对比](blink-v2-eye-comparison.png)：闭眼造型本身可读。
- [全画面差异图](blink-v2-difference.png)：平均 RGB 差异放大 4 倍；建筑、栏杆、衣物和头发仍有变化。
- [原始失败候选](blink-v2-generated-rejected.png)：供人工复核，不属于 `public/assets/hero/blink/` 正式资源。

## 后续决定

局部方案可以从 v1 或 v2 的眼部内容提取／制作透明眼部图层，但必须让眼外最终像素与 Base 完全一致，并再做接缝、Open / Half / Closed 节奏和页面实机验收。不能把裁剪合成后的整帧冒称为本次“原始整图生成成功”。Normal 阶段本轮不开始。
