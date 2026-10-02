"""Tower coverage closure: actual WebGL A/B, 24H sweep and motion coverage."""
from pathlib import Path
from io import BytesIO
import json, subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE, setup, capture, contact
from audit_pre_dawn_tower import time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/validation/tower-final'
SELECT=[0,30,120,210,240,270,283,300,330,360,390,480,600,720,900,1050,1080,1140,1200,1320,1440]
BOX=(1035,35,1100,110)

def main():
 OUT.mkdir(exist_ok=True)
 old=subprocess.check_output(['git','show','0f1078d:public/assets/hero/lighting/tower-receiver-mask.png'])
 beforemask=np.asarray(Image.open(BytesIO(old)),dtype=np.int16)
 newmask=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'),dtype=np.int16)
 delta=newmask-beforemask; ys,xs=np.nonzero(delta)
 stats={'maskChangedPixels':int(len(xs)),'maskChangedBounds':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())]}
 skin=np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]>=254
 frames={};before={};steps=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
  page.route('**/tower-receiver-mask.png',lambda r:r.fulfill(body=old,content_type='image/png'))
  setup(page)
  for minute in SELECT:
   time(page,minute);before[minute]=capture(page)
  page.close()
  page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)));setup(page)
  previous=None
  for minute in sorted(set(range(0,1441,15))|set(SELECT)):
   time(page,minute);f=capture(page);a=np.asarray(f,dtype=np.int16)
   if previous is not None:steps.append({'minute':minute,'fullMeanRgbStep':round(float(np.abs(a-previous).mean()),4)})
   previous=a
   if minute in SELECT:
    frames[minute]=f;d=np.abs(a-np.asarray(before[minute],dtype=np.int16))
    outside=d.copy();outside[30:113,1030:1105]=0
    stats[str(minute)]={'moon':page.locator('small').filter(has_text='Moon Direction').inner_text(),'faceMaxDelta':int(d[skin].max()),'outsideRepairMaxDelta':int(outside.max()),'fullMeanDelta':round(float(d.mean()),6),'maxDelta':int(d.max())}
    assert d[skin].max()==0 and outside.max()<=1,(minute,'outside repair changed')
    if minute in (390,720,1050,1320):assert d.max()==0,(minute,'frozen anchor changed')
    f.save(OUT/f'time-{minute:04d}.jpg',quality=94)
  stats['sweep']=steps
  stats['midnightMaxDelta']=int(np.abs(np.asarray(frames[0],dtype=np.int16)-np.asarray(frames[1440],dtype=np.int16)).max());assert stats['midnightMaxDelta']==0
  stats['webglError']=page.locator('canvas.hero-canvas').evaluate('n=>n.getContext("webgl2").getError()');assert not stats['webglError'] and not errors
  contact([(f'{m//60:02}:{m%60:02} '+stats[str(m)]['moon'],frames[m]) for m in SELECT],OUT/'24h-full.jpg',width=640)
  contact([(f'{m//60:02}:{m%60:02}',frames[m].crop((915,0,1110,365))) for m in SELECT],OUT/'24h-tower.jpg',width=300)
  contact([('04:43 BEFORE',before[283].crop(BOX)),('04:43 AFTER',frames[283].crop(BOX))],OUT/'gap-ab.jpg',width=520)
  contact([('04:43 BEFORE',before[283]),('04:43 AFTER',frames[283])],OUT/'full-ab.jpg',width=836)
  contact([(label,frames[m]) for label,m in [('Dawn',390),('Noon',720),('Dusk',1050),('Night',1320)]],OUT/'four-phases.jpg',width=836)
  for name,ts in [('night-review',[0,30,120,210,270,283]),('dawn-review',[300,330,360,390,480,600]),('dusk-review',[900,1050,1080,1140,1200,1320])]:
   contact([(f'{m//60:02}:{m%60:02}',frames[m]) for m in ts],OUT/f'{name}.jpg',width=700)
  # The mask uses the same deformation UV as the Base; sample actual motion.
  time(page,283)
  for label in ('Breathing on/off','Hair Motion on/off','Blink on/off'):page.get_by_label(label).check()
  motion=[]
  for i in range(8):
   page.wait_for_timeout(650);motion.append((f'motion {i}',capture(page).crop((1030,20,1110,135))))
  contact(motion,OUT/'motion-gap.jpg',width=320)
  page.close();browser.close()
 (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in stats.items() if k!='sweep'},indent=2))
def play24():
 import time as clock
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=browser.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)));setup(page,motion=True)
  time(page,0);page.get_by_role('button',name='Play',exact=True).click()
  start=clock.monotonic();samples=[];pairs=[]
  for i in range(13):
   page.wait_for_timeout(5000)
   minute=float(page.get_by_role('slider',name='24H Preview').input_value())
   elapsed=clock.monotonic()-start
   samples.append({'elapsed':round(elapsed,3),'minute':minute,'gl':page.locator('canvas.hero-canvas').evaluate('n=>n.getContext("webgl2").getError()')})
   if i%2==0:pairs.append((f'Play {minute/60:.2f}h',capture(page)))
  page.get_by_role('button',name='Pause',exact=True).click()
  assert not errors and all(x['gl']==0 for x in samples)
  assert any(b['minute']<a['minute'] for a,b in zip(samples,samples[1:])),'No full 24H wrap observed'
  contact(pairs,OUT/'play-24h.jpg',width=640)
  result={'elapsedSeconds':round(clock.monotonic()-start,2),'errors':errors,'allMotionEnabled':True,'samples':samples}
  (OUT/'play-24h.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
  browser.close();print(json.dumps(result,indent=2))

if __name__=='__main__':
 import sys
 if '--play' in sys.argv:play24()
 else:main()
