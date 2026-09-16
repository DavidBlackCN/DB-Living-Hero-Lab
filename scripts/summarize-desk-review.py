"""Arrange actual captures at fixed exposure; never synthesize lighting."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'docs/screenshots/desk-light-review'


def desk_board(view, hand=False):
    tile_w, tile_h = (640, 320) if hand else (1024, 440)
    sheet = Image.new('RGB', (tile_w*2, (tile_h+28)*2), '#191d22')
    draw = ImageDraw.Draw(sheet)
    for row, phase in enumerate(['before', 'after']):
        for col, time in enumerate(['noon', 'midnight']):
            image = Image.open(ROOT / phase / 'desk' / f'low-frequency-{time}-{view}.png')
            if hand:
                # Same source-registered crop in both versions; no alignment transform.
                image = image.crop((0, 100, 320, 260)).resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            sheet.paste(image, (col*tile_w, row*(tile_h+28)+28))
            draw.text((col*tile_w+10, row*(tile_h+28)+7), f'{phase} / {time} / {view}', fill='white')
    sheet.save(ROOT / f'{"hand" if hand else "desk"}-{view}-comparison.png')


for view in ['final', 'neutral', 'shadow']:
    desk_board(view)
desk_board('final', hand=True)

views = ['final', 'grayscale', 'neutral', 'projected', 'shadow', 'overlay', 'scene', 'exterior']
sheet = Image.new('RGB', (1920, 300*len(views)), '#191d22')
draw = ImageDraw.Draw(sheet)
for row, view in enumerate(views):
    for col, (name, time) in enumerate(zip(['morning','noon','dusk','night'], ['08:00','12:00','17:30','23:00'])):
        path = ROOT / 'after/acceptance' / f'{name}-{"final" if view=="grayscale" else view}.png'
        image = Image.open(path).convert('RGB')
        if view == 'grayscale':
            image = Image.fromarray(np.uint8(np.asarray(image,dtype=float) @ [.2126,.7152,.0722])).convert('RGB')
            image.save(path.with_name(f'{name}-grayscale.png'))
        sheet.paste(image.resize((480,270),Image.Resampling.LANCZOS),(col*480,row*300+25))
        draw.text((col*480+10,row*300+6), f'{time} / {view}', fill='white')
sheet.save(ROOT / 'four-times.png')
print(f'Local review sheets: {ROOT}')
