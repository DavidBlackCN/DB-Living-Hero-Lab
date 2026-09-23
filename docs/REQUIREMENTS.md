# Requirements · Stage 1

目标：以独立 Vite / Vue 3 / TypeScript / 原生 WebGL2 工程验证 DB Living Hero 的 Base 显示、统一坐标与可迁移模块边界。最终目标是 VuePress 2 / `vuepress-theme-plume` Blog 首页，而本阶段页面只是全屏实验壳。

当前冻结资产是 `base-albedo.png`。`blink-closed-eyes-v1.png` 为待实机验证候选。Normal、落叶、区域和语义 Mask、Emission 等尚未制作。后续能力包括 Blink、Breathing、Hair Motion、Leaves、24h Runtime Lighting；本阶段均不实现。

阶段 1 交付：按真实 Artwork Space 显示 Base，cover/contain、UV 映射、WebGL2 quad 渲染、静态回退、Debug 控件占位、DPR cap、后台按需绘制、reduced motion 静态策略。图像为 1672×941，宽高比约 1.77683；16:9 是页面目标比例，不是可替代真实素材尺寸的注册参数。

旧 `Requirement Draft v0.1` 的阶段顺序及“所有运行时代码都要等待全部资产冻结”与本次阶段 1 开工指令冲突。本阶段只实现 Base Renderer 基础设施；最终动效和光照仍等待相应素材冻结与视觉验收。早期文档作为设计历史归档于 `archive/`。
