"""Arrange actual browser captures without per-image exposure normalization."""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw

parser=argparse.ArgumentParser()
parser.add_argument('root', nargs='?', default='docs/screenshots/technical-art-alignment/final/alignment')
parser.add_argument('--prefix', default='v2')
args=parser.parse_args()
root=Path(args.root)
times=['dawn','noon','dusk','night']
views=['final','grayscale','neutral','normal','projected','lamp','exterior']
frames={}
for time in times:
    file=root/f'{args.prefix}-{time}-final.png'
    if not file.exists(): continue
    im=Image.open(file).convert('RGB')
    gray=np.asarray(im).astype(float)@np.array([.2126,.7152,.0722])
    Image.fromarray(np.uint8(np.rint(gray))).save(root/f'{args.prefix}-{time}-grayscale.png')
    frames[time]=gray
sheet=Image.new('RGB',(1600,len(views)*250),(24,24,24))
draw=ImageDraw.Draw(sheet)
for row,view in enumerate(views):
    for col,time in enumerate(times):
        file=root/f'{args.prefix}-{time}-{view}.png'
        if not file.exists():continue
        im=Image.open(file).convert('RGB');im.thumbnail((400,225))
        sheet.paste(im,(col*400,row*250+25))
        draw.text((col*400+6,row*250+7),f'{time} / {view}',fill='white')
sheet.save(root/'four-times.jpg',quality=94)
# Final grayscale structure after normalizing away mean energy. Includes baked
# art, so report relative differences instead of equating this with quality.
metrics=[]
for a,b in [('dawn','noon'),('noon','dusk'),('dawn','dusk')]:
    if a not in frames or b not in frames:continue
    # Registered foreground: hair, sleeves, hands, book/cup and desk.
    x=frames[a][100:1000,720:1700];y=frames[b][100:1000,720:1700]
    delta=x/x.mean()-y/y.mean()
    metrics.append(dict(pair=[a,b],normalizedMAE=float(np.abs(delta).mean()),
                        fractionOver5Percent=float((np.abs(delta)>.05).mean())))
(root/'grayscale-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
print(root/'four-times.jpg')

# Compact, reviewable comparisons; all panels retain capture exposure.
project=root.parent.parent
before=project/'before/audit'
if before.exists():
    compare=Image.new('RGB',(1600,500),(24,24,24));d=ImageDraw.Draw(compare)
    for row in range(2):
        for col,time in enumerate(times):
            file=(before/f'registered-{time}-final.png') if row==0 else root/f'v2-{time}-final.png'
            if not file.exists():continue
            im=Image.open(file);im.thumbnail((400,225));compare.paste(im,(col*400,row*250+25))
            d.text((col*400+5,row*250+6),f'{"Before v1" if row==0 else "After v2"} / {time}',fill='white')
    compare.save(root/'before-after.jpg',quality=95)
    night=Image.new('RGB',(1500,390),(24,24,24));d=ImageDraw.Draw(night)
    for col,(file,title) in enumerate([(before/'registered-night-final.png','Before / 23:00'),(root/'v2-night-final.png','After / 23:00'),(root/'v2-night-lamp.png','Isolated normal-aware lamp')]):
        if not file.exists():continue
        im=Image.open(file).crop((730,330,1750,1060));im.thumbnail((500,360));night.paste(im,(col*500,25));d.text((col*500+5,5),title,fill='white')
    night.save(root/'night-volume.jpg',quality=95)

if (root/'correction-night-on.png').exists():
    compare=Image.new('RGB',(1500,610),(24,24,24));d=ImageDraw.Draw(compare);metrics=[]
    for row,time in enumerate(['dusk','night']):
        off=Image.open(root/f'correction-{time}-off.png').convert('RGB')
        on=Image.open(root/f'correction-{time}-on.png').convert('RGB')
        a,b=np.asarray(off).astype(float),np.asarray(on).astype(float)
        delta=np.abs(a-b);metrics.append(dict(time=time,meanAbsoluteRGB=float(delta.mean()),maxAbsoluteRGB=float(delta.max())))
        diff=Image.fromarray(np.uint8(np.clip(delta*8,0,255)))
        for col,(im,label) in enumerate([(off,'Original base'),(on,'Correction on'),(diff,'Absolute difference x8')]):
            im.thumbnail((500,281));compare.paste(im,(col*500,row*305+24));d.text((col*500+5,row*305+5),time+' / '+label,fill='white')
    compare.save(root/'correction-comparison.jpg',quality=95)
    (root/'correction-image-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
