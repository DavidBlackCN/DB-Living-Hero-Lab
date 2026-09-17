"""Review fixed browser captures, including mean-normalized lighting structure."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

root = Path('docs/screenshots/light-layer-review')
# 1920x1080 screenshot coordinates, independently chosen on the source artwork.
regions = {'hair': (785,170,1370,720), 'cloth': (785,480,1400,770),
           'cup': (1522,716,1643,818), 'wall': (300,240,780,500),
           'chair': (500,535,615,635), 'foreground': (80,800,275,970)}
metrics = {}
for time in ['0600','1200','1730','2300']:
    frames = [Image.open(root / stage / 'shadow' / f'{time}-final.png').convert('RGB')
              for stage in ['before','after']]
    pair = Image.new('RGB',(1920,564),'#181818')
    draw = ImageDraw.Draw(pair)
    for i, frame in enumerate(frames):
        pair.paste(frame.resize((960,540)),(i*960,24))
        draw.text((i*960+12,6),f'{time} '+['BEFORE','AFTER'][i],fill='white')
    pair.save(root / f'{time}-compare.png')
    light = [np.asarray(Image.open(root / stage / 'shadow' / f'{time}-neutral.png')).astype(float)[:,:,0]
             for stage in ['before','after']]
    values = {}
    for name,(x0,y0,x1,y1) in regions.items():
        values[name] = []
        for data in light:
            patch=data[y0:y1,x0:x1]
            values[name].append({'mean':float(patch.mean()),
                'relativeContrast':float(patch.std()/max(patch.mean(),.001))})
    # Normalize mean brightness to 100, preserving only the spatial pattern.
    grayPair = Image.new('RGB',(1920,564),'#181818')
    for i,data in enumerate(light):
        normalized=np.uint8(np.clip(data*100/max(data.mean(),.001),0,255))
        grayPair.paste(Image.fromarray(normalized).convert('RGB').resize((960,540)),(i*960,24))
    ImageDraw.Draw(grayPair).text((12,6),f'{time} BEFORE / AFTER - equal mean lighting',fill='white')
    grayPair.save(root / f'{time}-equal-mean-lighting.png')
    for name,box in {'contacts':(900,740,1680,950),'face-straps':(1030,240,1280,700),
                     'sill':(1390,415,1870,675)}.items():
        w,h=box[2]-box[0],box[3]-box[1]
        crop=Image.new('RGB',(2*w,h+24),'#181818')
        for i,frame in enumerate(frames):crop.paste(frame.crop(box),(i*w,24))
        ImageDraw.Draw(crop).text((10,6),'BEFORE / AFTER',fill='white')
        crop.save(root / f'{time}-{name}.png')
    for view in ['base','exterior']:
        arrays=[np.asarray(Image.open(root/stage/'shadow'/f'{time}-{view}.png')).astype(int) for stage in ['before','after']]
        values[f'{view}MaxDifference']=int(np.abs(arrays[1]-arrays[0]).max())
    metrics[time]=values
(root/'structure-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))
