# 验收资料与回归

## 看什么

- [当前主页](final/desktop-home.png)、[一级菜单](final/desktop-primary.png)、[二级菜单](final/desktop-expanded.png)、[沉浸模式](final/desktop-immersive.png)、[画面菜单](final/view-menu.png)、[移动布局](final/mobile.png)。来源 `cd7bea5` 的最终主页验收。
- [四时段总览](final/four-phases.jpg)：[Dawn](final/dawn.png) / [Noon](final/noon.png) / [Dusk](final/dusk.png) / [Night](final/night.png)。固定帧关闭动效以便对照。
- [灯体注册](final/lamp-registration.png)、[Night 灯体近景](final/night-lamps.png)。最终 source mask 记录，不代表当前页面文字布局。
- [24H 场景检查](final/24h-scene.jpg)、[播放检查](final/24h-checks.json)。保留塔身收口记录；之后 Dawn 同步已调整，这张历史 contact sheet 不作为当前 Dawn 像素基准。
- [Dawn 动效](motion/dawn-25s.mp4)、[Dusk 动效](motion/dusk-25s.mp4)、[Night 动效](motion/night-25s.mp4)、[Noon 落叶](motion/noon-leaves-25s.mp4)、[Blink 慢放](motion/blink-slow-60fps.mp4)。来自最后对应动效阶段；后续灯光有收口，只用于复核运动方式。
- [长时间运行记录](final/long-run.json)。历史 R7.3B 性能记录，不承诺其他机器相同帧率。

`baseline/` 的四张原始 PNG 是 R7.4 冻结渲染基准，专供 `validate_visual.py`，不要重新压缩或自动更新。旧 Debug 按钮矩形及其后已验收修正的两盏灯玻璃范围（含采样边缘）由比较脚本显式排除；灯体由独立资产哈希及三面注册检查保护；灯旁 Bloom 仅允许 1 级显示码差异，其余画面逐像素相等。

## 本地验证

生产构建仅需 Node/pnpm。离线 Python 工具按需要安装 Pillow、numpy；天空生成另需 scipy、opencv-python；浏览器回归需要 Python Playwright 和 Edge。`HERO_BROWSER` 可指定 Chromium 可执行文件路径。生成脚本不应在普通回归时运行，以免覆盖冻结图。

```sh
pnpm typecheck
pnpm build
python scripts/validate_repository.py
python scripts/validate_blink_normal.py
python scripts/validate_lamp_masks.py
node scripts/validate_hero_ssr.mjs
```

启动开发服务器 `pnpm dev --host 127.0.0.1`（5173），另一终端执行：

```sh
python scripts/validate_final_integration.py
python scripts/validate_visual.py
```

集成检查包含资源失败/重试、WebGL fallback、质量预算、暂停、离屏、卸载/重挂、reduced-motion、子路径资源和自动降档。视觉检查比较四时段冻结像素，历史 UI/灯体差异范围除外。

构建后，在仓库根目录启动 `python -m http.server 4174 --bind 127.0.0.1`，另一个终端执行：

```sh
python scripts/validate_standalone.py
python scripts/validate_homepage_polish.py
```

页面检查使用 `/dist/` 子路径；后者会打开实际 Edge 窗口检查布局。输出全部进入忽略的 `artifacts/`，不会覆盖这里的验收材料。保留旧阶段视频并不表示它们在本轮重新跑过，当前执行结果见 [维护记录](../MAINTENANCE.md)。
