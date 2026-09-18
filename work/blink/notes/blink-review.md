# Blink 素材裁切验收

- 输入：`work/blink/source/hero-4k-digital-art.png`
- 裁切输出：`work/blink/source/hero-eye-context-open.png`
- 原图尺寸：`3840 x 2160`
- 裁切坐标：`x=1980, y=540, width=570, height=290`（左上角为原点，右/下边界不包含）
- 裁切图尺寸：`570 x 290`
- `docs/blink-regions.json`：已读取；使用其中的 debugCrop。
- 调试预览：`work/blink/generated/hero-eye-context-debug-preview.png`（缩略全图及彩色候选框）

`hero-eye-context-open.png` 是后续官方订阅图像编辑会话的直接编辑目标。
仅精确裁切并无损保存 PNG，不缩放、不重采样、不改色、不锐化、不加标记。
脚本已重新读取输出，验证尺寸、像素模式及所有像素字节与原图裁切一致。

`hero-eye-context-debug-preview.png` 仅供人工检查裁切位置，不进入运行时。
双眼框沿用现有候选坐标，不代表最终分割结果。

人工验收记录（当前源图与现有坐标）：裁切上边界截断了画面左侧眼睛上部，
未完整保留双眼和眉毛；现有双眼候选框偏低。按本次指定坐标原样输出，
未擅自调整。后续作为编辑目标前，需要确认此上下文范围是否足够。

本次仓库验证：`npm run build`、`npm run typecheck` 均通过。

重新执行（依赖 Pillow）：`python scripts/prepare-blink-crop.py`。
重复执行将覆盖上述两张输出图及本说明文档。
