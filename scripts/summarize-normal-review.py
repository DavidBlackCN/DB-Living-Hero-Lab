"""Local contact sheets and image differences from actual normal-map captures."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json

root=Path(__file__).resolve().parents[1]
folder=root/'docs/screenshots/normal-map-review/final/normals'
board=Image.new('RGB',(1920,1200),(25,29,34))
draw=ImageDraw.Draw(board)
for row,(variant,view) in enumerate([(v,w) for w in ['final','neutral'] for v in ['low-frequency','registered']]):
    for col,time in enumerate(['morning','noon','dusk','night']):
        im=Image.open(folder/f'{variant}-{time}-{view}.png')
        board.paste(im.resize((480,270)),(col*480,row*300+25))
        draw.text((col*480+10,row*300+5),f'{variant} / {time} / {view}',fill='white')
board.save(folder/'comparison.png')

board=Image.new('RGB',(1280,876),(25,29,34))
draw=ImageDraw.Draw(board)
images=[('source',root/'public/assets/hero-4k-digital-art.png',3.2),
        ('candidate',root/'public/assets/generated/normal-registered-v1.png',3.2),
        ('source guides',folder/'source-guides.png',1.6)]
boxes=[('hair',(620,60,860,260)),('sleeve',(460,330,700,530)),('book',(640,450,880,650)),('cup',(900,400,1140,600))]
for row,(label,path,scale) in enumerate(images):
    image=Image.open(path)
    for col,(name,box) in enumerate(boxes):
        crop=image.crop(tuple(round(v*scale) for v in box)).resize((320,267))
        board.paste(crop,(col*320,row*292+25))
        draw.text((col*320+10,row*292+5),f'{name} / {label}',fill='white')
board.save(folder/'surface-details.png')

metrics={}
for time in ['morning','noon','dusk','night']:
    a=np.asarray(Image.open(folder/f'low-frequency-{time}-final.png').convert('RGB'),dtype=float)
    b=np.asarray(Image.open(folder/f'registered-{time}-final.png').convert('RGB'),dtype=float)
    delta=np.abs(a-b)
    metrics[time]={'meanAbsoluteChannelDifference255':float(delta.mean()),'maxDifference255':float(delta.max())}
(folder/'final-differences.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metrics,indent=2))

review=folder.parents[1]
if (review/'mask-before/night-window-final.png').exists():
    board=Image.new('RGB',(960,330),(25,29,34));draw=ImageDraw.Draw(board)
    for col,phase in enumerate(['mask-before','final/acceptance']):
        image=Image.open(review/phase/'night-window-final.png').crop((190,35,320,120)).resize((480,300))
        board.paste(image,(col*480,25));draw.text((col*480+10,5),'before' if col==0 else 'after',fill='white')
    board.save(review/'pen-mask-comparison.png')
