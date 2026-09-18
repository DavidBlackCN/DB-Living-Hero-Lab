"""Compare registered browser outputs; never edit source/runtime artwork."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

root = Path('docs/screenshots/code-only-salvage')
results = {}
for time in ['0600', '1200', '1730', '2300']:
    final = [Image.open(root / stage / 'layers' / f'{time}-final.png').convert('RGB')
             for stage in ['before', 'after']]
    pair = Image.new('RGB', (1920, 564), '#181818')
    for i, image in enumerate(final):
        pair.paste(image.resize((960, 540)), (i * 960, 24))
        ImageDraw.Draw(pair).text((i * 960 + 10, 6), time + [' BEFORE', ' AFTER'][i], fill='white')
    pair.save(root / f'{time}-compare.png')
    neutral = [np.asarray(Image.open(root / stage / 'layers' / f'{time}-neutral.png'))[:, :, 0].astype(float)
               for stage in ['before', 'after']]
    for i, light in enumerate(neutral):
        normalized = np.clip(light * 100 / light.mean(), 0, 255).astype('uint8')
        pair.paste(Image.fromarray(normalized).convert('RGB').resize((960, 540)), (i * 960, 24))
    pair.save(root / f'{time}-equal-mean.png')
    difference = np.abs(np.asarray(final[1]).astype(float) - np.asarray(final[0]).astype(float))
    results[time] = {'meanAbsoluteFinalDifference8bit': float(difference.mean()),
                     'maxFinalDifference8bit': float(difference.max())}
    for name, box in {'near-lamp': (1430, 365, 1790, 675),
                      'desk': (1000, 745, 1750, 965),
                      'character': (1030, 225, 1450, 715)}.items():
        w, h = box[2] - box[0], box[3] - box[1]
        strip = Image.new('RGB', (w * 2, h + 24), '#181818')
        for i, image in enumerate(final):
            strip.paste(image.crop(box), (i * w, 24))
            ImageDraw.Draw(strip).text((i * w + 8, 6), ['BEFORE', 'AFTER'][i], fill='white')
        strip.save(root / f'{time}-{name}.png')

lamp = [np.asarray(Image.open(root / stage / 'layers' / '2300-lamp.png'))[:, :, 0] / 255
        for stage in ['before', 'after']]
# Fixed lower reading/table crop, independent of field geometry.
results['nightLamp'] = [
    {'litAreaAbovePointOne': int((a[740:1020, 950:1920] > .1).sum()),
     'meanNearTools': float(a[475:523, 1528:1570].mean()),
     'meanFrontDesk': float(a[952:1000, 1360:1456].mean())} for a in lamp]
correction = [np.asarray(Image.open(root / 'after/salvage' / f'2300-correction-{v}.png')).astype(float)
              for v in ['0', '0.25']]
results['optionalCorrection'] = {'meanAbsoluteDifference8bit': float(np.abs(correction[1]-correction[0]).mean())}
(root / 'comparison-metrics.json').write_text(json.dumps(results, indent=2), encoding='utf8')
print(json.dumps(results, indent=2))
