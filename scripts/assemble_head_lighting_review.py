"""Build the R6 Final head-lighting visual review from static browser captures."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path("docs/validation/r6-final-head")
BEFORE = ROOT / "before"
FINAL = ROOT / "final"
REVIEW = ROOT / "review"
REVIEW.mkdir(parents=True, exist_ok=True)


def head(stage: Path, name: str) -> Image.Image:
    return Image.open(stage / f"{name}-head.png").convert("RGB")


def pair(name: str) -> None:
    output = Image.new("RGB", (880, 413), "#20242d")
    draw = ImageDraw.Draw(output)
    for index, (stage, label) in enumerate(((BEFORE, "Before"), (FINAL, "After"))):
        x = index * 440
        draw.text((x + 10, 8), f"{name.upper()} {label}", fill="white")
        output.paste(head(stage, name), (x, 20))
    output.save(REVIEW / f"{name}-before-after.png")


for phase in ("dawn", "dusk", "night"):
    pair(phase)

four = Image.new("RGB", (880, 826), "#20242d")
draw = ImageDraw.Draw(four)
for index, phase in enumerate(("dawn", "noon", "dusk", "night")):
    x = index % 2 * 440
    y = index // 2 * 413
    draw.text((x + 10, y + 8), phase.upper(), fill="white")
    four.paste(head(FINAL, phase), (x, y + 20))
four.save(REVIEW / "four-head-contact.png")

under_eye = Image.new("RGB", (1184, 796), "#20242d")
draw = ImageDraw.Draw(under_eye)
for row, phase in enumerate(("dawn", "night")):
    for col, (stage, label) in enumerate(((BEFORE, "Before"), (FINAL, "After"))):
        x, y = col * 592, row * 398
        draw.text((x + 10, y + 8), f"{phase.upper()} {label}", fill="white")
        crop = head(stage, phase).crop((137, 185, 285, 279))
        under_eye.paste(crop.resize((592, 376), Image.Resampling.NEAREST), (x, y + 22))
under_eye.save(REVIEW / "dawn-night-under-eye-4x.png")

dusk_eye = Image.new("RGB", (1496, 474), "#20242d")
draw = ImageDraw.Draw(dusk_eye)
for col, (stage, label) in enumerate(((BEFORE, "Before"), (FINAL, "After"))):
    x = col * 748
    draw.text((x + 10, 8), f"DUSK {label}", fill="white")
    crop = head(stage, "dusk").crop((118, 160, 305, 271))
    dusk_eye.paste(crop.resize((748, 444), Image.Resampling.NEAREST), (x, 30))
dusk_eye.save(REVIEW / "dusk-eyes-4x.png")

rows = (("05h30", "06h", "dawn", "07h", "08h"),
        ("16h", "dusk", "19h", "20h", "night"))
transition = Image.new("RGB", (1100, 460), "#20242d")
draw = ImageDraw.Draw(transition)
for row, names in enumerate(rows):
    for col, name in enumerate(names):
        x, y = col * 220, row * 230
        draw.text((x + 8, y + 8), name.upper(), fill="white")
        transition.paste(head(FINAL, name).resize((220, 197), Image.Resampling.LANCZOS), (x, y + 24))
transition.save(REVIEW / "head-transition-contact.png")
