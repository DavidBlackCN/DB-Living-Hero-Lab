# R7.3A.2 Long-hair light balance

基线：`b6eb94a`。针对实机标注的 Dawn 画面左侧落发暗块与 Night 画面右侧落发浅亮面，只调整现有 Character Lighting Core 的头发材质响应。Base、Normal、运动遮罩、太阳/月亮方向与时段曲线保持原样。

## 判断与修正

- Dawn 暗块在关闭 Directional Shading 后仍存在：原画深色发束叠加低角度的 diffuse / band，并非 Hair sheen。对现有头发材质提高晨光最低接收、柔化背光 band，再沿原有左落发软权重恢复少量棕色。面部和白袖不走这条响应。
- Night 右侧浅亮面受 Moon directional response 影响，关闭 Hair sheen 几乎不变。将头发 Moon receive 向中性值收拢，Hair gain `1.22 → 1.08`，沿原有右落发软权重收窄过亮的体块。月光方向与其他角色材质仍共用原向量。
- 尝试过更窄的固定注册发束 mask；放大图暴露出发束中间的亮条，已撤回。最终沿用现有 RG 软权重，不增加运行时贴图或采样。

## 对照

- Dawn [局部 2×，左旧右新](r7-hair-light-balance/final/dawn-before-after-2x.png)；Night [局部 2×，左旧右新](r7-hair-light-balance/final/night-before-after-2x.png)。静态拍摄均关闭 Leaves、Blink、Breathing、Hair Motion，保持相同 2560×1440 视口和 Lit/Post 状态。
- 四时段全图：[Dawn](r7-hair-light-balance/final/dawn-final.png) / [Noon](r7-hair-light-balance/final/noon-final.png) / [Dusk](r7-hair-light-balance/final/dusk-final.png) / [Night](r7-hair-light-balance/final/night-final.png)。[Dawn 旧图](r7-hair-light-balance/before/dawn-final.png) / [Night 旧图](r7-hair-light-balance/before/night-final.png)。
- Dawn 暗处棕色发束更可读；Night 右侧浅亮面收敛，深浅仍沿发束分布。发丝自身的明暗和原画笔触保留。Noon / Dusk 全图检查未见新的脸部、服装或背景异常。
- 与 `b6eb94a` 的同尺寸固定帧逐像素比较：Noon、Dusk 最大 RGB 差均为 **0**；Dawn、Night 全图平均绝对 RGB 差为 0.300 / 0.184。改动集中在两侧头发，四时段其余观感保持稳定。

## 回归

`pnpm typecheck`、`pnpm build`、`validate_hair_motion.py`、`validate_lighting_detail.py`、`validate_character_coherence.py --final --seconds 2` 均通过。[回归数据](r7-hair-light-balance/regression/stats.json)记录 00:00/24:00 最大 RGB 差 0；04:30–07:00 与 16:30–20:00 相邻十分钟人物区域平均 RGB 最大变化为 10.437 / 5.102。Blink、Breathing、Hair、Leaves、Lamps、Post、隐藏页、静态质量、缩放与 reduced motion 检查通过。

固定 2D 原画里长发与背景交错，极细发尾仍保留原有轻微明暗不均；本轮避免扩张遮罩造成树叶染亮。结果待人工验收，不进入后续阶段。
