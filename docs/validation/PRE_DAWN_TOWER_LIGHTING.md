# Pre-Dawn Tower Lighting — 凌晨塔身大面受光收口

日期：2026-10-01。对照基线：`a0e34e5`（v2）。本轮仅处理人物左侧背景塔身的凌晨接收归属和月光塑形，等待人工验收。

## 根因

1. 旧 `architectureReceiver` 的该塔注册框右边界为 x=1056，帽子左上方背后的实际石材延伸至约 x=1075。遗漏的石材走了另一条接收链路。
2. 原有石材颜色筛选及 `foregroundReceive` 排除将一整块可见塔身切成了零碎接收区域。头发间隙里的背景又可能落入 motion B 驱动的 accessory/character 接收。B 是运动覆盖缓冲，并非可靠的建筑/人物材质分割。
3. Base 自带右侧较亮的绘画色差。凌晨月光虽然已经偏向画面左侧，原有过宽 wrapped receive 和较弱的石材方向响应仍不足以建立左侧主亮面；少数归属错误的像素反而显得更亮。

[旧接收归属诊断](pre-dawn-tower/diagnosis.jpg)展示 04:36 的成图、建筑覆盖、character receive 和 Moon receive。

## 修正方法

### 固定注册的完整石材覆盖

新增 `public/assets/hero/lighting/tower-receiver-mask.png`，1672×941，与 Base 同坐标。

- 覆盖整块可见塔身，包含帽子旁遗漏的石材、窗洞及发丝之间真正露出的背景。
- 排除帽子、玫瑰、头发、藤叶和袖子；边界只作约半个 source px 的向内收口。
- 这是材质归属资产，没有存储亮度、冷色涂层或两处亮斑的压暗值。
- `scripts/paint_tower_receiver.py` 保存固定轮廓；离线以冻结 Base 的颜色和连通组件辅助排除前景。运行时不做 CV 或颜色阈值计算。
- 与 Base 一样使用 `sampleUv`，继续随既有 Breath → Head → Hair 坐标链采样，没有改变运动幅度。

[注册覆盖叠图](pre-dawn-tower/receiver-overlay.png)。本轮没有重画 Base、Normal 或已冻结的天空接缝素材。

### 整个塔身共享 Moon 向量

在现有 Scene Lighting 中，注册石材具有实际受光归属的优先权，避免再接受错误的 character/accessory 材质增益。该覆盖只替换石材的 radiance，**不改 character 接收值或 Atmosphere/Bloom 的 metadata**。

- 左面 Normal：`normalize(-0.70, 0, 0.71)`；右面：`normalize(0.71, 0, 0.70)`，构成近似正交的大面。
- 塔角 x=990–1004 内平滑插值法线，避免生硬的黑亮分界。
- 两面均计算 `dot(towerNormal, moonDirection)`，通过 `smoothstep(-0.30, 1.00, facing)` 得到柔和接收。
- 该塔的局部 Moon key 系数为 0.48，乘原有 `moonHeightGain`；冷色仍为 `(0.35, 0.51, 0.82)`。原有环境光 `ambientColor × ambientIntensity × 0.88` 保留，让背面仍有读图能力。
- 方向接管权重为 `smoothstep(0.40, 0.60, -moonDirection.x) × skyNight × moonHandoff`。随着月光偏左平滑接入，随原有 Dawn 交接退出，没有按时刻硬切，也没有改变 Moon/Sun 曲线。
- 保留共享 `upperSceneFactor`。灯光仍在这之后走原来的链路，没有调整 Lamp source / influence / timing。

旧建筑逻辑仍用于其他塔楼和时段；本轮没有全局删除它。**在这段时间、这块注册石材上，颜色筛选造成的碎片归属和错误人物材质补亮被替换**。不是在两处红框上分别盖暗色，也没有全局压暗 Night。

## 固定时刻验收

同一 1672×941 实际 WebGL2 画面、DPR 1；静态对照关闭运动，其他显示参数相同。表中的亮度比是固定左右石材 ROI 内、只取全覆盖像素的显示 RGB 平均值，用于辅助判断，不是照度测量。

