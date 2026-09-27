"""Capture registered Sky/foreground seam review at the user-marked regions."""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


WIDTH, HEIGHT = 2048, 1033
ART_WIDTH, ART_HEIGHT = 1672, 941
PHASES = (("dawn", 390), ("noon", 720), ("dusk", 1050), ("night", 1320))
REGIONS = {
    "left-vine": (825, 0, 970, 365),
    "right-roof": (1360, 115, 1672, 325),
    "ribbon": (1235, 170, 1360, 345),
    "top-leaves": (840, 0, 1672, 165),
}


def screen_box(source: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    scale = WIDTH / ART_WIDTH
    top = (HEIGHT - ART_HEIGHT * scale) / 2
    x0, y0, x1, y1 = source
    return tuple(round(value) for value in (x0 * scale, y0 * scale + top, x1 * scale, y1 * scale + top))


def save_crops(frame: Image.Image, output: Path, phase: str) -> None:
    for region, box in REGIONS.items():
        crop = frame.crop(screen_box(box))
        crop.save(output / f"{phase}-{region}.png")
        if phase == "night":
            crop.resize((crop.width * 2, crop.height * 2), Image.Resampling.NEAREST).save(
                output / f"night-{region}-2x.png"
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        page.get_by_label("Render view").select_option("lit")
        slider = page.locator(".time-control input[type=range]")
        page.add_style_tag(content=".debug-panel { visibility: hidden !important; }")
        for phase, minutes in PHASES:
            slider.evaluate(
                "(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }",
                minutes,
            )
            page.wait_for_timeout(150)
            frame = Image.open(BytesIO(page.screenshot())).convert("RGB")
            frame.save(args.output / f"{phase}-full.png")
            save_crops(frame, args.output, phase)
        browser.close()

    sheet = Image.new("RGB", (WIDTH, HEIGHT))
    for index, (phase, _) in enumerate(PHASES):
        frame = Image.open(args.output / f"{phase}-full.png").convert("RGB")
        thumb = frame.resize((WIDTH // 2, HEIGHT // 2))
        sheet.paste(thumb, ((index % 2) * WIDTH // 2, (index // 2) * HEIGHT // 2))
    ImageDraw.Draw(sheet).text((8, 8), "DAWN / NOON / DUSK / NIGHT", fill="white")
    sheet.save(args.output / "four-phase-contact.png")


if __name__ == "__main__":
    main()
