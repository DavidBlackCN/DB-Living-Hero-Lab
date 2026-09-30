"""Capture an explicitly served frozen commit; never overwrite old archives."""
from io import BytesIO
import numpy as np
from PIL import Image


def frozen_phases(browser, url, size, disabled=()):
    page = browser.new_page(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1)
    page.goto(url, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves", *disabled):
        page.get_by_label(label).uncheck()
    page.add_style_tag(content=".debug-panel { opacity: 0 !important; }")
    result = {}
    for phase in ("Dawn", "Noon", "Dusk", "Night"):
        page.get_by_role("button", name=phase, exact=True).click()
        page.wait_for_timeout(100)
        result[phase.lower()] = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"))
    page.close()
    return result