| 时刻 | Moon 方位 / 高度 | 主亮面与过渡 | 左 / 右显示亮度比 |
| --- | --- | --- | --- |
| [03:30](pre-dawn-tower/03h30.jpg) | 137° / 33° | 左侧大面较亮，右侧保留柔和环境光 | 1.142 |
| [04:00](pre-dawn-tower/04h00.jpg) | 141° / 27° | 左侧主亮面连续 | 1.210 |
| [04:30](pre-dawn-tower/04h30.jpg) | 144° / 19° | 左侧主亮面成立，右侧两处碎亮不再走异常接收 | 1.163 |
| [04:36](pre-dawn-tower/04h36.jpg) | 144° / 18° | 用户问题时刻，左面较亮，右侧间隙与同面石材一致 | 1.147 |
| [05:00](pre-dawn-tower/05h00.jpg) | 145° / 12° | 低月光减弱，左面仍略亮 | 1.106 |
| [05:15](pre-dawn-tower/05h15.jpg) | 145° / 12° | 左面轻微受光，开始交接 | 1.139 |
| [05:30](pre-dawn-tower/05h30.jpg) | 145° / 12° | 左面仍略亮，接管逐渐退出 | 1.126 |
| [06:00](pre-dawn-tower/06h00.jpg) | 144° / 12° | 太阳链路逐渐主导，恢复既有 Dawn 面关系 | 0.674 |
| [06:30](pre-dawn-tower/dawn.jpg) | 142° / 12° | 本轮覆盖退出；与基线 Dawn 逐像素一致 | 0.626 |

- [全部时刻全景](pre-dawn-tower/pre-dawn-full-times.jpg)
- [全部时刻塔身近景](pre-dawn-tower/pre-dawn-tower-times.jpg)
- [04:36 全图 before / after](pre-dawn-tower/04h36-full-ab.jpg)
- [04:36 塔身 before / after](pre-dawn-tower/04h36-tower-ab.jpg)
- [去除 Base 色差后的接收能量 before / after](pre-dawn-tower/receiving-energy-ab.jpg)
- 无损原截图：[before](pre-dawn-tower/04h36-before.png) / [after](pre-dawn-tower/04h36-after.png)

04:36 的两处红框在归一化接收图中，从约 108.33 / 98.96 下降到同一右侧石材面的 57.33；左面接收图的标准差为 0。左侧亮面由整面的法线与 Moon 点积产生，不随帽子/头发距离增亮。

## 连续性与隔离

`scripts/audit_pre_dawn_tower.py` 用 Vite 的测试路由分别加载基线 shader / 当前 shader；测试替换不进入产品。统计在原始截图上计算，JPEG 仅用于交付浏览。

- 02:00–04:00 每 5 分钟采样，整块注册塔身相邻平均 RGB 变化最大 1.932；接管平滑。
- 05:30–06:30 每分钟采样。基线最大相邻变化 1.499，新版 1.489；本轮修正差量自身最大相邻变化 0.486，没有放大原有太阳升起过渡。
- 所有验收时刻 Face 实心覆盖区 RGB 差为 0；character metadata 全图差为 0。
- 覆盖外最大差不超过 1/255。20:00、22:00、02:00 仅出现单个像素、单通道 1/255 的 shader 量化差；Dawn、Noon、Dusk、00:00 均完全一致。
- 00:00 / 24:00 完全一致。

[原始统计](pre-dawn-tower/audit-stats.json)。此统计和实际近景共同验收，不能仅凭数值宣称美术已获用户认可。

## 工程与性能

- `pnpm typecheck`：通过。
- `pnpm build`：通过。
- `python scripts/audit_pre_dawn_tower.py`：通过。
- `python scripts/validate_atmosphere.py docs/validation/pre-dawn-tower/regression --mode regression`：通过。覆盖 context restore、1920/2560/4K/mobile resize、DPR 3、reduced motion、hidden tab、static quality、Blink、Breathing/Head/Hair、Leaves、Lamp 与 Post smoke test，以及 Dawn/Dusk 连续性。
- [关键回归统计](pre-dawn-tower/regression-stats.json)。这些是 smoke / 生命周期检查，没有重验收被冻结系统的美术。
- 增加一张静态纹理、一次 shader 采样，无新 pass、无新 RAF。当前 fragment sampler 数达到 WebGL2 最低保证的 16 个，实际设备编译及 context restore 均无 GL error。
- 新 PNG 约 8.6 KiB；按现有 RGBA 上传约占 6 MiB 显存。
- 本机 Edge/ANGLE D3D11、1920×1080、04:36、Motion ON、Post/Atmosphere ON 的 6 秒 A/B：绘制均为 10 次/帧，观察频率 26.67 → 26.66 fps，GPU 中位 0.244 → 0.245 ms。仅作该设备短时检查，非所有设备的性能保证。[性能记录](pre-dawn-tower/performance-stats.json)。

