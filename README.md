# Black Sister Living Hero Lab

独立的 Living Hero 光影实验工程。当前完成 **窗户边界校准与时段投光迭代（2026-09-16）**，以原始 4K 插画为底图，使用 Vite + TypeScript + WebGL2；debug UI 为原生 DOM，核心引擎独立。

本轮人工验收入口：[四时段七视图、灰度与窗框配准](docs/screenshots/spatial-light-review/README.md)。
实现、验证和限制见 [空间光影阶段记录](docs/logs/spatial-light-review.md)。
测试截图、实验预览、性能采样 JSON 和运行日志均为本地产物，不提交到 GitHub；图片链接需在本地生成后查看。原始插画和运行所需技术贴图继续纳入版本管理。

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

当前默认加载四张可再生成的 SVG 技术贴图：人物轮廓遮罩、场景区域遮罩、低频法线、空间遮挡数据。轮廓源文件在 `docs/scene-regions.json`，执行 `npm run assets:generate` 再生成，然后刷新页面。重新生成需要 Python 3 + Pillow + NumPy（`python -m pip install Pillow numpy`），用于从原图提取局部白花遮挡；运行应用和 build 不需要 Python。细发丝、花枝与透明物体仍是近似分割。也可通过 `normalUrl` / `maskUrl` / `sceneMaskUrl` 替换为同尺寸精修贴图；`lightShapingUrl` 接受相同比例、准确配准的较低分辨率数据图。

玻璃轮廓直接按原图边界栅格化，已删除会产生缝隙的内缩羽化，Scene / Overlay / Final / Exterior Mask 使用一致覆盖值。时段投光配合背光压暗、物体投影与接触阴影；夜景分为冷色窗外、暖色台灯光池和暗室。Bloom、蒸汽已有实现，本轮未扩展其他动效。原图已有日照与阴影仍无法完全消除，低频法线也无法还原细发丝和衣褶。先人工验收，再决定高质量配准法线的制作；尚未迁移到 Blog。
