"""R7.3A fixed-view character captures and motion/lifecycle regression."""

from __future__ import annotations

import argparse
import json
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"
PHASES = ("Dawn", "Noon", "Dusk", "Night")


def setup(page, phase: str, *, motion: bool) -> None:
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.get_by_role("button", name=phase, exact=True).click()
    page.get_by_label("Leaves").uncheck()
    page.get_by_label("Blink on/off").uncheck()
    if not motion:
        page.get_by_label("Breathing on/off").uncheck()
        page.get_by_label("Hair Motion on/off").uncheck()
    page.get_by_role("button", name="Hide", exact=True).click()
    page.wait_for_timeout(250)


def stills(browser, output: Path, *, final: bool) -> dict:
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    for phase in PHASES:
        if phase != PHASES[0]:
            page.get_by_role("button", name="Debug", exact=True).click()
            page.get_by_role("button", name=phase, exact=True).click()
            page.get_by_role("button", name="Hide", exact=True).click()
        else:
            setup(page, phase, motion=False)
        page.screenshot(path=str(output / f"{phase.lower()}.png"))
    night = Image.open(output / "night.png")
    dawn = Image.open(output / "dawn.png")
    for name, frame in (("night", night), ("dawn", dawn)):
        frame.crop((770, 0, 1410, 900)).save(output / f"{name}-figure.png")
        frame.crop((875, 25, 1190, 340)).resize((630, 630)).save(output / f"{name}-head-2x.png")
    page.get_by_role("button", name="Debug", exact=True).click()
    slider = page.get_by_role("slider", name="24H Preview")
    for minute, label in ((0, "00"), (120, "02"), (1440, "24")):
        slider.evaluate("(node, minute) => { node.value = String(minute); node.dispatchEvent(new Event('input', {bubbles: true})); }", minute)
        page.get_by_role("button", name="Hide", exact=True).click()
        page.screenshot(path=str(output / f"night-{label}h.png"))
        page.get_by_role("button", name="Debug", exact=True).click()
    midnight = np.asarray(Image.open(output / "night-00h.png").convert("RGB"), dtype=np.int16)
    end = np.asarray(Image.open(output / "night-24h.png").convert("RGB"), dtype=np.int16)
    midnight_delta = int(np.max(np.abs(midnight[:, 300:] - end[:, 300:])))
    page.close()
    if final:
        diagnostic(browser, output)
    return {"midnightMaxRgbDelta": midnight_delta}


def diagnostic(browser, output: Path) -> None:
    for mode in ("on", "off"):
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        if mode == "off":
            page.goto(URL + "?hairSheen=off", wait_until="networkidle")
            page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
            page.get_by_role("button", name="Night", exact=True).click()
            for label in ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off"):
                page.get_by_label(label).uncheck()
            page.get_by_role("button", name="Hide", exact=True).click()
        else:
            setup(page, "Night", motion=False)
        page.screenshot(path=str(output / f"night-sheen-{mode}.png"))
        page.close()


def video(browser, output: Path, phase: str, seconds: int, *, secondary_off: bool = False, combined: bool = False) -> None:
    context = browser.new_context(viewport={"width": 960, "height": 540}, device_scale_factor=1,
        record_video_dir=str(output), record_video_size={"width": 960, "height": 540})
    page = context.new_page()
    if combined:
        page.goto(URL, wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name=phase, exact=True).click()
        page.get_by_role("button", name="Hide", exact=True).click()
    elif secondary_off:
        page.goto(URL + "?hairSecondary=off", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name=phase, exact=True).click()
        for label in ("Leaves", "Blink on/off"):
            page.get_by_label(label).uncheck()
        page.get_by_role("button", name="Hide", exact=True).click()
    else:
        setup(page, phase, motion=True)
    page.wait_for_timeout(seconds * 1000)
    page.close()
    source = Path(page.video.path())
    context.close()
    suffix = "-combined" if combined else "-secondary-off" if secondary_off else ""
    destination = output / f"{phase.lower()}-{seconds}s{suffix}.mp4"
    cap = cv2.VideoCapture(str(source))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    writer = cv2.VideoWriter(str(destination), cv2.VideoWriter_fourcc(*"mp4v"), fps, (960, 540))
    assert cap.isOpened() and writer.isOpened() and fps >= 10, (source, fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, total - round(fps * seconds)))
    count = 0
    samples = []
    while count < round(fps * seconds):
        ok, frame = cap.read()
        if not ok:
            break
        writer.write(frame)
        if count in (0, round(fps * seconds / 3), round(fps * seconds * 2 / 3)):
            samples.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        count += 1
    cap.release()
    writer.release()
    source.unlink()
    assert count >= fps * seconds * 0.95, (destination, count)
    contact = Image.new("RGB", (960 * len(samples), 540))
    for index, image in enumerate(samples):
        contact.paste(image, (960 * index, 0))
    contact.save(output / f"{phase.lower()}-motion-contact{suffix}.jpg", quality=90)


