"""Capture the independent Moon Direction and static R6.5D review frames."""

import argparse
import csv
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


TIMES = (
    ("dawn", 390), ("noon", 720), ("dusk", 1050),
    ("20h", 1200), ("22h", 1320), ("00h", 0),
    ("02h", 120), ("04h30", 270), ("24h", 1440),
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
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        slider = page.get_by_role("slider", name="24H Preview")
        moon_label = page.locator("small").filter(has_text="Moon Direction")
        solar_label = page.locator("label.range-control").filter(has_text=re.compile(r"^Direction\s+\d+"))
        rows = []
        dusk_solar_angle = 0
        for name, minutes in TIMES:
            slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
            page.wait_for_timeout(100)
            rows.append((name, minutes, moon_label.inner_text()))
            if name == "dusk":
                dusk_solar_angle = int(re.search(r"Direction\s+(\d+)", solar_label.inner_text()).group(1))
            page.screenshot(path=str(args.output / f"{name}.png"))
        browser.close()
    readings = {name: tuple(map(int, re.search(r"Moon Direction\s+(\d+).*Elevation\s+(\d+)", value).groups()))
                for name, _, value in rows}
    assert dusk_solar_angle > 90 and readings["20h"][0] < 90, "Dusk sun and early Moon must be on opposite sides"
    assert all(readings[a][0] < readings[b][0] for a, b in zip(("20h", "22h", "00h", "02h"), ("22h", "00h", "02h", "04h30")))
    assert readings["20h"][1] < readings["00h"][1] and readings["04h30"][1] < readings["00h"][1]
    assert readings["00h"] == readings["24h"], "Moon direction must wrap at midnight"
    with (args.output / "moon-directions.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(("name", "minutes", "debug_readout"))
        writer.writerows(rows)
    for row in rows:
        print(*row)


if __name__ == "__main__":
    main()
