"""Create a registered semantic-refinement candidate for the frozen Base-4.

The handful of in-memory region hints describe broad materials only. They are
not runtime masks, and the output is always one RGB image in Base pixel space.
Run from the repository root: python scripts/generate_normal_v2.py
"""

from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public/assets/hero/base/base-albedo.png"
V1 = ROOT / "public/assets/hero/normal/base-normal-v1.png"
OUTPUT = ROOT / "public/assets/hero/normal/base-normal-v2.png"
SIZE = (1672, 941)


def polygon_mask(points: list[tuple[int, int]], feather: float = 8) -> np.ndarray:
    image = Image.new("L", SIZE, 0)
    ImageDraw.Draw(image).polygon(points, fill=255)
    return np.asarray(image.filter(ImageFilter.GaussianBlur(feather)), np.float32) / 255


def soften_gate(gate: np.ndarray, radius: float = 4) -> np.ndarray:
    image = Image.fromarray((gate * 255).astype(np.uint8), "L")
    return np.asarray(image.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255


def field_from_v1(image: Image.Image, blur: float, strength: float) -> np.ndarray:
    rgb = np.asarray(image.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255
    xy = (rgb[..., :2] * 2 - 1) * strength
    return np.concatenate((xy, np.ones((*xy.shape[:2], 1), np.float32)), axis=-1)


def apply(field: np.ndarray, candidate: np.ndarray, weight: np.ndarray) -> None:
    field[:] = field * (1 - weight[..., None]) + candidate * weight[..., None]


def main() -> None:
    base_image = Image.open(BASE).convert("RGB")
    v1_image = Image.open(V1).convert("RGB")
    if base_image.size != SIZE or v1_image.size != SIZE:
        raise ValueError("Base and Normal v1 must both match 1672x941 Artwork Space")

    base = np.asarray(base_image, np.float32)
    red, green, blue = base[..., 0], base[..., 1], base[..., 2]
    yy, xx = np.mgrid[0:SIZE[1], 0:SIZE[0]].astype(np.float32)

    # Broad default: architectural forms remain, painted specks and linework fade.
    normal = field_from_v1(v1_image, blur=12, strength=0.52)

    # Large stone planes survive even where the painted texture is uniform.
    stone_color = soften_gate(((np.abs(red - green) < 30) &
                               (np.abs(green - blue) < 27) &
                               (red > 78) & (red < 235)).astype(np.float32), 4)
    pillar = polygon_mask([(540, 0), (851, 0), (854, 562), (526, 571)], 9)
    pillar_field = field_from_v1(v1_image, blur=25, strength=0.38)
    pillar_field[..., 0] += -0.01 + 0.115 * np.tanh((xx - 745) / 13)
    apply(normal, pillar_field, pillar * stone_color * 0.88)

    rail_top = polygon_mask([(0, 701), (725, 697), (851, 685), (913, 690),
                             (913, 724), (0, 757)], 7)
    rail_top = np.maximum(rail_top, polygon_mask([(1420, 661), (1672, 651),
                                                  (1672, 697), (1420, 712)], 7))
    rail_field = field_from_v1(v1_image, blur=22, strength=0.25)
    rail_field[..., 1] -= 0.17
    apply(normal, rail_field, rail_top * stone_color * 0.85)

    # Sky has no reliable local surface orientation. Color gating protects the
    # distant towers and autumn foliage inside this intentionally broad area.
    sky_region = polygon_mask([(840, 0), (1672, 0), (1672, 235), (1460, 205),
                               (1300, 165), (1180, 85), (1020, 70), (840, 95)], 12)
    sky_color = soften_gate(((blue > red + 7) & (blue > green + 4) &
                             (green > 120)).astype(np.float32), 3)
    neutral = np.zeros_like(normal)
    neutral[..., 2] = 1
    apply(normal, neutral, sky_region * sky_color * 0.95)

    # Garments: keep broad fold direction, discard vest shading and plaid edges.
    shirt = polygon_mask([(1000, 335), (1065, 343), (1072, 467), (1009, 597),
                          (892, 695), (840, 647), (928, 530), (958, 385)], 9)
    shirt = np.maximum(shirt, polygon_mask([(1243, 331), (1280, 345), (1355, 522),
                                            (1398, 680), (1350, 730), (1289, 603),
                                            (1260, 486)], 9))
    apply(normal, field_from_v1(v1_image, blur=14, strength=0.48), shirt * 0.9)

    vest = polygon_mask([(1060, 339), (1112, 353), (1165, 430), (1215, 351),
                         (1260, 350), (1274, 564), (1217, 596), (1067, 585)], 10)
    vest_field = field_from_v1(v1_image, blur=25, strength=0.3)
    vest_field[..., 0] += np.clip((xx - 1165) / 180, -1, 1) * 0.08
    apply(normal, vest_field, vest * 0.93)

    skirt = polygon_mask([(1075, 585), (1293, 583), (1383, 844),
                          (1230, 860), (977, 856)], 8)
    skirt_field = field_from_v1(v1_image, blur=22, strength=0.52)
    skirt_field[..., 0] += np.sin((xx - 1040) / 26) * 0.055
    apply(normal, skirt_field, skirt * 0.94)

    # Two long hair masses get gently curved volume across their widths. A color
    # gate avoids bending the background between separated locks.
    hair_color = soften_gate(((red > green * 1.10) & (green > blue * 1.04) &
                              (red < 220) & (red > 45)).astype(np.float32), 3)
    left_hair = polygon_mask([(1058, 90), (1140, 110), (1110, 293),
                              (1132, 593), (905, 587), (887, 442), (987, 286)], 10)
    right_hair = polygon_mask([(1180, 85), (1267, 99), (1302, 295),
                               (1453, 550), (1430, 626), (1240, 547),
                               (1190, 300)], 10)
    hair_field = field_from_v1(v1_image, blur=17, strength=0.30)
    left_center = 1063 - 0.13 * (yy - 160)
    right_center = 1242 + 0.24 * (yy - 160)
    hair_field[..., 0] += (np.clip((xx - left_center) / 115, -1, 1) * 0.18 * left_hair +
                           np.clip((xx - right_center) / 125, -1, 1) * 0.18 * right_hair)
    hair_field[..., 1] += 0.04 * (left_hair + right_hair)
    apply(normal, hair_field, np.maximum(left_hair, right_hair) * hair_color * 0.9)

    # Face: replace the iris/eyelash and blush-derived relief with one continuous
    # shallow curved surface. Expand the complexion gate across the eyes.
    face_region = polygon_mask([(1088, 190), (1122, 177), (1171, 183),
                                (1215, 203), (1230, 240), (1204, 282),
                                (1165, 301), (1127, 287), (1090, 251)], 5)
    skin_color = ((red > 165) & (red > green * 1.045) &
                  (green > blue * 1.015)).astype(np.uint8) * 255
    skin_image = Image.fromarray(skin_color, "L").filter(ImageFilter.MaxFilter(21))
    skin_gate = np.asarray(skin_image.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    face_field = np.zeros_like(normal)
    face_field[..., 0] = np.clip((xx - 1157) / 93, -1, 1) * 0.22
    face_field[..., 1] = np.clip((yy - 239) / 84, -1, 1) * 0.16
    face_field[..., 2] = 1
    apply(normal, face_field, face_region * skin_gate * 0.98)

    # Exposed hands and legs are broad skin surfaces, without line-art relief.
    skin_regions = [
        [(746, 654), (780, 645), (838, 654), (879, 678), (855, 699), (748, 703)],
        [(1356, 730), (1404, 733), (1413, 811), (1386, 848), (1355, 815)],
        [(1055, 832), (1155, 833), (1203, 941), (1031, 941)],
        [(1200, 836), (1295, 836), (1321, 941), (1181, 941)],
    ]
    skin_region = np.maximum.reduce([polygon_mask(points, 7) for points in skin_regions])
    skin_field = field_from_v1(v1_image, blur=23, strength=0.12)
    apply(normal, skin_field, skin_region * skin_gate * 0.93)

    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    rgb = np.clip(np.rint((normal * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(rgb, "RGB").save(OUTPUT, optimize=True)
    print(f"{OUTPUT.relative_to(ROOT)}: {SIZE}, RGB, registered source pixels")


if __name__ == "__main__":
    main()