def regression(browser, output: Path) -> dict:
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    setup(page, "Night", motion=True)
    first = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)
    page.wait_for_timeout(1700)
    second = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)
    head_delta = int(np.count_nonzero(np.abs(first[120:320, 900:1160] - second[120:320, 900:1160]) > 2))
    assert head_delta > 500, "Head motion stalled"
    page.get_by_role("button", name="Debug", exact=True).click()
    page.get_by_label("Show Breathing Region").check()
    page.get_by_label("Show Hair Region").check()
    page.get_by_role("button", name="Hide", exact=True).click()
    page.screenshot(path=str(output / "motion-regions.png"))
    page.get_by_role("button", name="Debug", exact=True).click()
    page.get_by_label("Show Breathing Region").uncheck()
    page.get_by_label("Show Hair Region").uncheck()
    page.get_by_label("Blink on/off").check()
    page.evaluate("() => document.querySelector('.blink-layer').__vueParentComponent.emit('amount', 1)")
    assert page.locator("canvas.hero-canvas").evaluate("node => node.__vueParentComponent.props.blinkAmount") == 1
    page.evaluate("() => document.querySelector('.blink-layer').__vueParentComponent.emit('amount', 0)")
    page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, value: true}); document.dispatchEvent(new Event('visibilitychange'))")
    paused = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"))
    page.wait_for_timeout(500)
    assert np.array_equal(paused[:, 300:], np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"))[:, 300:])
    page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, value: false}); document.dispatchEvent(new Event('visibilitychange'))")
    page.get_by_label("Blink on/off").uncheck()
    page.get_by_label("Breathing on/off").uncheck()
    page.get_by_label("Hair Motion on/off").uncheck()
    lamps_on = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)
    page.get_by_label("Lamps on/off").uncheck()
    lamps_off = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)
    lamp_delta = np.abs(lamps_on - lamps_off)
    assert lamp_delta[:450, :350].mean() > 0.05, "Lamp contribution vanished"
    assert lamp_delta[:, 850:].mean() < 0.05, "Lamp changed the figure"
    page.get_by_label("Lamps on/off").check()
    page.get_by_label("Post Processing on/off").uncheck()
    assert page.get_by_text("Mode: WebGL2").count() == 1
    page.get_by_label("Post Processing on/off").check()
    page.get_by_label("Leaves").check()
    assert page.locator(".leaves-canvas").count() == 1
    page.get_by_label("Leaves").uncheck()
    page.get_by_label("Quality").select_option("static")
    assert page.get_by_label("Hair Motion on/off").is_disabled()
    page.set_viewport_size({"width": 560, "height": 800})
    assert page.locator(".hero-image").count() > 0
    page.close()
    reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    reduced.goto(URL, wait_until="networkidle")
    assert reduced.get_by_label("Hair Motion on/off").is_disabled()
    reduced.close()
    return {"headMotionChangedRgbSamples": head_delta, "lampCorridorMeanRgbDelta": round(float(lamp_delta[:450, :350].mean()), 3),
        "lampFigureMeanRgbDelta": round(float(lamp_delta[:, 850:].mean()), 3),
        "blink": "passed", "lamps": "passed", "leaves": "passed", "post": "passed", "hiddenTab": "passed",
        "staticQuality": "passed", "resize": "passed", "reducedMotion": "passed"}


def continuity(browser) -> dict:
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=1)
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    for label in ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off"):
        page.get_by_label(label).uncheck()
    slider = page.get_by_role("slider", name="24H Preview")
    windows = ((270, 420), (990, 1200))
    results = {}
    for start, end in windows:
        previous = None
        deltas = []
        for minute in range(start, end + 1, 10):
            slider.evaluate("(node, value) => { node.value = String(value); node.dispatchEvent(new Event('input', {bubbles: true})); }", minute)
            current = np.asarray(Image.open(BytesIO(page.screenshot())).convert("RGB"), dtype=np.int16)[25:525, 520:935]
            if previous is not None:
                deltas.append(round(float(np.abs(current - previous).mean()), 3))
            previous = current
        key = f"{start//60:02d}:{start%60:02d}-{end//60:02d}:{end%60:02d}"
        results[key] = {"maxAdjacent10mMeanRgbDelta": max(deltas), "deltas": deltas}
        assert max(deltas) < 12, (key, max(deltas))
    page.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--seconds", type=int, default=20)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        stats = stills(browser, output, final=args.final)
        for phase in ("Noon", "Night"):
            video(browser, output, phase, args.seconds)
        if args.final:
            video(browser, output, "Noon", 8, secondary_off=True)
            for phase in ("Noon", "Night"):
                video(browser, output, phase, args.seconds, combined=True)
            stats.update(regression(browser, output))
            stats["twilightContinuity"] = continuity(browser)
        browser.close()
    (output / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
