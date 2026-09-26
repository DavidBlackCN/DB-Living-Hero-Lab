"""Capture clean four-phase character-lighting review frames."""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


TIMES = (("dawn", 390), ("noon", 720), ("dusk", 1050), ("night", 1320))
HEAD = (822, 14, 1262, 407)
BASELINE = Path("docs/validation/r6-final-head/final")


def labeled(image: Image.Image, label: str) -> Image.Image:
    copy = image.copy()
    draw = ImageDraw.Draw(copy)
    draw.rectangle((0, 0, min(copy.width, 125), 20), fill=(25, 29, 37))
    draw.text((7, 4), label.upper(), fill="white")
    return copy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    fulls: list[Image.Image] = []
    heads: list[Image.Image] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        page.get_by_label("Render view").select_option("lit")
        slider = page.locator(".time-control input[type=range]")
        page.add_style_tag(content=".debug-panel { visibility: hidden !important; }")
        for name, minutes in TIMES:
            slider.evaluate(
                "(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }",
                minutes,
            )
            page.wait_for_timeout(120)
            full = Image.open(BytesIO(page.screenshot())).convert("RGB")
            head = full.crop(HEAD)
            full.save(args.output / f"{name}-full.png")
            head.save(args.output / f"{name}-head.png")
            fulls.append(labeled(full.resize((720, 450)), name))
            heads.append(labeled(head, name))
        browser.close()

    full_contact = Image.new("RGB", (1440, 900))
    head_contact = Image.new("RGB", (1760, 393))
    for index, (full, head) in enumerate(zip(fulls, heads)):
        full_contact.paste(full, ((index % 2) * 720, (index // 2) * 450))
        head_contact.paste(head, (index * 440, 0))
    full_contact.save(args.output / "four-full-contact.png")
    head_contact.save(args.output / "four-head-contact.png")

    for name, _ in TIMES:
        old = Image.open(BASELINE / f"{name}-head.png").convert("RGB")
        new = Image.open(args.output / f"{name}-head.png").convert("RGB")
        comparison = Image.new("RGB", (880, 393))
        comparison.paste(labeled(old, "before"), (0, 0))
        comparison.paste(labeled(new, "after"), (440, 0))
        comparison.save(args.output / f"{name}-before-after.png")


if __name__ == "__main__":
    main()
