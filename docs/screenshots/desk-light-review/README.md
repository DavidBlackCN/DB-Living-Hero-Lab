# 左手与桌面光影验收

重点：画面左侧手腕／手背的块状受光、书页上的错位投影及夜間桌面光池。左列中午，右列午夜；对比图上行为修改前，下行为修改后。

- **[左手放大前后对照](hand-final-comparison.png)**
- [桌面 Final 前后对照](desk-final-comparison.png)
- [桌面 Neutral 前后对照](desk-neutral-comparison.png)
- [桌面 Shadow 前后对照](desk-shadow-comparison.png)
- [四时段八视图总览](four-times.png)：含 Final 灰度转换；无逐图曝光归一化。
- [原因、文件改动与测试结果](../../logs/desk-light-review.md)

## 原始浏览器截图

| 时间 | Final | Neutral | Scene | Overlay | Projected | Exterior | Shadow |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 08:00 | [查看](after/acceptance/morning-final.png) | [查看](after/acceptance/morning-neutral.png) | [查看](after/acceptance/morning-scene.png) | [查看](after/acceptance/morning-overlay.png) | [查看](after/acceptance/morning-projected.png) | [查看](after/acceptance/morning-exterior.png) | [查看](after/acceptance/morning-shadow.png) |
| 12:00 | [查看](after/acceptance/noon-final.png) | [查看](after/acceptance/noon-neutral.png) | [查看](after/acceptance/noon-scene.png) | [查看](after/acceptance/noon-overlay.png) | [查看](after/acceptance/noon-projected.png) | [查看](after/acceptance/noon-exterior.png) | [查看](after/acceptance/noon-shadow.png) |
| 17:30 | [查看](after/acceptance/dusk-final.png) | [查看](after/acceptance/dusk-neutral.png) | [查看](after/acceptance/dusk-scene.png) | [查看](after/acceptance/dusk-overlay.png) | [查看](after/acceptance/dusk-projected.png) | [查看](after/acceptance/dusk-exterior.png) | [查看](after/acceptance/dusk-shadow.png) |
| 23:00 | [查看](after/acceptance/night-final.png) | [查看](after/acceptance/night-neutral.png) | [查看](after/acceptance/night-scene.png) | [查看](after/acceptance/night-overlay.png) | [查看](after/acceptance/night-projected.png) | [查看](after/acceptance/night-exterior.png) | [查看](after/acceptance/night-shadow.png) |

额外的 **00:00／12:00** 桌面 Base／Final／Neutral／Scene／Shadow 近景位于 `after/desk/`；包括低频 normal 与 registered 候选两种版本。候选四时段全图位于 `after/normals/`。

本轮窗户 mask 未调整；23:00 Exterior 与上轮逐像素一致。配准 normal 已按校准区域重建，但仍为候选，尚未替换默认版本。

## 复现

PowerShell，在仓库根目录：

```powershell
npm run assets:generate
npm run assets:normal
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/desk-light-review/after'
npm run test:visual
python scripts/summarize-desk-review.py
```

`before/desk/` 来自修改前 `a4f6d11` 的同配置浏览器截图；重建前后对照需要保留它。所有测试图片、指标 JSON 和临时日志均被 Git 忽略，仅说明和重建脚本提交到仓库。测试为 7 项单元测试、31 项浏览器测试，均通过。
