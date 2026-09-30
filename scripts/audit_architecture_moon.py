"""Actual-render building Moon handoff against the frozen 55d995c shader."""

import json
from pathlib import Path
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

from validate_atmosphere import EDGE, capture, contact, setup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/validation/night-architecture-moon'
TIMES = (('20h',1200),('22h',1320),('00h',0),('02h',120),('04h30',270))
COLUMN = (915,30,1060,320)


def set_time(page, minutes):
    page.get_by_role('slider',name='24H Preview').evaluate(
        "(node,value)=>{node.value=String(value);node.dispatchEvent(new Event('input',{bubbles:true}));}",minutes)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    original = subprocess.check_output(['git','show','55d995c:src/shaders/hero.frag.glsl']).decode('utf-8')
    current = (ROOT/'src/shaders/hero.frag.glsl').read_text(encoding='utf-8')
    frames,stats = {},{}
    skin = np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]
    face_core = skin >= 254
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=EDGE,headless=True,
            args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
        for mode in ('before','after'):
            page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            if mode=='before':
                page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(
                    body='export default '+json.dumps(original)+';',content_type='application/javascript'))
            setup(page)
            for name,minutes in (*TIMES,('dawn',390),('noon',720),('dusk',1050),('24h',1440)):
                set_time(page,minutes)
                readout=page.locator('small').filter(has_text='Moon Direction').inner_text()
                frame=capture(page,OUT/f'{name}-{mode}.png')
                frames[name,mode]=frame
                if mode=='after':
                    stats[name]={'minutes':minutes,'moon':readout}
            assert not errors,errors
            page.close()
        # Hold 22:00, exposure, Sky, materials and the character key fixed.
        # Only reverse architecture's lateral Moon vector for source isolation.
        page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
        reversed_arch=current.replace('dot(architectureNormal, moonDirection)',
            'dot(architectureNormal, vec3(-moonDirection.x, moonDirection.yz))')
        assert reversed_arch != current
        page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(
            body='export default '+json.dumps(reversed_arch)+';',content_type='application/javascript'))
        setup(page);set_time(page,1320)
        reversed_frame=capture(page)
        contact([('22:00 actual Moon',frames['22h','after'].crop(COLUMN)),
                 ('22:00 reverse architecture Moon X / audit only',reversed_frame.crop(COLUMN))],
                OUT/'direction-isolation-ab.jpg',width=560)
        stats['directionIsolationMeanRgbDelta']=round(float(np.abs(
            np.asarray(reversed_frame,dtype=np.int16)[130:280,950:1045]-
            np.asarray(frames['22h','after'],dtype=np.int16)[130:280,950:1045]).mean()),4)
        assert stats['directionIsolationMeanRgbDelta'] > 3, 'Building lighting does not respond to Moon direction'
        page.close()
        browser.close()
    pairs,crops,before_crops,full=[] ,[],[],[]
    for name,_ in TIMES:
        before,after=frames[name,'before'],frames[name,'after']
        label=stats[name]['moon']
        pairs.extend([(name+' OLD',before.crop(COLUMN)),(name+' '+label,after.crop(COLUMN))])
        crops.append((name+' '+label,after.crop(COLUMN)))
        before_crops.append((name+' OLD',before.crop(COLUMN)))
        full.append((name+' '+label,after))
        delta=np.abs(np.asarray(after,dtype=np.int16)-np.asarray(before,dtype=np.int16))
        stats[name]['roseColumnMeanRgbDelta']=round(float(delta[60:300,1000:1050].mean()),4)
        # Safely inside the character; material feather transitions are audited separately.
        stats[name]['faceMaxRgbDelta']=int(delta[face_core].max())
        assert stats[name]['faceMaxRgbDelta'] <= 1, 'Architecture change relit the face'
        stats[name]['columnMeanRgb']=np.asarray(after)[130:280,1025:1045].mean((0,1)).round(3).tolist()
        front=np.asarray(after)[130:280,950:980].mean((0,1))
        side=np.asarray(after)[130:280,1025:1045].mean((0,1))
        stats[name]['frontToSideRgbRatio']=round(float(front.mean()/side.mean()),4)
        angle,elevation=map(int,re.search(r'Direction (\d+).*Elevation (\d+)',label).groups())
        entry='RIGHT' if angle<65 else 'higher / near center' if angle<=105 else 'LEFT'
        labelled=Image.new('RGB',(after.width,after.height+36),(22,24,29))
        labelled.paste(after,(0,36))
        pen=ImageDraw.Draw(labelled)
        pen.text((16,12),f'{name} | Moon from image {entry} | Azimuth {angle} deg | Elevation {elevation} deg',fill='white')
        if entry in ('RIGHT','LEFT'):
            start,end=(1610,1530) if entry=='RIGHT' else (1530,1610)
            pen.line((start,18,end,18),fill=(150,185,240),width=2)
            sign=1 if end>start else -1
            pen.polygon([(end,18),(end-sign*9,12),(end-sign*9,24)],fill=(150,185,240))
        labelled.save(OUT/f'{name}-labelled.png')
    contact(pairs,OUT/'column-before-after.jpg',width=560)
    contact(crops,OUT/'column-night-contact.jpg',width=560)
    contact(before_crops,OUT/'column-old-contact.jpg',width=560)
    contact(full,OUT/'night-moon-contact.jpg',width=836)
    contact([('22:00 BEFORE',frames['22h','before']),
             ('22:00 AFTER',frames['22h','after'])],OUT/'22h-full-ab.jpg',width=836)
    # A single row makes the side reversal easier to read at normal display size.
    strip=Image.new('RGB',(1200,704),(22,24,29))
    pen=ImageDraw.Draw(strip)
    for index,(name,label) in enumerate((('20h','20:00 | Moon RIGHT | 35 deg / 12 deg'),
                                        ('00h','00:00 | Moon HIGH | 81 deg / 54 deg'),
                                        ('04h30','04:30 | Moon LEFT | 144 deg / 19 deg'))):
        pen.text((index*400+8,10),label,fill='white')
        strip.paste(frames[name,'after'].crop((915,80,1060,320)).resize((400,662)),(index*400,36))
    strip.save(OUT/'night-plane-directions.jpg',quality=92)
    for name in ('dawn','noon','dusk'):
        delta=np.abs(np.asarray(frames[name,'after'],dtype=np.int16)-np.asarray(frames[name,'before'],dtype=np.int16))
        stats[name]['maxRgbDelta']=int(delta.max())
    stats['midnightMaxRgbDelta']=int(np.abs(np.asarray(frames['00h','after'],dtype=np.int16)-np.asarray(frames['24h','after'],dtype=np.int16)).max())
    assert stats['midnightMaxRgbDelta']==0
    assert all(stats[name]['maxRgbDelta']==0 for name in ('dawn','noon','dusk'))
    assert stats['20h']['frontToSideRgbRatio'] < 1.0, 'Early-night side plane is not brighter'
    assert stats['02h']['frontToSideRgbRatio'] > 1.0, 'Lit tower plane did not shift across the night'
    (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':
    main()
