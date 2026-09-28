"""Capture R7.2 motion and check leaf depth, lifecycle, and Lit coexistence."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"
PHASES = ("Dawn", "Noon", "Dusk", "Night")
INSTRUMENT_LEAVES = """(() => {
  window.leafDraws = [];
  window.leafFrames = [];
  const original = CanvasRenderingContext2D.prototype.drawImage;
  const clear = CanvasRenderingContext2D.prototype.clearRect;
  CanvasRenderingContext2D.prototype.clearRect = function (...args) {
    if (this.canvas.classList.contains('leaves-canvas')) window.leafFrames.push(performance.now());
    return clear.apply(this, args);
  };
  CanvasRenderingContext2D.prototype.drawImage = function (...args) {
    if (this.canvas.classList.contains('leaves-canvas')) {
      const transform = this.getTransform();
      const rect = document.querySelector('.hero-image')?.getBoundingClientRect();
      if (rect) window.leafDraws.push({
        t: performance.now(),
        x: (transform.e - rect.left) / rect.width * 1672,
        y: (transform.f - rect.top) / rect.height * 941,
        alpha: this.globalAlpha,
      });
    }
    return original.apply(this, args);
  };
})()"""


def trim_video(source: Path, destination: Path, seconds: int) -> None:
    capture = cv2.VideoCapture(str(source))
    fps = capture.get(cv2.CAP_PROP_FPS)
    frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    assert capture.isOpened() and fps >= 10 and frames >= fps * seconds
    writer = cv2.VideoWriter(str(destination), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    assert writer.isOpened()
    capture.set(cv2.CAP_PROP_POS_FRAMES, max(0, frames - round(seconds * fps)))
    count = 0
    while count < round(seconds * fps):
        ok, frame = capture.read()
        if not ok:
            break
        writer.write(frame)
        count += 1
    writer.release()
    capture.release()
    assert count >= seconds * fps * 0.95, (destination, count)


def motion_contact(video: Path, destination: Path, seconds: int) -> None:
    capture = cv2.VideoCapture(str(video))
    fps = capture.get(cv2.CAP_PROP_FPS)
    frames = []
    for second in (0, seconds * 0.2, seconds * 0.4, seconds * 0.6, seconds * 0.8, seconds * 0.96):
        capture.set(cv2.CAP_PROP_POS_FRAMES, round(second * fps))
        ok, frame = capture.read()
        assert ok
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    capture.release()
    width, height = frames[0].shape[1], frames[0].shape[0]
    contact = Image.new("RGB", (width * 3, height * 2))
    for index, frame in enumerate(frames):
        contact.paste(Image.fromarray(frame), ((index % 3) * width, (index // 3) * height))
    contact.save(destination)


def capture_static(browser, output: Path) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
    page.add_init_script(INSTRUMENT_LEAVES)
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    assert page.get_by_label("Leaves").is_checked()
    assert page.locator(".leaves-canvas").count() == 1
    for phase in PHASES:
        page.get_by_role("button", name=phase, exact=True).click()
        page.get_by_role("button", name="Hide", exact=True).click()
        page.wait_for_timeout(250)
        page.screenshot(path=str(output / f"{phase.lower()}.png"))
        page.get_by_role("button", name="Debug", exact=True).click()

    page.get_by_role("button", name="Noon", exact=True).click()
    page.get_by_label("Leaf debug").select_option("depth")
    page.get_by_role("button", name="Hide", exact=True).click()
    page.wait_for_timeout(200)
    page.screenshot(path=str(output / "depth-face-debug.png"))
    page.get_by_role("button", name="Debug", exact=True).click()
    page.get_by_label("Leaf debug").select_option("none")

    # A stationary A/B isolates the leaf tint from the WebGL lamp contribution.
    page.get_by_role("button", name="Night", exact=True).click()
    page.get_by_label("Breathing on/off").uncheck()
    page.get_by_label("Hair Motion on/off").uncheck()
    page.get_by_label("Blink on/off").uncheck()
    page.wait_for_timeout(500)
    page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, value: true}); document.dispatchEvent(new Event('visibilitychange'))")
    paused_frames = page.evaluate("window.leafFrames.length")
    page.wait_for_timeout(250)
    assert page.evaluate("window.leafFrames.length") == paused_frames, "Hidden leaf RAF continued"
    page.get_by_label("Leaf debug").select_option("lamp-off")
    page.get_by_role("button", name="Hide", exact=True).click()
    page.screenshot(path=str(output / "night-leaf-lamp-tint-off.png"))
    page.get_by_role("button", name="Debug", exact=True).click()
    page.get_by_label("Leaf debug").select_option("none")
    page.get_by_role("button", name="Hide", exact=True).click()
    page.screenshot(path=str(output / "night-leaf-lamp-tint-on.png"))
    off = Image.open(output / "night-leaf-lamp-tint-off.png").convert("RGB")
    on = Image.open(output / "night-leaf-lamp-tint-on.png").convert("RGB")
    difference = ImageChops.difference(off, on)
    difference.crop((0, 0, 400, 580)).save(output / "night-leaf-lamp-tint-difference.png")
    for label, frame in (("off", off), ("on", on)):
        frame.crop((0, 80, 240, 300)).resize((960, 880), Image.Resampling.NEAREST).save(
            output / f"night-leaf-lamp-tint-{label}-4x.png")
    difference.crop((0, 80, 240, 300)).point(lambda value: min(255, value * 32)).resize(
        (960, 880), Image.Resampling.NEAREST).save(output / "night-leaf-lamp-tint-audit-32x.png")
    page.get_by_role("button", name="Debug", exact=True).click()
    page.evaluate("Object.defineProperty(document, 'hidden', {configurable: true, value: false}); document.dispatchEvent(new Event('visibilitychange'))")

    # The existing lifecycle and other Lit motion paths must still compose.
    page.get_by_label("Breathing on/off").check()
    page.get_by_label("Hair Motion on/off").check()
    page.get_by_label("Blink on/off").check()
    page.clock.pause_at(datetime(2026, 9, 28, 12, 0, 0))
    page.get_by_role("button", name="Preview Blink").click()
    assert page.locator(".blink-layer.is-closed").count() == 1
    page.clock.resume()
    assert page.locator(".leaves-canvas").count() == 1
    page.get_by_label("Quality").select_option("static")
    assert page.locator(".leaves-canvas").count() == 0
    page.get_by_label("Quality").select_option("auto")
    assert page.locator(".leaves-canvas").count() == 1
    page.set_viewport_size({"width": 560, "height": 800})
    page.wait_for_timeout(300)
    assert "10 active" in page.locator(".debug-panel").inner_text()
    assert page.locator(".leaves-canvas").evaluate("node => node.width > 0 && node.height > 0")
    page.close()

    reduced = browser.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    reduced.goto(URL, wait_until="networkidle")
    assert reduced.locator(".leaves-canvas").count() == 0
    reduced.close()


def capture_motion(browser, output: Path, phase: str, seconds: int) -> dict:
    context = browser.new_context(viewport={"width": 960, "height": 540}, device_scale_factor=1,
                                  record_video_dir=str(output), record_video_size={"width": 960, "height": 540})
    context.add_init_script(INSTRUMENT_LEAVES)
    page = context.new_page()
    page.goto(URL, wait_until="networkidle")
    page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
    page.get_by_role("button", name=phase, exact=True).click()
    page.get_by_role("button", name="Hide", exact=True).click()
    page.evaluate("window.leafDraws = []; window.leafFrames = []; window.leafCaptureStart = performance.now()")
    page.wait_for_timeout((seconds + 2) * 1000)
    samples = page.evaluate("""() => ({
      elapsed: (performance.now() - window.leafCaptureStart) / 1000,
      draws: window.leafDraws,
      frames: window.leafFrames,
      count: document.querySelector('.leaves-canvas') ? 18 : 0,
    })""")
    page.close()
    source_video = Path(page.video.path())
    context.close()
    video = output / f"{phase.lower()}-25s.mp4"
    trim_video(source_video, video, seconds)
    source_video.unlink()
    motion_contact(video, output / f"{phase.lower()}-motion-contact.png", seconds)
    draws = samples["draws"]
    eye_bins = sorted({int((entry["t"] - draws[0]["t"]) / 150) for entry in draws
                       if abs(entry["x"] - 1150) < 100 and abs(entry["y"] - 205) < 45 and entry["alpha"] > 0.3})
    eye_events = sum(index == 0 or eye_bins[index] > eye_bins[index - 1] + 1 for index in range(len(eye_bins)))
    return {"phase": phase, "seconds": round(samples["elapsed"], 2), "drawCalls": len(draws),
            "estimatedLeafFps": round(len(samples["frames"]) / samples["elapsed"], 1),
            "obviousEyeOverlapEvents": eye_events,
            "eyeOverlapBins150ms": len(eye_bins)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--seconds", type=int, default=25)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"])
        capture_static(browser, args.output)
        results = [capture_motion(browser, args.output, phase, args.seconds) for phase in ("Noon", "Dusk", "Night")]
        browser.close()
    (args.output / "motion-stats.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
