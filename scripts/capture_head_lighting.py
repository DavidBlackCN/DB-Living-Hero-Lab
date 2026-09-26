"""Static, registered R6 head-lighting review at anchors and transition times."""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


HEAD = (822, 14, 1262, 407)
TIMES = (
    ("05h30", 330), ("06h", 360), ("06h29", 389), ("dawn", 390),
    ("06h31", 391), ("07h", 420), ("08h", 480), ("noon", 720),
    ("16h", 960), ("17h29", 1049), ("dusk", 1050), ("17h31", 1051),
    ("19h", 1140), ("19h59", 1199), ("20h", 1200), ("20h01", 1201),
    ("21h59", 1319), ("night", 1320), ("22h01", 1321),
    ("00h", 0), ("24h", 1440),
)
ANCHORS = {"dawn", "noon", "dusk", "night"}


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
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        page.get_by_label("Render view").select_option("lit")
        slider = page.get_by_role("slider", name="24H Preview")
        for name, minutes in TIMES:
            slider.evaluate(
                "(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }",
                minutes,
            )
            page.wait_for_timeout(120)
            frame = Image.open(BytesIO(page.screenshot())).convert("RGB")
            frame.crop(HEAD).save(args.output / f"{name}-head.png")
            if name in ANCHORS:
                frame.save(args.output / f"{name}-full.png")
        browser.close()


if __name__ == "__main__":
    main()
