"""Capture repeatable WebGL hair-motion review frames and optional full-composition holds."""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--strength", type=float, default=1)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--gif", action="store_true")
    parser.add_argument("--head", action="store_true", help="Crop dynamic review to the head and nearby hair")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader", "--disable-web-security"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name="Noon", exact=True).click()
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Blink on/off").uncheck()
        page.get_by_label("Leaves").uncheck()
        slider = page.locator("label.range-control").filter(has_text="Hair Strength").locator("input")
        slider.evaluate("(element, value) => { element.value=String(value); element.dispatchEvent(new Event('input',{bubbles:true})); }", args.strength)
        page.get_by_label("Show Hair Region").check()
        page.screenshot(path=str(args.output / "region-overlay.png"))
        page.get_by_label("Show Hair Region").uncheck()
        page.screenshot(path=str(args.output / "t0.png"))
        page.wait_for_timeout(2200)
        page.screenshot(path=str(args.output / "t2.png"))
        page.wait_for_timeout(2200)
        page.screenshot(path=str(args.output / "t4.png"))
        if args.gif:
            frames = []
            crop = (785, 15, 1195, 385) if args.head else (730, 190, 1280, 630)
            for _ in range(32):
                page.wait_for_timeout(190)
                frames.append(Image.open(BytesIO(page.screenshot())).convert("RGB").crop(crop).quantize(colors=96))
            frames[0].save(args.output / "normal-preview.gif", save_all=True, append_images=frames[1:], duration=190, loop=0, optimize=True)
        page.get_by_label("Breathing on/off").check()
        page.wait_for_timeout(1800)
        page.screenshot(path=str(args.output / "breathing-hair.png"))
        page.get_by_label("Blink on/off").check()
        page.get_by_role("button", name="Preview Blink").click()
        page.screenshot(path=str(args.output / "blink-hair.png"))
        if args.head:
            page.get_by_label("Render view").select_option("base")
            page.get_by_role("button", name="Preview Blink").click()
            page.screenshot(path=str(args.output / "base-blink-hair.png"))
            page.get_by_label("Render view").select_option("lit")
        page.get_by_label("Leaves").check()
        page.get_by_role("button", name="Night", exact=True).click()
        page.wait_for_timeout(1800)
        page.screenshot(path=str(args.output / "night-full.png"))
        if args.gif:
            frames = []
            for _ in range(32):
                page.wait_for_timeout(190)
                frames.append(Image.open(BytesIO(page.screenshot())).convert("RGB").crop(crop).quantize(colors=96))
            frames[0].save(args.output / "full-composition.gif", save_all=True, append_images=frames[1:], duration=190, loop=0, optimize=True)
        if args.full:
            for name in ("Dawn", "Noon", "Dusk", "Night"):
                page.get_by_role("button", name=name, exact=True).click()
                page.wait_for_timeout(22000)
                page.screenshot(path=str(args.output / f"{name.lower()}.png"))
        browser.close()


if __name__ == "__main__":
    main()
