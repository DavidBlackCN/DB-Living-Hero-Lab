"""Fixed-scale browser review; no per-panel exposure or contrast normalization."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

p=argparse.ArgumentParser()
p.add_argument('stage',nargs='?',default='after')
args=p.parse_args()
root=Path('docs/screenshots/lighting-convergence')/args.stage/'convergence'
times=['0600','0700','0800','1200','1730','2300']
for time in times:
    rgb=np.asarray(Image.open(root/f'{time}-final.png').convert('RGB')).astype(float)
    gray=np.uint8(np.rint(rgb@np.array([.2126,.7152,.0722])))
    Image.fromarray(gray).save(root/f'{time}-grayscale.png')

def sheet(name,columns,rows):
    out=Image.new('RGB',(400*len(columns),250*len(rows)),(24,24,24));d=ImageDraw.Draw(out)
    for row,view in enumerate(rows):
        for col,time in enumerate(columns):
            im=Image.open(root/f'{time}-{view}.png').convert('RGB');im.thumbnail((400,225))
            out.paste(im,(col*400,row*250+25));d.text((col*400+5,row*250+5),f'{time} / {view}',fill='white')
    out.save(root/name,quality=95)
sheet('morning.jpg',times[:4],['final','grayscale','neutral','projected','directional'])
sheet('four-times.jpg',['0600','1200','1730','2300'],['final','grayscale','neutral','projected','lamp'])

# All crops retain native source pixel scale (3.2 pixels per reference unit).
regions={
    'bangs':(652,45,839,196),'front-lock':(630,180,703,356),
    'tied-long-hair':(815,194,949,455),'left-sleeve':(474,278,605,540),
    'right-sleeve':(770,294,885,499),'torso':(606,278,759,453),
    'left-hand':(578,475,705,538),'right-hand':(865,463,945,524),
    'book':(625,485,944,583),'cup':(943,428,1073,549),
    'chair':(312,325,393,520),'laptop':(910,554,1200,675),
    'lamp-shade':(906,142,997,238),'window-left':(870,230,1018,337),
    'window-right':(1025,218,1200,402),
}
for name,box in regions.items():
    box=tuple(round(v*3.2) for v in box)
    # Source, effective normal and actual Final. No false-color relighting of source.
    images=[Image.open(root/f'native-{v}.png').crop(box).convert('RGB') for v in ['base','normal','final']]
    w,h=images[0].size;out=Image.new('RGB',(w*3,h+24),(24,24,24));d=ImageDraw.Draw(out)
    for i,(im,label) in enumerate(zip(images,['Source','Normal v2','23:00 Final'])):
        out.paste(im,(w*i,24));d.text((w*i+4,5),label,fill='white')
    out.save(root/f'detail-{name}.jpg',quality=97)

before=root.parents[1]/'before/convergence'
if args.stage!='before' and before.exists():
    out=Image.new('RGB',(1600,1000),(24,24,24));d=ImageDraw.Draw(out)
    for row,(folder,view) in enumerate([(before,'final'),(root,'final'),(before,'neutral'),(root,'neutral')]):
        for col,time in enumerate(times[:4]):
            im=Image.open(folder/f'{time}-{view}.png');im.thumbnail((400,225));out.paste(im,(col*400,row*250+25))
            d.text((col*400+4,row*250+5),f'{"Before" if folder==before else "After"} / {time} / {view}',fill='white')
    out.save(root/'morning-before-after.jpg',quality=95)
    protected={}
    for time in ['1200','1730','2300']:
        protected[time]={}
        for view in ['final','neutral','directional','projected','lamp','exterior']:
            a=np.asarray(Image.open(before/f'{time}-{view}.png'));b=np.asarray(Image.open(root/f'{time}-{view}.png'))
            protected[time][view]=int(np.any(a!=b,axis=-1).sum())
    (root/'protected-pixels.json').write_text(json.dumps(protected,indent=2)+'\n')
print(root/'morning.jpg')
