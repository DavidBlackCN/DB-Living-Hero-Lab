"""Bake source-registered, authored surface fields; never derive height from color.

This is a deterministic geometry candidate, not recovered ground-truth geometry.
Differentiate each unmasked surface first, then composite normalized vectors.
Differentiating a masked height would emboss every silhouette with a false rim.
"""
import json
import re
import argparse
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
regions = json.loads((ROOT / 'docs/scene-regions.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version', choices=['v1', 'v2'], default='v2')
parser.add_argument('--correction-only', action='store_true', help='Use the existing v2 normal to bake an optional bounded gain experiment')
args = parser.parse_args()
source = 'normal-surfaces-v1.json' if args.version == 'v1' else 'normal-surfaces.json'
surfaces = json.loads((ROOT / 'docs' / source).read_text(encoding='utf-8'))
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


def ribbon_field(xx, yy, ribbon):
    """A tapered bent cylinder, not a luminance bump or an additive height ridge.

    Closest centerline tangent defines the cross-section. Blend unit directions
    with compact, soft support so adjacent locks do not accumulate mound height.
    End taper removes the spherical caps of v1's distance-to-curve Gaussian.
    """
    controls = np.asarray(ribbon['points'], dtype=np.float32)
    ts = np.linspace(0, 1, 81)[:, None]
    curve = (1-ts)**3*controls[0]+3*(1-ts)**2*ts*controls[1]+3*(1-ts)*ts**2*controls[2]+ts**3*controls[3]
    distance = np.full_like(xx, np.inf)
    signed, tangent_x, tangent_y, progress = [np.zeros_like(xx) for _ in range(4)]
    for index, (a, b) in enumerate(zip(curve[:-1], curve[1:])):
        ab = b-a
        length = max(np.linalg.norm(ab), 1e-6)
        t = np.clip(((xx-a[0])*ab[0]+(yy-a[1])*ab[1])/(length*length), 0, 1)
        px, py = xx-a[0]-t*ab[0], yy-a[1]-t*ab[1]
        d = px*px+py*py
        closer = d < distance
        distance = np.minimum(distance, d)
        signed = np.where(closer, (px*ab[1]-py*ab[0])/length, signed)
        tangent_x = np.where(closer, ab[0]/length, tangent_x)
        tangent_y = np.where(closer, ab[1]/length, tangent_y)
        progress = np.where(closer, (index+t)/80, progress)
    q = signed/ribbon['width']
    smooth = lambda v: np.clip(v, 0, 1)**2*(3-2*np.clip(v, 0, 1))
    support = 1-smooth((np.sqrt(distance)/ribbon['width']-.65)/.55)
    support *= smooth(progress/.12)*smooth((1-progress)/.14)
    cross = np.clip(q, -.95, .95)*ribbon['strength']
    target = np.stack([cross*tangent_y, -cross*tangent_x, np.sqrt(1-cross*cross)], axis=-1)
    return target, support[:, :, None]


if args.correction_only:
    # Conservative intrinsic experiment: invert only a weak assumed broad key
    # light, not source color/texture. This cannot identify real reflectance or
    # erase painted cast shadows. No UV displacement, blur or repaint of Hero.
    n = np.asarray(Image.open(ROOT / 'public/assets/generated/normal-registered-v2.png'), dtype=np.float32)/127.5-1
    n = unit(n)
    baked_direction = unit(np.array([.65, -.45, .60], dtype=np.float32))
    response = .18+.82*np.maximum(n @ baked_direction, 0)
    reference = .18+.82*baked_direction[2]
    gain = (.50+.50*reference)/(.50+.50*response)
    ev = np.clip(np.log2(gain), -.25, .15)
    support = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for name, strength in [('hair', .85), ('cloth', .65), ('bodice', .55),
                           ('book', .80), ('cup', .80), ('desk', .40)]:
        support = np.maximum(support, path_mask(regions[name])*strength)
    # Explicitly preserve face/eyes, hands, hat and exterior. Avoid guessing
    # skin reflectance or changing identity to obtain a flatter source.
    for name in ['face','handLeft','handRight','hat','windowGlassLeft','windowGlassRight','laptop']:
        support *= 1-path_mask(regions[name])
    ev *= support
    encoded = np.uint8(np.clip(np.rint(128+ev*254), 0, 255))
    output = ROOT / 'public/assets/generated/intrinsic-correction-v1.png'
    Image.fromarray(encoded).save(output)
    print(output, 'EV range:', float(ev.min()), float(ev.max()))
    raise SystemExit(0)

y, x = np.mgrid[:HEIGHT, :WIDTH].astype(np.float32)/SCALE
result = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
result[:, :, 2] = 1
for layer in surfaces['layers']:
    mask = path_mask(layer.get('path') or regions[layer['region']])
    for exclusion in layer.get('exclude', []):
        mask *= 1-path_mask(regions[exclusion])
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
    for ribbon in layer.get('ribbons', []):
        # The Bezier stays inside its control hull; outside this padded box the
        # compact-support ribbon is exactly zero. Avoid evaluating a whole 4K
        # material layer for every small finger/fold.
        control = np.asarray(ribbon['points'])
        pad = ribbon['width']*1.21
        rx0, ry0 = np.maximum(np.floor((control.min(axis=0)-pad)*SCALE).astype(int), [x0,y0])
        rx1, ry1 = np.minimum(np.ceil((control.max(axis=0)+pad)*SCALE).astype(int)+1, [x1,y1])
        if rx1 <= rx0 or ry1 <= ry0:
            continue
        area = np.s_[ry0-y0:ry1-y0, rx0-x0:rx1-x0]
        target, weight = ribbon_field(xx[area], yy[area], ribbon)
        normals[area] = unit(normals[area]*(1-weight)+target*weight)
    alpha = mask[y0:y1, x0:x1, None]
    result[y0:y1, x0:x1] = unit(result[y0:y1, x0:x1]*(1-alpha)+normals*alpha)
    print('Baked', layer['name'])

output = ROOT / f'public/assets/generated/normal-registered-{args.version}.png'
Image.fromarray(np.uint8(np.clip(np.rint((result*.5+.5)*255), 0, 255))).save(output)
print(output)
