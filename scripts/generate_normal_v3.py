"""Local Normal v3 corrections on top of the registered v2 bitmap.

All masks exist only during generation. No runtime mask is exported.
Run from the repository root: python scripts/generate_normal_v3.py
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public/assets/hero/base/base-albedo.png"
V2 = ROOT / "public/assets/hero/normal/base-normal-v2.png"
OUTPUT = ROOT / "public/assets/hero/normal/base-normal-v3.png"
SIZE = (1672, 941)


def polygon(points: list[tuple[int, int]], feather: float) -> np.ndarray:
    mask = Image.new("L", SIZE, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return np.asarray(mask.filter(ImageFilter.GaussianBlur(feather)), np.float32) / 255


def tube(points: list[tuple[int, int]], width: int, feather: float = 2) -> np.ndarray:
    mask = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.line(points, fill=255, width=width, joint="curve")
    for point in points:
        r = width / 2
        draw.ellipse((point[0] - r, point[1] - r, point[0] + r, point[1] + r), fill=255)
    return np.asarray(mask.filter(ImageFilter.GaussianBlur(feather)), np.float32) / 255


def blend(out: np.ndarray, field: np.ndarray, mask: np.ndarray) -> None:
    out[:] = out * (1 - mask[..., None]) + field * mask[..., None]


def decode(image: Image.Image) -> np.ndarray:
    rgb = np.asarray(image, np.float32) / 255
    vectors = rgb * 2 - 1
    vectors /= np.linalg.norm(vectors, axis=-1, keepdims=True)
    return vectors


def main() -> None:
    base_image = Image.open(BASE).convert("RGB")
    v2_image = Image.open(V2).convert("RGB")
    if base_image.size != SIZE or v2_image.size != SIZE:
        raise ValueError("Base and v2 must share 1672x941 Artwork Space")
    base = np.asarray(base_image, np.float32)
    red, green, blue = base[..., 0], base[..., 1], base[..., 2]
    yy, xx = np.mgrid[0:SIZE[1], 0:SIZE[0]].astype(np.float32)
    v2 = decode(v2_image)
    out = v2.copy()
    neutral = np.zeros_like(out)
    neutral[..., 2] = 1

    # Individually traced outer locks. The narrow tubes and explicit per-lock
    # directions replace v2's broad hair-color gate at the outer edges.
    locks = [
        ([(1073, 246), (1036, 287), (989, 332), (937, 385)], 12, -0.07, 0.025),
        ([(1067, 271), (1034, 321), (997, 378), (959, 439)], 13, -0.055, 0.035),
        ([(1084, 304), (1057, 364), (1032, 426), (1007, 489)], 14, -0.035, 0.04),
        ([(1260, 271), (1294, 327), (1330, 394), (1372, 468)], 13, 0.055, 0.035),
        ([(1248, 290), (1275, 354), (1302, 423), (1332, 494)], 12, 0.035, 0.04),
    ]
    hair_color = ((red > green * 1.08) & (green > blue * 1.025) &
                  (red > 44) & (red < 220)).astype(np.float32)
    hair_gate = np.asarray(Image.fromarray((hair_color * 255).astype(np.uint8), "L")
                           .filter(ImageFilter.GaussianBlur(2)), np.float32) / 255
    all_locks = np.zeros((SIZE[1], SIZE[0]), np.float32)
    for points, width, tilt_x, tilt_y in locks:
        region = tube(points, width)
        all_locks = np.maximum(all_locks, region)
        center_x = np.interp(yy, [p[1] for p in points], [p[0] for p in points])
        field = neutral.copy()
        field[..., 0] = tilt_x + np.clip((xx - center_x) / (width / 2), -1, 1) * 0.07
        field[..., 1] = tilt_y
        blend(out, field, region * hair_gate * 0.85)

    # Unresolved holes between those strands should not inherit a brown mass's
    # normal from v2. Only the outer crossing corridors are neutralized.
    left_edge = polygon([(896, 310), (1037, 270), (1050, 380), (983, 579),
                         (877, 592), (875, 408)], 8)
    right_edge = polygon([(1276, 279), (1355, 322), (1469, 479),
                          (1461, 606), (1343, 592), (1276, 434)], 8)
    gaps = np.maximum(left_edge, right_edge) * (1 - all_locks) * (1 - hair_gate)
    blend(out, neutral, gaps * 0.65)
    # Color alone cannot separate russet leaves from hair. These two outer
    # background windows are explicitly neutral unless a traced lock crosses.
    background_gaps = polygon([(875, 367), (934, 355), (951, 431),
                               (919, 542), (875, 548)], 6)
    background_gaps = np.maximum(background_gaps, polygon([(1383, 354), (1473, 409),
                                                            (1471, 589), (1416, 576),
                                                            (1376, 445)], 6))
    blend(out, neutral, background_gaps * (1 - all_locks) * 0.78)

    # A little more low-pass filtering inside garments removes residual stripe
    # and line-art response while keeping v2's long-scale volume unchanged.
    garment = polygon([(973, 348), (1060, 342), (1070, 470), (996, 598),
                       (876, 688), (855, 645), (918, 540)], 6)
    garment = np.maximum(garment, polygon([(1255, 346), (1281, 360),
                                           (1342, 535), (1387, 694),
                                           (1358, 719), (1288, 579)], 6))
    garment = np.maximum(garment, polygon([(1082, 410), (1240, 404),
                                           (1263, 555), (1204, 574),
                                           (1083, 558)], 5))
    garment = np.maximum(garment, polygon([(1097, 606), (1291, 607),
                                           (1362, 827), (1224, 837),
                                           (994, 835)], 6))
    smoothed = decode(v2_image.filter(ImageFilter.GaussianBlur(8)))
    blend(out, smoothed, garment * 0.72)

    # Distant masonry responds less than the foreground pillar. Color gating
    # excludes blue sky, autumn leaves, and most foreground hair silhouettes.
    distant = polygon([(858, 0), (1051, 0), (1048, 332), (862, 365)], 8)
    distant = np.maximum(distant, polygon([(1280, 0), (1672, 0),
                                           (1672, 649), (1457, 631),
                                           (1413, 306), (1280, 244)], 8))
    masonry = ((np.abs(red - green) < 19) & (np.abs(green - blue) < 22) &
               (red > 72) & (red < 235)).astype(np.float32)
    masonry = np.asarray(Image.fromarray((masonry * 255).astype(np.uint8), "L")
                          .filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    distant_field = decode(v2_image.filter(ImageFilter.GaussianBlur(16)))
    distant_field[..., :2] *= 0.46
    blend(out, distant_field, distant * masonry * 0.88)

    # Decorative stone below the accepted railing top stays shallow.
    carving = polygon([(0, 839), (975, 825), (975, 941), (0, 941)], 8)
    carving = np.maximum(carving, polygon([(1420, 798), (1672, 787),
                                           (1672, 941), (1420, 941)], 8))
    carved_field = decode(v2_image.filter(ImageFilter.GaussianBlur(11)))
    carved_field[..., :2] *= 0.55
    blend(out, carved_field, carving * masonry * 0.8)

    out /= np.linalg.norm(out, axis=-1, keepdims=True)
    rgb = np.clip(np.rint((out * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)

    # Exact preservation of v2's accepted areas takes precedence over nearby
    # feathering. This also makes unintended global edits testable.
    protected = np.zeros((SIZE[1], SIZE[0]), bool)
    protected[170:310, 1070:1245] = True            # face
    protected[0:590, 520:870] = True               # main pillar
    protected[650:835, 0:900] = True               # left railing
    protected[630:795, 1400:1672] = True           # right railing
    protected |= ((blue > red + 7) & (blue > green + 4) &
                  (green > 120) & (yy < 235) & (xx > 840))  # sky
    v2_rgb = np.asarray(v2_image)
    rgb[protected] = v2_rgb[protected]
    Image.fromarray(rgb, "RGB").save(OUTPUT, optimize=True)
    changed = np.any(rgb != v2_rgb, axis=2)
    print(f"{OUTPUT.relative_to(ROOT)}: {SIZE}, RGB")
    print(f"changed pixels {np.count_nonzero(changed)}; protected changed {np.count_nonzero(changed & protected)}")


if __name__ == "__main__":
    main()
