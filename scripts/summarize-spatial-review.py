"""Arrange actual browser captures; no simulated lighting or per-image levels."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

root = Path(__file__).resolve().parents[1] / 'docs/screenshots/spatial-light-review'
names = ['morning', 'noon', 'dusk', 'night']
times = ['08:00', '12:00', '17:30', '23:00']


def capture(phase, name, view):
    folder = root / phase / 'acceptance'
    image = Image.open(folder / f'{name}-{"final" if view == "grayscale" else view}.png').convert('RGB')
    if view == 'grayscale':
        image = Image.fromarray(np.uint8(np.asarray(image, dtype=np.float32) @ [.2126, .7152, .0722])).convert('RGB')
        image.save(folder / f'{name}-grayscale.png')
    return image


def board(rows, output):
    sheet = Image.new('RGB', (1920, 300 * len(rows)), (25, 29, 34))
    draw = ImageDraw.Draw(sheet)
    for row, (phase, view) in enumerate(rows):
        for col, (name, time) in enumerate(zip(names, times)):
            image = capture(phase, name, view)
            sheet.paste(image.resize((480, 270), Image.Resampling.LANCZOS), (col*480, row*300+25))
            draw.text((col*480+10, row*300+5), f'{phase} / {time} / {view}', fill='white')
    sheet.save(root / output)


board([('final', v) for v in ['final', 'grayscale', 'neutral', 'projected', 'shadow']], 'comparison.png')
board([('final', v) for v in ['scene', 'overlay', 'exterior']], 'regions.png')
if (root / 'before/acceptance/morning-final.png').exists():
    board([(p, v) for v in ['final', 'grayscale'] for p in ['before', 'final']], 'before-after.png')

sheet = Image.new('RGB', (1056, 675), (25, 29, 34))
draw = ImageDraw.Draw(sheet)
for col, view in enumerate(['base', 'overlay', 'exterior']):
    image = Image.open(root / f'final/acceptance/night-right-pane-{view}.png')
    sheet.paste(image, (col*352, 25))
    draw.text((col*352+10, 5), f'23:00 / {view}', fill='white')
sheet.save(root / 'window-registration.png')
print(f'Created local review sheets in {root}')
