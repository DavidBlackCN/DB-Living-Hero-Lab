# 空间光影 / 窗框配准验收（2026-09-16）

基线为 `bef0321`。图片和测量 JSON 只保留在本地，Git 只跟踪本说明和生成脚本。

## 建议查看顺序

1. [原图 / Overlay / Exterior Mask 窗框放大对照](window-registration.png)
2. [修改前后 Final 与相同算法灰度对照](before-after.png)
3. [四时段 Final / 灰度 / Neutral / Projected / Shadow 总览](comparison.png)
4. [四时段 Scene / Overlay / Exterior 总览](regions.png)

## 最终独立截图

| 时间 | Final | Neutral | Scene | Overlay | Projected Light Only | Exterior Mask | Shadow |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 08:00 | [查看](final/acceptance/morning-final.png) | [查看](final/acceptance/morning-neutral.png) | [查看](final/acceptance/morning-scene.png) | [查看](final/acceptance/morning-overlay.png) | [查看](final/acceptance/morning-projected.png) | [查看](final/acceptance/morning-exterior.png) | [查看](final/acceptance/morning-shadow.png) |
| 12:00 | [查看](final/acceptance/noon-final.png) | [查看](final/acceptance/noon-neutral.png) | [查看](final/acceptance/noon-scene.png) | [查看](final/acceptance/noon-overlay.png) | [查看](final/acceptance/noon-projected.png) | [查看](final/acceptance/noon-exterior.png) | [查看](final/acceptance/noon-shadow.png) |
| 17:30 | [查看](final/acceptance/dusk-final.png) | [查看](final/acceptance/dusk-neutral.png) | [查看](final/acceptance/dusk-scene.png) | [查看](final/acceptance/dusk-overlay.png) | [查看](final/acceptance/dusk-projected.png) | [查看](final/acceptance/dusk-exterior.png) | [查看](final/acceptance/dusk-shadow.png) |
| 23:00 | [查看](final/acceptance/night-final.png) | [查看](final/acceptance/night-neutral.png) | [查看](final/acceptance/night-scene.png) | [查看](final/acceptance/night-overlay.png) | [查看](final/acceptance/night-projected.png) | [查看](final/acceptance/night-exterior.png) | [查看](final/acceptance/night-shadow.png) |

## 23:00 窗口放大

| 区域 | 原图 | Final | Scene | Overlay | Exterior Mask |
| --- | --- | --- | --- | --- | --- |
| 右侧整块玻璃 | [查看](final/acceptance/night-right-pane-base.png) | [查看](final/acceptance/night-right-pane-final.png) | [查看](final/acceptance/night-right-pane-scene.png) | [查看](final/acceptance/night-right-pane-overlay.png) | [查看](final/acceptance/night-right-pane-exterior.png) |
| 下缘与摆件 | [查看](final/acceptance/night-window-base.png) | [查看](final/acceptance/night-window-final.png) | [查看](final/acceptance/night-window-scene.png) | [查看](final/acceptance/night-window-overlay.png) | [查看](final/acceptance/night-window-exterior.png) |

仅修 mask 的 Phase B 截图保留在 `mask/acceptance/`；投光修改前为 `before/acceptance/`。

## 复现

```powershell
npm run assets:generate
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/spatial-light-review/final'
npm run test:visual
python scripts/summarize-spatial-review.py
```

全景 1920×1080，DPR 1；窗口截图取自 2400×1350 视口。固定时间，减少动态开启，动画与蒸汽关闭，曝光 0、Bloom .22、投光强度 .42，其余默认。Neutral 为固定 ×.6 的光照亮度；Final 灰度统一使用 Rec.709 权重，不做逐图自动提亮或归一化。Projected 不包含环境光或台灯；Shadow 展示艺术指导暗部字段，不是深度图。

生成脚本可以在新克隆中只生成当前对照；没有旧版本图片时跳过 before/after。旧版图片必须从旧代码单独运行获得，不能用新渲染器伪造。

本地测量：[贴边采样](final/acceptance/window-edge-results.json)、[投光位置与物体覆盖](final/acceptance/projected-metrics.json)、[亮暗与夜景分区](final/acceptance/spatial-contrast.json)。

算法、改动文件、验证和限制见 [阶段记录](../../logs/spatial-light-review.md)。完成本轮后等待人工验收，不继续新增动效。
