"""Capture the four fixed Runtime Lighting anchors from the running Vite page."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


ANCHORS = ("Dawn", "Noon", "Dusk", "Night")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:5173/")
    parser.add_argument("--extras", action="store_true", help="Also capture intermediate slider times")
    parser.add_argument("--timeline", action="store_true", help="Capture the 12 requested 24H checkpoints")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader", "--disable-web-security"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto(args.url, wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_label("Render view").select_option("lit")
        for name in ANCHORS:
            page.get_by_role("button", name=name, exact=True).click()
            page.wait_for_timeout(300)
            page.screenshot(path=str(args.output / f"{name.lower()}.png"))
        if args.extras or args.timeline:
            slider = page.locator(".time-control input[type=range]")
            checkpoints = (0, 120, 270, 330, 390, 480, 720, 960, 1050, 1200, 1320, 1440) if args.timeline else (0, 540, 900, 1200, 1440)
            for minutes in checkpoints:
                slider.evaluate("(element, value) => { element.value = String(value); element.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
                page.wait_for_timeout(300)
                page.screenshot(path=str(args.output / f"{minutes // 60:02d}{minutes % 60:02d}.png"))
        print(f"Captured Lit/WebGL2 + Sky at {args.output}")
        browser.close()


if __name__ == "__main__":
    main()
