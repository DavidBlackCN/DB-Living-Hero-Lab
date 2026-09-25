"""Focused R4 browser regression for motion locality and lifecycle."""

from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MASK = np.asarray(Image.open(ROOT / "public/assets/hero/motion/hair-motion-mask.png"))
assert MASK.shape == (941, 1672, 4)
assert np.count_nonzero(MASK[:245, :, :2]) == 0, "Head/root area must stay protected"
assert np.count_nonzero(MASK[650:, :, :2]) == 0, "Lower scene must stay protected"


def frame(page) -> np.ndarray:
    return np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=True,
        args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader", "--disable-web-security"],
    )
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.get_by_role("button", name="Noon", exact=True).click()
    page.get_by_label("Breathing on/off").uncheck()
    page.get_by_label("Blink on/off").uncheck()
    page.get_by_label("Leaves").uncheck()
    page.get_by_label("Hair Motion on/off").uncheck()
    off = frame(page)
    page.wait_for_timeout(1200)
    assert np.array_equal(off[:, 310:], frame(page)[:, 310:]), "Hair OFF must be on demand"
    page.get_by_label("Hair Motion on/off").check()
    start = frame(page)
    page.wait_for_timeout(2400)
    later = frame(page)
    delta = np.abs(later - start)
    assert np.count_nonzero(delta[320:610, 760:1260] > 2) > 1000, "Hair should visibly move"
    assert np.array_equal(start[135:285, 940:1100], later[135:285, 940:1100]), "Face/eyes moved"
    assert np.array_equal(start[730:850, 320:760], later[730:850, 320:760]), "Background moved"
    page.get_by_label("Render view").select_option("normal")
    normal_start = frame(page)
    page.wait_for_timeout(1800)
    normal_delta = np.abs(frame(page) - normal_start)
    print("Normal motion pixels", np.count_nonzero(normal_delta[320:610, 760:1260] > 1))
    assert np.count_nonzero(normal_delta[320:610, 760:1260] > 1) > 100, "Normal map did not follow hair UV"
    page.get_by_label("Render view").select_option("lit")
    page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: true }); document.dispatchEvent(new Event('visibilitychange'))")
    hidden = frame(page)
    page.wait_for_timeout(1100)
    assert np.array_equal(hidden[:, 310:], frame(page)[:, 310:]), "Hidden hair frame changed"
    page.evaluate("Object.defineProperty(document, 'hidden', { configurable: true, value: false }); document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_timeout(1300)
    assert not np.array_equal(hidden[:, 310:], frame(page)[:, 310:]), "Hair did not resume"
    reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    reduced.goto("http://127.0.0.1:5173/", wait_until="networkidle")
    reduced.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    assert reduced.get_by_label("Hair Motion on/off").is_disabled()
    assert reduced.get_by_label("Hair Strength").is_disabled()
    reduced.close()
    page.get_by_label("Quality").select_option("static")
    assert page.get_by_label("Hair Motion on/off").is_disabled()
    assert page.get_by_text("Mode: static").is_visible()
    browser.close()

print("Hair mask, WebGL motion locality, Normal UV, hidden/reduced/static: passed")
