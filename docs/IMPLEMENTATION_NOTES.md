# Implementation notes

Vue 只管理容器、生命周期、调试状态和质量选择。`src/engine/` 是普通 TypeScript，不依赖 Vue；GLSL 单独存放。未来迁入 VuePress 时复制 engine、shaders、config 与已验收资产，并由目标组件重新绑定 Canvas 生命周期。

`HeroCanvas` 在挂载后加载 Base，验证真实尺寸，再建立 WebGL2 context、shader、texture 和 quad。ResizeObserver 触发按需重绘；卸载时释放资源。context lost 时显示底层 `<img>`，restored 时重新初始化。页面在 Canvas 准备好前始终显示同一 Base 图片，避免黑屏。

Blink v1 与整图生成重试 v2 的差异均遍布全画面，整图路线已终止。验证记录见 [`validation/BLINK_V1_VALIDATION.md`](validation/BLINK_V1_VALIDATION.md) 和 [`validation/BLINK_V2_FULL_FRAME_RETRY.md`](validation/BLINK_V2_FULL_FRAME_RETRY.md)。`scripts/extract_blink_eyes.py` 从 v1 裁出两个带 5 px 羽化的 RGBA 眼部图，区域记录在 `src/config/hero.ts`。`BlinkLayer.vue` 只将它们按 Artwork Layout 贴到 Base 上；`BlinkTimeline.ts` 管自动随机间隔、预览脉冲和后台暂停。Canvas 和底层 `<img>` 始终使用同一 Base，不会再因 Blink 重建 WebGL 纹理。眼区外的合成结果与 Base 完全一致。

`layoutArtwork` 统一算 cover/contain；默认 Auto 在 viewport 宽高比低于 0.9 时选 contain，其他情况选 cover。UV 与 Source Pixel、CSS Display 坐标转换都在同一模块。GLSL 用相同布局给 quad 定位。UV 定义为左上原点。Canvas 像素用受限 DPR（默认 2）缩放。cover 允许超出 viewport 的裁切，contain 留出背景边。

`auto` 在 reduced motion 下仍使用按需绘制的 WebGL Lit，以保留真实时钟驱动的光照和天空；`static` 始终静态；`balanced` 可用于强制检查 WebGL。面板记录上次绘制耗时。Leaves 有独立的限帧 RAF，`visibilitychange` 在后台停止并在恢复时重置计时。reduced motion 无论 Quality 是否为 balanced 都关闭 Leaves。

Leaves 的 `LeafField` 不依赖 Vue，使用 Canvas 2D Alpha Blend 绘制四张 PNG，职责包含纹理加载、粒子状态、共享风、resize、暂停和销毁。`LeavesLayer.vue` 只桥接生命周期与活动数量。覆层裁到 Artwork 在 viewport 中可见的矩形；粒子内部位置为该矩形的归一化坐标，速度以 CSS px/s 计，在 resize 后继续运动。覆层在 Base WebGL 或静态 `<img>` 之上，关闭 Base Renderer 不影响 Leaves 开关。移动端降低数量，静态和 reduced motion 移除整个覆层。

Normal 技术 v1 用 `scripts/generate_normal.py` 对 Base 亮度做 3 px / 16 px 模糊、梯度计算和单位向量编码，生成完全同尺寸、逐像素注册的 RGB 图；约定 R 向右、G 向下、B 朝向观察者。`HeroCanvas` 验证 Normal 尺寸并加载第二张 WebGL 纹理。Debug 的 Normal map 显示原始编码，Test Light 以角度滑杆改变方向，着色器对 Base 施加小幅相对亮度响应；默认 Base 视图不受影响。测试视图隐藏 Blink，避免局部眼图与测试光照混合。此资产是管线与方向验证用的浅浮雕法线；亮度边缘会混入原画阴影，不应直接视为最终物理表面结构。Runtime Lighting 还需人工修正面部、头发、衣料等语义区域，确定光照范围／色温／遮挡，并做桌面与移动端性能和观感验收。

Normal v2 在 `scripts/generate_normal_v2.py` 离线生成，以冻结 Base 和 v1 为输入：先平滑并衰减 v1 高频，再用少量内存中的多边形与颜色条件提示修正脸／皮肤、两侧发量、衣物、石柱／栏杆及天空。输出仍是单张与 Base 严格注册的 RGB PNG，页面配置已从 v1 指向 v2；没有引入运行时 Masks、正式 24h 光照或新的动画模块。详见 [`validation/NORMAL_V2_VALIDATION.md`](validation/NORMAL_V2_VALIDATION.md)。该 v2 仍是候选，细发束、人物遮挡和背景建筑的语义方向需要继续人工校正，不可直接冻结为最终 Runtime Lighting 法线。

Normal v3 由 `scripts/generate_normal_v3.py` 以 v2 为像素基底局部合成：窄发束沿各自路径赋予方向，交叠背景缝隙退到近中性；袖子、背心和裙摆内部再低通，远景塔楼／墙面与下方石雕降低方向幅度。脸、天空、主石柱和栏杆在输出前直接恢复 v2 原像素。`scripts/validate_blink_normal.py` 验证尺寸、局部改动边界与受保护区域；`scripts/diagnose_normal_v3.py` 生成四组局部六光向／1.3× stress 对照。页面 Normal URL 已指向 v3。当前 Normal 阶段的冻结依据见 [`validation/NORMAL_V3_VALIDATION.md`](validation/NORMAL_V3_VALIDATION.md)。

Runtime Lighting Foundation v1 使用独立于 Vue 的 `LightingState` 作为 renderer 输入。`heroConfig.lighting` 集中保存方向、Key / Ambient 颜色与强度、wrapped diffuse 阈值和柔化宽度；Vue 页面层只持有可编辑状态并桥接 Debug Panel 与 `HeroCanvas`。`BaseRenderer` 将 state 映射为 GLSL uniforms，shader 使用冻结的 Normal v3 计算单方向光的柔和 toon-like diffuse，并以中性朝向的 diffuse 响应作基准，避免整体抬亮；ambient fill 保持很弱。Base view 不受光照影响，Lighting off 时 Lit 回到 Base。Blink 与 Leaves 只在 Base view 显示，避免污染 Normal / Lit 对照。该阶段没有 24h Timeline、Mask、PBR、阴影或后处理。详细参数与人工检查见 [`validation/LIGHTING_FOUNDATION_V1.md`](validation/LIGHTING_FOUNDATION_V1.md)；VuePress 迁移时 engine 和 shader 仍可独立搬迁。

R2A.1 将连续 `lightingFor(minutes)` 与日照曲线集中在 `src/config/lighting.ts`，Vue 只保存手动选择的分钟数并把结果送入 renderer。Fragment shader 对 Base 做精确 sRGB/linear 转换，再叠加 Normal-driven key diffuse、sky/ambient fill 与邻域 Normal 得出的宽尺度 painted band；`relightStrength` 在 linear space 混合 Base 与 relit 结果。Debug 的 0-1440、step 1 slider 只用于人工校准，无系统时钟、自动播放或 post processing。参考项目取舍见 [`reference/KUMENG_LIGHTING_NOTES.md`](reference/KUMENG_LIGHTING_NOTES.md)。
