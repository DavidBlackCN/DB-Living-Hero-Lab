# Dawn Sky / Scene Synchronization

基线 `ecc955e`。用户指出天空先亮，建筑/人物光照后亮。本轮调整范围为 05:00–06:30 晨间过渡。

## 根因与修复

天空 `skyFor()` 从 05:00–06:30 连续混合 Night/Dawn，但 `lightingFor()` 的主能量插值从 05:30 才开始，光色又单独跟随太阳高度。05:00–05:30 仅靠一个很弱的临时环境光补偿；实测天空已变亮，场景反而稍微变暗。

现在晨间 Key intensity、Ambient intensity、exposure 和两种光色直接共用 `skyFor()` 的同一 mix。起点采用原 05:00 光照，终点采用已验收的 06:30 Dawn；删除原独立 predawn fill hump。无需修改天空素材、遮罩、shader 或太阳/月亮方向。

其他时段、人物材质响应、动作、Lamp、Leaves、Atmosphere 和 Post 参数均未修改。天空与物体不需要相同亮度；本轮统一的是过渡时间与进度，保留各自的材质受光。

## 实测

固定场景非天空区域的显示 RGB 均值：

| 时间 | 修复前 | 修复后 |
| --- | ---: | ---: |
| 05:00 | 33.10 | 33.10 |
| 05:15 | 32.38 | 35.35 |
| 05:30 | 31.74 | 41.18 |
| 05:45 | 36.50 | 49.55 |
| 06:00 | 49.11 | 59.98 |
| 06:15 | 65.76 | 70.48 |
| 06:30 | 78.34 | 78.34 |

以 05:00/06:30 作为 0/1 归一化两个区域的亮度进度，7 个固定时刻的天空/场景平均绝对差从 0.203 降至 0.074，减少约 64%。这是验收区域的图像指标，不是物理照度误差。每 5 分钟检查，天空、场景与脸部采样区域在晨间均单调增亮，没有初段变暗。

视觉复查：05:15 建筑和人物开始跟随天空苏醒；05:30–06:00 不再出现明显亮天空配深夜人物的滞后感；06:30 回到同一 Dawn 锚点。无需进一步加亮。

## 验收素材

- [05:00–06:30 before / after](dawn-sync/dawn-ab.jpg)
- [晨间连续时刻](dawn-sync/dawn-times.jpg)
- [四时段锚点](dawn-sync/four-phases.jpg)
- [固定时刻数据](dawn-sync/audit-stats.json)
- [关键回归数据](dawn-sync/regression-stats.json)

`pnpm typecheck`、`pnpm build`、实际渲染专项审查及现有 regression 通过。04:30–07:00 每 5 分钟 A/B，另检 00:00、03:30、Noon、Dusk、Night、24:00；05:00–06:30 区间外所有受检帧完全一致，00:00/24:00 一致。早晨相邻 10 分钟全图平均 RGB 最大变化由 10.855 降至 8.005；傍晚采样保持原结果。

回归涵盖 context restore、4K/mobile resize、reduced-motion、hidden tab、static quality、Blink/Motion、Lamp、Leaves、Post。无新增资源或绘制任务。当前作为修正后的视觉冻结候选，等待人工复查；未进入下一阶段。