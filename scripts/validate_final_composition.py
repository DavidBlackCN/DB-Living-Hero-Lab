"""Check the Lit composition, frozen baselines, and local Blink material response."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/validation/r3-final-composition"
FROZEN = ROOT / "docs/validation/r2b-time-controller"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PHASES = ("Dawn", "Noon", "Dusk", "Night")
EYES = (slice(165, 270), slice(945, 1115))


def screenshot(page) -> np.ndarray:
    return np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        assert page.get_by_label("Render view").input_value() == "lit"
        for label in ("Lighting on/off", "Sky on/off", "Breathing on/off", "Blink on/off", "Leaves"):
            assert page.get_by_label(label).is_checked(), label
        page.evaluate("""() => {
            window.blinkCloses = 0;
            new MutationObserver(() => { if (document.querySelector('.blink-layer')?.classList.contains('is-closed')) window.blinkCloses++ })
                .observe(document.querySelector('.blink-layer'), { attributes: true, attributeFilter: ['class'] });
        }""")

        for phase in PHASES:
            page.get_by_role("button", name=phase, exact=True).click()
            page.wait_for_timeout(400)
            page.screenshot(path=str(OUT / f"{phase.lower()}.png"))
            if phase == "Night":
                clip = []
                for index in range(20):
                    page.wait_for_timeout(900)
                    if index == 9:
                        page.get_by_role("button", name="Preview Blink").click()
                        assert page.locator(".blink-layer.is-closed").count() == 1
                        page.screenshot(path=str(OUT / "night-full-closed.png"))
                    clip.append(Image.fromarray(screenshot(page).astype(np.uint8)).resize((720, 450)).quantize(colors=128))
                clip[0].save(OUT / "lit-full-composition.gif", save_all=True, append_images=clip[1:], duration=900, loop=0, optimize=True)
            else:
                page.wait_for_timeout(18000)
            assert page.get_by_text("Mode: WebGL2").is_visible()
            assert page.locator(".leaves-canvas").count() == 1
            assert page.locator(".blink-layer").count() == 1
        print(f"Automatic Lit Blink closures during four 18-second views: {page.evaluate('window.blinkCloses')}")
        assert page.evaluate("window.blinkCloses") >= 4

        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
        page.wait_for_timeout(250)
        assert page.locator(".blink-layer.is-closed").count() == 0
        hidden_frame = screenshot(page)[:, 310:]
        page.wait_for_timeout(1800)
        assert np.array_equal(hidden_frame, screenshot(page)[:, 310:]), "Hidden composition kept animating"
        page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange'))")
        page.wait_for_timeout(1200)
        assert not np.array_equal(hidden_frame, screenshot(page)[:, 310:]), "Visible composition did not resume"

        # Freeze dynamic layers to compare the unchanged R2A/R2B artwork output.
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Blink on/off").uncheck()
        page.get_by_label("Leaves").uncheck()
        for phase in PHASES:
            page.get_by_role("button", name=phase, exact=True).click()
            page.wait_for_timeout(70)
            current = screenshot(page)[:, 310:]
            frozen = np.asarray(Image.open(FROZEN / f"{phase.lower()}.png").convert("RGB"), dtype=np.int16)[:, 310:]
            assert np.max(np.abs(current - frozen)) <= 1, f"Frozen {phase} regression"

        # Close each eye inside the Lit shader while the clock is paused. The
        # unchanged Normal and the phase's lighting are still applied afterward.
        page.get_by_label("Blink on/off").check()
        page.clock.pause_at(datetime(2026, 9, 25, 12, 0, 0))
        for phase in PHASES:
            page.get_by_role("button", name=phase, exact=True).click()
            opened = screenshot(page)
            page.get_by_role("button", name="Preview Blink").click()
            assert page.locator(".blink-layer.is-closed").count() == 1
            closed = screenshot(page)
            Image.fromarray(closed.astype(np.uint8)).save(OUT / f"{phase.lower()}-closed.png")
            changed = np.abs(closed[EYES] - opened[EYES])
            assert changed.mean() > 0.1, f"Lit {phase} closed eyes are not visible"
            outside = np.abs(closed - opened)
            outside[EYES] = 0
            assert np.max(outside[:, 310:]) <= 1, f"Lit {phase} blink changed pixels outside the eyes"
            print(f"{phase} eye-region mean RGB change: {changed.mean():.3f}")
            page.clock.run_for(160)
            assert page.locator(".blink-layer.is-closed").count() == 0
            assert np.max(np.abs(screenshot(page)[:, 310:] - opened[:, 310:])) <= 1

        # Static quality and reduced motion keep static/Lit semantics.
        page.get_by_label("Quality").select_option("static")
        assert page.locator(".leaves-canvas").count() == 0
        assert not page.get_by_label("Blink on/off").is_checked()
        assert page.locator(".blink-layer.is-closed").count() == 0
        page.close()
        reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        reduced.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        reduced.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        assert reduced.locator(".leaves-canvas").count() == 0
        assert not reduced.get_by_label("Breathing on/off").is_checked()
        assert not reduced.get_by_label("Blink on/off").is_checked()
        reduced.close()
        browser.close()
    print("R3.1 full Lit composition and frozen visual regression: passed")


if __name__ == "__main__":
    main()
