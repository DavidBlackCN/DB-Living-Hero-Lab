"""Fixed-scale lighting/shadow comparisons from actual browser captures."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw

root=Path('docs/screenshots/lighting-shadow-convergence');out=root/'review';out.mkdir(parents=True,exist_ok=True)
times=['0600','1200','1730','2300']
def frame(stage,time,view):
    return Image.open(root/stage/'shadow'/f'{time}-{view}.png').convert('RGB')
def sheet(name,rows,box=None,size=(640,360)):
    w,h=size; im=Image.new('RGB',(w*2,(h+25)*len(rows)),'#181818');d=ImageDraw.Draw(im)
    for row,(time,view) in enumerate(rows):
        for col,stage in enumerate(['before','after']):
            p=frame(stage,time,view)
            if box:p=p.crop(tuple(round(v*1.6) for v in box))
            p.thumbnail(size);im.paste(p,(col*w,row*(h+25)+25))
            d.text((col*w+4,row*(h+25)+5),f'{stage} / {time} / {view}',fill='white')
    im.save(out/name,quality=97)
sheet('four-times.jpg',[(t,'final') for t in times])
for t in ['0600','1730','2300']:
    sheet(f'{t}-before-after.jpg',[(t,v) for v in ['final','neutral','shadow','lamp']])
sheet('lamp-sill.jpg',[('2300',v) for v in ['final','lamp','shadow']],(855,235,1200,450),(552,344))
sheet('face-cloth.jpg',[(t,'final') for t in ['1200','1730','2300']],(575,135,810,440),(376,488))
sheet('reading-area.jpg',[(t,'final') for t in ['1730','2300']],(578,437,1080,594),(753,236))
for t in ['1730','2300']:
    off=root/'after/shadow'/f'{t}-shadow-off-final.png'
    if off.exists():
        panel=Image.new('RGB',(1280,385),'#181818');d=ImageDraw.Draw(panel)
        for i,(p,label) in enumerate([(Image.open(off),'shadow 0'),(frame('after',t,'final'),'shadow .65')]):
            p.thumbnail((640,360));panel.paste(p,(i*640,25));d.text((i*640+4,5),f'{t} / {label}',fill='white')
        panel.save(out/f'{t}-shadow-control.jpg',quality=97)
boxes={'face':(698,183,749,223),'chest':(650,320,715,405),'right-hair':(854,310,889,383),
       'right-sleeve':(808,373,838,450),'left-page':(680,530,730,548),'right-page':(855,515,882,533),
       'cup':(970,460,1025,498),'front-desk':(850,595,910,625),'right-desk':(1070,486,1120,520),
       'tools':(955,297,981,327),'under-lamp':(970,341,1000,349),'frame':(1035,320,1060,348)}
data={}
for t in times:
    data[t]={}
    for v in ['final','neutral','shadow','lamp','exterior','base']:
        a=np.asarray(frame('before',t,v),float);b=np.asarray(frame('after',t,v),float)
        regions={}
        for n,box in boxes.items():
            x0,y0,x1,y1=[round(x*1.6) for x in box];aa=a[y0:y1,x0:x1];bb=b[y0:y1,x0:x1]
            regions[n]={'before':aa.mean(axis=(0,1)).round(3).tolist(),'after':bb.mean(axis=(0,1)).round(3).tolist()}
        data[t][v]={'changedPixels':int(np.any(a!=b,axis=-1).sum()),'meanAbsDelta':float(np.abs(a-b).mean()),'regions':regions}
    rgb=np.asarray(frame('after',t,'final'),float)
    Image.fromarray(np.uint8(np.rint(rgb@np.array([.2126,.7152,.0722])))).save(out/f'{t}-grayscale.png')
(out/'comparison.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(out)
