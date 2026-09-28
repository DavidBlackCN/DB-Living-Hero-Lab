"""Capture R7.1 fixed-time lamps, switch transitions, and R6-off regressions."""

import argparse
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


SIZE = (2048, 1033)
TIMES = (990, 1050, 1080, 1110, 1200, 1320, 0, 300, 330, 360, 390, 720)
ROOT = Path(__file__).resolve().parents[1]
for mask_name in ("lamp-source-mask.png", "lamp-influence-mask.png"):
    registered = np.asarray(Image.open(ROOT / "public/assets/hero/lighting" / mask_name).convert("RGBA"))
    assert registered.shape == (941, 1672, 4)
    assert not np.any(registered[:, 390:, :2]) and not np.any(registered[548:, :, :2]), "Lamp mask escaped corridor"

# At a horizontal cut through each lantern the source must resolve into three
# separate panes, leaving the dark metal mullions unlit.
source = np.asarray(Image.open(ROOT / "public/assets/hero/lighting/lamp-source-mask.png"))
for channel, row, left, right in ((0, 150, 30, 68), (1, 260, 142, 172)):
    lit = source[row, left:right, channel] > 128
    runs = np.diff(np.r_[False, lit, False].astype(np.int8))
    assert np.count_nonzero(runs == 1) == 3, "Each lamp needs three distinct glass panes"
assert source[150, 63, 0] > 200 and source[150, 64, 0] > 128, "Near right pane still misses its outer edge"
assert source[260, 147, 1] < 32 and source[260, 148, 1] < 32, "Far left pane spills into its metal rim"


def frame(page) -> Image.Image:
    page.wait_for_timeout(130)
    return Image.open(BytesIO(page.screenshot())).convert("RGB")


