"""Tower Moon-center handoff: receiving energy, actual frames, wrap and isolation."""
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE,setup,capture,contact
from audit_pre_dawn_tower import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/validation/tower-moon-handoff'
TIMES=(('22h',1320),('23h30',1410),('00h',0),('00h30',30),('01h',60),('01h30',90),('02h',120),('02h30',150),('03h',180),('03h30',210),('04h15',255),('05h',300),('dawn',390),('noon',720),('dusk',1050),('24h',1440))
NIGHT_NAMES=[name for name,_ in TIMES[:10]]
BOX=(915,0,1110,365)

def mean_plane(image,mask,x0,x1):
 return float(np.asarray(image,dtype=float)[120:260,x0:x1][mask[120:260,x0:x1]].mean())

def install(page,shader):
 page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
 setup(page)

def main():
 OUT.mkdir(exist_ok=True,parents=True)
 mask=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'))==255
 outside=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'))==0
 skin=np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]>=254
 before=subprocess.check_output(['git','show','efc6c32:src/shaders/hero.frag.glsl']).decode('utf-8')
 after=(ROOT/'src/shaders/hero.frag.glsl').read_text(encoding='utf-8')
 frames={};stats={};energy={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  for mode,shader in [('before',before),('after',after)]:
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   install(page,shader)
   for name,minute in TIMES:
    time(page,minute);f=capture(page);frames[name,mode]=f
    if mode=='after':stats[name]={'minutes':minute,'moon':page.locator('small').filter(has_text='Moon Direction').inner_text()}
    if name=='02h':f.save(OUT/f'{name}-{mode}.png')
   assert not errors,errors
   assert page.locator('canvas.hero-canvas').evaluate('n=>n.getContext("webgl2").getError()')==0
   # Dense 1-minute samples across midnight and the center-ownership join.
   previous=None;steps=[];per_minute={}
   for minute in range(1420,1481):
    time(page,minute%1440);f=capture(page);a=np.asarray(f,dtype=np.int16)
    per_minute[minute]={'left':round(mean_plane(f,mask,950,980),3),'right':round(mean_plane(f,mask,1025,1035),3)}
    if previous is not None:steps.append(round(float(np.abs(a-previous)[mask].mean()),3))
    previous=a
   stats[mode+'MidnightContinuity']={'stepMinutes':1,'maxMeanRgbStep':max(steps),'steps':steps,'planeMeans':per_minute}
   # 30-minute observation: both receiving planes must move throughout the arc.
   page.close()
  for mode,shader in [('before',before),('after',after)]:
   expr='clamp(relitLinear/max(baseLinear,vec3(0.0001))*2.0,0.0,1.0)'
   debug=shader.replace('outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);',
    f'outColor = u_view == 2 ? vec4({expr},1.0) : vec4(showMotionRegions(displayColor, regions, hairRegion),base.a);')
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1);install(page,debug)
   page.get_by_label('Post Processing on/off').uncheck()
   for name,minute in TIMES[3:7]:
    time(page,minute);energy[name,mode]=capture(page)
   page.close()
   metadata=shader.replace('outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);',
    'outColor = u_view == 2 ? vec4(vec3(character),1.0) : vec4(showMotionRegions(displayColor, regions, hairRegion),base.a);')
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1);install(page,metadata)
   page.get_by_label('Post Processing on/off').uncheck();time(page,30)
   frames['metadata',mode]=capture(page);page.close()
  browser.close()
 for name,_ in TIMES:
  a=np.asarray(frames[name,'after'],dtype=np.int16);b=np.asarray(frames[name,'before'],dtype=np.int16);d=np.abs(a-b)
  stats[name]['faceMaxDelta']=int(d[skin].max());assert d[skin].max()<=1
  stats[name]['outsideMaskMaxDelta']=int(d[outside].max());assert d[outside].max()<=1
  for mode in ('before','after'):
   stats[name][mode]={'leftMeanRgb':round(mean_plane(frames[name,mode],mask,950,980),3),'rightMeanRgb':round(mean_plane(frames[name,mode],mask,1025,1035),3)}
  if name in ('22h','23h30','03h30','04h15','05h','dawn','noon','dusk'):
   stats[name]['maxDelta']=int(d.max());assert d.max()<=1 and d.mean()<0.00001,(name,'Changed accepted other times')
 midnight=np.abs(np.asarray(frames['00h','after'],dtype=np.int16)-np.asarray(frames['24h','after'],dtype=np.int16))
 stats['midnightMaxDelta']=int(midnight.max());assert midnight.max()==0
 metadata=np.abs(np.asarray(frames['metadata','after'],dtype=np.int16)-np.asarray(frames['metadata','before'],dtype=np.int16))
 stats['characterMetadataMaxDelta']=int(metadata.max());assert metadata.max()==0
 assert stats['afterMidnightContinuity']['maxMeanRgbStep']<0.75,'Abrupt ownership handoff'
 previous_l=None;previous_r=None
 for name in ('00h30','01h','01h30','02h','02h30','03h'):
  l=stats[name]['after']['leftMeanRgb'];r=stats[name]['after']['rightMeanRgb']
  if previous_l is not None:assert l>previous_l and r<previous_r,'Left/right receiving did not transfer together'
  previous_l,previous_r=l,r
 assert stats['01h']['after']['leftMeanRgb']>stats['00h30']['after']['leftMeanRgb']+2,'Left receiving still starts too late'
 assert stats['02h']['after']['leftMeanRgb']>stats['02h']['before']['leftMeanRgb']+6,'No meaningful early-left repair'
 stats['receivingEnergy']={}
 for name in ('00h30','01h','01h30','02h'):
  stats['receivingEnergy'][name]={mode:{'left':round(mean_plane(energy[name,mode],mask,950,980),3),'right':round(mean_plane(energy[name,mode],mask,1025,1035),3)} for mode in ('before','after')}
 e=stats['receivingEnergy'];assert abs(e['00h30']['after']['left']-e['00h30']['after']['right'])<1,'Unbalanced center receiving'
 assert e['01h']['after']['left']>e['00h30']['after']['left'] and e['01h']['after']['right']<e['00h30']['after']['right'],'Normal-driven transfer absent'
 contact([(n+' '+stats[n]['moon'],frames[n,'after']) for n in NIGHT_NAMES],OUT/'night-full-times.jpg',width=640)
 contact([(n+' '+stats[n]['moon'],frames[n,'after'].crop(BOX)) for n in NIGHT_NAMES],OUT/'night-tower-times.jpg',width=320)
 contact([('02:00 BEFORE',frames['02h','before']),('02:00 AFTER',frames['02h','after'])],OUT/'02h-full-ab.jpg',width=836)
 contact([('02:00 BEFORE',frames['02h','before'].crop(BOX)),('02:00 AFTER',frames['02h','after'].crop(BOX))],OUT/'02h-tower-ab.jpg',width=585)
 contact([(n+' '+mode,frames[n,mode].crop(BOX)) for n in ('00h30','01h','02h') for mode in ('before','after')],OUT/'center-handoff-ab.jpg',width=320)
 contact([(n+' '+mode+' receiving',energy[n,mode].crop(BOX)) for n in ('00h30','01h','02h') for mode in ('before','after')],OUT/'receiving-energy-ab.jpg',width=320)
 (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in stats.items() if 'Continuity' not in k},indent=2))
 print('midnight maximum 1-minute mean steps:',stats['beforeMidnightContinuity']['maxMeanRgbStep'],stats['afterMidnightContinuity']['maxMeanRgbStep'])

if __name__=='__main__':main()
