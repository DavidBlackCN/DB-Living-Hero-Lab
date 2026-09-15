"""Build contact sheets from actual Playwright captures; no simulated renders."""
from pathlib import Path
from PIL import Image, ImageDraw
import json
import numpy as np

root = Path(__file__).resolve().parents[1] / 'docs/screenshots/window-light-review'
root.mkdir(parents=True, exist_ok=True)
names = ['morning', 'noon', 'dusk', 'night']
labels = ['08:00', '12:00', '17:30', '23:00']
for phase in ['before', 'stage1', 'stage2']:
    folder = root / phase / 'acceptance'
    required = [folder / f'{name}-{view}.png' for name in names for view in ['final', 'neutral', 'projected']]
    if not all(path.is_file() for path in required):
        print(f'Skipping {phase}: local captures are incomplete or absent.')
        continue
    board = Image.new('RGB', (1920, 1200), (25, 29, 34))
    draw = ImageDraw.Draw(board)
    for row, view in enumerate(['final', 'grayscale', 'neutral', 'projected']):
        for col, (name, label) in enumerate(zip(names, labels)):
            source_view = 'final' if view == 'grayscale' else view
            image = Image.open(folder / f'{name}-{source_view}.png')
            if view == 'grayscale':
                # Same Rec.709 luma weights across images; no auto levels.
                rgb = np.asarray(image.convert('RGB'), dtype=np.float32)
                image = Image.fromarray(np.uint8(rgb @ [.2126, .7152, .0722])).convert('RGB')
                image.save(folder / f'{name}-grayscale.png')
            board.paste(image.resize((480, 270)), (col*480, row*300+25))
            draw.text((col*480+10, row*300+5), f'{label} / {view}', fill='white')
    board.save(folder / 'comparison.png')

window_captures = [root / phase / 'acceptance' / f'night-window-{view}.png'
                   for phase in ['before', 'stage2'] for view in ['final', 'overlay']]
if all(path.is_file() for path in window_captures):
    board = Image.new('RGB', (1520, 640), (25, 29, 34))
    draw = ImageDraw.Draw(board)
    for col, phase in enumerate(['before', 'stage2']):
        for row, view in enumerate(['final', 'overlay']):
            image = Image.open(root / phase / 'acceptance' / f'night-window-{view}.png')
            board.paste(image, (col*760, row*320+25))
            draw.text((col*760+10, row*320+5), f'{phase} / 23:00 / {view}', fill='white')
    board.save(root / 'window-before-after.png')
else:
    print('Skipping window before/after: historical captures are local-only.')

# Record the exact source contract next to the screenshots.
(root / 'capture-settings.json').write_text(json.dumps({
    'viewport': [1920, 1080], 'deviceScaleFactor': 1,
    'timesMinutes': [480, 720, 1050, 1380],
    'animation': False, 'steam': False, 'reducedMotion': True,
    'exposureEV': 0, 'bloom': .22, 'projectedIntensity': .42,
    'neutralDisplayScale': {'before': 1, 'stage1': 1, 'stage2': .6},
    'note': 'Compare Neutral within a stage; its fixed display scale changed in stage2. Final grayscale uses identical luma conversion throughout.',
}, indent=2)+'\n', encoding='utf-8')