def sheet(images: list[tuple[str, Image.Image]], columns: int, width: int) -> Image.Image:
    height = round(width * SIZE[1] / SIZE[0])
    rows = (len(images) + columns - 1) // columns
    result = Image.new("RGB", (columns * width, rows * (height + 24)), (18, 20, 25))
    pen = ImageDraw.Draw(result)
    for index, (label, image) in enumerate(images):
        x, y = (index % columns) * width, (index // columns) * (height + 24)
        pen.text((x + 6, y + 5), label, fill="white")
        result.paste(image.resize((width, height)), (x, y + 24))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"],
        )
        page = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]}, device_scale_factor=1)
        page.goto("http://127.0.0.1:5173/", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        for label in ("Breathing on/off", "Hair Motion on/off", "Blink on/off", "Leaves"):
            page.get_by_label(label).uncheck()
        page.get_by_label("Render view").select_option("lit")
        hidden_for_captures = page.add_style_tag(content=".debug-panel { opacity: 0 !important; }")
        slider = page.locator(".time-control input[type=range]")

        def set_time(minutes: int) -> None:
            slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', { bubbles: true })); }", minutes)

        captures = []
        for minutes in TIMES:
            set_time(minutes)
            image = frame(page)
            name = f"{minutes // 60:02d}h{minutes % 60:02d}"
            image.save(args.output / f"{name}.png")
            captures.append((f"{minutes // 60:02d}:{minutes % 60:02d}", image))
        sheet(captures, 4, 600).save(args.output / "timeline-contact.png")
        sheet([(label, image) for label, image in captures if label in
               ("06:30", "12:00", "17:30", "22:00")], 2, 900).save(args.output / "four-phase-contact.png")
        sheet([(label, image) for label, image in captures if label in
               ("16:30", "17:30", "18:00", "18:30", "20:00")], 3, 600).save(args.output / "dusk-transition.png")
        sheet([(label, image) for label, image in captures if label in
               ("05:00", "05:30", "06:00", "06:30")], 4, 500).save(args.output / "dawn-transition.png")

        page.get_by_label("Lamps on/off").uncheck()
        for phase, minutes in (("dawn", 390), ("noon", 720), ("dusk", 1050), ("night", 1320)):
            set_time(minutes)
            frozen = np.asarray(Image.open(ROOT / f"docs/validation/r6-final-closure/final/{phase}-full.png").convert("RGB"))
            assert np.array_equal(np.asarray(frame(page)), frozen), f"Lamps OFF changed R6 {phase}"
        page.get_by_label("Lamps on/off").check()

        set_time(1320)
        on = frame(page)
        page.get_by_label("Lamps on/off").uncheck()
        off = frame(page)
        off.save(args.output / "22h00-off.png")
        sheet([("LAMPS OFF", off), ("LAMPS ON", on)], 2, 900).save(args.output / "22h00-off-on.png")
        for name, image in (("off", off), ("on", on)):
            image.crop((0, 0, 740, 770)).save(args.output / f"22h00-lamps-{name}-crop.png")
        page.get_by_label("Lamps on/off").check()
        page.get_by_label("Bloom on/off").uncheck()
        no_bloom = frame(page)
        no_bloom.save(args.output / "22h00-no-bloom.png")
        sheet([("BLOOM OFF", no_bloom), ("BLOOM ON", on)], 2, 900).save(args.output / "22h00-bloom-comparison.png")
        page.get_by_label("Lamps on/off").uncheck()
        no_bloom_no_lamps = frame(page)
        assert np.mean(np.asarray(no_bloom, dtype=np.int16)[60:600, :490]
                       - np.asarray(no_bloom_no_lamps, dtype=np.int16)[60:600, :490]) > 1, "Surface lamp requires Bloom"
        page.get_by_label("Lamps on/off").check()
        page.get_by_label("Bloom on/off").check()
        for view in ("source", "influence"):
            page.get_by_label("Lamp mask preview").select_option(view)
            frame(page).save(args.output / f"lamp-{view}-debug.png")
        page.get_by_label("Lamp mask preview").select_option("none")
        set_time(1440)
        midnight_24 = frame(page)
        midnight_00 = next(image for label, image in captures if label == "00:00")
        assert np.array_equal(np.asarray(midnight_24), np.asarray(midnight_00)), "Midnight wrap changed"
        reference = np.asarray(Image.open(ROOT / "docs/validation/r6-final-closure/final/night-full.png").convert("RGB"))
        assert np.array_equal(np.asarray(off), reference), "Lamps OFF did not restore frozen R6"
        reference_noon = np.asarray(Image.open(ROOT / "docs/validation/r6-final-closure/final/noon-full.png").convert("RGB"))
        noon = next(image for label, image in captures if label == "12:00")
        assert np.array_equal(np.asarray(noon), reference_noon), "Noon changed from R6"
        corridor = (slice(60, 600), slice(0, 490))
        nearby = np.asarray(on, dtype=np.int16)[corridor]
        baseline = np.asarray(off, dtype=np.int16)[corridor]
        assert np.mean(nearby - baseline) > 1, "Lamps had no visible corridor effect"
        assert np.array_equal(np.asarray(on)[:, 950:1770], np.asarray(off)[:, 950:1770]), "Lamps changed the figure"
        static_frame = np.asarray(frame(page))
        page.wait_for_timeout(1100)
        assert np.array_equal(static_frame, np.asarray(frame(page))), "Static lamps kept drawing"
        weights = page.evaluate("""async () => {
          const {lampWeightFor} = await import('/src/config/lamps.ts');
          return [Array.from({length: 37}, (_, i) => lampWeightFor(1000 + i * 5)),
            Array.from({length: 25}, (_, i) => lampWeightFor(300 + i * 5)),
            lampWeightFor(0), lampWeightFor(1440), lampWeightFor(720)];
        }""")
        dusk, dawn, start, end, noon_weight = weights
        assert all(a <= b for a, b in zip(dusk, dusk[1:])), "Dusk lamp fade is not monotone"
        assert all(a >= b for a, b in zip(dawn, dawn[1:])), "Dawn lamp fade is not monotone"
        assert max(abs(a - b) for a, b in zip(dusk, dusk[1:])) < 0.12
        assert max(abs(a - b) for a, b in zip(dawn, dawn[1:])) < 0.12
        assert start == end == 1 and noon_weight == 0, "Night hold or 24H wrap changed"
        # Lit motion systems remain active with lamps; a paused figure needs no RAF.
        set_time(1320)
        page.get_by_label("Hair Motion on/off").check()
        page.get_by_label("Breathing on/off").check()
        moving = np.asarray(frame(page), dtype=np.int16)
        page.wait_for_timeout(1200)
        assert np.abs(np.asarray(frame(page), dtype=np.int16)[80:900, 950:1700]
                      - moving[80:900, 950:1700]).mean() > 0.02, "Character motion stopped"
        page.get_by_label("Hair Motion on/off").uncheck()
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Leaves").check()
        assert page.locator(".leaves-canvas").count() == 1, "Leaves layer missing"
        page.get_by_label("Leaves").uncheck()
        page.get_by_label("Blink on/off").check()
        page.get_by_role("button", name="Preview Blink").click()
        assert page.locator(".blink-layer.is-closed").count() == 1, "Blink did not close"
        page.get_by_label("Blink on/off").uncheck()
        set_time(1050)
        page.get_by_role("button", name="Play", exact=True).click()
        page.wait_for_timeout(1100)
        assert int(slider.input_value()) > 1050, "Play did not advance through lamp fade"
        assert page.get_by_text("Mode: WebGL2").count() == 1, "Play lost the renderer"
        page.get_by_role("button", name="Pause", exact=True).click()
        hidden_for_captures.evaluate("node => node.remove()")
        set_time(1320)
        assert page.get_by_label("Lamps on/off").is_checked()
        page.screenshot(path=str(args.output / "22h00-panel-visible.png"))
        canvas = page.locator(".hero-canvas").element_handle()
        assert canvas is not None
        page.get_by_role("button", name="Hide", exact=True).click()
        assert not page.locator(".debug-panel").is_visible()
        assert page.get_by_role("button", name="Debug", exact=True).is_visible()
        assert int(slider.input_value()) == 1320
        assert canvas.evaluate("node => node.isConnected && node.isSameNode(document.querySelector('.hero-canvas'))")
        page.screenshot(path=str(args.output / "22h00-panel-hidden.png"))
        page.get_by_role("button", name="Debug", exact=True).click()
        assert page.locator(".debug-panel").is_visible()
        assert int(slider.input_value()) == 1320
        assert page.get_by_label("Lamps on/off").is_checked()
        page.get_by_role("button", name="Play", exact=True).click()
        page.get_by_role("button", name="Hide", exact=True).click()
        # The 60-second day can wrap past midnight while SwiftShader is busy.
        page.wait_for_function("Number(document.querySelector('.time-control input[type=range]').value) !== 1320", timeout=5000)
        page.get_by_role("button", name="Debug", exact=True).click()
        page.get_by_role("button", name="Pause", exact=True).click()
        browser.close()
        print(f"R6 four phases OFF and Noon ON exact; 00:00/24:00 exact; corridor gain {np.mean(nearby - baseline):.2f} RGB; Bloom OFF and motion passed")


if __name__ == "__main__":
    main()
