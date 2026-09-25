"""Capture and measure Breathing v1 on the real WebGL2 page."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASELINE = Path(__file__).resolve().parents[1] / "docs/validation/r3-2c-final/noon.png"


def frame(page) -> np.ndarray:
    return np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--strength", type=float, default=1.0)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_label("Hair Motion on/off").uncheck()
        page.get_by_label("Blink on/off").uncheck()
        page.get_by_label("Leaves").uncheck()
        page.get_by_label("Lighting Detail on/off").uncheck()
        page.get_by_label("Post Processing on/off").uncheck()
        page.get_by_role("button", name="Noon", exact=True).click()
        page.get_by_label("Show Breathing Region").check()
        page.screenshot(path=str(args.output / "region.png"))
        page.get_by_label("Show Breathing Region").uncheck()
        strength = page.get_by_label("Breathing Strength")
        strength.evaluate("(element, value) => { element.value = String(value); element.dispatchEvent(new Event('input', { bubbles: true })); }", args.strength)
        page.get_by_label("Breathing on/off").uncheck()
        off = frame(page)
        page.screenshot(path=str(args.output / "off.png"))
        page.get_by_label("Breathing on/off").check()
        frames = []
        for index in range(20):
            page.wait_for_timeout(900)
            image = frame(page)
            frames.append(image)
            if index in (0, 5, 10, 15, 19):
                Image.fromarray(image.astype(np.uint8)).save(args.output / f"phase-{index}.png")
        Image.fromarray(frames[0][280:610, 850:1170].astype(np.uint8)).save(args.output / "torso-first.png")
        Image.fromarray(frames[10][280:610, 850:1170].astype(np.uint8)).save(args.output / "torso-later.png")
        torso_clip = [Image.fromarray(image[280:610, 850:1170].astype(np.uint8)).quantize(colors=128) for image in frames]
        torso_clip[0].save(args.output / "torso-18s.gif", save_all=True, append_images=torso_clip[1:],
            duration=900, loop=0, optimize=True)
        torso = (slice(335, 590), slice(905, 1135))
        face = (slice(95, 285), slice(930, 1120))
        stone = (slice(750, 850), slice(500, 850))
        for label, area in (("torso", torso), ("face", face), ("stone", stone)):
            deltas = [float(np.abs(image[area] - off[area]).mean()) for image in frames]
            print(f"{label}: mean RGB delta min={min(deltas):.3f} max={max(deltas):.3f}")
        frozen = np.asarray(Image.open(BASELINE).convert("RGB"), dtype=np.int16)
        assert np.array_equal(off[:, 310:], frozen[:, 310:]), "Breathing OFF must match frozen R2B pixels"
        assert all(np.max(np.abs(image[face] - off[face])) <= 1 for image in frames), "Head and eyes must remain still"
        assert all(np.array_equal(image[stone], off[stone]) for image in frames), "Stone must remain still"
        for name in ("Dawn", "Noon", "Dusk", "Night"):
            page.get_by_role("button", name=name, exact=True).click()
            page.wait_for_timeout(300)
            page.screenshot(path=str(args.output / f"{name.lower()}.png"))
            page.wait_for_timeout(5200)
            assert page.get_by_text("Mode: WebGL2").is_visible()
        page.get_by_label("Render view").select_option("normal")
        page.wait_for_timeout(5200)
        page.screenshot(path=str(args.output / "normal.png"))
        page.get_by_label("Render view").select_option("base")
        page.get_by_label("Blink on/off").check()
        page.get_by_label("Leaves").check()
        assert page.get_by_label("Blink on/off").is_enabled()
        assert page.get_by_label("Leaves").is_enabled()
        page.get_by_role("button", name="Preview Blink").click()
        assert page.locator(".blink-eye.is-closed").count() == 2
        page.screenshot(path=str(args.output / "blink-preview.png"))
        page.wait_for_timeout(5200)
        assert "FPS" in page.locator("footer").inner_text()
        page.screenshot(path=str(args.output / "base-with-blink-leaves.png"))

        page.get_by_label("Render view").select_option("lit")
        page.get_by_label("Breathing on/off").check()
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
        before_hide = frame(page)
        page.wait_for_timeout(1800)
        hidden = frame(page)
        assert np.array_equal(before_hide[:, 310:], hidden[:, 310:]), "Hidden breathing frame changed"
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange'))")
        page.wait_for_timeout(1200)
        assert not np.array_equal(hidden[:, 310:], frame(page)[:, 310:]), "Breathing did not resume"
        reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        reduced.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        reduced.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        assert reduced.get_by_label("Breathing on/off").is_disabled()
        assert reduced.get_by_label("Breathing Strength").is_disabled()
        reduced.close()
        browser.close()
    print(f"Breathing captures saved to {args.output}")


if __name__ == "__main__":
    main()
