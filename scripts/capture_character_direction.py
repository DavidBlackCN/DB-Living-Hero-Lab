"""Capture deterministic four-phase character lighting and Night diagnostics."""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


SIZE = (2048, 1033)
PHASES = (("dawn", 390), ("noon", 720), ("dusk", 1050), ("night", 1320))
HEAD_BOX = (1050, 0, 1620, 500)
FIGURE_BOX = (930, 0, 1770, 1033)
EDGE_BOX = (950, 0, 1210, 420)


def capture(page, output: Path, name: str) -> None:
    frame = Image.open(BytesIO(page.screenshot())).convert("RGB")
    frame.save(output / f"{name}-full.png")
    for suffix, box in (("head", HEAD_BOX), ("figure", FIGURE_BOX), ("head-left-edge", EDGE_BOX)):
        frame.crop(box).save(output / f"{name}-{suffix}.png")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--diagnose", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        page.get_by_label("Render view").select_option("lit")
        page.add_style_tag(content=".debug-panel { opacity: 0 !important; }")
        slider = page.locator(".time-control input[type=range]")
        for phase, minutes in PHASES:
            slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
            page.wait_for_timeout(180)
            capture(page, args.output, phase)
        if args.diagnose:
            for name, label in (("no-sky", "Sky on/off"), ("no-post", "Post Processing on/off"),
                                ("no-direction", "Directional Shading on/off")):
                checkbox = page.get_by_label(label)
                checkbox.uncheck()
                page.wait_for_timeout(180)
                capture(page, args.output, f"night-{name}")
                checkbox.check()
        browser.close()
    sheet = Image.new("RGB", SIZE)
    for index, (phase, _) in enumerate(PHASES):
        frame = Image.open(args.output / f"{phase}-full.png")
        sheet.paste(frame.resize((SIZE[0] // 2, SIZE[1] // 2)),
                    ((index % 2) * SIZE[0] // 2, (index // 2) * SIZE[1] // 2))
    ImageDraw.Draw(sheet).text((8, 8), "DAWN / NOON / DUSK / NIGHT", fill="white")
    sheet.save(args.output / "four-phase-contact.png")


if __name__ == "__main__":
    main()
