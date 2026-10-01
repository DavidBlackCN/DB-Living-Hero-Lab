"""Targeted actual-render shadow softening and frozen-system isolation audit."""
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE,setup,capture,contact
from audit_pre_dawn_tower import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/validation/pre-dawn-tower-softening'
TIMES=(('03h30',210),('04h00',240),('04h15',255),('04h30',270),('04h36',276),('05h00',300),('05h30',330),('06h00',360),('dawn',390),('noon',720),('dusk',1050),('20h',1200),('22h',1320),('00h',0),('02h',120),('24h',1440))
BOX=(915,0,1110,365)

def main():
 OUT.mkdir(exist_ok=True,parents=True)
 mask=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'))>=254
 outside=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'))==0
 skin=np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]>=254
 old=subprocess.check_output(['git','show','77406ed:src/shaders/hero.frag.glsl']).decode('utf-8')
 new=(ROOT/'src/shaders/hero.frag.glsl').read_text(encoding='utf-8')
 frames={};stats={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  for mode,shader in [('before',old),('after',new)]:
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
   page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
   setup(page)
   for name,minutes in TIMES:
    time(page,minutes);frames[name,mode]=capture(page)
    if name=='04h15':frames[name,mode].save(OUT/f'{name}-{mode}.png')
    if mode=='after':
     stats[name]={'minutes':minutes,'moon':page.locator('small').filter(has_text='Moon Direction').inner_text()}
     if minutes in [m for _,m in TIMES[:9]]:frames[name,mode].save(OUT/f'{name}.jpg',quality=95)
   assert not errors,errors
   assert page.locator('canvas.hero-canvas').evaluate('n=>n.getContext("webgl2").getError()')==0
   # Check the tower in 5-minute actual frames through sunrise; no motion.
   previous=None;steps=[]
   for minutes in range(210,391,5):
    time(page,minutes);current=np.asarray(capture(page),dtype=np.int16)[mask]
    if previous is not None:steps.append(round(float(np.abs(current-previous).mean()),3))
    previous=current
   stats[mode+'Continuity']={'stepMinutes':5,'maxMeanRgbStep':max(steps),'steps':steps}
   page.close()
  browser.close()
 for name,_ in TIMES:
  a=np.asarray(frames[name,'after'],dtype=np.int16);b=np.asarray(frames[name,'before'],dtype=np.int16);d=np.abs(a-b)
  stats[name]['faceMaxDelta']=int(d[skin].max());assert d[skin].max()<=1
  stats[name]['outsideMaskMaxDelta']=int(d[outside].max());assert d[outside].max()<=1
  for mode,f in [('before',b),('after',a)]:
   l=float(f[120:260,950:980][mask[120:260,950:980]].mean())
   r=float(f[120:260,1025:1035][mask[120:260,1025:1035]].mean())
   stats[name][mode]={'leftMeanRgb':round(l,3),'rightMeanRgb':round(r,3),'gap':round(l-r,3),'ratio':round(l/r,3)}
  if name in ('03h30','04h00','04h15','04h30','04h36','05h00','05h30'):
   assert stats[name]['after']['ratio']>1.0,'Lost the subtle left-facing main plane'
  elif name=='06h00':
   stats[name]['maxDelta']=int(d.max());assert d.max()<=3,'Dawn handoff changed too much'
  elif name in ('00h','02h','24h'):
   # These tower-only frames were intentionally changed by the Moon-center handoff.
   stats[name]['maxDelta']=int(d.max())
  else:
   stats[name]['maxDelta']=int(d.max());assert d.max()<=1 and d.mean()<0.00001,(name,'Changed a frozen other phase')
 assert stats['04h15']['after']['gap']<stats['04h15']['before']['gap']*.5,'Shadow remains too heavy'
 assert stats['04h15']['after']['rightMeanRgb']>stats['04h15']['before']['rightMeanRgb']*1.1
 assert stats['afterContinuity']['maxMeanRgbStep']<=stats['beforeContinuity']['maxMeanRgbStep']+.1
 stats['midnightMaxDelta']=int(np.abs(np.asarray(frames['00h','after'],dtype=np.int16)-np.asarray(frames['24h','after'],dtype=np.int16)).max());assert stats['midnightMaxDelta']==0
 contact([('04:15 BEFORE',frames['04h15','before']),('04:15 AFTER',frames['04h15','after'])],OUT/'04h15-full-ab.jpg',width=836)
 contact([('04:15 BEFORE',frames['04h15','before'].crop(BOX)),('04:15 AFTER',frames['04h15','after'].crop(BOX))],OUT/'04h15-tower-ab.jpg',width=585)
 contact([(n+' '+stats[n]['moon'],frames[n,'after'].crop(BOX)) for n,_ in TIMES[:9]],OUT/'tower-times.jpg',width=420)
 (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
