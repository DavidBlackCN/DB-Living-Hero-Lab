# 仓库维护

## 保留标准

- 能运行：当前源代码、20 张运行图、构建配置与依赖锁文件。
- 能维护：有效回归脚本、当前素材生成链及必需输入、组件 API/架构说明。
- 能验收：最终页面/四时段图片、少量具有独立用途的动态记录、像素回归基准。
- 不再保留：被最终结果替代的 round/before/after 图集、失败素材、过期阶段报告、旧 Debug UI 诊断脚本、停用的天空压暗素材。

本地中间产物统一放在 `artifacts/`（已忽略）。需要分享时，精选放入 `docs/validation/` 并写清版本、用途和限制；不要整目录提交全部原始帧。历史通过 `git log` / `git show <commit>:<path>` 查阅。

## 2026-10-03 清理

清理前基线为当前 `v2`。删除清单共 1,084 个旧路径，约 1,125.7 MiB，其中少量被精选复制或作为制作源迁出，所以这不是净节省值。已删除内容不再在工作树留一个同样庞大的 archive。

- 保留精选 `final/`、`motion/` 和 `baseline/`，阶段流水文档合并为当前状态说明。
- `public/` 只含运行资产。Normal v1/v2、闭眼提取源、Sky matte 迁到 `sources/hero/`；相应生成器/验证器路径同步。
- 移除无运行或生成引用的 `sky-edge-tone.png`、`sky-edge-override.png`。
- 将有效浏览器公共函数抽到 `browser_support.py`，保留当前组件/主页/SSR/资产回归，移除失效旧调试页面脚本。
- 所有生成截图改写入 `artifacts/`。README/AGENTS/素材/动画/阶段入口按当前版本更新。
- 借鉴[参考项目 README](https://github.com/buger404/KumengScreen/blob/main/README.md)的功能、实现、运行、目录分工组织；本项目继续使用 pnpm/Vue，不照搬其运行命令。

本轮不改渲染或 UI 逻辑、不重生成任何运行图，不清理 `.git` 历史、依赖目录或用户技能目录。旧 blob 仍留在 Git，工作树/部署包减小不等于 Git 仓库立即变小；没有执行历史重写或强制 GC。

## 验证

通过：typecheck、build、SSR、20 张运行图哈希、Normal/Blink 注册、六面灯罩、组件集成生命周期、主页与多尺寸浏览器检查、本地文档链接及脚本导入检查。38 个 src 文件与清理前哈希完全一致。

四时段旧基准比较：除历史 Debug 按钮与已验收灯罩修正区外一致；Night 灯旁 Bloom 有 26 个像素的 1 级显示码差异，限定在局部范围允许（不放宽其他画面）。运行图仍由冻结哈希完整保护。[具体检查结果](validation/final/cleanup-checks.json)。

整理后 docs 从 **1,040 文件 / 1,121.87 MiB** 降到约 **34 文件 / 80.3 MiB**；scripts 从 60 个降至 20 个有效工具；public 去掉约 3.66 MiB 非运行内容（其中 3.61 MiB 移到 sources 保留制作链）。工作树净减少约 **1.02 GiB**，不含 Git 历史大小。

命令入口见 [验收说明](validation/README.md)。
