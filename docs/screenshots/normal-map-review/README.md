# 笔具遮挡修正与配准 normal v1 候选

基线 `3769bdb`。本轮先修红框物体，再启动 normal 制作。

## 1. 红框 mask

原因是 `penCup` 曲线漏掉了笔具顶部与右侧的浅色实体。已按原图扩展该局部轮廓；其余窗框、左下缘过渡、右玻璃和 shader 均未改。

[红框局部修改前后](pen-mask-comparison.png) · [最终 23:00 Final 放大](final/acceptance/night-window-final.png) · [Overlay](final/acceptance/night-window-overlay.png) · [Exterior](final/acceptance/night-window-exterior.png)

新增三处笔具采样 `(935,263)`、`(947,264)`、`(951,270)`（1200×675 原图坐标）。外景覆盖须低于 5/255，允许虚焦边缘的极小量化余量；背景、窗框原有检查保持不变。

改动：`docs/scene-regions.json`、生成的 `scene-masks.svg`、`tests/visual/window-light.visual.spec.ts`。

## 2. Normal 制作结果与取舍

使用 imagegen 技能和内置图像工具尝试了一张完整 normal。输出为 1672×941，并重绘了书本等局部几何，未通过配准要求，**未接入运行**。完整输入要求、工具和输出路径见 [提示词记录](../../prompts/normal-map-v1.md)。拒用的图片只保留本地。

随后制作了可复现的 **3840×2160 authored normal v1 候选**，可在 `/?normal=registered` 预览。普通 `/` 保留低频版本。运行资产为 `public/assets/generated/normal-registered-v1.png`。

### 方法

- `docs/normal-surfaces.json`：原图 1200×675 坐标中的表面轮廓、发束／褶皱引导曲线及体积参数。书页分面线沿弯曲书脊重新校准。
- `scripts/generate-registered-normal.py`：原生 4K 栅格化轮廓，沿曲线构造平滑曲面，用曲面梯度得到方向，合成并归一化为 RGB 法线。
- 发束与衣袖增加中频曲率；杯身使用柱面，杯口为倾斜平面，书本左右页分别建模。脸部和手部变化很弱，不把眼睛和线稿压成凹槽。
- 先求曲面导数再按轮廓合成，避免把轮廓边界误做成一圈凸起。没有用颜色亮度或已有阴影生成 bump，没有移动或重画底图。
- 编码为 `RGB = (XYZ × .5 + .5) × 255`；+X 向右、+Y 向下、+Z 朝观察者。墙面／玻璃保持 `(128,128,255)`。
- `src/app/main.ts` 仅增加候选 URL 选择；无 shader 修改、额外纹理或额外渲染 pass。法线贴图仍占原有 4K RGB8 插槽，source texture 总量仍为 97.24 MiB。

### 检查结果

- 尺寸 3840×2160；抽样最大单位向量误差约 .006，最小 Z 约 .71（包括 8-bit 量化）。
- 验证墙面／玻璃平坦、脸部克制、桌面朝上、杯身左右方向相反、书页朝上。
- 法线强度设为零后，两版本 Final 截图逐像素一致，已加入自动断言。
- 原图 SHA-256 未变。沿原图坐标绘制的引导图用于人工检查真实轮廓配准；自动方向检查不能代替这一步。

## 3. 验收图

[四时段 Final / Neutral 前后对照](final/normals/comparison.png)

[原图 / Normal / 引导线局部对照](final/normals/surface-details.png) · [完整引导线](final/normals/source-guides.png)

[低频 Normal](final/normals/low-frequency-noon-normal.png) · [候选 Normal](final/normals/registered-noon-normal.png)

| 时间 | 低频 Final | 候选 Final | 候选 Neutral |
| --- | --- | --- | --- |
| 08:00 | [查看](final/normals/low-frequency-morning-final.png) | [查看](final/normals/registered-morning-final.png) | [查看](final/normals/registered-morning-neutral.png) |
| 12:00 | [查看](final/normals/low-frequency-noon-final.png) | [查看](final/normals/registered-noon-final.png) | [查看](final/normals/registered-noon-neutral.png) |
| 17:30 | [查看](final/normals/low-frequency-dusk-final.png) | [查看](final/normals/registered-dusk-final.png) | [查看](final/normals/registered-dusk-neutral.png) |
| 23:00 | [查看](final/normals/low-frequency-night-final.png) | [查看](final/normals/registered-night-final.png) | [查看](final/normals/registered-night-neutral.png) |

隔离方向光诊断：[低频](final/normals/low-frequency-directional-only.png) / [候选](final/normals/registered-directional-only.png)。此诊断关闭环境光、投光、台灯、Bloom 和 stylized band，双方使用相同设置。

## 4. 还没有完成的质量目标

v1 是**配准制作的起点，不是已经验收的最终高质量 normal**。曲面来自人工定义，细发丝、领口、指节和衣褶仍未逐一重建；边界延续部分现有近似 region。AI 图片的细节更丰富，但几何漂移使其不能直接使用。

目前 Final 改变量温和：现有 normal 只影响方向光；投光束和台灯没有读取 normal，23:00 的太阳系数为零，因此夜间两版相同。没有通过提高饱和度、光强或改 shader 夸大本次收益。

下一步应先审查轮廓和曲率，再精修有收益的发束／衣褶局部；通过后才适合讨论将配准法线用于窗光和台灯的表面响应。本轮没有执行这些后续光照改动。

## 5. 验证与复现

`npm run typecheck`、`npm run build`、`npm test`（7/7）、`npm run test:visual`（29/29）通过。

```powershell
npm run assets:generate
npm run assets:normal
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/normal-map-review/final'
npm run test:visual
python scripts/summarize-normal-review.py
```

`tests/visual/normal-map.visual.spec.ts` 保存实际浏览器对照并检查方向与禁用后的相等性；`scripts/summarize-normal-review.py` 整理接触表和差异数据。测试图片、AI 失败候选和 JSON 保持本地忽略；normal 运行候选、生成脚本、曲面源文件和文档纳入 Git。
