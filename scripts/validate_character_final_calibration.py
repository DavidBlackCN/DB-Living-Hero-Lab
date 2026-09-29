"""Large-viewport R7.3A.1 visual captures against the c97b2c4 baseline."""

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
STILL = (2560, 1440)
VIDEO = (1920, 1080)


def prepare(page, phase: str, *, isolate: bool) -> None:
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.get_by_role("button", name=phase, exact=True).click()
    if isolate:
        page.get_by_label("Leaves").uncheck()
        page.get_by_label("Blink on/off").uncheck()
    page.get_by_role("button", name="Hide", exact=True).click()
    page.wait_for_timeout(250)


def stills(browser, output: Path) -> None:
    page = browser.new_page(viewport={"width": STILL[0], "height": STILL[1]}, device_scale_factor=1)
    prepare(page, "Dawn", isolate=True)
    page.get_by_role("button", name="Debug", exact=True).click()
    page.get_by_label("Breathing on/off").uncheck()
    page.get_by_label("Hair Motion on/off").uncheck()
    for index, phase in enumerate(PHASES):
        if index:
            page.get_by_role("button", name=phase, exact=True).click()
        page.get_by_role("button", name="Hide", exact=True).click()
        page.screenshot(path=str(output / f"{phase.lower()}-2560.png"))
        page.get_by_role("button", name="Debug", exact=True).click()
    slider = page.get_by_role("slider", name="24H Preview")
    slider.evaluate("(node) => { node.value = '0'; node.dispatchEvent(new Event('input', {bubbles: true})); }")
    page.get_by_role("button", name="Hide", exact=True).click()
    page.screenshot(path=str(output / "night-00h-2560.png"))
    page.close()


def motion(browser, output: Path, phase: str, seconds: int, *, isolate: bool, secondary_off: bool = False) -> None:
    name = phase.lower() + ("-secondary-off" if secondary_off else "-combined" if not isolate else "-isolate")
    context = browser.new_context(viewport={"width": VIDEO[0], "height": VIDEO[1]}, device_scale_factor=1,
        record_video_dir=str(output), record_video_size={"width": VIDEO[0], "height": VIDEO[1]})
    page = context.new_page()
    if secondary_off:
        page.goto(URL + "?hairSecondary=off", wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name=phase, exact=True).click()
        page.get_by_label("Leaves").uncheck()
        page.get_by_label("Blink on/off").uncheck()
        page.get_by_role("button", name="Hide", exact=True).click()
    else:
        prepare(page, phase, isolate=isolate)
    page.wait_for_timeout(seconds * 1000)
    page.close()
    source = Path(page.video.path())
    context.close()
    destination = output / f"{name}-{seconds}s.mp4"
    capture = cv2.VideoCapture(str(source))
    fps = capture.get(cv2.CAP_PROP_FPS)
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    writer = cv2.VideoWriter(str(destination), cv2.VideoWriter_fourcc(*"mp4v"), fps, VIDEO)
    assert capture.isOpened() and writer.isOpened() and fps >= 10, (source, fps)
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, total - round(fps * seconds)))
    count = 0
    while count < round(fps * seconds):
        ok, frame = capture.read()
        if not ok:
            break
        writer.write(frame)
        count += 1
    writer.release()
    capture.release()
    source.unlink()
    assert count >= fps * seconds * 0.95, (destination, count)
    print(destination.name, count, "frames", fps, "fps")


