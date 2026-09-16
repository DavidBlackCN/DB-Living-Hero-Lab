# 左下玻璃 mask：消除硬切与前景块状遮挡

基线 `983c725`。只改左下窗户 mask 的离线生成；shader、时段光照、右侧玻璃未改。

## 原因与改动

上轮修正了下缘位置，但原图这一带有景深虚化，mask 仍然是近乎二值的硬切线。同时 `penCup` 的旧多边形向上包进了笔尖上方的背景，产生了明显直角块状遮挡。

- `docs/scene-regions.json`：保留玻璃几何边界；添加左下缘内侧约 2.4 参考像素（7.7 原图像素）的覆盖过渡；将笔具前景改为沿原图的曲线轮廓，并补上穿过下缘的虚焦细杆。
- `scripts/generate-scene-assets.mjs`：只给左玻璃下缘生成斜向 alpha 渐变，仍裁剪在玻璃轮廓内；笔具边缘与虚焦杆分别使用 .8 / 2.5 参考像素的模糊。右玻璃保持原有栅格覆盖。没有恢复整窗侵蚀，也没有加入 shader UV 补丁。
- `public/assets/generated/scene-masks.svg`：重新生成。没有增加运行时纹理或渲染 pass；其他生成资产内容不变。
- `tests/visual/window-light.visual.spec.ts`：检查笔尖本体被保护、旧多边形占用的背景恢复为玻璃；左下缘新增连续过渡断言。右侧贴边标准未放宽。

## 验收

[修改前后 Final / Exterior Mask 放大对比](comparison.png)

[Final](after/acceptance/night-window-final.png) · [Scene](after/acceptance/night-window-scene.png) · [Overlay](after/acceptance/night-window-overlay.png) · [Exterior Mask](after/acceptance/night-window-exterior.png)

左下缘 4 对采样：距边界内侧 12 个原图像素均为 255，内侧 5 像素为 133–155、内侧 2 像素为 34–56，窗框侧 3 像素均为 0。由此检查的是渐变覆盖，而非把硬边整体向外模糊。

与上版 Scene 截图逐像素比较：右侧玻璃变化像素为 0，Scene G/B（受光区域／灯源）变化像素为 0。

验证通过：`npm run typecheck`、`npm run build`、`npm test`（7/7）、`npm run test:visual`（27/27）。图片与测量 JSON 仅保留本地，现有 `.gitignore` 已排除。

复现当前截图：

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/left-mask-softness/after'
npm run test:visual
```

这是局部艺术指导配准，虚焦细杆仍为近似覆盖。最终自然程度以此次放大图人工验收为准。
