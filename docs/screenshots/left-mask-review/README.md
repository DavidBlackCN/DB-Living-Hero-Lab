# 左侧玻璃下缘局部修正

仅修正用户指出的左侧窗框下缘误覆盖，基线 `92cbcae`。

- `docs/scene-regions.json`：上移 `windowGlassLeft` 下缘到原图玻璃/窗框顶部过渡处，局部约 20 个原图像素；保留原有左侧斜边直线，与新下缘求交。其余 region 和 shader/光照参数未改。
- `public/assets/generated/scene-masks.svg`：由原生成脚本重新生成；其余运行贴图内容不变。
- `docs/window-edge-probes.json`、`tests/visual/window-light.visual.spec.ts`：新增 4 对左下缘原图坐标采样，分别检查玻璃与窗框两侧，防止原先只覆盖右侧边界的测试漏检。

## 23:00 验收

[修改前后：原图 / Final / Exterior Mask](comparison.png)

[Final 下缘放大](after/acceptance/night-window-final.png) · [Scene](after/acceptance/night-window-scene.png) · [Overlay](after/acceptance/night-window-overlay.png) · [Exterior Mask](after/acceptance/night-window-exterior.png)

[贴边采样结果](after/acceptance/window-edge-results.json)。截图和 JSON 被现有 `.gitignore` 排除，仅在本地保留。

复现截图：

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/left-mask-review/after'
npm run test:visual
```

验证：`npm run typecheck`、`npm run build`、`npm test`（7/7）、`npm run test:visual`（27/27）。本轮没有调整投光、夜景分区或其他动效。
