"""Browser checks for the R2B controller and frozen R2A anchor images."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/validation/r2b-time-controller"
BASELINE = ROOT / "docs/validation/r3-2c-final"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PRESETS = {"Dawn": 390, "Noon": 720, "Dusk": 1050, "Night": 1320}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=EDGE,
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.clock.install(time=datetime(2026, 9, 24, 23, 30, 0))
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Hair Motion on/off").uncheck()
        page.get_by_label("Blink on/off").uncheck()
        page.get_by_label("Leaves").uncheck()
        page.get_by_label("Render view").select_option("lit")
        output = page.locator(".time-control output")
        mode = page.locator(".time-mode")
        slider = page.locator(".time-control input[type=range]")

        assert output.inner_text() == "23:30"
        assert mode.inner_text() == "Time: Realtime"
        page.clock.run_for(2000)
        assert output.inner_text() == "23:30"

        for name, minutes in PRESETS.items():
            page.get_by_role("button", name=name, exact=True).click()
            assert int(slider.input_value()) == minutes
            assert mode.inner_text() == "Time: Manual"
            page.wait_for_timeout(100)
            shot = OUT / f"{name.lower()}.png"
            image_bytes = page.screenshot()
            if not shot.exists():
                shot.write_bytes(image_bytes)
            current = np.asarray(Image.open(BytesIO(image_bytes)).convert("RGB"))[:, 310:]
            baseline_name = "night-after.png" if name == "Night" else f"{name.lower()}.png"
            frozen = np.asarray(Image.open(BASELINE / baseline_name).convert("RGB"))[:, 310:]
            assert current.shape == frozen.shape
            assert np.max(np.abs(current.astype(np.int16) - frozen.astype(np.int16))) <= 1, name

        page.clock.run_for(2000)
        assert output.inner_text() == "22:00", "Manual time must stay frozen"
        page.get_by_role("button", name="Back to now").click()
        assert mode.inner_text() == "Time: Realtime"
        assert output.inner_text() == "23:30"

        def select(minutes: int) -> None:
            slider.evaluate(
                "(element, value) => { element.value = String(value); element.dispatchEvent(new Event('input', { bubbles: true })); }",
                minutes,
            )
            assert mode.inner_text() == "Time: Manual"
            assert int(slider.input_value()) == minutes

        for start in (0, 390, 1050, 1320):
            select(start)
            page.get_by_role("button", name="Play", exact=True).click()
            assert mode.inner_text() == "Time: Playing"
            page.clock.run_for(5000)
            actual = float(page.evaluate("document.querySelector('.time-control input').value"))
            expected = (start + 120) % 1440
            assert min(abs(actual - expected), 1440 - abs(actual - expected)) <= 2, (start, actual, expected)
            page.get_by_role("button", name="Pause", exact=True).click()
            assert mode.inner_text() == "Time: Manual"
            frozen = output.inner_text()
            page.clock.run_for(1000)
            assert output.inner_text() == frozen

        select(1439)
        before_midnight = OUT / "before-midnight.png"
        if not before_midnight.exists():
            page.screenshot(path=str(before_midnight))
        page.get_by_role("button", name="Play", exact=True).click()
        page.clock.run_for(100)
        assert int(slider.input_value()) in (0, 1, 2)
        page.get_by_role("button", name="Pause", exact=True).click()
        select(0)
        midnight = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"))[:, 310:]
        select(1440)
        end = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"))[:, 310:]
        assert np.array_equal(midnight, end), "00:00 and 24:00 must render identically"

        select(1320)
        page.get_by_role("button", name="Play", exact=True).click()
        page.clock.run_for(1000)
        before_hide = float(page.evaluate("document.querySelector('.time-control input').value"))
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
        page.clock.run_for(5000)
        assert abs(float(page.evaluate("document.querySelector('.time-control input').value")) - before_hide) <= 1
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange'))")
        page.clock.run_for(1000)
        resumed = float(page.evaluate("document.querySelector('.time-control input').value"))
        assert 20 <= resumed - before_hide <= 26, (before_hide, resumed)
        page.get_by_role("button", name="Pause", exact=True).click()

        page.get_by_role("button", name="Back to now").click()
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
        page.clock.run_for(60_000)
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange'))")
        assert output.inner_text() == "23:31"

        reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        reduced.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        reduced.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        assert reduced.get_by_role("button", name="Play", exact=True).is_disabled()
        assert reduced.locator(".time-mode").inner_text() == "Time: Realtime"
        reduced.close()
        browser.close()
    print("R2B browser controller, visibility, reduced motion, and four frozen anchors: passed")


if __name__ == "__main__":
    main()
