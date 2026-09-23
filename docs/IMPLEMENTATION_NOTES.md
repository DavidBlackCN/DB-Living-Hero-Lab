# Implementation notes

Vue 只管理容器、生命周期、调试状态和质量选择。`src/engine/` 是普通 TypeScript，不依赖 Vue；GLSL 单独存放。未来迁入 VuePress 时复制 engine、shaders、config 与已验收资产，并由目标组件重新绑定 Canvas 生命周期。

`HeroCanvas` 在挂载后加载 Base，验证真实尺寸，再建立 WebGL2 context、shader、texture 和 quad。ResizeObserver 触发按需重绘；卸载时释放资源。context lost 时显示底层 `<img>`，restored 时重新初始化。页面在 Canvas 准备好前始终显示同一 Base 图片，避免黑屏。

`layoutArtwork` 统一算 cover/contain；默认 Auto 在 viewport 宽高比低于 0.9 时选 contain，其他情况选 cover。UV 与 Source Pixel、CSS Display 坐标转换都在同一模块。GLSL 用相同布局给 quad 定位。UV 定义为左上原点。Canvas 像素用受限 DPR（默认 2）缩放。cover 允许超出 viewport 的裁切，contain 留出背景边。

`auto` 遇到 reduced motion 使用静态图；`static` 始终静态；`balanced` 用于强制检查 WebGL。阶段 1 不存在持续动画循环，因此后台无需计时；页面回到前台会重绘。未来动画模块必须在 `visibilitychange` 暂停更新。Frame 面板显示上次按需绘制耗时；FPS 显示 idle，避免伪造持续帧率。

质量策略及当前降级只覆盖静态与 WebGL 选择。移动端先保证 Base、Canvas 尺寸和静态回退。Normal、Lighting 与动效等候素材与视觉验收。
