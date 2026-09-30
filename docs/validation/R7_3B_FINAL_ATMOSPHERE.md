# R7.3B — Final Atmosphere / Overall Polish

基线：`eb3a488`（包含已验收 R7.3A 与连续 Blink）。本轮为 **visual polish frozen candidate**，等待人工验收；未进入 R7.4。

## 范围与显示链

Character Lighting、Sun/Moon、Motion、Blink、Leaves、Lamp 光照/时序/遮罩、Base/Normal、Sky RGB/时序/接缝资产均未改。Scene RGB 的原有计算未改；新增内容只写显示元数据。

链路：原有 Scene HDR → 原有四级 Bloom → ACES → 原有 R6 grading → 克制远景空气层次 → 微量 final grading。没有新增 GPU pass、全分辨率模糊或 RAF。

- 新增固定注册的 `public/assets/hero/atmosphere/scene-depth.png`，1672×941。人工多边形限定远景建筑/树线与回廊深处，保护完整人物、近处柱体藤蔓、栏杆及下部场景；生成脚本无颜色阈值。
- Scene 使用同一 Motion 后的 `sampleUv` 取 depth，再扣除实际 Sky alpha 与现有 Character coverage。不会在天空上画块状阴影或在人头周围建立径向亮雾。
- 原有 Bloom gate 从 R8 扩为 RG8：R 为 Bloom eligibility，G 为远景权重；复用原 MRT 和 final Post。新增一个 source sampler，共使用 15 个，小于 WebGL2 保证的 16 个。
- 所谓空气层次是微量背景颜色/对比/饱和度压缩，不是真实深度、体积雾或景深模糊。
- Debug 保留 `Atmosphere on/off`；`Haze on/off` 和 `Final Grade on/off` 放在折叠项中。关闭不改变时间/动画/Renderer 生命周期。

## 最终参数

修改文件：`src/config/atmosphere.ts`、`post.ts`、`hero.ts`；`LivingHero.vue`、`HeroCanvas.vue`、`DebugPanel.vue`；`BaseRenderer.ts`、`PostPipeline.ts`；`hero.frag.glsl`、`post.frag.glsl`；depth 资产/生成脚本；新增 Atmosphere/冻结基线验证脚本、四份已有回归脚本的基线/连续 Blink 适配，以及本记录/阶段 checkpoint。具体灯/人物/动画配置未变。

所有参数复用 R6 `postTimeWeights` 的连续 hold/transition windows；未改原有 Post 数值或时段曲线。

| 时段 | 最大远景混合量 | 远景 saturation | Bloom 原强度倍率 | 微量 final grading |
| --- | ---: | ---: | ---: | --- |
| Dawn 06:30 | 4.5% | 0.975 | 0.75 | saturation 0.996，红/蓝 tint 0.998/1.002 |
| Noon 12:00 | 0 | 1.000 | 1.00 | identity，保持基线 |
| Dusk 17:30 | 3.5% | 0.985 | 0.75 | saturation 1.003，红/蓝 tint 1.003/0.999 |
| Night 22:00 | 5.0% | 0.955 | 1.00 | saturation 0.990，红/蓝 tint 0.997/1.003 |

远景目标色分别为 Dawn `(0.60,0.65,0.72)`、Dusk `(0.57,0.43,0.36)`、Night `(0.15,0.18,0.23)`；实际混合量还乘局部 depth。Night 不用亮白雾，不抬 exposure/ambient。近景层次与人物主光继续来自冻结 Scene。

Bloom 收口通过现有 gate 实现：非 Noon 时，人物作为 Bloom 来源减少 90%，灯 influence 内的反射表面来源减少至多 85%，玻璃 emissive 仍保留。灯体与墙面 Scene illumination 不变。Dawn/Dusk 的 Bloom 再乘 0.75；Night 保留原灯光 Bloom 强度。不会用 Bloom 承担局部灯照明。

