"""Assemble registered screenshot crops for the R6.5E visual review."""

from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path("docs/validation/r6-5e")
REVIEW = ROOT / "review"
REVIEW.mkdir(parents=True, exist_ok=True)


def crop_pair(name: str, frame: str, box: tuple[int, int, int, int], scale: int) -> None:
    crops = []
    for stage in ("before", "after"):
        image = Image.open(ROOT / stage / frame).convert("RGB")
        crops.append(image.crop(box).resize(
            ((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.Resampling.NEAREST
        ))
    output = Image.new("RGB", (crops[0].width * 2, crops[0].height + 38), "#20242d")
    draw = ImageDraw.Draw(output)
    for index, (stage, image) in enumerate(zip(("Before", "After"), crops)):
        x = index * image.width
        draw.text((x + 12, 11), stage, fill="white")
        output.paste(image, (x, 38))
    output.save(REVIEW / f"{name}-{scale}x.png")


crop_pair("dawn-face", "dawn.png", (954, 134, 1152, 316), 2)
crop_pair("dawn-face", "dawn.png", (990, 174, 1100, 270), 4)
crop_pair("night-hair", "22h.png", (762, 65, 1332, 550), 2)

names = ("04h30", "05h", "05h30", "06h")
thumb_width = 560
thumb_height = 350
sheet = Image.new("RGB", (thumb_width * 2, (thumb_height + 30) * 2), "#20242d")
draw = ImageDraw.Draw(sheet)
for index, name in enumerate(names):
    source = Image.open(ROOT / "after" / f"{name}.png").convert("RGB")
    thumb = source.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
    x = (index % 2) * thumb_width
    y = (index // 2) * (thumb_height + 30)
    draw.text((x + 12, y + 8), name, fill="white")
    sheet.paste(thumb, (x, y + 30))
sheet.save(REVIEW / "dawn-transition-contact.png")
