"""Assemble the R6.5D eye, Night, and Moon direction review images."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1] / "docs/validation/r6-5d-moon"
BEFORE = ROOT / "baseline"
AFTER = ROOT / "final"


def frame(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def labeled_sheet(items: list[tuple[Image.Image, str]], columns: int, size: tuple[int, int], output: str) -> None:
    width, height = size
    rows = (len(items) + columns - 1) // columns
    sheet = Image.new("RGB", (width * columns, (height + 30) * rows), (12, 16, 23))
    draw = ImageDraw.Draw(sheet)
    for index, (image, label) in enumerate(items):
        x, y = (index % columns) * width, (index // columns) * (height + 30)
        draw.text((x + 10, y + 8), label, fill=(245, 240, 229))
        sheet.paste(image.resize(size, Image.Resampling.LANCZOS), (x, y + 30))
    sheet.save(AFTER / output, quality=93)


def main() -> None:
    eye_box = (930, 145, 1115, 270)
    labeled_sheet([
        (frame(BEFORE / "06h30.png").crop(eye_box), "Dawn before · screen-left eye"),
        (frame(AFTER / "dawn.png").crop(eye_box), "Dawn after · screen-left eye"),
    ], 2, (740, 500), "dawn-eye-before-after-4x.jpg")

    art = (310, 0, 1440, 900)
    labeled_sheet([
        (frame(BEFORE / "22h.png").crop(art), "Night before · R6.5C"),
        (frame(AFTER / "22h.png").crop(art), "Night after · R6.5D"),
    ], 2, (1130, 900), "night-before-after.jpg")
    labeled_sheet([
        (frame(AFTER / "dusk.png").crop(art), "17:30 · Sun 144° · from screen-right"),
        (frame(AFTER / "22h.png").crop(art), "22:00 · Moon 49° · from screen-left"),
    ], 2, (1130, 900), "dusk-vs-night.jpg")

    people = (740, 40, 1290, 740)
    labeled_sheet([
        (frame(BEFORE / "22h.png").crop(people), "Character before"),
        (frame(AFTER / "22h.png").crop(people), "Character after"),
    ], 2, (825, 1050), "night-character-1-5x.jpg")
    stone = (320, 600, 1430, 810)
    labeled_sheet([
        (frame(BEFORE / "22h.png").crop(stone), "Stone before"),
        (frame(AFTER / "22h.png").crop(stone), "Stone after"),
    ], 2, (1110, 210), "night-stone.jpg")

    labels = [
        ("20h", "20:00 · Moon 35° / 12°"),
        ("22h", "22:00 · Moon 49° / 40°"),
        ("00h", "00:00 · Moon 81° / 54°"),
        ("02h", "02:00 · Moon 116° / 49°"),
        ("04h30", "04:30 · Moon 144° / 19°"),
    ]
    labeled_sheet([(frame(AFTER / f"{name}.png").crop(art), label) for name, label in labels],
                  3, (700, 558), "moon-direction-contact.jpg")


if __name__ == "__main__":
    main()
