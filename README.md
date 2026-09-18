# Black Sister Living Hero Lab

最新一轮：**Code-only Lighting Salvage（2026-09-18）**。拆开灯具发光、近场、桌面和人物受光，收小桌面尾部，补前躯干/书架遮光与杯底接触；清晨改为更清冷的低角度光。保留 noon/dusk、窗区与原图，correction 默认关闭。[本轮记录与性能结果](docs/logs/code-only-lighting-salvage.md) · [四时段及前后对照](docs/screenshots/code-only-salvage/README.md)。建议人工验收后冻结光照核心，本轮未进入动画。以下为历史记录。

最新一轮（2026-09-18）：先完成 [KumengScreen 源码拆解](docs/logs/kumeng-lighting-analysis.md)，再将环境光、窗光、投光、台灯反射与发光分开合成；补强接触遮挡、体块暗面和左侧空间响应。[实现与验证记录](docs/logs/light-layer-review.md) · [四时刻截图和同亮度对照](docs/screenshots/light-layer-review/README.md)。本地 49 项视觉检查通过；高 DPR 软件渲染有额外开销，真实 GPU 性能待验证。以下为历史更新。

最新修正：[窗框以下异常遮罩带](docs/logs/window-interior-fix.md)。已校准错位的室内窗台受光区域，并补齐笔筒接收区。[局部前后对照](docs/screenshots/window-interior-fix/comparison.png)。

本轮更新：**Hero 底层光影收敛 3（2026-09-17）**。独立玻璃锚点与硬裁剪、增强接触/定向暗部、灯下窗台与右后侧照明、左侧空间响应。参见 [本轮记录](docs/logs/spatial-convergence-3.md) 与 [四时刻截图及前后对照](docs/screenshots/spatial-convergence-3/README.md)。以下前轮记录保留作历史背景。

独立的 Living Hero 光影实验工程。当前完成 **Lighting / Shadow Convergence（2026-09-17）**。
本轮收拢右后侧灯池、补齐灯下窗台接收区，并加入可控的接触遮挡和柔和体积暗面。停止开发，等待人工验收。继续使用原始 4K 插画、Vite + TypeScript + WebGL2；debug UI 为原生 DOM，核心引擎独立。原画 baked light 限制仍然存在。

本轮验收入口：[黄昏、夜景前后及阴影开关对照](docs/screenshots/lighting-shadow-convergence/README.md)。
实现、验证和限制见 [Lighting / Shadow 记录](docs/logs/lighting-shadow-convergence.md)；[Convergence 2 记录](docs/logs/lighting-convergence-2.md)保留历史过程。
测试截图、实验预览、性能采样 JSON 和运行日志均为本地产物，不提交到 GitHub；图片链接需在本地生成后查看。原始插画和运行所需技术贴图继续纳入版本管理。

普通 `/` 默认展示 v2；`/?normal=registered`（或 `v1`）保留 v1；`/?normal=low-frequency` 保留低频对照。`npm run assets:normal` 重建 v2，`npm run assets:normal -- --version v1` 重建 v1。曲面为手工近似，自动检查通过不等于最终艺术验收。

`/?correction=1` 加载可开关的增益实验（默认页面不加载）。实验已结束，收益有限，继续默认关闭。面板可切换 Original / Correction，并查看 Correction、Corrected Base；Base 始终显示原图。`npm run assets:correction` 从 v2 重建实验贴图。它只能温和修正推定的固定受光，无法移除原画阴影或恢复真正 albedo。

最新修正：[左手、书页与桌面光影验收](docs/screenshots/desk-light-review/README.md)。校准左手和书本轮廓，消除桌面区域穿过袖子的受光错误，删除无深度依据的整轮廓平移投影。两套 normal 均已复核，候选同步采用修正后的区域。

## 本地运行

推荐 Node.js 22.12+（本机验证：22.17.1）。

```sh
npm ci
npm run dev
```

打开终端显示的地址，默认 **http://127.0.0.1:5173/**。根页面就是调试页面，无需额外路由。若默认 npm 缓存目录无写权限，使用 `npm ci --cache .npm-cache`。

```sh
npm run typecheck
npm test
npm run build
npm run preview
```

视觉回归截图：

```sh
npm run test:visual
```

该命令会启动独立 Vite 开发服务器，并在固定 1440x900 Chromium 视口中生成四个时段、四个 debug view 和 Coffee Steam 启用态截图到 `docs/screenshots/phase3/`。

## 调试

- 时间滑条：0–24h，拖动自动退出 realtime；24:00 与次日 00:00 等价。
- Realtime：读取电脑本地时间；大数字为当前渲染时间，小数字为目标时间。
- Dawn / Noon / Dusk / Night：06:00 / 12:00 / 17:30 / 23:00。
- 曝光、环境光、窗光、台灯、法线强度、脸部保护可独立调整。
- 柔和阴影 / 接触遮挡：默认 0.65，设为 0 关闭接触和局部环境遮挡；体块响应由法线、Stylized 和柔和度控制。Shadow / Occlusion 显示入射光的遮挡比例；Ambient Fill Only、Form Light Bands、Contact Visibility 分别检查环境光、体块和接触数据。
- 新增头发／服装受光、夜间日光抑制；关闭「区域光照增强」可对照一版效果。
- Final / Base / Normal / Masks / Lighting / Scene / Overlay 视图用于对照与配准检查；Neutral、Projected Light Only、Exterior Mask、Shadow / Occlusion 用于隔离检查光、玻璃边界和暗部。
- 动画开关当前控制时间平滑过渡；减少动态效果会立即跳到目标时间，默认尊重系统偏好。
- 点击面板标题可收起面板。完整保留原图，非 16:9 屏幕出现留边。

## 文件结构与说明

```text
src/app/          启动与布局
src/debug-ui/     调试控件
src/engine/       渲染、shader、时间、光照、素材加载
tests/            时间边界与光照连续性测试
public/assets/    用户原图（保持原样）
  generated/      后续技术资产与格式说明
docs/architecture.md
docs/logs/phase1-notes.md
docs/prompts/     技术资产提示词预留
docs/screenshots/ dawn / noon / dusk / night 实际浏览器截图
```

当前默认加载人物遮罩、场景遮罩、空间遮挡三个 SVG，以及配准 normal v2 PNG。轮廓源文件在 `docs/scene-regions.json`，执行 `npm run assets:generate` 重建 SVG；`npm run assets:normal` 从 `docs/normal-surfaces.json` 重建 v2，然后刷新页面。重新生成需要 Python 3 + Pillow + NumPy（`python -m pip install Pillow numpy`）；运行应用和 build 不需要 Python。细发丝、花枝与透明物体仍是近似分割。也可通过 `normalUrl` / `maskUrl` / `sceneMaskUrl` 替换为同尺寸精修贴图；`lightShapingUrl` 接受相同比例、准确配准的较低分辨率数据图。

玻璃轮廓直接按原图边界栅格化；左玻璃下缘有匹配原图虚焦的局部过渡，Scene / Overlay / Final / Exterior Mask 使用一致覆盖值。时段投光配合背光压暗和轻微的书本／杯垫接触阴影；夜景分为冷色窗外、暖色台灯光池和暗室。投光和台灯均响应表面法线，无接收面高度依据的整轮廓平移投影仍被排除。Bloom、蒸汽保留，本轮未扩展其他动效。v2 曲面依然是人工近似，原图已有日照与阴影无法完全消除；可选 correction 也不等于恢复 albedo。当前停在光照验收阶段，尚未迁移到 Blog。
