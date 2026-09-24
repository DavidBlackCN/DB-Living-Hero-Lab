"""Build registered, restrained time-of-day sky art for the frozen hero base."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public/assets/hero/base/base-albedo.png"
OUT = ROOT / "public/assets/hero/sky"
QA = ROOT / "docs/validation/sky-assets"


def make_mask(rgb: np.ndarray) -> np.ndarray:
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[:h, :w]
    r, g, b = (rgb[:, :, i].astype(np.float32) for i in range(3))
    blue = np.minimum(b - r, b - g)
    light = (r + g + b) / 3

    labels = np.full((h, w), cv2.GC_PR_FGD, np.uint8)
    labels[(xx < 840) | (yy > 430)] = cv2.GC_BGD
    labels[(xx > 840) & (yy < 390) & (blue > 3) & (light > 153)] = cv2.GC_PR_BGD
    labels[(xx > 850) & (yy < 320) & (blue > 10) & (light > 175)] = cv2.GC_BGD
    labels[(xx > 840) & (yy < 410) & ((r - b > 8) | (light < 115))] = cv2.GC_FGD
    # A few indisputable open-sky seeds distributed across each opening.
    for x, y, radius in [(905, 65, 8), (1090, 12, 8), (1295, 37, 8),
                         (1420, 62, 8), (1580, 15, 8), (1450, 182, 8)]:
        cv2.circle(labels, (x, y), radius, cv2.GC_BGD, -1)
    bg = np.zeros((1, 65), np.float64)
    fg = np.zeros((1, 65), np.float64)
    cv2.grabCut(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), labels, None, bg, fg, 6, cv2.GC_INIT_WITH_MASK)
    mask = np.where((labels == cv2.GC_BGD) | (labels == cv2.GC_PR_BGD), 255, 0).astype(np.uint8)
    # The blue-gray sky is the only cool, light surface in the exposed openings.
    # This conservative color gate prevents GrabCut from leaking into brown hair,
    # limestone, and the lower distant architecture.
    mask[(xx < 850) | (yy > 320) | (blue < 3) | (light < 155)] = 0
    count, components, stats, _ = cv2.connectedComponentsWithStats((mask > 0).astype(np.uint8))
    for component in range(1, count):
        if stats[component, cv2.CC_STAT_AREA] < 5:
            mask[components == component] = 0
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return cv2.GaussianBlur(mask, (0, 0), .65)


def sky_plate(rgb: np.ndarray, name: str) -> np.ndarray:
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[:h, :w].astype(np.float32)
    anchors = {
        "dawn": [(0, (166, 181, 195)), (110, (186, 194, 203)), (265, (205, 201, 197))],
        "noon": [(0, (180, 190, 204)), (120, (194, 201, 211)), (265, (212, 214, 218))],
        "dusk": [(0, (128, 139, 155)), (105, (159, 155, 165)), (205, (206, 170, 160)), (290, (225, 183, 156))],
        "night": [(0, (35, 41, 47)), (265, (49, 52, 55))],
    }[name]
    plate = np.stack([
        np.interp(yy, [a[0] for a in anchors], [a[1][ch] for a in anchors])
        for ch in range(3)
    ], axis=-1).astype(np.float32)
    if name != "night":
        # Retain only very broad cloud variation from the frozen sky.  This
        # follows its painted shapes without carrying its blue color into dusk.
        source_luma = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
        cloud = cv2.GaussianBlur(source_luma, (0, 0), 18) - cv2.GaussianBlur(source_luma, (0, 0), 70)
        cloud = np.clip(cloud, -14, 14)
        strength = {"dawn": .22, "noon": .34, "dusk": .18}[name]
        plate += cloud[:, :, None] * strength
    else:
        # Very broad, deterministic atmospheric variation.  Its few-level
        # range adds depth without reading as clouds or painted detail.
        rng = np.random.default_rng(26)
        coarse = rng.normal(0, 1, (5, 9)).astype(np.float32)
        air = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_CUBIC)
        air = cv2.GaussianBlur(air, (0, 0), 90)
        visible_air = air[:260, 850:1644]
        air = (air - visible_air.mean()) / max(float(visible_air.std()), 1e-6)
        air = np.clip(air * 1.8, -3.5, 3.5)
        plate += air[:, :, None]
    # Minute atmospheric variation avoids a flat color band, while night
    # remains calm and nearly uniform in the small visible openings.
    if name != "night":
        plate += (np.sin(xx / 235) + np.cos((xx + yy) / 310))[:, :, None] * 1.1
    return np.uint8(np.clip(plate, 0, 255))


def main() -> None:
    rgb = np.asarray(Image.open(BASE).convert("RGB"))
    mask = make_mask(rgb)
    OUT.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask).save(OUT / "sky-mask.png")
    tint = rgb.copy().astype(np.float32)
    tint[:, :, 0] = tint[:, :, 0] * (1 - mask / 255 * .65) + 255 * (mask / 255 * .65)
    tint[:, :, 1] *= 1 - mask / 255 * .65
    tint[:, :, 2] *= 1 - mask / 255 * .65
    Image.fromarray(tint.astype(np.uint8)).save(QA / "mask-overlay.png")
    previews = []
    for name in ("dawn", "noon", "dusk", "night"):
        plate = sky_plate(rgb, name)
        rgba = np.dstack((plate, mask))
        Image.fromarray(rgba, "RGBA").save(OUT / f"sky-{name}.png")
        alpha = mask.astype(np.float32)[:, :, None] / 255
        composite = np.uint8(np.clip(rgb * (1 - alpha) + plate * alpha, 0, 255))
        Image.fromarray(composite).save(QA / f"sky-{name}-on-base.png")
        previews.append(Image.fromarray(composite).resize((836, 470)))
    montage = Image.new("RGB", (1672, 940))
    for index, preview in enumerate(previews):
        montage.paste(preview, ((index % 2) * 836, (index // 2) * 470))
    montage.save(QA / "four-sky-comparison.png")
    print("mask pixels", np.count_nonzero(mask), "range", np.where(mask > 0)[1].min(), np.where(mask > 0)[1].max(), np.where(mask > 0)[0].max())


if __name__ == "__main__":
    main()
