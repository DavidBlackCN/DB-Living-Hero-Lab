"""Author registered pigment and Sky-mixture repair plates for fixed seams.

Fixed polygons select the known defects. Only pale, old-sky-mixed pixels near
the existing boundary borrow pigment from adjacent interior leaves or stone.
The pigment plate replaces Albedo before lighting. A paired Night-only plate
recovers Sky mixture in distant foliage. Neither multiplies final display color.
"""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public/assets/hero"
SKY = ASSETS / "sky"
SIZE = (1672, 941)

# Fixed Artwork-Space review areas. The boundary band, rather than these broad
# polygons, determines which pixels may actually change.
AREAS = [
    [(810, 0), (986, 0), (998, 374), (827, 374)],  # left vine / distant column
    [(944, 0), (1105, 0), (1091, 226), (960, 259)],  # upper central pillar
    [(1272, 208), (1325, 205), (1325, 310), (1272, 312)],  # ribbon-side gap
    [(1355, 68), (1672, 50), (1672, 345), (1350, 342)],  # roof and spires
    [(1395, 0), (1672, 0), (1672, 139), (1460, 108)],  # upper-right foliage
]
SKY_GAPS = [
    [(902, 175), (961, 170), (970, 343), (900, 345)],
    [(1271, 214), (1324, 209), (1324, 305), (1271, 307)],
    [(1370, 181), (1416, 175), (1422, 232), (1368, 236)],
    [(1444, 166), (1480, 160), (1490, 225), (1441, 229)],
    [(1537, 140), (1605, 135), (1605, 214), (1535, 215)],
    [(1583, 0), (1672, 0), (1672, 129), (1581, 111)],
]


