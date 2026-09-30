"""Capture fixed-time and pass-isolation views for R7.3A.3."""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"


def set_time(page, minute: int) -> None:
    page.get_by_role("slider", name="24H Preview").evaluate(
        "(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }",
        minute,
    )
    page.wait_for_timeout(180)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--motion", action="store_true")
    parser.add_argument("--query", default="")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        page = browser.new_page(viewport={"width": 2560, "height": 1440}, device_scale_factor=1)
        page.goto(URL + args.query, wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        labels = ("Leaves", "Blink on/off") if args.motion else ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off")
        for label in labels:
            page.get_by_label(label).uncheck()
        for minute in ((390, 1320) if args.motion else (300, 360, 390, 420, 480, 1320)):
            set_time(page, minute)
            if args.motion:
                page.wait_for_timeout(3200)
            name = f"{minute//60:02d}h{minute%60:02d}"
            page.screenshot(path=str(args.output / f"{name}-final.png"))
            if minute not in (390, 1320):
                continue
            for label, mode in (("Sky on/off", "sky-off"),
                                ("Directional Shading on/off", "directional-off"),
                                ("Post Processing on/off", "post-off"),
                                ("Bloom on/off", "bloom-off"),
                                ("Lighting on/off", "lighting-off")):
                page.get_by_label(label).uncheck()
                page.wait_for_timeout(80)
                page.screenshot(path=str(args.output / f"{name}-{mode}.png"))
                page.get_by_label(label).check()
        page.close()
        browser.close()


if __name__ == "__main__":
    main()
