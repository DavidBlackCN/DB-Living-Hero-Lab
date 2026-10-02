# Tower Final Coverage & 24H Review

基线：`0f1078d`。本轮仅修复人物贝雷帽左上方塔身漏覆盖，完成 24H 实际渲染与全动画 Play 审查。建议冻结当前 R7.3B 视觉收口，等待用户最终人工确认；未开始 R7.4。

## 修复原因与范围

旧塔身 polygon 在 artwork `x≈1075, y≈44–80` 附近过早内收，未贴合实际石材与帽沿相交的轮廓。漏出的窄楔形石材仍沿用旧背景受光，凌晨成为不合理亮缝。已沿原画重新注册右上轮廓，并在下部顺着帽沿收回。修改的是同一塔身材质覆盖，不新增光源、压暗层或色调 patch。

- 改动共 361 个 mask 像素（包括抗锯齿权重变化），范围 `x=1061–1080, y=38–97`。
- 现有 0.5 source px 内缩与抗锯齿保留，避免覆盖帽子和玫瑰。
- shader、Moon/Sun 曲线、人物受光、Atmosphere、Lamp、Leaves、Blink、Hair Motion 均无代码或参数变更。
- mask 与 Base 共用变形后 UV，8 个 motion ON 放大帧中未再次露出宽亮缝。

## 验收截图

- [04:43 红框局部 before / after](tower-final/gap-ab.jpg)
- [04:43 全图 before / after](tower-final/full-ab.jpg)
- [注册区域 Overlay](tower-final/receiver-overlay.png)
- [开启动作的接缝连续帧](tower-final/motion-gap.jpg)
- [Dawn / Noon / Dusk / Night](tower-final/four-phases.jpg)
- [全天 21 个重点时刻，全图及 Moon 角度](tower-final/24h-full.jpg)
- [全天塔身近景](tower-final/24h-tower.jpg)
- [夜间审查](tower-final/night-review.jpg) / [晨间审查](tower-final/dawn-review.jpg) / [傍晚审查](tower-final/dusk-review.jpg)
- [全动画 Play 截图序列](tower-final/play-24h.jpg)

## 24H 判断

| 时段 | 实际观察与判断 |
| --- | --- |
| 20:00–00:30 | 月亮自一侧升高，塔面保持同一方向响应；冷暗环境与局部暖灯分工清晰。中线附近过渡柔和。 |
| 00:30–03:30 | 左侧接收渐增，右侧渐弱；保留上轮连续交接，没有两小时迟滞。 |
| 03:30–05:00 | 左面轻微主受光，右面保留环境亮度；帽旁与发隙没有独立亮块，红框宽亮缝已消除。 |
| 05:00–06:30 | 月光逐渐退出，晨光与天空接替；没有因本轮修复新增跳变或局部补光。 |
| Dawn / Noon | 晨间较冷柔，中午清晰中性；本轮与基线逐像素相同。 |
| Dusk / Night | 暖夕照逐渐转为冷月环境，暖灯保留局部作用；本轮锚点与基线逐像素相同。 |

对当前固定插画的艺术化昼夜模型，方向、明暗和冷暖关系合理，可以进入总集成。它仍是基于原画与 Normal 的二维受光，不是天文模拟或真实三维投射阴影；原画两面固有色差仍然保留。放大图可见约一个 source px 的柔化边缘，属于原画景深/抗锯齿过渡，没有再形成整条额外亮缝，正常 Hero 尺寸下不构成冻结阻碍。

## 测试

- `pnpm typecheck`、`pnpm build` 通过。
- `python scripts/audit_tower_final.py`：00:00–24:00 每 15 分钟渲染，另加入 04:43 等重点时刻，共 98 个不同时间值；保存 21 个重点时刻截图。所有重点时刻 Face 与修复矩形外最大像素差为 0；Dawn/Noon/Dusk/Night 全图差为 0；00:00/24:00 差为 0；WebGL 错误为 0。
- `python scripts/audit_tower_final.py --play`：全部动画开启，实际运行 68.17 秒，按现有 60 秒/天速度跨过完整 24H 和午夜；无 JS/WebGL 错误。
- 现有 `validate_atmosphere.py --mode regression` 通过：context restore、4K/mobile resize、reduced-motion、hidden tab、static quality、Blink/Motion/Leaves/Lamps/Post，以及早晚过渡采样。
- 无新纹理、sampler、draw call、RAF；替换现有同尺寸 mask，运行时成本不增加。未重复进行 GPU 性能基准。
- [固定截图审查数据](tower-final/audit-stats.json)、[Play 数据](tower-final/play-24h.json)、[关键回归](tower-final/regression-stats.json)。

## 下一阶段建议

项目检查点已将下一阶段命名为 **R7.4 — Final Integration**。建议范围是冻结资产与参数、梳理可迁移 Hero 组件接口、收口加载/静态降级与质量档、复查桌面/移动端/4K 和生命周期，再准备 VuePress 2 / vuepress-theme-plume 首页接入。此为下一阶段建议，本轮未实施。