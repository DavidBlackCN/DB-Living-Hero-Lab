"""Record Lit/Sky-on 24H luminance and an hourly visual contact sheet."""

from __future__ import annotations

import argparse
import csv
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


def mean_luminance(linear: np.ndarray, boxes: tuple[tuple[int, int, int, int], ...]) -> float:
    pixels = np.concatenate([linear[y0:y1, x0:x1].reshape(-1, 3) for x0, y0, x1, y1 in boxes])
    return float((pixels @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).mean())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:5173/")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (1920, 1200))
    rows: list[dict[str, float | str]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto(args.url, wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Render view").select_option("lit")
        slider = page.locator(".time-control input[type=range]")

        for minutes in range(0, 1441, 15):
            slider.evaluate("(element, value) => { element.value = String(value); element.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
            page.wait_for_timeout(50)
            image = Image.open(BytesIO(page.screenshot())).convert("RGB")
            rgb = np.asarray(image, dtype=np.float32) / 255.0
            linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
            rows.append({
                "time": f"{minutes // 60:02d}:{minutes % 60:02d}",
                "artwork": mean_luminance(linear, ((310, 0, 1440, 900),)),
                "face": mean_luminance(linear, ((930, 90, 1110, 300),)),
                "white_shirt": mean_luminance(linear, ((730, 300, 920, 650), (1130, 300, 1245, 670))),
            })
            if minutes % 60 == 0:
                index = minutes // 60
                sheet.paste(image.resize((384, 240)), ((index % 5) * 384, (index // 5) * 240))

        browser.close()

    with (args.output / "luminance-15min.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("time", "artwork", "face", "white_shirt"))
        writer.writeheader()
        writer.writerows(rows)
    sheet.save(args.output / "hourly-contact.png")

    by_time = {row["time"]: row for row in rows}
    noon = float(by_time["12:00"]["artwork"])
    daylight_peak = max((row for row in rows if "06:30" <= row["time"] <= "17:30"), key=lambda row: float(row["artwork"]))
    night_face = float(by_time["22:00"]["face"])
    evening_face_min = min(float(row["face"]) for row in rows if "17:30" <= row["time"] <= "20:00")
    print(f"Noon artwork={noon:.5f}; daylight peak={daylight_peak['time']} {float(daylight_peak['artwork']):.5f}")
    print(f"Evening minimum face={evening_face_min:.5f}; Night 22:00 face={night_face:.5f}")
    assert float(daylight_peak["artwork"]) <= noon + 0.001
    assert evening_face_min >= night_face - 0.001
    assert abs(float(by_time["00:00"]["artwork"]) - float(by_time["24:00"]["artwork"])) < 0.0001


if __name__ == "__main__":
    main()
