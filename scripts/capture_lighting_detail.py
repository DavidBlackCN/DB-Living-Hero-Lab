"""Capture deterministic four-phase R5 Lighting Detail A/B frames."""

import argparse
import json
import re
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--full", action="store_true", help="Also hold the complete animated composition")
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
        for name in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(name).uncheck()
        detail = page.get_by_label("Lighting Detail on/off")
        for phase in ("Dawn", "Noon", "Dusk", "Night"):
            page.get_by_role("button", name=phase, exact=True).click()
            detail.uncheck()
            page.screenshot(path=str(args.output / f"{phase.lower()}-before.png"))
            detail.check()
            page.screenshot(path=str(args.output / f"{phase.lower()}-after.png"))
        if args.full:
            page.get_by_label("Breathing on/off").check()
            page.get_by_label("Hair Motion on/off").check()
            page.get_by_label("Blink on/off").check()
            page.get_by_label("Leaves").check()
            frame_times = []
            for phase in ("Dawn", "Noon", "Dusk", "Night"):
                page.get_by_role("button", name=phase, exact=True).click()
                page.wait_for_timeout(22000)
                page.screenshot(path=str(args.output / f"{phase.lower()}-combined.png"))
                if phase in ("Noon", "Dusk", "Night"):
                    frames = []
                    for _ in range(24):
                        page.wait_for_timeout(180)
                        image = Image.open(BytesIO(page.screenshot())).convert("RGB")
                        frames.append(image.crop((760, 35, 1300, 660)).resize((432, 500)).quantize(colors=96))
                        status = page.locator(".debug-panel footer").inner_text()
                        match = re.search(r"Base frame: ([\d.]+) ms", status)
                        if match:
                            frame_times.append(float(match.group(1)))
                    frames[0].save(args.output / f"{phase.lower()}-motion.gif", save_all=True,
                                   append_images=frames[1:], duration=180, loop=0, optimize=True)
            page.get_by_role("button", name="Preview Blink").click()
            page.locator(".blink-layer.is-closed").wait_for(timeout=1000)
            page.screenshot(path=str(args.output / "night-blink-closed.png"))
            (args.output / "frame-times.json").write_text(json.dumps(frame_times), encoding="utf-8")
        browser.close()


if __name__ == "__main__":
    main()