参考 [KumengScreen Post shaders](https://github.com/buger404/KumengScreen/blob/main/lib/post-shaders.ts) 与 [Post settings](https://github.com/buger404/KumengScreen/blob/main/lib/post-settings.ts)，仅对照 HDR/Bloom/ACES/grading 的组织关系，没有复制具体参数。

## 固定截图与动态验收

[四时段全图 A/B](r7-3b-final/four-phases-ab.jpg)（左 OFF，右 ON） · [四时段成图](r7-3b-final/four-phases.jpg) · [时间对照](r7-3b-final/time-contact.jpg)

- [Dawn](r7-3b-final/dawn.png)：远景稍柔，脸部与头发不重打光；[头部 A/B](r7-3b-final/dawn-head-ab.jpg)。
- [Noon](r7-3b-final/noon.png)：全图 ON/OFF **逐像素一致**。
- [Dusk](r7-3b-final/dusk.png)：收掉部分亮雾，暖光仍来自原 Scene；[头部 A/B](r7-3b-final/dusk-head-ab.jpg)。
- [Night](r7-3b-final/night.png)：冷远景/冷月人物/左侧暖灯关系保留；[远景 A/B](r7-3b-final/night-far-scene-ab.jpg)、[头部 A/B](r7-3b-final/night-head-ab.jpg)、[灯区 A/B](r7-3b-final/night-lamp-ab.jpg)、[Bloom OFF](r7-3b-final/night-bloom-off.png)。未观察到新黄圈、白袖发光或运动边缘亮雾。
- [depth 注册范围](r7-3b-final/depth-registration.jpg)：青色仅为辅助资产范围图；运行时额外扣除 Sky/Character，不会覆盖图中天空。

全系统 ON 的 25 秒实际渲染预览：[Dawn](r7-3b-final/dawn-25s.mp4) · [Dusk](r7-3b-final/dusk-25s.mp4) · [Night](r7-3b-final/night-25s.mp4)。截图采集后按正常时间重采样到 30fps，**不是原生固定 30fps capture**；不改变播放速度。连续帧对照：对应 `*-motion-contact.jpg`。

## 基线、连续性与回归

真实 `eb3a488` 源码另起只读对照服务，而非拿数轮前截图硬比。Atmosphere OFF 的四时段与该提交 **最大 RGB 差均为 0**；Noon ON 亦为 0。首次检查发现关闭时微量浮点舍入，已让 identity 分支直接跳过新增颜色计算，最终对照完全一致。

- build / typecheck / `git diff --check`：通过。
- Blink/Normal 注册 validator：通过，眼区外变化 0；冻结资产未修改。
- Character coherence：Blink、Breathing、Hair、Lamp、Leaves、Post、hidden tab、static quality、resize、reduced-motion 均通过；灯对人物区域 RGB 差 0。
- Lamp validator：以当前 frozen commit 代替历史 R6 图片，通过三面玻璃/金属分隔、灯区域、连续启停、关灯基线、Bloom OFF 和动画共存检查。
- Leaves validator：25 秒 Noon/Dusk/Night，明显遮眼事件均为 0；hidden/reduced/static/resize 与连续 Blink 共存通过。
- Post validator：以当前 frozen commit 检查 Post OFF、Scene/Post 接续、Bloom 局部性及夜间新增漂移，通过。
- Time controller：以当前 frozen commit 替代历史 R3 图片，preset/manual/play/pause/realtime、hidden/reduced 与 wrap 通过。新增 `--angle d3d11` 可避免软件渲染下加速时钟检查过慢。
- 00:00/24:00 固定图最大 RGB 差 0；04:30–07:00 与 16:30–20:00 逐 10 分钟图像检查通过，相邻平均差最大 10.556 / 5.063。该数值是原场景正常晨昏变化，不等同于零亮度变化。
- Atmosphere 在 20:00–05:00 为稳定 Night 参数；未引入深夜重新变亮曲线。独立 Moon direction 仍遵循原模型，夜间人物受光会自然移动。

验证脚本在传入 `--baseline-url http://127.0.0.1:5174` 时使用另行服务的当前冻结源码；不传则保留原历史检查语义。详细数值见 `r7-3b-final/*-stats.json`。

## 性能与稳定性

Windows Edge / ANGLE D3D11 / **RTX 5070 Ti**，Night，Motion ON、Blink/Leaves OFF 的专项 GPU timing：

| 视口 | frozen eb3a488 GPU 中位 ms | 新版 ON GPU 中位 ms | 新版 ON P95 ms |
| --- | ---: | ---: | ---: |
| 1920×1080 | 0.210 | 0.220 | 0.223 |
| 2560×1440 | 0.342 | 0.358 | 0.369 |
| 3840×2160 | 0.726 | 0.763 | 0.964 |

每帧仍为 10 draws。Motion-only 观测约 26.67 次绘制/秒，OFF/ON 一致（既有 ≤30fps 调度，非显示器 FPS）。GPU timer 覆盖 Scene 至最终 Post；本机结果不代表低端集显。4K 新增元数据约 8.3MB，加固定源纹理约 6.3MB，未新增全分辨率 RGBA 后期目标。截图：[4K](r7-3b-final/night-3840x2160.png)、[mobile DPR3](r7-3b-final/night-mobile-dpr3-reduced.png)；DPR3 被现有 cap2 限制至 780×1688。

全系统与 24H Play 连续运行 **610.8 秒**：页面错误 0、WebGL error 0，累计约 119 万次 draws。JS heap 8.6–31.8MiB，观测到 GC 回落；未做长期泄漏证明。context lost → fallback → restore、1080/1440/4K/mobile resize 均无 GL 错误。[10 分钟后截图](r7-3b-final/night-after-10min.png) 与 `long-run.json` 已保留。

## 已知限制与结论

- 效果有意克制：Night 全图平均 RGB 变化约 0.138，主要在远景；不宣称重做光照或产生体积雾。
- 固定 depth 只适用于当前注册构图，未来替换 Base 必须重画；不是通用深度估计。
- Dawn 黑块仍按此前用户决定单独监控，本轮未复现、未用 haze 掩盖，不能记作已修复。
- 没有新增 vignette/grain/DOF/god rays，也未改灯/人物受光来配合 Post。

建议将本版作为 **R7.3B 冻结候选**交人工验收；验收通过后再冻结。当前停止，不进入 R7.4。
