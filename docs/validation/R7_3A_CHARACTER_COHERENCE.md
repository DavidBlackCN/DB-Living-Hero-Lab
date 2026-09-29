# R7.3A — Character Coherence Pass

基线：`6321e0b`，当前 `v2`。本轮只整理人物运动和人物受光；Base-4、Normal v3、天空、灯、落叶、Post、Blink 素材与时间曲线均未改。

## 判断与实现

参考项目的 [motion / scene shader](https://github.com/buger404/KumengScreen/blob/main/lib/scene-shader.ts)、[painted lighting](https://github.com/buger404/KumengScreen/blob/main/lib/stylized-lighting.ts) 和 [daylight model](https://github.com/buger404/KumengScreen/blob/main/lib/daylight.ts) 使用共享呼吸节奏与同一方向光；本项目只借鉴组织原则，没有搬用坐标、遮罩或参数。

### Motion hierarchy

原先 head mass 的 X/Y 主要由 6.4s / 9.1s 周期推动，breath link 只有 0.12。现在 5.2s breathing phase 推动 head mass 的主纵向起伏与轻微横移，分别带约 0.20s / 0.28s 相位滞后。独立 6.4s / 9.1s 漂移降至 0.12/0.06（X）与 0.08（Y），避免头部像浮在肩上。身体仍使用原有呼吸形变与 4.8 source-px 上限；whole head、上段发丝、下段长发仍分别维持 1.8 / 3.0 / 5.2 source-px 的原有强度上限。上段发丝先继承头部 UV 位移，再叠加既有 secondary sway；下段长发轨迹不变。Blink 仍在共享 UV 后采样。

### Character Lighting chain

`shared Sun / Moon direction → broad Normal → painted receive → material gain → optional hair sheen`。

- Face Normal 的同材质过滤距离由 4 增至 7 source px。Moon 人物接收增加 11px broad Normal 外环采样，只在人物区域执行；不修改 Normal v3 素材。
- Night 的 Face 仍用同一个 Moon 向量，但降低其 Y 分量到 0.24，前向 Z 至少 0.85，并以更宽的 receive 曲线解释脸部。没有眼睛、脸颊或局部补光层。
- 删除 `characterMoonSide` 的屏幕 X 偏置。人物 Night 主体只由 filtered broad Normal 与 Moon direction 决定。
- Moon material gain 从 hair 1.40→1.27、clothing 1.26→1.20、vest 1.50→1.30、accessory 0.78→0.88；Face 保持 1.00。共享 receive 的极端明暗差略收窄，减少碎法线被材质倍率放大的痕迹。
- 删除沿左右发束和贴脸发丝单独叠加的 lunar ribbon。Night 只保留非常窄且低强度的 crown polish，强度 0.012；Day sheen 仍仅作材质收尾。`?hairSheen=off` 可做开发态 A/B，`?hairSecondary=off` 可检验只剩 body+head 的运动，均不进入正式 Debug UI。

没有新增局部 light/darken patch、材质遮罩或新光源；太阳/月亮方向与全天时间曲线未改。Noon 基线在静帧中像素一致，Dawn/Dusk 肉眼基本不变；Night 全画面平均 RGB 差约 0.8，人物主区域约 1.9，重点在平顺体块对比，不提高全局曝光。

## 验收素材

- [四时段整图 contact sheet](r7-3a-character/final/four-phase-contact.jpg)；单图：[Dawn](r7-3a-character/final/dawn.png) / [Noon](r7-3a-character/final/noon.png) / [Dusk](r7-3a-character/final/dusk.png) / [Night](r7-3a-character/final/night.png)。
- [Night 全图 before/after](r7-3a-character/final/night-before-after.jpg)、[人物全身 before/after](r7-3a-character/final/night-figure-before-after.png)、[Night 头发与脸 2×](r7-3a-character/final/night-head-before-after.png)、[Dawn 头部 2×](r7-3a-character/final/dawn-head-before-after.png)。
- 20s 正常速度 before/after（关闭 Leaves/Blink 以隔离人物运动）：[Noon](r7-3a-character/final/noon-before-after-20s.mp4) / [Night](r7-3a-character/final/night-before-after-20s.mp4)；20s 全组合（Leaves/Blink/Breathing/Hair/Lamps/Post）：[Noon](r7-3a-character/final/noon-20s-combined.mp4) / [Night](r7-3a-character/final/night-20s-combined.mp4)。另有 [Noon head+torso 20s](r7-3a-character/final/noon-head-torso-20s.mp4)、[secondary hair OFF 8s](r7-3a-character/final/noon-8s-secondary-off.mp4)、[motion region overlay](r7-3a-character/final/motion-regions.png)。
- [Night hair sheen OFF/ON](r7-3a-character/final/night-sheen-off-on-head.png) 与 [差异放大审查](r7-3a-character/final/night-sheen-difference-24x.png)。关闭 sheen 后头发仍靠 broad Normal 呈现主体体积；开关只轻微改变 crown。
- [00:00](r7-3a-character/final/night-00h.png) / [02:00](r7-3a-character/final/night-02h.png) / [24:00](r7-3a-character/final/night-24h.png)，00:00/24:00 像素一致。

## 回归与限制

`pnpm typecheck`、`pnpm build`、`python scripts/validate_hair_motion.py`、`python scripts/validate_lighting_detail.py` 通过。`scripts/validate_character_coherence.py` 检查四时段、Night 20s、Breathing/Hair/Blink、Lamp/Leaves/Post、hidden tab、reduced motion、static quality、resize、00:00/24:00 与晨昏 10 分钟连续性；[统计](r7-3a-character/final/stats.json)中最大相邻人物区域平均 RGB 变化为晨间 10.381、傍晚 5.099，没有离散阶跃。Night 灯光 A/B 的人物区平均 RGB 差为 0。

旧版 `validate_time_controller.py` 与 `validate_post.py` 的历史冻结像素基线分别是 R2B/R6，现有 R7.1/R7.2 项目在 Dawn 对比即失败；不能把这两个旧基线断言用作本轮结果。新 validator 针对当前分支验证时间和 Post 共存。

性能：未增加 RAF 或纹理资产。人物 Night shader 多 4 个 broad Normal tap，限于人物区域；开发态 Edge/SwiftShader 960×540 动画调试面板最近帧约 0.3–0.6 ms（CPU 提交时间，不代表 GPU 总耗时）。录制为 25 fps，原有 30 draw/s 动画上限维持。

已知轻微限制：Night 深色背心主要靠原画纹理保持可读，局部深褶仍偏暗；没有为此叠加提亮补丁。固定 2D Normal 与绘制阴影仍不能表达真实 3D 自遮挡。待人工验收后再决定是否冻结人物系统；不进入 R7.3B。
