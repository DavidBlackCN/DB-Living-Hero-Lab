"""Fixed viewport captures for the Dawn/Night long-hair light balance."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"
SIZE = (2560, 1440)
HAIR_CROPS = {
    "dawn": (1160, 360, 1670, 1160),
    "night": (1760, 340, 2290, 1130),
}


def capture(browser, output: Path, phase: str, mode: str) -> None:
    page = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]}, device_scale_factor=1)
    page.goto(URL + ("?hairSheen=off" if mode == "sheen-off" else ""), wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.get_by_role("button", name=phase, exact=True).click()
    for label in ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off"):
        page.get_by_label(label).uncheck()
    if mode == "directional-off":
        page.get_by_label("Directional Shading on/off").uncheck()
    elif mode == "base":
        page.get_by_label("Render view").select_option("base")
    elif mode == "detail-off":
        page.get_by_label("Lighting Detail on/off").uncheck()
    elif mode == "post-off":
        page.get_by_label("Post Processing on/off").uncheck()
    page.get_by_role("button", name="Hide", exact=True).click()
    page.screenshot(path=str(output / f"{phase.lower()}-{mode}.png"))
    page.close()


def crops(output: Path) -> None:
    for phase, box in HAIR_CROPS.items():
        modes = ("final", "directional-off", "detail-off", "post-off")
        panels = [Image.open(output / f"{phase}-{mode}.png").convert("RGB").crop(box) for mode in modes]
        contact = Image.new("RGB", (panels[0].width * len(panels), panels[0].height))
        for index, panel in enumerate(panels):
            contact.paste(panel, (index * panel.width, 0))
        contact.save(output / f"{phase}-diagnostic.jpg", quality=92)


def compare(before: Path, after: Path) -> None:
    for phase, box in HAIR_CROPS.items():
        old = Image.open(before / f"{phase}-final.png").convert("RGB").crop(box)
        new = Image.open(after / f"{phase}-final.png").convert("RGB").crop(box)
        sheet = Image.new("RGB", (old.width * 4, old.height * 2))
        sheet.paste(old.resize((old.width * 2, old.height * 2)), (0, 0))
        sheet.paste(new.resize((new.width * 2, new.height * 2)), (old.width * 2, 0))
        sheet.save(after / f"{phase}-before-after-2x.png")
        delta = np.abs(np.asarray(new, dtype=np.int16) - np.asarray(old, dtype=np.int16))
        print(f"{phase}: crop mean delta {delta.mean():.3f}, max {delta.max()}, changed pixels {(delta.max(axis=2) > 2).sum()}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--final-only", action="store_true")
    parser.add_argument("--compare-before", type=Path)
    parser.add_argument("--compare-only", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.compare_only:
        if not args.compare_before:
            parser.error("--compare-only requires --compare-before")
        compare(args.compare_before, args.output)
        return
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        for phase in (("Dawn", "Noon", "Dusk", "Night") if args.final_only else ("Dawn", "Night")):
            for mode in (("final",) if args.final_only else ("final", "directional-off", "detail-off", "post-off")):
                capture(browser, args.output, phase, mode)
        if not args.final_only:
            capture(browser, args.output, "Night", "sheen-off")
        browser.close()
    if not args.final_only:
        crops(args.output)
    if args.compare_before:
        compare(args.compare_before, args.output)


if __name__ == "__main__":
    main()
