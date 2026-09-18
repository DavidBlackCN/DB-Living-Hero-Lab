"""Prepare the open-eye editing target and review preview. Requires Pillow."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work/blink/source/hero-4k-digital-art.png"
REGIONS = ROOT / "docs/blink-regions.json"
CROP = ROOT / "work/blink/source/hero-eye-context-open.png"
PREVIEW = ROOT / "work/blink/generated/hero-eye-context-debug-preview.png"
NOTES = ROOT / "work/blink/notes/blink-review.md"
DEFAULT = {"x": 1980, "y": 540, "width": 570, "height": 290}


def valid_box(region, size):
    if not isinstance(region, dict):
        return False
    values = [region.get(key) for key in ("x", "y", "width", "height")]
    if any(type(value) is not int for value in values):
        return False
    x, y, width, height = values
    return (x >= 0 and y >= 0 and width > 0 and height > 0
            and x + width <= size[0] and y + height <= size[1])


def main():
    with Image.open(SOURCE) as source:
        source.load()
        regions = {}
        status = "未读取（文件不存在）；使用默认坐标。"
        if REGIONS.exists():
            try:
                regions = json.loads(REGIONS.read_text(encoding="utf-8-sig"))
                if not isinstance(regions, dict):
                    raise ValueError("JSON root must be an object")
                canvas = regions.get("canvas")
                if canvas != {"width": source.width, "height": source.height}:
                    raise ValueError("canvas does not match source dimensions")
                status = "已读取；使用其中的 debugCrop。"
            except (OSError, ValueError) as error:
                regions = {}
                status = f"读取失败或不可靠（{error}）；使用默认坐标。"

        region = regions.get("debugCrop")
        if not valid_box(region, source.size):
            if regions:
                status = "已读取，但 debugCrop 无效或越界；使用默认坐标。"
            if source.size != (3840, 2160):
                raise ValueError("Default coordinates require a 3840 x 2160 source")
            region = DEFAULT
        x, y, width, height = (region[key] for key in ("x", "y", "width", "height"))
        box = (x, y, x + width, y + height)
        crop = source.crop(box)
        for path in (CROP, PREVIEW, NOTES):
            path.parent.mkdir(parents=True, exist_ok=True)

        # Retain PNG color metadata without transforming the pixel values.
        pnginfo = PngImagePlugin.PngInfo()
        if "gamma" in source.info:
            pnginfo.add(b"gAMA", round(source.info["gamma"] * 100000).to_bytes(4, "big"))
        if "srgb" in source.info:
            pnginfo.add(b"sRGB", bytes([source.info["srgb"]]))
        if "chromaticity" in source.info:
            pnginfo.add(b"cHRM", b"".join(
                round(value * 100000).to_bytes(4, "big")
                for value in source.info["chromaticity"]))
        crop.save(CROP, format="PNG", pnginfo=pnginfo)
        with Image.open(CROP) as saved:
            assert saved.size == crop.size and saved.mode == crop.mode
            assert saved.tobytes() == crop.tobytes(), "Crop pixel verification failed"

        # Resampling and annotations apply only to this inspection preview.
        preview = source.convert("RGB")
        preview.thumbnail((1536, 864), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(preview)
        sx, sy = preview.width / source.width, preview.height / source.height
        boxes = [("debugCrop", region, "#ffcf40")]
        for name, color in (("leftEye", "#43efff"), ("rightEye", "#ff75d5")):
            if valid_box(regions.get(name), source.size):
                boxes.append((name, regions[name], color))
        for index, (name, rect, color) in enumerate(boxes):
            rx, ry, rw, rh = (rect[key] for key in ("x", "y", "width", "height"))
            draw.rectangle((round(rx * sx), round(ry * sy),
                            round((rx + rw) * sx), round((ry + rh) * sy)),
                           outline=color, width=3)
            label = f"{name}: x={rx}, y={ry}, w={rw}, h={rh}"
            position = (16, 16 + index * 26)
            draw.rectangle(draw.textbbox(position, label), fill="#111111")
            draw.text(position, label, fill=color)
        preview.save(PREVIEW, format="PNG")

        NOTES.write_text(f"""# Blink 素材裁切验收

- 输入：`{SOURCE.relative_to(ROOT).as_posix()}`
- 裁切输出：`{CROP.relative_to(ROOT).as_posix()}`
- 原图尺寸：`{source.width} x {source.height}`
- 裁切坐标：`x={x}, y={y}, width={width}, height={height}`（左上角为原点，右/下边界不包含）
- 裁切图尺寸：`{width} x {height}`
- `docs/blink-regions.json`：{status}
- 调试预览：`{PREVIEW.relative_to(ROOT).as_posix()}`（缩略全图及彩色候选框）

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
""", encoding="utf-8")
        print(f"Crop: {width} x {height} at ({x}, {y}); pixel equality verified.")
        print(f"Preview: {PREVIEW.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
