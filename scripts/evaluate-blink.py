from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'public/assets/hero-4k-digital-art.png'
OUT = ROOT / 'docs/blink-debug'
OUT.mkdir(parents=True, exist_ok=True)

# Initial conservative hand placement in the original 3840x2160 image.
# This is an experiment only; it is not a claim of final eye segmentation.
regions = {
    'canvas': {'width': 3840, 'height': 2160},
    'leftEye': {'x': 2080, 'y': 625, 'width': 190, 'height': 125},
    'rightEye': {'x': 2310, 'y': 620, 'width': 190, 'height': 125},
    'debugCrop': {'x': 1980, 'y': 540, 'width': 570, 'height': 290},
    'method': 'manual candidate placement; eye masks are intentionally conservative',
}

import json
(ROOT / 'docs/blink-regions.json').write_text(json.dumps(regions, indent=2) + '\n', encoding='utf-8')

source = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
if source is None:
    raise SystemExit('Could not read source image')

crop = regions['debugCrop']
x, y, w, h = crop['x'], crop['y'], crop['width'], crop['height']
cv2.imwrite(str(OUT / 'source-eyes.png'), source[y:y+h, x:x+w])

# Masks cover only iris/sclera candidates, leaving brows, lashes, lids and hair untouched.
mask = np.zeros(source.shape[:2], np.uint8)
for eye in (regions['leftEye'], regions['rightEye']):
    ex, ey, ew, eh = eye['x'], eye['y'], eye['width'], eye['height']
    cv2.ellipse(mask, (ex + ew // 2, ey + eh // 2), (ew // 3, eh // 4), 0, 0, 360, 255, -1)

filled = cv2.inpaint(source, mask, 5, cv2.INPAINT_TELEA)

# Draw fine, low-contrast eyelash arcs at 4x resolution then downsample for antialiasing.
layer = Image.fromarray(cv2.cvtColor(filled, cv2.COLOR_BGR2RGBA))
draw = ImageDraw.Draw(layer)
for eye in (regions['leftEye'], regions['rightEye']):
    ex, ey, ew, eh = eye['x'], eye['y'], eye['width'], eye['height']
    # A shallow arc follows the original eye direction without making a cartoon smile.
    box = (ex + ew // 7, ey + eh // 3, ex + ew - ew // 7, ey + eh * 2 // 3)
    draw.arc(box, 195, 345, fill=(58, 39, 37, 185), width=7)

result = cv2.cvtColor(np.array(layer), cv2.COLOR_RGBA2BGRA)
cv2.imwrite(str(OUT / 'closed-candidate.png'), result)
cv2.imwrite(str(OUT / 'closed-preview.png'), result[y:y+h, x:x+w])

diff = cv2.absdiff(source, result[:, :, :3])
diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
heat = np.zeros_like(source)
heat[:, :, 2] = np.clip(diff_gray * 5, 0, 255)
cv2.imwrite(str(OUT / 'difference.png'), heat)

rgba = np.zeros((*source.shape[:2], 4), np.uint8)
changed = np.max(diff, axis=2) > 2
rgba[changed, :3] = cv2.cvtColor(result[:, :, :3], cv2.COLOR_BGR2RGB)[changed]
rgba[changed, 3] = np.clip(diff_gray[changed] * 8, 0, 255)
Image.fromarray(rgba).crop((x, y, x+w, y+h)).save(OUT / 'overlay-preview.png')

outside = mask == 0
outside_changed = int(np.count_nonzero((diff_gray > 8) & outside))
inside_changed = int(np.count_nonzero((diff_gray > 8) & (mask > 0)))
print(json.dumps({'outside_changed_pixels': outside_changed, 'inside_changed_pixels': inside_changed}))
