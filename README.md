# Black Sister Living Hero Lab

独立的 Living Hero 光影实验工程。当前已在 Lighting MVP 基础上完成 **Phase 2 区域光照迭代**，以原始 4K 插画为底图，使用 Vite + TypeScript + WebGL2；debug UI 为原生 DOM，核心引擎独立。

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

## 调试

- 时间滑条：0–24h，拖动自动退出 realtime；24:00 与次日 00:00 等价。
- Realtime：读取电脑本地时间；大数字为当前渲染时间，小数字为目标时间。
- Dawn / Noon / Dusk / Night：06:00 / 12:00 / 17:30 / 23:00。
- 曝光、环境光、窗光、台灯、法线强度、脸部保护可独立调整。
- 新增头发／服装受光、夜间日光抑制；关闭「区域光照增强」可对照一版效果。
- Final / Base / Normal / Masks / Lighting / Scene / Overlay 视图用于对照与配准检查。
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

当前默认加载三张可再生成的 SVG 技术贴图：人物轮廓遮罩、场景区域遮罩、低频法线。轮廓源文件在 `docs/scene-regions.json`，执行 `npm run assets:generate` 再生成，然后刷新页面。它们仍是手工近似，细发丝、花枝与玻璃尚未精确分割。也可通过 `normalUrl` / `maskUrl` / `sceneMaskUrl` 替换为同尺寸精修贴图。

窗外夜间亮度现已独立控制，台灯不再照亮窗外区域。原图已有日照和阴影仍无法完全消除；尚未实现眨眼、呼吸、头发运动、蒸汽或 bloom。下一步继续细化复杂边缘，并制作轻量微动画资产。详见 [架构说明](docs/architecture.md)、[Phase 2 记录](docs/logs/phase2-notes.md) 与 [最新截图](docs/screenshots/phase2/README.md)。
