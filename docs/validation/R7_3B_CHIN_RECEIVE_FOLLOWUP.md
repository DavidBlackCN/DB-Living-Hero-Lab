# R7.3B — 下巴 / 颈部受光衔接补全

基线 `62929ab`。用户复查指出 Dawn / Night 的下巴深影仍明显；上一轮只清理鼻部和面中 coverage，不足以覆盖下颌到颈部的实际交界。

## 根因与修正

旧 Face R 多边形止于下颌，2.5 px 羽化沿下巴迅速降到零；露出的颈部完全未注册。原画已画有下颌投向颈部的阴影，Normal 在此处基本平滑，但运行时又把这些皮肤像素混进 architecture receive，Dawn / Night 加重其深色和割裂感。

把现有皮肤多边形沿真实颈部轮廓接到领口上沿，脸与颈部连续共享同一柔和 Sun/Moon receive。羽化现在位于皮肤外轮廓，不再穿过下巴内部。未新增局部补光、阴影补丁、shader 参数、sampler 或 pass。原画的轻微颈部投影与下颌细轮廓保留。

- `(1150,294)` 下颌交界 R：72 → 255；`(1135,300)` 颈部 R：0 → 255。
- 2539 个 R 像素变更，bounds `(1101,266)`–`(1185,322)`；G Hair / B Iris / A 逐字节不变。
- 同 shader / 光照 / Post、仅替换旧新 material asset 的实际 A/B，Dawn / Night 的额外压暗减轻。变更 ROI 以外最大 RGB 差：Dawn / Night 0，Noon / Dusk 1（显示收尾的微量差）。Noon / Dusk 只在同一颈部受光区域产生必要变化。
- Base、Normal、Character Motion、Blink、Lamp、Leaves、Atmosphere / Post 参数和时间曲线均未改。

## 验收

- 下巴 / 颈部 8×：[Dawn before / after](r7-3b-chin-followup/dawn-jaw-ab.jpg) · [Night before / after](r7-3b-chin-followup/night-jaw-ab.jpg)。
- 头部 3×：[Dawn](r7-3b-chin-followup/dawn-head-ab.jpg) · [Noon](r7-3b-chin-followup/noon-head-ab.jpg) · [Dusk](r7-3b-chin-followup/dusk-head-ab.jpg) · [Night](r7-3b-chin-followup/night-head-ab.jpg)。
- [四时段当前头部](r7-3b-chin-followup/four-heads.jpg) · [四时段全图](r7-3b-chin-followup/four-phases.jpg) · [Dawn 全图](r7-3b-chin-followup/dawn-after.png) · [Night 全图](r7-3b-chin-followup/night-after.png)。
- 根因对照：[皮肤 coverage](r7-3b-chin-followup/skin-coverage-ab.jpg) · [原画下颌 / 颈部](r7-3b-chin-followup/base-jaw.png) · [原 Normal 局部](r7-3b-chin-followup/normal-jaw.png)。

`pnpm typecheck` / `pnpm build`、实际-render coverage audit、Character coherence / Atmosphere lifecycle regression 通过。00:00 / 24:00 最大 RGB 差 0；晨昏逐 10 分钟连续性通过。Blink、Head / Hair / Breathing、Leaves、Lamp、Post、hidden tab、reduced motion、static quality、context restore 和 1080p / 1440p / 4K / mobile resize smoke 通过。详情见 `audit-stats.json` / `regression-stats.json`。

修改：`scripts/paint_material_mask.py`、`public/assets/hero/material/material-mask.png`；新增 `scripts/audit_chin_receive.py`，旧 coverage audit 的允许边界同步包括已露出的颈部；本记录、checkpoint 与验收图。没有重复长时性能测试，渲染结构不变。

剩余可见的是原画自带的颈部结构投影；本轮不声称消除所有下颌阴影。请重点判断 Dawn / Night 是否已达到自然、柔和的衔接。停止等待人工验收，不进入新阶段。
