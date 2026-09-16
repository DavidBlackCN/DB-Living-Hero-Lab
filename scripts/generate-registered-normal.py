"""Bake source-registered, authored surface fields; never derive height from color.

This is a deterministic geometry candidate, not recovered ground-truth geometry.
Differentiate each unmasked surface first, then composite normalized vectors.
Differentiating a masked height would emboss every silhouette with a false rim.
"""
import json
import re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
regions = json.loads((ROOT / 'docs/scene-regions.json').read_text(encoding='utf-8'))
surfaces = json.loads((ROOT / 'docs/normal-surfaces.json').read_text(encoding='utf-8'))
WIDTH, HEIGHT, SCALE = 3840, 2160, 3.2


def path_mask(path):
    """Rasterize our explicit absolute M/L/H/V/C/Q/Z source paths at native size."""
    image = Image.new('L', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    current = np.zeros(2)
    points = []
    for command, args in re.findall(r'([MLHVCQZ])([^MLHVCQZ]*)', path):
        values = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', args)]
        if command == 'Z':
            draw.polygon([tuple(p*SCALE) for p in points], fill=255)
            points = []
            continue
        if command in ('M', 'L'):
            current = np.array(values)
            points.append(current)
        elif command in ('H', 'V'):
            current = current.copy()
            current[0 if command == 'H' else 1] = values[0]
            points.append(current)
        else:
            controls = [current, *np.asarray(values).reshape(-1, 2)]
            for t in np.linspace(0, 1, 65)[1:]:
                curve = np.array(controls)
                while len(curve) > 1:
                    curve = curve[:-1]*(1-t)+curve[1:]*t
                points.append(curve[0])
            current = controls[-1]
    return np.asarray(image.filter(ImageFilter.GaussianBlur(.8)), dtype=np.float32)/255


def unit(vector):
    return vector / np.maximum(np.linalg.norm(vector, axis=-1, keepdims=True), 1e-6)


y, x = np.mgrid[:HEIGHT, :WIDTH].astype(np.float32)/SCALE
result = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
result[:, :, 2] = 1
for layer in surfaces['layers']:
    mask = path_mask(layer.get('path') or regions[layer['region']])
    ys, xs = np.nonzero(mask)
    x0, x1 = max(0, xs.min()-4), min(WIDTH, xs.max()+5)
    y0, y1 = max(0, ys.min()-4), min(HEIGHT, ys.max()+5)
    xx, yy = x[y0:y1, x0:x1], y[y0:y1, x0:x1]
    height = np.zeros_like(xx)
    for ridge in layer.get('ridges', []):
        controls = np.asarray(ridge['points'])
        ts = np.linspace(0, 1, 49)[:, None]
        curve = (1-ts)**3*controls[0]+3*(1-ts)**2*ts*controls[1]+3*(1-ts)*ts**2*controls[2]+ts**3*controls[3]
        distance = np.full_like(xx, np.inf)
        for a, b in zip(curve[:-1], curve[1:]):
            ab = b-a
            t = np.clip(((xx-a[0])*ab[0]+(yy-a[1])*ab[1])/max(np.dot(ab, ab), 1e-6), 0, 1)
            distance = np.minimum(distance, (xx-a[0]-t*ab[0])**2+(yy-a[1]-t*ab[1])**2)
        height += ridge['height']*np.exp(-distance/(2*ridge['radius']**2))
    dy, dx = np.gradient(height, 1/SCALE)
    normals = np.broadcast_to(np.asarray(layer['normal'], dtype=np.float32), (*xx.shape, 3)).copy()
    normals[:, :, 0] -= dx
    normals[:, :, 1] -= dy
    if 'ellipsoid' in layer:
        e = layer['ellipsoid']
        normals[:, :, 0] += np.clip((xx-e['center'][0])/e['radius'][0], -1, 1)*e['strength'][0]
        normals[:, :, 1] += np.clip((yy-e['center'][1])/e['radius'][1], -1, 1)*e['strength'][1]
    if 'cylinder' in layer:
        c = layer['cylinder']
        nx = np.clip((xx-c['centerX'])/c['radius'], -1, 1)*c['strength']
        normals[:, :, 0] = nx
        normals[:, :, 2] = np.sqrt(1-nx*nx)
    normals = unit(normals)
    alpha = mask[y0:y1, x0:x1, None]
    result[y0:y1, x0:x1] = unit(result[y0:y1, x0:x1]*(1-alpha)+normals*alpha)
    print('Baked', layer['name'])

output = ROOT / 'public/assets/generated/normal-registered-v1.png'
Image.fromarray(np.uint8(np.clip(np.rint((result*.5+.5)*255), 0, 255))).save(output)
print(output)
