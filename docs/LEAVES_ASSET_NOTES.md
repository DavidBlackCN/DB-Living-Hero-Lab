# Leaves · asset notes

## 当前交付

四张独立 PNG 位于 `public/assets/hero/leaves/`。每张为 1024×1024 RGBA，只有一片完整的五裂秋叶，四周为真实透明像素。它们是供后续场景预览的候选 master，尚未做运行时粒子与最终美术冻结。

参考 [KumengScreen](https://github.com/buger404/KumengScreen#%E5%8A%A8%E6%95%88%E4%B8%8E%E8%8A%B1%E7%93%A3) 的独立透明花瓣纹理资产思路；这里重新制作秋叶，不复用其素材或应用结构。

| 文件 | 颜色与形态 | 主体范围（按 alpha ≥ 128 的包围盒） |
| --- | --- | --- |
| `leaf-01.png` | 低饱和赭黄，窄长中裂片与轻微上卷的右缘 | 749×692 px |
| `leaf-02.png` | 暖橙褐，左缘明显卷曲且叶缘略不规则 | 738×749 px |
| `leaf-03.png` | 灰橄榄金棕，斑驳细纹、下方一裂片轻卷 | 737×749 px |
| `leaf-04.png` | 深红棕／枯棕，小缺口与右缘卷曲 | 748×740 px |

最大方向的主体范围约为画布的 72–73%；`leaf-01` 的另一方向约为 68%，保留了叶形比例。四张原始图分别生成，未通过旋转或调色复制。绘制内容只做等比缩放、居中透明留边、去除极低 alpha 散点和 1024×1024 导出。

## 生图提示词基线

四张均使用独立生成请求。共同要求：`single complete five-lobed maple-like autumn leaf; isolated transparent RGBA particle sprite; refined hand-painted 2D anime background prop matching a calm muted autumn campus illustration; centered square composition; short intact petiole; gentle intrinsic texture and curl shading only; real transparent alpha with clean antialiased edges; no background, ground, cast shadow, glow, bloom, branch, cluster, second leaf, strong directional light, lettering or watermark`。

- `leaf-01`: `muted low-saturation ochre yellow; olive-brown veins; fine asymmetric serration; slightly curled upper-right tip`。
- `leaf-02`: `muted warm orange-brown; burnt-sienna veins; softly curled left lobe; naturally uneven dry edge`。
- `leaf-03`: `desaturated gray-olive gold-brown; umber veins; subtly asymmetric lobes; folded lower-right lobe and sparse mottling`。
- `leaf-04`: `deep desaturated red-brown / withered burgundy-brown; narrower upper lobes, broader lower lobes, small margin chips and one curled edge`。

要求主体目标约为画布 70–75%；图像生成工具实际输出 1254×1254，因此用等比缩放与透明留边导出 1024×1024 master，没有在后处理里重绘叶片。

## 验收与后续

程序检查：四张均为 RGBA / 1024×1024，四条画布边缘 alpha 全为 0，主体周围至少约 12% 透明留白；文件内容各不相同。已逐张检查轮廓，并在浅灰与深灰底上检查透明边缘。尚需在真实 Base 场景中以预期粒子尺寸和运动方式做人眼验收。

若以后需要 atlas，可从这四张 master 派生打包版本，保留每片的透明 padding 与纹理过滤安全边；目前不创建 atlas，也不改变 master。动态 Leaves 开关继续保持禁用，直到粒子系统实现。
