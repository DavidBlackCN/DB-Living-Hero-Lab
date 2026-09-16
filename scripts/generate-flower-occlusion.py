"""Extract only warm/white foreground within authored flower ROIs; never repaint.

The cool skyline behind the white bouquet makes this narrow color separation
useful here. It is NOT general segmentation. Geometry and thresholds live in
scene-regions.json. Output is grayscale coverage, embedded into scene-masks.svg.
"""
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parents[1]
regions = json.loads((root / 'docs/scene-regions.json').read_text(encoding='utf-8'))
source = Image.open(root / 'public/assets/hero-4k-digital-art.png').convert('RGB')
scale = source.width / 1200
roi = Image.new('L', source.size)
draw = ImageDraw.Draw(roi)
# Parse the deliberately polygon-only source path (M/L/H/V/Z), so all geometry
# remains in scene-regions.json rather than being duplicated in this generator.
points = []
x = y = 0.0
for command, data in re.findall(r'([MLHVZ])([^MLHVZ]*)', regions['windowFlowers']):
    values = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', data)]
    if command == 'Z':
        draw.polygon(points, fill=255)
        points = []
        continue
    if command in ('M', 'L'):
        x, y = values
    elif command == 'H':
        x = values[0]
    elif command == 'V':
        y = values[0]
    points.append((x*scale, y*scale))
config = regions['windowFlowerExtraction']
radius = round(config['roiPadding'] * scale)
roi = roi.filter(ImageFilter.MaxFilter(radius*2+1))
rgb = np.asarray(source, dtype=np.float32)
def smooth(value, bounds):
    t = np.clip((value-bounds[0])/(bounds[1]-bounds[0]), 0, 1)
    return t*t*(3-2*t)
warm = smooth(rgb[:,:,0]-rgb[:,:,2], config['redMinusBlue'])
luma = rgb[:,:,0]*.2126 + rgb[:,:,1]*.7152 + rgb[:,:,2]*.0722
coverage = warm * smooth(luma, config['minimumLuminance']) * np.asarray(roi)/255
# Broad search polygons also contain out-of-focus exterior foliage. Require a
# nearby bright petal seed, rather than cutting those background colors into
# opaque polygon-shaped islands. Confirmed shaded petal seeds are source data.
seeds = Image.fromarray(np.uint8((luma > config['seedLuminance']) & (warm > .95) & (np.asarray(roi) > 0))*255)
seed_draw = ImageDraw.Draw(seeds)
for sx, sy in config['foregroundSeeds']:
    seed_draw.ellipse((sx*scale-2, sy*scale-2, sx*scale+2, sy*scale+2), fill=255)
reach = round(config['seedReach']*scale)
near_petals = seeds.filter(ImageFilter.MaxFilter(reach*2+1)).filter(ImageFilter.GaussianBlur(1.0))
coverage *= np.asarray(near_petals)/255
# Fine antialiasing, not a broad spatial blur. The reference polygons are search
# areas only, so they cannot become opaque polygon-shaped cutouts in the sky.
mask = Image.fromarray(np.uint8(coverage*255)).filter(ImageFilter.GaussianBlur(.45))
out = root / 'public/assets/generated/window-flower-occlusion.png'
mask.save(out)
