"""Focused R5 material registration, A/B, and closed-eye checks."""

from datetime import datetime
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MASK = np.asarray(Image.open(ROOT / "public/assets/hero/material/material-mask.png"))
assert MASK.shape == (941, 1672, 4)
assert not np.any(MASK[:, :, 3]), "Unused material alpha must stay clear"
assert np.max(MASK[230:275, 1100:1200, 0]) == 255, "Face core missing"
assert np.max(MASK[110:170, 1100:1220, 1]) == 255, "Crown core missing"
assert np.max(MASK[205:245, 1115:1200, 2]) == 255, "Iris support missing"
assert not np.any(MASK[350:, :, :3]), "Material mask leaked into clothing or lower scene"


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
    for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
        page.get_by_label(label).uncheck()
    page.get_by_role("button", name="Noon", exact=True).click()
    detail = page.get_by_label("Lighting Detail on/off")
    detail.uncheck()
    baseline = frame(page)
    detail.check()
    polished = frame(page)
    detail.uncheck()
    assert np.array_equal(baseline[:, 310:], frame(page)[:, 310:]), "Detail OFF failed to restore baseline"
    assert np.array_equal(baseline[340:, 310:], polished[340:, 310:]), "Material response leaked into clothing or scene"
    assert np.array_equal(baseline[:340, 310:850], polished[:340, 310:850]), "Material response leaked into architecture"
    crown = np.abs(polished[110:185, 920:1110] - baseline[110:185, 920:1110]).mean()
    face = np.abs(polished[190:300, 950:1100] - baseline[190:300, 950:1100]).mean()
    assert crown > 1.0 and face > 0.7, f"Detail is too faint: crown={crown:.2f} face={face:.2f}"
    page.get_by_role("button", name="Night", exact=True).click()
    night_off = frame(page)
    detail.check()
    night_on = frame(page)
    night_crown = np.abs(night_on[110:185, 920:1110] - night_off[110:185, 920:1110]).mean()
    assert night_crown < crown * 0.15, "Night hair sheen remains too strong"

    page.get_by_role("button", name="Noon", exact=True).click()
    page.get_by_label("Blink on/off").check()
    page.clock.pause_at(datetime(2026, 9, 25, 12, 0, 0))
    detail.uncheck()
    open_off = frame(page)
    page.get_by_role("button", name="Preview Blink").click()
    page.locator(".blink-layer.is-closed").wait_for(timeout=1000)
    closed_off = frame(page)
    page.clock.run_for(300)
    detail.check()
    open_on = frame(page)
    page.get_by_role("button", name="Preview Blink").click()
    page.locator(".blink-layer.is-closed").wait_for(timeout=1000)
    closed_on = frame(page)
    assert np.abs(closed_on[170:270, 950:1110] - open_on[170:270, 950:1110]).mean() > 0.1
    eye_boxes = ((990, 202, 1005, 222), (1048, 219, 1065, 241))
    open_glint = max(float((open_on[y0:y1, x0:x1] - open_off[y0:y1, x0:x1]).max())
                     for x0, y0, x1, y1 in eye_boxes)
    closed_glint = max(float((closed_on[y0:y1, x0:x1] - closed_off[y0:y1, x0:x1]).max())
                       for x0, y0, x1, y1 in eye_boxes)
    assert open_glint > closed_glint + 1.0, f"Closed-eye glint not suppressed: {open_glint}, {closed_glint}"
    browser.close()

print(f"R5 mask, Detail OFF baseline, locality, Night sheen, and Blink glint: passed; "
      f"Noon crown delta {crown:.2f}, face delta {face:.2f}, Night crown {night_crown:.2f}")