def main() -> None:
    base = np.asarray(Image.open(ASSETS / "base/base-albedo.png").convert("RGB"), dtype=np.float32) / 255
    sky = np.asarray(Image.open(SKY / "sky-mask.png").convert("L"), dtype=np.float32) / 255
    if base.shape[:2] != (SIZE[1], SIZE[0]) or sky.shape != base.shape[:2]:
        raise ValueError("Artwork registration mismatch")

    area_image = Image.new("L", SIZE, 0)
    for polygon in AREAS:
        ImageDraw.Draw(area_image).polygon(polygon, fill=255)
    area = np.asarray(area_image, dtype=np.float32) / 255
    gap_image = Image.new("L", SIZE, 0)
    for polygon in SKY_GAPS:
        ImageDraw.Draw(gap_image).polygon(polygon, fill=255)
    gap_soft = cv2.GaussianBlur(np.asarray(gap_image, dtype=np.float32) / 255,
                                (0, 0), 3.0)
    # The tower's actual left wall starts around x=1325 in this fixed artwork.
    # Protect the wall and all three spires while leaving the ribbon-side
    # opening at x=1271..1324 available for old-sky replacement.
    tower_image = Image.new("L", SIZE, 0)
    tower_draw = ImageDraw.Draw(tower_image)
    tower_draw.rectangle((1320, 40, 1408, 164), fill=255)
    tower_draw.rectangle((1305, 110, 1324, 164), fill=255)
    tower_draw.rectangle((1325, 165, 1408, 276), fill=255)
    tower_core = np.asarray(tower_image, dtype=np.float32) / 255
    tower_protect = cv2.GaussianBlur(tower_core, (0, 0), 1.2)
    ribbon_image = Image.new("L", SIZE, 0)
    ImageDraw.Draw(ribbon_image).polygon(SKY_GAPS[1], fill=255)
    ribbon_soft = cv2.GaussianBlur(np.asarray(ribbon_image, dtype=np.float32) / 255,
                                  (0, 0), 2.0)

    sky_core = sky >= 0.985
    sky_distance = distance_transform_edt(~sky_core)
    stone_core = (sky <= 0.01) & (sky_distance >= 6.0)
    stone_distance, stone_index = distance_transform_edt(~stone_core, return_indices=True)
    stone_interior = base[stone_index[0], stone_index[1]]
    # Warm-pigment seeds are taken from the fixed leaf/tree details, not from
    # the pale surrounding sky. Nearby stone uses its own interior seed.
    warm_core = (sky < 0.03) & (base[:, :, 0] - base[:, :, 2] > 0.075) \
        & (base[:, :, 0] - base[:, :, 1] > 0.025)
    warm_distance, warm_index = distance_transform_edt(~warm_core, return_indices=True)
    warm_interior = base[warm_index[0], warm_index[1]]
    deep_seed = (warm_core & (np.mean(base, axis=2) < 0.64)).astype(np.float32)
    seed_density = cv2.GaussianBlur(deep_seed, (0, 0), 9.0)
    deep_color = np.stack([
        cv2.GaussianBlur(base[:, :, channel] * deep_seed, (0, 0), 9.0)
        / np.maximum(seed_density, 0.001)
        for channel in range(3)
    ], axis=2)
    foliage_color = np.where((seed_density > 0.002)[..., None], deep_color, warm_interior)
    leaf_nearby = np.clip((19.0 - warm_distance) / 8.0, 0, 1)
    # Blue spill relative to an actual leaf/stone interior is the only color
    # cue. It modulates a hand-located repair, not the global Sky matte.
    leaf_spill = np.clip((base[:, :, 2] - warm_interior[:, :, 2] - 0.015) / 0.15, 0, 1)
    stone_spill = np.clip((base[:, :, 2] - stone_interior[:, :, 2] - 0.025) / 0.18, 0, 1)
    leaf_weight = leaf_nearby * np.clip((leaf_spill - 0.10) / 0.32, 0, 1)
    stone_weight = (1 - leaf_nearby) * stone_spill * np.clip((11 - stone_distance) / 5, 0, 1)
    recovered = np.where((leaf_nearby > 0.4)[..., None], warm_interior, stone_interior)
    # A quarter of the source color retains soft distant brush texture.
    recovered = recovered * 0.88 + base * 0.12
    leaf_band = np.clip((15.0 - sky_distance) / 6.0, 0, 1)
    stone_band = np.clip((8.0 - sky_distance) / 5.0, 0, 1)
    edge = (sky < 0.985).astype(np.float32)
    # Smooth the authored ROI cut only; never blur the material edge itself.
    area_soft = cv2.GaussianBlur(area, (0, 0), 4.0)
    edge *= area_soft
    strength = np.clip(edge * (leaf_weight * leaf_band + stone_weight * stone_band * 0.55), 0, 1)
    strength *= 1 - tower_protect
    strength[tower_core > 0.5] = 0
    # The distant tree crowns carry a broader old-sky mix than the crisp
    # foreground leaves. Reconstruct only their pale pigment, with a feathered
    # hand located region; no architecture or opaque foliage is selected.
    rgb = np.uint8(np.rint(np.clip(recovered, 0, 1) * 255))
    alpha = np.uint8(np.rint(strength * 255))
    Image.fromarray(np.dstack([rgb, alpha]), "RGBA").save(SKY / "sky-edge-reconstruction.png")

    # Estimate the old-sky fraction of each fixed foliage edge from the line
    # between its local painted pigment and nearby original open sky. This is
    # the paired decontamination term, not a display-space darkening mask.
    _, sky_index = distance_transform_edt(~sky_core, return_indices=True)
    old_sky = base[sky_index[0], sky_index[1]]
    axis = old_sky - foliage_color
    projection = np.clip(np.sum((base - foliage_color) * axis, axis=2) /
                         np.maximum(np.sum(axis * axis, axis=2), 0.015), 0, 1)
    material_contrast = np.clip(np.sqrt(np.sum(axis * axis, axis=2)) / 0.22, 0, 1)
    luma_gate = np.clip((np.mean(base, axis=2) - 0.48) / 0.18, 0, 1)
    leaf_connected = np.clip((32 - warm_distance) / 9, 0, 1)
    boundary = np.clip((42 - sky_distance) / 12, 0, 1)
    coverage = gap_soft * projection * material_contrast * luma_gate \
        * np.maximum(leaf_connected * boundary, ribbon_soft) * (sky < 0.985)
    # One-pixel smoothing removes isolated salt-and-pepper islands without
    # softening the real leaf silhouette in the source picture.
    coverage = cv2.GaussianBlur(coverage.astype(np.float32), (0, 0), 0.7)
    # The ribbon-side opening contains nearly pure old sky in small gaps;
    # finish replacing that contribution instead of leaving a pale residue.
    coverage = np.clip(coverage * (1 + 0.52 * ribbon_soft), 0, 1)
    coverage *= 1 - tower_protect
    coverage[tower_core > 0.5] = 0
    coverage_alpha = np.uint8(np.rint(np.clip(coverage, 0, 1) * 255))
    night_foreground = np.uint8(np.rint(np.clip(foliage_color * 0.85 + base * 0.15, 0, 1) * 255))
    Image.fromarray(np.dstack((night_foreground, coverage_alpha)), "RGBA").save(SKY / "sky-edge-skyfill.png")

    print(f"reconstruction: {int(np.count_nonzero(alpha))} edge pixels; "
          f"Night Sky coverage: {int(np.count_nonzero(coverage_alpha))} pixels")


if __name__ == "__main__":
    main()
