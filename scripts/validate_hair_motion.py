"""Focused R4 browser regression for motion locality and lifecycle."""

from io import BytesIO
from pathlib import Path

import numpy as np
import cv2
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MASK = np.asarray(Image.open(ROOT / "public/assets/hero/motion/hair-motion-mask.png"))
assert MASK.shape == (941, 1672, 4)
assert np.count_nonzero(MASK[:245, :, :2]) == 0, "Lower hair roots changed"
assert np.count_nonzero(MASK[650:, :, :2]) == 0, "Lower scene must stay protected"
assert MASK[235, 1150, 2] > 220 and MASK[90, 1160, 2] > 220, "Face/hat need one head mass"
assert MASK[210, 1125, 3] == 0 and MASK[233, 1190, 3] == 0, "Blink patches must avoid secondary hair"
assert np.max(MASK[280:390, 1010:1080, 3]) > 180, "Image-left side hair is missing"
assert np.max(MASK[290:400, 1240:1320, 3]) > 180, "Image-right side hair is missing"


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
    assert np.count_nonzero(delta[160:285, 945:1090] > 2) > 1000, "Head mass remained static"
    gray_start = cv2.cvtColor(start.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    gray_later = cv2.cvtColor(later.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    face_shift, _ = cv2.phaseCorrelate(gray_start[220:280, 990:1060], gray_later[220:280, 990:1060])
    hat_shift, _ = cv2.phaseCorrelate(gray_start[45:145, 930:1100], gray_later[45:145, 930:1100])
    assert abs(face_shift[0] - hat_shift[0]) < 1.5 and abs(face_shift[1] - hat_shift[1]) < 1.5, "Head features separated"
    assert np.array_equal(start[730:850, 320:760], later[730:850, 320:760]), "Background moved"
    page.get_by_label("Render view").select_option("normal")
    normal_start = frame(page)
    page.wait_for_timeout(1800)
    normal_delta = np.abs(frame(page) - normal_start)
    print("Normal motion pixels", np.count_nonzero(normal_delta[320:610, 760:1260] > 1))
    assert np.count_nonzero(normal_delta[320:610, 760:1260] > 1) > 100, "Normal map did not follow hair UV"
    page.get_by_label("Render view").select_option("lit")
    page.get_by_label("Blink on/off").check()
    for view in ("base", "lit"):
        page.get_by_label("Render view").select_option(view)
        page.get_by_role("button", name="Preview Blink").click()
        page.locator(".blink-layer.is-closed").wait_for(timeout=1000)
        if view == "base":
            assert page.locator(".blink-eye").count() == 0, "Moving Base head must use registered shader Blink"
        closed = frame(page)
        page.wait_for_timeout(330)
        opened = frame(page)
        assert np.count_nonzero(np.abs(closed[170:255, 955:1090] - opened[170:255, 955:1090]) > 4) > 500, f"{view} Blink missing"
    page.get_by_label("Blink on/off").uncheck()
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

print("Hair/head masks, rigid head, Base/Lit Blink, Normal UV, background, hidden/reduced/static: passed")
