"""Audit five-minute Dawn/Dusk lighting parameters and frozen visual frames."""

import argparse
import csv
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


TIMES = tuple(range(320, 441, 5)) + tuple(range(1000, 1221, 5))
SAMPLES = (330, 360, 390, 420, 1020, 1050, 1080, 1110, 1140, 1170, 1200, 1220)
BOXES = {
    "face": (930, 95, 1110, 300),
    "figure": (720, 65, 1290, 890),
    "architecture": (355, 75, 715, 700),
    "sky": (1220, 0, 1420, 230),
}


def luminance(frame: np.ndarray, box: tuple[int, int, int, int]) -> float:
    x0, y0, x1, y1 = box
    return float(np.mean(frame[y0:y1, x0:x1] @ np.array([0.2126, 0.7152, 0.0722])))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    samples = []
    prior = None

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
        page.add_style_tag(content=".debug-panel { visibility: hidden !important; }")
        state = page.evaluate("""async times => {
          const [{lightingFor}, {skyFor}, {moonDirectionFor}] = await Promise.all([
            import('/src/config/lighting.ts'), import('/src/config/sky.ts'), import('/src/config/moonlight.ts')
          ]);
          return times.map(minutes => ({minutes, lighting: lightingFor(minutes), sky: skyFor(minutes), moon: moonDirectionFor(minutes)}));
        }""", TIMES)
        slider = page.locator(".time-control input[type=range]")
        for sample in state:
            minutes = sample["minutes"]
            slider.evaluate(
                "(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }",
                minutes,
            )
            page.wait_for_timeout(55)
            frame = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.float32)
            lighting = sample["lighting"]
            sky = sample["sky"]
            night_weight = (1 - sky["mix"] if sky["first"] == "night" else 0) + (sky["mix"] if sky["second"] == "night" else 0)
            row = {
                "time": f"{minutes // 60:02d}:{minutes % 60:02d}",
                "intensity": lighting["intensity"],
                "ambient": lighting["ambientIntensity"],
                "exposure": lighting["exposureStops"],
                "sky_night": night_weight,
                "sun_x": lighting["direction"]["x"],
                "moon_x": sample["moon"]["x"],
            }
            for name, box in BOXES.items():
                row[name] = luminance(frame, box)
                x0, y0, x1, y1 = box
                row[f"{name}_step"] = float(np.mean(np.abs(frame[y0:y1, x0:x1] - prior[y0:y1, x0:x1]))) if prior is not None else 0.0
            rows.append(row)
            prior = frame if minutes != 440 else None
            if minutes in SAMPLES:
                image = Image.fromarray(frame.astype(np.uint8))
                image.save(args.output / f"{minutes // 60:02d}h{minutes % 60:02d}.png")
                samples.append((minutes, image.resize((480, 300))))
        browser.close()

    with (args.output / "twilight-5min.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    sheet = Image.new("RGB", (1920, 900))
    draw = ImageDraw.Draw(sheet)
    for index, (minutes, image) in enumerate(samples):
        x, y = (index % 4) * 480, (index // 4) * 300
        sheet.paste(image, (x, y))
        draw.rectangle((x, y, x + 70, y + 21), fill=(20, 24, 35))
        draw.text((x + 5, y + 5), f"{minutes // 60:02d}:{minutes % 60:02d}", fill="white")
    sheet.save(args.output / "twilight-contact.png")
    for name in BOXES:
        peaks = sorted(rows, key=lambda row: row[f"{name}_step"], reverse=True)[:4]
        print(name, ", ".join(f"{row['time']}={row[f'{name}_step']:.2f}" for row in peaks))


if __name__ == "__main__":
    main()
