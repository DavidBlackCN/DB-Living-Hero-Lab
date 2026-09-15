# Window / Projected Light 人工验收

图像和采样 JSON 仅保留在本地，已加入 `.gitignore`，不提交到 GitHub。新克隆仓库需先运行下方命令生成当前截图；历史 before / stage1 对比只在保留了对应本地截图时可用。

## 先看这两张

- [窗框：修改前 / 最终，23:00 Final 与 Overlay 放大对比](window-before-after.png)
- [四时段：Final / Final 灰度 / Neutral / Projected 对比](stage2/acceptance/comparison.png)

完整无 UI 截图 1920×1080，DPR 1，固定时间，曝光 0，关闭动画与蒸汽；Bloom 默认 .22，投光强度 .42。窗边近景以 2× 参考坐标输出。原图未改动。

## 最终截图：四时段 × 五视图

| 时间 | Final | Scene | Overlay | Neutral | Projected Light Only |
| --- | --- | --- | --- | --- | --- |
| 08:00 | [查看](stage2/acceptance/morning-final.png) | [查看](stage2/acceptance/morning-scene.png) | [查看](stage2/acceptance/morning-overlay.png) | [查看](stage2/acceptance/morning-neutral.png) | [查看](stage2/acceptance/morning-projected.png) |
| 12:00 | [查看](stage2/acceptance/noon-final.png) | [查看](stage2/acceptance/noon-scene.png) | [查看](stage2/acceptance/noon-overlay.png) | [查看](stage2/acceptance/noon-neutral.png) | [查看](stage2/acceptance/noon-projected.png) |
| 17:30 | [查看](stage2/acceptance/dusk-final.png) | [查看](stage2/acceptance/dusk-scene.png) | [查看](stage2/acceptance/dusk-overlay.png) | [查看](stage2/acceptance/dusk-neutral.png) | [查看](stage2/acceptance/dusk-projected.png) |
| 23:00 | [查看](stage2/acceptance/night-final.png) | [查看](stage2/acceptance/night-scene.png) | [查看](stage2/acceptance/night-overlay.png) | [查看](stage2/acceptance/night-neutral.png) | [查看](stage2/acceptance/night-projected.png) |

Scene 红色为玻璃覆盖，绿色为室内受光面，蓝色为灯发光区。
Neutral 是固定比例的光照灰度显示；Projected 是投光系数，夜间必须全黑。

### 窗框专项

- 原图：[Base 放大](stage2/acceptance/night-window-base.png)
- 第一阶段：[Final](stage1/acceptance/night-window-final.png) / [Scene](stage1/acceptance/night-window-scene.png) / [Overlay](stage1/acceptance/night-window-overlay.png)
- 最终：[Final](stage2/acceptance/night-window-final.png) / [Scene](stage2/acceptance/night-window-scene.png) / [Overlay](stage2/acceptance/night-window-overlay.png)
- [修改前整组对比](before/acceptance/comparison.png) / [仅修 mask 整组对比](stage1/acceptance/comparison.png)

验收点：右窗下方原来的蓝色斜带是否消失；横窗框/窗台不应出现在红色 mask 内。细花枝、笔具和透明物体仍为近似，不能把窗框验证等同于所有室内物体逐像素分割完成。

### 投光专项

08:00 的主要投光在杯子和右桌面；12:00 更宽、更高、更中性；17:30 跨越靠窗头发、肩部、书本和桌面；23:00 无白天投光。请同时看 Final 灰度行，区分投光形状变化与色温变化。

[GPU 采样与去总亮度后的形状差异](stage2/acceptance/projected-metrics.json)。它验证位置/形状，不替代人工审美评价。
注意：Neutral 的显示比例由旧版 1 改为最终 .6 以避免裁白，因此只在同一阶段内比较 Neutral。Final 灰度转换在所有阶段保持一致。

## 验证与复现

第一阶段：typecheck / build / 6 项单测 / 24 项视觉测试通过。
最终：typecheck / build / 7 项单测 / 25 项视觉测试通过。

```powershell
$env:VISUAL_OUTPUT_ROOT='docs/screenshots/window-light-review/stage2'
npm run typecheck
npm run build
npm test
npm run test:visual
python scripts/summarize-visual-review.py
```

`before` 是改代码前实拍；不要用新代码重录覆盖它。若开启新的迭代，请换输出目录。已清理旧阶段与重复截图；本轮 before / stage1 / stage2 验收图保留在本地。汇总脚本会跳过不存在的历史阶段。

文件清单、算法和限制：[阶段记录](../../logs/window-light-review.md)。Blink：[评估与素材规范](../../logs/blink-registered-plan.md)。

本轮到此停止，等待人工验收。
