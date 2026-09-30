# R7.3B final fix — 四时段空气层次与 Face coverage

基线 `f56cd9f`，本轮等待人工验收。最新要求明确需要 Noon 也有 Atmosphere 开关差异，取代上一轮 Noon ON/OFF 必须一致的约束。

## Atmosphere 收口

继续使用现有固定注册 scene depth、原 MRT 元数据和 final Post；没有新增 pass、sampler、模糊、RAF 或人物局部效果。仅调整背景空气混合量、远景饱和度和空气目标色；全局曝光、final grading、Bloom 强度与保护参数未改。

| 时段 | 最大空气混合量（仍乘 depth） | 远景 saturation | 空气目标 RGB | 可见作用 |
| --- | ---: | ---: | --- | --- |
| Dawn 06:30 | 9% | 0.950 | 0.60 / 0.65 / 0.72 | 清冷远景稍退后，保留近景清晰度 |
| Noon 12:00 | 12% | 0.960 | 0.67 / 0.68 / 0.70 | 中性空气压缩远景对比，不改变人物主光 |
| Dusk 17:30 | 16% | 0.935 | 0.60 / 0.45 / 0.38 | 暖远景层次更完整，避免新增橙色全屏滤镜 |
| Night 22:00 | 20% | 0.920 | 0.21 / 0.235 / 0.27 | 冷暗远景后退，与原暖灯回廊形成更清楚的空间层次 |

以上是 depth=1 时的上限，不是全画面的混合比例。Sky/Character coverage 仍从原 depth 路径扣除；时段仍复用连续 `postTimeWeights`，未重写曲线。远景固定 ROI 的平均 RGB OFF/ON 差分别为 7.793 / 6.567 / 5.203 / 5.961；数值仅作变化证据，最终自然度仍需人工判断。

## 脸部脏影根因与清理

根因是现有 R5 material mask 的 Face R 通道按皮肤颜色筛选：`red-green` / `green-blue` 条件把原画浅色鼻部高光、下巴边缘排除。这些像素在统一 character receive 中漏回 architecture 分支，低光下显成灰鼻斑和细碎脏下巴；并非需要增加 AO 修正或局部补光。

修复保留原有脸部多边形、羽化、注册与 upper boundary，仅移除面中/下脸的 pigment gate。上脸边界仍拒绝暗刘海。没有增加鼻子/下巴 patch，没有改 Face directional 模型、太阳/月光方向、Normal 或 Base。

- 鼻部 `(1155,245)`：Face R 47 → 255；下巴 `(1150,290)`：18 → 211。
- 4209 个 R 通道像素改变，范围 `(1072,182)`–`(1228,296)`；Hair G / Iris B / unused A 逐字节不变。
- 实机 A/B 用请求替换旧 material asset，保持相同 shader、Lighting、Post，并关闭 Atmosphere，只隔离 Face coverage。鼻部灰斑与下巴细碎脏影明显改善；原画温和的下巴到脖颈体积阴影保留。
- 本轮 Atmosphere OFF 使用修正后的 Face coverage，因此不再宣称它与 `f56cd9f` 整图逐像素一致。

## 验收图

- [四时段 Atmosphere OFF / ON](r7-3b-final-fix/four-phases-ab.jpg)：每行左 OFF、右 ON，双方均使用修正 Face coverage。
- [四时段全图](r7-3b-final-fix/four-phases.jpg)：[Dawn](r7-3b-final-fix/dawn.png) / [Noon](r7-3b-final-fix/noon.png) / [Dusk](r7-3b-final-fix/dusk.png) / [Night](r7-3b-final-fix/night.png)。
- [四时段头部近景](r7-3b-final-fix/four-heads.jpg)：[Dawn](r7-3b-final-fix/dawn-head.png) / [Noon](r7-3b-final-fix/noon-head.png) / [Dusk](r7-3b-final-fix/dusk-head.png) / [Night](r7-3b-final-fix/night-head.png)。
- Face 根因隔离对照：[Dawn 4×](r7-3b-final-fix/dawn-face-coverage-ab.jpg) / [Noon](r7-3b-final-fix/noon-face-coverage-ab.jpg) / [Dusk](r7-3b-final-fix/dusk-face-coverage-ab.jpg) / [Night 4×](r7-3b-final-fix/night-face-coverage-ab.jpg) / [Face R 通道](r7-3b-final-fix/face-mask-ab.jpg)。
- [Night 同 Post 全图 coverage A/B](r7-3b-final-fix/night-coverage-full-ab.jpg)；[时段连续性对照](r7-3b-final-fix/time-contact.jpg)。
- 远景 Atmosphere A/B：[Dawn](r7-3b-final-fix/dawn-far-scene-ab.jpg) / [Noon](r7-3b-final-fix/noon-far-scene-ab.jpg) / [Dusk](r7-3b-final-fix/dusk-far-scene-ab.jpg) / [Night](r7-3b-final-fix/night-far-scene-ab.jpg)。

## 验证与范围

通过：`pnpm typecheck`、`pnpm build`、Blink/Normal validator、Atmosphere stills/regression、Face coverage isolation audit。00:00/24:00 最大 RGB 差 0。04:30–07:00、16:30–20:00 逐 10 分钟连续性检查通过；相邻平均变化最大 10.352 / 5.015，与原晨昏变化一致，未新增硬切。

Character coherence smoke 覆盖 Blink、Breathing/Head/Hair、Leaves、Lamps、Post、hidden tab、static quality、resize、reduced motion；context restore 和 1080p/1440p/4K/mobile resize 通过。Face 修复对灯区最大 RGB 差 0；灯开关对人物区域平均差 0。详见本目录 `stills-stats.json`、`face-audit-stats.json`、`regression-stats.json`。

性能结构未变：固定 texture 数量、draw/pass 数、DPR 与按需绘制机制沿用上一轮；本轮没有重复 10 分钟长测或 GPU benchmark，先前数据见 R7.3B 记录。本轮静态与生命周期回归通过不等于重新测得相同 GPU 时间。

修改源码/资产：`src/config/atmosphere.ts`、`scripts/paint_material_mask.py`、`public/assets/hero/material/material-mask.png`；验证：`scripts/validate_atmosphere.py`、`scripts/audit_atmosphere_final_fix.py`；另更新本记录、checkpoint 与验收截图。

未改 Motion、Blink、Lamp、Leaves、Base、Normal、Sky 接缝修复资产。仍是固定景深辅助资产，不是真实体积雾；原画自然的颈部投影并非本次要消除的脏影。用户此前暂缓的 Dawn 天空黑块仍单独待确认，本轮未标记修复。完成后停止等待人工验收，不进入后续阶段。
