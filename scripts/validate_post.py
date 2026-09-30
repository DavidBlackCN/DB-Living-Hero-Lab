"""R6 baseline, bloom locality, and late-night continuity regression."""

from io import BytesIO
import argparse
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from frozen_baseline import frozen_phases


ROOT = Path(__file__).resolve().parents[1]
R5 = ROOT / "docs/validation/r5-lighting-detail/round6"


def image(page) -> np.ndarray:
    return np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)


parser = argparse.ArgumentParser()
parser.add_argument('--baseline-url', help='Current frozen commit server, replacing old R5 screenshot baseline')
args = parser.parse_args()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        headless=True,
        args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
    )
    current_frozen = frozen_phases(browser, args.baseline_url, (1440, 900),
        ('Directional Shading on/off', 'Post Processing on/off')) if args.baseline_url else None
    baseline_page = None
    if args.baseline_url:
        baseline_page = browser.new_page(viewport={'width':1440, 'height':900}, device_scale_factor=1)
        baseline_page.goto(args.baseline_url, wait_until='networkidle')
        baseline_page.get_by_text('Mode: WebGL2').wait_for(timeout=30000)
        for label in ('Breathing on/off','Hair Motion on/off','Blink on/off','Leaves','Directional Shading on/off'):
            baseline_page.get_by_label(label).uncheck()
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    if current_frozen:
        page.add_style_tag(content='.debug-panel {opacity:0 !important;}')
        baseline_page.add_style_tag(content='.debug-panel {opacity:0 !important;}')
    page.get_by_label("Directional Shading on/off").uncheck()
    for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
        page.get_by_label(label).uncheck()
    post = page.get_by_label("Post Processing on/off")
    bloom = page.get_by_label("Bloom on/off")
    preview = page.get_by_label("Post preview")
    for phase in ("Dawn", "Noon", "Dusk", "Night"):
        page.get_by_role("button", name=phase, exact=True).click()
        post.uncheck()
        before = image(page)
        frozen = current_frozen[phase.lower()] if current_frozen else np.asarray(Image.open(R5 / f"{phase.lower()}-after.png").convert("RGB"), dtype=np.int16)
        assert np.array_equal(before[:, 310:], frozen[:, 310:]), f"Post OFF altered frozen {phase}"
        post.check()
        bloom.uncheck()
        scene_post = image(page)
        assert np.abs(scene_post[:, 310:] - before[:, 310:]).mean() < 2.5, f"{phase} baseline drift"
        bloom.check()
        final = image(page)
        if phase == "Noon":
            shirt = np.abs(final[300:650, 1130:1245] - scene_post[300:650, 1130:1245])
            assert shirt.mean() < 1.0 and shirt.max() < 8, "Noon white shirt bloomed"
        if phase == "Night":
            assert np.abs(final[:, 310:] - scene_post[:, 310:]).mean() < 0.3, "Night bloom raised the scene"
        preview.select_option("bright")
        bright = image(page)
        assert bright[50:850, 310:].max() < 210, f"{phase} bright-pass clipping"
        preview.select_option("final")

    slider = page.locator(".time-control input[type=range]")
    night = []
    night_frozen = []
    for minutes in (1320, 1380, 0, 120, 270, 1440):
        slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)
        frame = image(page)
        night.append(float(frame[80:750, 310:].mean()))
        if baseline_page:
            baseline_page.get_by_role('slider', name='24H Preview').evaluate("(node, value) => {node.value=String(value); node.dispatchEvent(new Event('input',{bubbles:true}));}", minutes)
            night_frozen.append(float(image(baseline_page)[80:750,310:].mean()))
    assert abs(night[2] - night[5]) < 0.01, "00:00 / 24:00 mismatch"
    hold = [a-b for a,b in zip(night,night_frozen)] if baseline_page else night
    assert max(hold[:5]) - min(hold[:5]) < 0.5, f"Night drift relative to frozen lighting: {hold}"
    browser.close()

print("R6 Post OFF baseline, Scene/Post handoff, bloom locality, and Night hold: passed")
