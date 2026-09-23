# Implementation notes

Vue 只管理容器、生命周期、调试状态和质量选择。`src/engine/` 是普通 TypeScript，不依赖 Vue；GLSL 单独存放。未来迁入 VuePress 时复制 engine、shaders、config 与已验收资产，并由目标组件重新绑定 Canvas 生命周期。

`HeroCanvas` 在挂载后加载 Base，验证真实尺寸，再建立 WebGL2 context、shader、texture 和 quad。ResizeObserver 触发按需重绘；卸载时释放资源。context lost 时显示底层 `<img>`，restored 时重新初始化。页面在 Canvas 准备好前始终显示同一 Base 图片，避免黑屏。

Blink 候选整图的差异遍布全画面，不应把 Debug 的静态候选切换直接改成自动眨眼。验证记录见 [`validation/BLINK_V1_VALIDATION.md`](validation/BLINK_V1_VALIDATION.md)。未来若采用局部闭眼方案，应继续复用 Artwork Space 坐标，只在双眼区域合成，避免背景和头发随帧变化。

`layoutArtwork` 统一算 cover/contain；默认 Auto 在 viewport 宽高比低于 0.9 时选 contain，其他情况选 cover。UV 与 Source Pixel、CSS Display 坐标转换都在同一模块。GLSL 用相同布局给 quad 定位。UV 定义为左上原点。Canvas 像素用受限 DPR（默认 2）缩放。cover 允许超出 viewport 的裁切，contain 留出背景边。

`auto` 遇到 reduced motion 使用静态 Base；`static` 始终静态；`balanced` 用于强制检查 WebGL Base。Base 仍是按需绘制，面板记录上次绘制耗时。Leaves 有独立的限帧 RAF，`visibilitychange` 在后台停止并在恢复时重置计时。reduced motion 无论 Quality 是否为 balanced 都关闭 Leaves。

Leaves 的 `LeafField` 不依赖 Vue，使用 Canvas 2D Alpha Blend 绘制四张 PNG，职责包含纹理加载、粒子状态、共享风、resize、暂停和销毁。`LeavesLayer.vue` 只桥接生命周期与活动数量。覆层裁到 Artwork 在 viewport 中可见的矩形；粒子内部位置为该矩形的归一化坐标，速度以 CSS px/s 计，在 resize 后继续运动。覆层在 Base WebGL 或静态 `<img>` 之上，关闭 Base Renderer 不影响 Leaves 开关。移动端降低数量，静态和 reduced motion 移除整个覆层。Normal、Lighting 与其他动效仍等待素材与视觉验收。
