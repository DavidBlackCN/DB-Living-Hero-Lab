"""Capture actual rendered Blink frames, including the normal motion lifecycle."""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import cv2
import numpy as np
from playwright.sync_api import sync_playwright


EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "http://127.0.0.1:5173/"
FACE = {"x": 755, "y": 25, "width": 280, "height": 245}


def screenshot_frame(page) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(page.screenshot(clip=FACE), dtype=np.uint8), cv2.IMREAD_COLOR)


def writer(path: Path, fps: int) -> cv2.VideoWriter:
    result = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps,
                             (FACE["width"], FACE["height"]))
    if not result.isOpened():
        raise RuntimeError(f"Could not open video writer: {path}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--short", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=EDGE, headless=True,
            args=["--enable-webgl", "--use-gl=angle", "--use-angle=d3d11"])
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.goto(URL, wait_until="networkidle")
        page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
        page.get_by_role("button", name="Noon", exact=True).click()
        page.get_by_label("Leaves").uncheck()
        page.get_by_role("button", name="Hide", exact=True).click()

        # Drive the same Vue amount event used by the timeline. Each screenshot
        # is the actual WebGL + Post result, not a synthetic image blend.
        slow = writer(args.output / "blink-envelope-slow-60fps.mp4", 60)
        key_frames = {}
        for index in range(21):
            age = index / 20
            amount = math.sin(math.pi * age) ** 0.6
            page.evaluate("value => document.querySelector('.blink-layer').__vueParentComponent.emit('amount', value)", amount)
            page.wait_for_timeout(30)
            frame = screenshot_frame(page)
            if index in (0, 5, 10, 15, 20):
                key_frames[index] = frame
            for _ in range(4):
                slow.write(frame)
        slow.release()
        cv2.imwrite(str(args.output / "blink-envelope-contact.jpg"),
            cv2.hconcat([key_frames[i] for i in (0, 5, 10, 15, 20)]))

        # This pass uses the autonomous random interval at normal speed.
        if not args.short:
            page.evaluate("() => document.querySelector('.blink-layer').__vueParentComponent.emit('amount', 0)")
            normal = writer(args.output / "blink-normal-20s.mp4", 30)
            start = time.monotonic()
            captures: list[tuple[float, np.ndarray]] = []
            while time.monotonic() - start < 20:
                captures.append((time.monotonic() - start, screenshot_frame(page)))
            cursor = 0
            for frame_number in range(600):
                timestamp = frame_number / 30
                while cursor + 1 < len(captures) and captures[cursor + 1][0] <= timestamp:
                    cursor += 1
                normal.write(captures[cursor][1])
            normal.release()
            print(f"Normal speed: {len(captures)} real frames over 20s")

            page.close()
            page = browser.new_page(viewport={"width": 3840, "height": 2160}, device_scale_factor=1)
            page.goto(URL, wait_until="networkidle")
            page.get_by_text("Mode: WebGL2").wait_for(timeout=30000)
            page.get_by_role("button", name="Noon", exact=True).click()
            page.get_by_label("Leaves").uncheck()
            page.get_by_role("button", name="Hide", exact=True).click()
            page.screenshot(path=str(args.output / "blink-4k-open.png"))
            page.evaluate("() => document.querySelector('.blink-layer').__vueParentComponent.emit('amount', 1)")
            page.screenshot(path=str(args.output / "blink-4k-closed.png"))
        browser.close()


if __name__ == "__main__":
    main()