def compare(output: Path, baseline: Path) -> dict:
    metrics = {}
    contact = Image.new("RGB", (STILL[0] * 2, STILL[1] * 2))
    for index, phase in enumerate(PHASES):
        before = Image.open(baseline / f"{phase.lower()}-2560.png").convert("RGB")
        after = Image.open(output / f"{phase.lower()}-2560.png").convert("RGB")
        contact.paste(after, ((index % 2) * STILL[0], (index // 2) * STILL[1]))
        if phase in ("Dawn", "Night"):
            for label, box in (("full", (0, 0, *STILL)),
                               ("head", (1380, 25, 2110, 690)),
                               ("figure", (1270, 0, 2280, 1440)),
                               ("sleeves-vest", (1270, 420, 2260, 1190))):
                left = before.crop(box)
                right = after.crop(box)
                pair = Image.new("RGB", (left.width * 2, left.height))
                pair.paste(left, (0, 0))
                pair.paste(right, (left.width, 0))
                pair.save(output / f"{phase.lower()}-{label}-before-after.jpg", quality=90)
        delta = np.abs(np.asarray(after, dtype=np.int16) - np.asarray(before, dtype=np.int16))
        metrics[phase.lower()] = {"wholeMeanRgbDelta": round(float(delta.mean()), 3),
            "figureMeanRgbDelta": round(float(delta[0:1340, 1270:2280].mean()), 3)}
    contact.save(output / "four-phase-2560-contact.jpg", quality=88)
    return metrics


def extras(browser, output: Path, baseline: Path) -> None:
    for mode in ("on", "off"):
        page = browser.new_page(viewport={"width": STILL[0], "height": STILL[1]}, device_scale_factor=1)
        page.goto(URL + ("?hairSheen=off" if mode == "off" else ""), wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name="Night", exact=True).click()
        for label in ("Leaves", "Blink on/off", "Breathing on/off", "Hair Motion on/off"):
            page.get_by_label(label).uncheck()
        page.get_by_role("button", name="Hide", exact=True).click()
        page.screenshot(path=str(output / f"night-sheen-{mode}-2560.png"))
        page.close()
    on = Image.open(output / "night-sheen-on-2560.png").convert("RGB")
    off = Image.open(output / "night-sheen-off-2560.png").convert("RGB")
    box = (1380, 25, 2110, 690)
    pair = Image.new("RGB", (1460, 665))
    pair.paste(off.crop(box), (0, 0))
    pair.paste(on.crop(box), (730, 0))
    pair.save(output / "night-sheen-off-on-head.jpg", quality=92)

    for phase in ("noon", "night"):
        old = cv2.VideoCapture(str(baseline / f"{phase}-isolate-20s.mp4"))
        new = cv2.VideoCapture(str(output / f"{phase}-isolate-20s.mp4"))
        fps = min(old.get(cv2.CAP_PROP_FPS), new.get(cv2.CAP_PROP_FPS))
        writer = cv2.VideoWriter(str(output / f"{phase}-motion-before-after-20s.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"), fps, (1920, 540))
        head_writer = cv2.VideoWriter(str(output / f"{phase}-head-torso-20s.mp4"),
            cv2.VideoWriter_fourcc(*"mp4v"), fps, (950, 850))
        assert old.isOpened() and new.isOpened() and writer.isOpened() and head_writer.isOpened()
        for _ in range(round(fps * 20)):
            ok_old, before = old.read()
            ok_new, after = new.read()
            if not (ok_old and ok_new):
                break
            writer.write(np.concatenate((cv2.resize(before, (960, 540)),
                cv2.resize(after, (960, 540))), axis=1))
            head_writer.write(after[0:850, 820:1770])
        old.release()
        new.release()
        writer.release()
        head_writer.release()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--seconds", type=int, default=20)
    parser.add_argument("--extras-only", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        if not args.extras_only:
            stills(browser, args.output)
            for phase in ("Noon", "Night"):
                motion(browser, args.output, phase, args.seconds, isolate=True)
            if args.baseline:
                motion(browser, args.output, "Noon", args.seconds, isolate=False)
                motion(browser, args.output, "Night", args.seconds, isolate=False)
                motion(browser, args.output, "Noon", 8, isolate=True, secondary_off=True)
        if args.baseline:
            extras(browser, args.output, args.baseline)
        browser.close()
    if args.baseline and not args.extras_only:
        stats = compare(args.output, args.baseline)
        (args.output / "visual-metrics.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
