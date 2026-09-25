"""Capture comparable static directional-shading frames through the debug UI."""

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--full", action="store_true")
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
        slider = page.get_by_role("slider", name="24H Preview")
        directional = page.get_by_label("Directional Shading on/off") if args.compare else None
        for name, minutes in (("06h30", 390), ("09h", 540), ("12h", 720), ("15h", 900),
                              ("17h30", 1050), ("22h", 1320), ("00h", 0), ("02h", 120),
                              ("04h30", 270), ("24h", 1440)):
            slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
            page.wait_for_timeout(100)
            if directional:
                directional.uncheck()
                page.screenshot(path=str(args.output / f"{name}-off.png"))
                directional.check()
            page.screenshot(path=str(args.output / f"{name}.png"))
        if args.full:
            for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
                page.get_by_label(label).check()
            for name, minutes in (("dawn", 390), ("noon", 720), ("dusk", 1050), ("night", 1320)):
                slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
                page.wait_for_timeout(4000)
                page.screenshot(path=str(args.output / f"{name}-combined.png"))
        browser.close()


if __name__ == "__main__":
    main()
