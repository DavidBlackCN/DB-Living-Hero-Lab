"""Lighting Convergence 2: fixed-exposure browser comparisons, no normalization."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

root = Path('docs/screenshots/lighting-convergence-2')
out = root / 'review'
out.mkdir(parents=True, exist_ok=True)
times = ['0600', '1200', '1730', '2300']

def frame(stage, time, view):
    return Image.open(root / stage / 'convergence' / f'{time}-{view}.png').convert('RGB')

def panel(name, columns, rows, crop=None, size=(640, 360)):
    w, h = size
    sheet = Image.new('RGB', (w * len(columns), (h + 25) * len(rows)), '#181818')
    draw = ImageDraw.Draw(sheet)
    for y, (time, view) in enumerate(rows):
        for x, stage in enumerate(columns):
            im = frame(stage, time, view)
            if crop:
                im = im.crop(tuple(round(v * 1.6) for v in crop))
            im.thumbnail(size)
            sheet.paste(im, (x * w, y * (h + 25) + 25))
            draw.text((x * w + 5, y * (h + 25) + 5), f'{stage} / {time} / {view}', fill='white')
    sheet.save(out / name, quality=96)

panel('four-times-before-after.jpg', ['before', 'after'], [(t, 'final') for t in times])
panel('room-before-after.jpg', ['before', 'after'],
      [(t, v) for t in times[:3] for v in ['final', 'projected']], (0, 70, 560, 675), (560, 605))
for t in times[:3]:
    panel(f'room-{t}.jpg', ['before', 'after'], [(t, v) for v in ['final', 'projected']],
          (0, 70, 560, 675), (560, 605))
panel('night-before-after.jpg', ['before', 'after'],
      [('2300', v) for v in ['final', 'neutral', 'lamp']], (565, 135, 1090, 600), (630, 558))
panel('morning-review.jpg', ['before', 'after'], [('0600', v) for v in ['final', 'neutral', 'projected']])
for t in times:
    a = np.asarray(frame('after', t, 'final'), dtype=float)
    Image.fromarray(np.uint8(np.rint(a @ np.array([.2126, .7152, .0722])))).save(out / f'{t}-grayscale.png')

# Native pixel crops; compare before/after without rescaling fine edges.
details = {'hair-sleeve': (810,280,922,472), 'hands-book': (610,480,940,583),
           'cup-coaster-pen': (940,428,1100,583), 'window-left': (870,230,1018,337),
           'window-right': (1025,218,1200,402)}
for name, box in details.items():
    box = tuple(round(v*3.2) for v in box)
    images = [Image.open(root/s/'convergence/native-final.png').crop(box).convert('RGB') for s in ['before','after']]
    w,h = images[0].size
    sheet = Image.new('RGB',(w*2,h+25),'#181818'); draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(images):
        sheet.paste(im,(i*w,25)); draw.text((i*w+5,5),['before / 23:00','after / 23:00'][i],fill='white')
    sheet.save(out/f'detail-{name}.jpg',quality=97)

# Fixed, artwork-located rectangles; statistics use unchanged display encoding.
boxes = {
    'wall': (180, 180, 330, 380), 'shelf': (50, 200, 112, 370),
    'chair-space': (278, 350, 367, 472), 'foreground': (50, 500, 175, 620),
    'face': (704, 182, 751, 224), 'chest': (650, 320, 715, 405),
    'right-hair': (854, 310, 889, 383), 'right-sleeve': (808, 373, 838, 450),
    'left-hand': (611, 495, 674, 517), 'right-hand': (892, 480, 928, 505),
    'book': (736, 518, 809, 540), 'cup': (970, 460, 1025, 498),
    'coaster': (960, 530, 1028, 540), 'pen-desk': (984, 557, 1094, 578),
}
metrics = {}
for t in times:
    metrics[t] = {}
    for view in ['final', 'neutral', 'projected', 'lamp', 'exterior']:
        a = np.asarray(frame('before', t, view), dtype=float)
        b = np.asarray(frame('after', t, view), dtype=float)
        regions = {}
        for name, box in boxes.items():
            x0, y0, x1, y1 = [round(v * 1.6) for v in box]
            av, bv = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
            regions[name] = {'beforeRGB': av.mean(axis=(0, 1)).round(3).tolist(),
                             'afterRGB': bv.mean(axis=(0, 1)).round(3).tolist(),
                             'meanAbsDelta': float(np.abs(av - bv).mean().round(3))}
        metrics[t][view] = {'changedPixels': int(np.any(a != b, axis=-1).sum()), 'regions': regions}
(out / 'comparison.json').write_text(json.dumps(metrics, indent=2) + '\n', encoding='utf-8')
print(out)