## 改动文件与保留限制

- `src/shaders/hero.frag.glsl`：塔身材质优先接收及连续凌晨大面 Moon 响应。
- `src/engine/renderer/BaseRenderer.ts`：静态 texture 生命周期。
- `src/config/hero.ts`、`src/components/LivingHero.vue`、`src/components/HeroCanvas.vue`：注册资产路径、异步加载、尺寸校验及传递。
- `public/assets/hero/lighting/tower-receiver-mask.png`、`scripts/paint_tower_receiver.py`：固定覆盖及生成依据。
- `scripts/audit_pre_dawn_tower.py`：本轮针对性验证。
- 本记录、验收图与 `docs/STAGE_CHECKPOINT.md`。

保留原画中的窗洞、石材明暗笔触和景深；不会把塔面抹成无细节平板。局部抗锯齿边界仍是保守注册，建议人工重点检查玫瑰边缘与发丝间隙。人物、Atmosphere、Leaves、Blink、Hair Motion、Lamp、全局时间曲线及其参数均未修改。到此停止，等待人工验收。
## 人工反馈收口：阴影过重 → 暗面柔化

2026-10-01，以上 `77406ed` 版本被用户指出 04:15 塔身阴影过于显眼。本节是当前结果；上面的参数、统计和截图保留作历史对照。

本轮生产代码只改 `src/shaders/hero.frag.glsl` 的塔身接收响应：

- 阴面接收不再降到零，改为 `mix(towerShadowFloor, 1.0, facingBand)`。这是整面 wrapped response，不是新增局部补光或压暗素材。
- `towerShadowFloor` 随原有 Moon 高度在 0.06–0.10 之间平滑变化；临近 Dawn 收敛，避免把右面又抬成主亮面。主光方向、Moon key 0.48、环境光、接管时间权重均未改。
- 塔角过渡由 x=990–1004 的 14 source px，扩大到 x=986–1012 的 26 source px。
- 固定塔身 mask、人物、Atmosphere、Lamp、Leaves、Blink、Hair/Breath Motion 和其他光照参数均未改；没有新增纹理、pass 或 RAF。

04:15 固定石材 ROI：暗面平均显示 RGB 从 53.360 提高到 60.361，约增加 13%；两面显示亮度差从 10.562 收到 3.754，约减少 64%。这是成图显示统计，不是阴影物理强度百分比。左侧仍略亮。

| 时刻 | 左 / 右显示亮度比（柔化后） |
| --- | --- |
| 03:30 | 1.021 |
| 04:00 | 1.067 |
| 04:15 | 1.062 |
| 04:30 | 1.049 |
| 04:36 | 1.045 |
| 05:00 | 1.038 |
| 05:30 | 1.071 |

验收：[04:15 塔身 before / after](pre-dawn-tower-softening/04h15-tower-ab.jpg)、[04:15 全图 before / after](pre-dawn-tower-softening/04h15-full-ab.jpg)、[03:30–Dawn 近景序列](pre-dawn-tower-softening/tower-times.jpg)。

`pnpm typecheck`、`pnpm build`、`scripts/audit_tower_softening.py` 和现有 Atmosphere/Character 生命周期回归通过。所有固定截图的 Face 与 mask 外像素差均为 0；Dawn / Noon / Dusk / 20:00 / 22:00 / 00:00 / 02:00 全图差为 0；00:00 / 24:00 一致。06:00 残余修正只在塔身覆盖内，最大 3/255，仍随原有交接退出。五分钟采样的塔身 Dawn 最大变化 7.370 → 7.302，没有放大过渡。

[本轮针对性统计](pre-dawn-tower-softening/audit-stats.json)、[关键回归统计](pre-dawn-tower-softening/regression-stats.json)。旧塔身 audit 的显示亮度比门槛从 1.05 调为 1.0，保留左侧主亮面方向检查；新增 softening audit 另要求 04:15 两面差值至少减少一半、暗面提高至少 10%，与本次人工反馈一致。

保留正常窗洞与原画材质笔触，不追求把建筑磨成均匀平板。到此停止，等待人工验收。