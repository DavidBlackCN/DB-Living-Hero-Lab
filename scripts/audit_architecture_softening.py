"""Actual-render 03:54 tower/foreground correction against a9abc73."""
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE, setup, capture, contact

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/validation/night-architecture-softening'
TIMES=(('20h',1200),('22h',1320),('00h',0),('02h',120),('03h54',234),('04h30',270),('dawn',390),('noon',720),('dusk',1050),('24h',1440))
BOX=(925,100,1080,370)

def set_time(page,minutes):
    page.get_by_role('slider',name='24H Preview').evaluate("(n,v)=>{n.value=String(v);n.dispatchEvent(new Event('input',{bubbles:true}));}",minutes)

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    frames={};stats={}
    original=subprocess.check_output(['git','show','a9abc73:src/shaders/hero.frag.glsl']).decode('utf-8')
    reference=subprocess.check_output(['git','show','55d995c:src/shaders/hero.frag.glsl']).decode('utf-8')
    current=(ROOT/'src/shaders/hero.frag.glsl').read_text(encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
        for mode,shader in [('before',original),('after',current),('character-reference',reference)]:
            page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
            errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
            page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
            setup(page)
            for name,minutes in TIMES if mode!='character-reference' else [('03h54',234)]:
                set_time(page,minutes)
                frames[name,mode]=capture(page,OUT/f'{name}-{mode}.png')
                if mode=='after':stats[name]={'moon':page.locator('small').filter(has_text='Moon Direction').inner_text()}
            assert not errors,errors
            page.close()
        # Material ownership preview only, not a production debug mode.
        debug_current=current.replace('  outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);',
            '  outColor = u_view == 2 ? vec4(vec3(architectureField.a),1.0) : vec4(showMotionRegions(displayColor, regions, hairRegion),base.a);')
        debug_original=original.replace('  outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);',
            '  outColor = u_view == 2 ? vec4(vec3(architectureField.a),1.0) : vec4(showMotionRegions(displayColor, regions, hairRegion),base.a);')
        for mode,shader in [('before',debug_original),('after',debug_current)]:
            page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
            page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
            setup(page);page.get_by_label('Post Processing on/off').uncheck();set_time(page,234)
            frames['coverage',mode]=capture(page,OUT/f'receiver-{mode}.png')
            page.close()
        browser.close()
    contact([('03:54 BEFORE',frames['03h54','before'].crop(BOX)),('03:54 AFTER',frames['03h54','after'].crop(BOX))],OUT/'03h54-tower-shirt-ab.jpg',width=620)
    contact([('03:54 BEFORE',frames['03h54','before']),('03:54 AFTER',frames['03h54','after'])],OUT/'03h54-full-ab.jpg',width=836)
    contact([('Receiver BEFORE',frames['coverage','before'].crop(BOX)),('Receiver AFTER / shirt excluded',frames['coverage','after'].crop(BOX))],OUT/'receiver-coverage-ab.jpg',width=500)
    contact([(n+' '+stats[n]['moon'],frames[n,'after']) for n,_ in TIMES[:6]],OUT/'night-times.jpg',width=836)
    contact([(n,frames[n,'after'].crop(BOX)) for n in ('20h','00h','03h54','04h30')],OUT/'night-tower-times.jpg',width=450)
    skin=np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]>=254
    for name,_ in TIMES:
        a=np.asarray(frames[name,'after'],dtype=np.int16);b=np.asarray(frames[name,'before'],dtype=np.int16)
        delta=np.abs(a-b)
        stats[name]['faceMaxRgbDelta']=int(delta[skin].max())
        stats[name]['frontToSideRgbRatio']=round(float(a[130:280,950:980].mean()/a[130:280,1025:1045].mean()),4)
        stats[name]['rightPlaneMeanRgb']=round(float(a[130:280,1025:1045].mean()),4)
        stats[name]['beforeRightPlaneMeanRgb']=round(float(b[130:280,1025:1045].mean()),4)
        assert stats[name]['faceMaxRgbDelta']<=1
        if name in ('dawn','noon','dusk'):
            stats[name]['maxRgbDelta']=int(delta.max());assert delta.max()==0
    # Independent painted shirt samples visibly affected in the user's screenshot.
    # Compare to the frozen character receive before architecture ownership changed.
    sample=np.asarray(Image.open(ROOT/'public/assets/hero/base/base-albedo.png'))
    shirt=np.zeros(skin.shape,dtype=bool)
    shirt[336:348,1010:1025]=True
    shirt &= (sample.min(axis=2)>160)&(sample.max(axis=2)-sample.min(axis=2)<35)
    stats['shirtSampleCount']=int(shirt.sum());assert shirt.sum()>50
    ref=np.asarray(frames['03h54','character-reference'],dtype=np.int16)
    for mode in ('before','after'):
        stats[mode+'ShirtMeanRgbError']=round(float(np.abs(np.asarray(frames['03h54',mode],dtype=np.int16)-ref)[shirt].mean()),4)
    assert stats['afterShirtMeanRgbError'] < stats['beforeShirtMeanRgbError']*0.2,'Building shading still contaminates shirt'
    coverage=np.asarray(frames['coverage','after'])[:,:,0]
    stats['shirtReceiverMax']=int(coverage[shirt].max());assert stats['shirtReceiverMax']==0
    assert stats['20h']['frontToSideRgbRatio']<1
    assert stats['04h30']['frontToSideRgbRatio']>1
    assert stats['03h54']['rightPlaneMeanRgb']>stats['03h54']['beforeRightPlaneMeanRgb']
    stats['midnightMaxRgbDelta']=int(np.abs(np.asarray(frames['00h','after'],dtype=np.int16)-np.asarray(frames['24h','after'],dtype=np.int16)).max())
    assert stats['midnightMaxRgbDelta']==0
    (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
