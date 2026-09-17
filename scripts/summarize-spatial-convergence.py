"""Compare fixed-exposure browser captures; never modifies runtime artwork."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

root = Path('docs/screenshots/spatial-convergence-3')
metrics = {}
for time in ['0600', '1200', '1730', '2300']:
    before = Image.open(root / 'before/shadow' / f'{time}-final.png').convert('RGB')
    after = Image.open(root / 'after/shadow' / f'{time}-final.png').convert('RGB')
    pair = Image.new('RGB', (1920, 564), '#16191d')
    pair.paste(before.resize((960, 540)), (0, 24))
    pair.paste(after.resize((960, 540)), (960, 24))
    draw = ImageDraw.Draw(pair)
    draw.text((12, 6), f'{time} BEFORE', fill='white')
    draw.text((972, 6), f'{time} AFTER', fill='white')
    pair.save(root / f'{time}-comparison.png')
    delta = np.asarray(after).astype(float) - np.asarray(before).astype(float)
    metrics[time] = {'meanAbsoluteDisplayChange': float(np.abs(delta).mean())}
    # Paired source-aligned crops preserve native screenshot pixels.
    for name, box in {'contacts': (900, 740, 1680, 950),
                      'lamp-sill': (1320, 320, 1800, 700),
                      'face-straps': (1030, 240, 1280, 700)}.items():
        x0, y0, x1, y1 = box
        crop = Image.new('RGB', ((x1-x0)*2, y1-y0+24), '#16191d')
        crop.paste(before.crop(box), (0, 24))
        crop.paste(after.crop(box), (x1-x0, 24))
        ImageDraw.Draw(crop).text((8, 5), 'BEFORE                                       AFTER', fill='white')
        crop.save(root / f'{time}-{name}.png')
    for view in ['base', 'exterior']:
        a = np.asarray(Image.open(root / 'before/shadow' / f'{time}-{view}.png')).astype(float)
        b = np.asarray(Image.open(root / 'after/shadow' / f'{time}-{view}.png')).astype(float)
        metrics[time][f'{view}MaxDifference'] = float(np.abs(a-b).max())
(root / 'comparison-metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
print(json.dumps(metrics, indent=2))
