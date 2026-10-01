"""Pre-Dawn actual-render surface continuity, isolation and key direction audit."""
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE, setup, capture, contact
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/validation/pre-dawn-tower'
TIMES=(('03h30',210),('04h00',240),('04h30',270),('04h36',276),('05h00',300),('05h15',315),('05h30',330),('06h00',360),('dawn',390),('20h',1200),('22h',1320),('00h',0),('02h',120),('noon',720),('dusk',1050),('24h',1440))
BOX=(915,0,1110,365)

def time(page,minutes):
 page.get_by_role('slider',name='24H Preview').evaluate("(n,v)=>{n.value=String(v);n.dispatchEvent(new Event('input',{bubbles:true}));}",minutes)

def main():
 OUT.mkdir(exist_ok=True,parents=True);frames={};stats={}
 before=subprocess.check_output(['git','show','a0e34e5:src/shaders/hero.frag.glsl']).decode()
 after=(ROOT/'src/shaders/hero.frag.glsl').read_text(encoding='utf-8')
 mask=np.asarray(Image.open(ROOT/'public/assets/hero/lighting/tower-receiver-mask.png'))
 skin=np.asarray(Image.open(ROOT/'public/assets/hero/material/material-mask.png'))[:,:,0]>=254
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  for mode,shader in [('before',before),('after',after)]:
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
   setup(page)
   for name,minutes in TIMES:
    time(page,minutes);frames[name,mode]=capture(page)
    if name=='04h36':frames[name,mode].save(OUT/f'{name}-{mode}.png')
    if mode=='after' and minutes in [v for _,v in TIMES[:9]]:frames[name,mode].save(OUT/f'{name}.jpg',quality=95)
    if mode=='after':stats[name]={'minutes':minutes,'moon':page.locator('small').filter(has_text='Moon Direction').inner_text()}
   assert not errors,errors
   stats[mode+'GlCaps']=page.locator('canvas.hero-canvas').evaluate("n=>{const g=n.getContext('webgl2');return {samplers:g.getParameter(g.MAX_TEXTURE_IMAGE_UNITS),error:g.getError()};}")
   page.close()
  # Source isolation: inspect normalized receiving energy and frozen metadata,
  # avoiding Base pigment and final Post as confounders.
  for mode,shader in [('before',before),('after',after)]:
   for diagnostic,expr in [('receive','clamp(relitLinear/max(baseLinear,vec3(0.0001))*3.0,0.0,1.0)'),('character','vec3(character)')]:
    debug=shader.replace('outColor = vec4(showMotionRegions(displayColor, regions, hairRegion), base.a);',
     f'outColor = u_view == 2 ? vec4({expr},1.0) : vec4(showMotionRegions(displayColor, regions, hairRegion),base.a);')
    page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
    page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(debug)+';',content_type='application/javascript'))
    setup(page);time(page,276);page.get_by_label('Post Processing on/off').uncheck()
    frames[diagnostic,mode]=capture(page);page.close()
  # Adjacent 5-minute actual frames: both the new receiver handoff and Dawn fade.
  page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
  setup(page)
  stats['towerContinuity']={}
  for start,end in ((120,240),(270,390)):
   previous=None;deltas=[]
   for minute in range(start,end+1,5):
    time(page,minute);current=np.asarray(capture(page),dtype=np.int16)
    if previous is not None:
     deltas.append(round(float(np.abs(current-previous)[mask>=254].mean()),3))
    previous=current
   stats['towerContinuity'][f'{start}-{end}']={'stepMinutes':5,'meanRgbDeltas':deltas,'maxMeanRgbDelta':max(deltas)}
   if start==120:assert max(deltas)<2.5,'Abrupt late-night receiver activation'
  page.close()
  minute_frames={}
  for mode,shader in [('before',before),('after',after)]:
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
   page.route('**/src/shaders/hero.frag.glsl?*',lambda route:route.fulfill(body='export default '+json.dumps(shader)+';',content_type='application/javascript'))
   setup(page)
   for minute in range(330,391):
    time(page,minute);minute_frames[mode,minute]=np.asarray(capture(page),dtype=np.int16)[mask>=254]
   page.close()
  baseline_steps=[];after_steps=[];effect_steps=[]
  for minute in range(331,391):
   baseline_steps.append(float(np.abs(minute_frames['before',minute]-minute_frames['before',minute-1]).mean()))
   after_steps.append(float(np.abs(minute_frames['after',minute]-minute_frames['after',minute-1]).mean()))
   effect=minute_frames['after',minute]-minute_frames['before',minute]
   previous_effect=minute_frames['after',minute-1]-minute_frames['before',minute-1]
   effect_steps.append(float(np.abs(effect-previous_effect).mean()))
  stats['dawnFadeOneMinute']={'baselineMaxMeanRgbStep':round(max(baseline_steps),3),
    'afterMaxMeanRgbStep':round(max(after_steps),3),'localChangeMaxMeanRgbStep':round(max(effect_steps),3)}
  assert max(effect_steps)<1.5,'New tower receiving fade is discontinuous'
  browser.close()
 pairs=[]
 for name,_ in TIMES[:9]:
  a=np.asarray(frames[name,'after'],dtype=np.int16);b=np.asarray(frames[name,'before'],dtype=np.int16)
  diff=np.abs(a-b)
  stats[name]['faceMaxRgbDelta']=int(diff[skin].max());assert diff[skin].max()<=1
  stats[name]['outsideMaskMaxRgbDelta']=int(diff[mask==0].max())
  stats[name]['leftMeanRgb']=round(float(a[120:260,950:980][mask[120:260,950:980]>=254].mean()),3)
  stats[name]['rightMeanRgb']=round(float(a[120:260,1025:1035][mask[120:260,1025:1035]>=254].mean()),3)
  stats[name]['leftToRightRatio']=round(stats[name]['leftMeanRgb']/stats[name]['rightMeanRgb'],3)
  # Human review requested gentler separation: retain direction, not a 5% minimum contrast.
  if name in ('03h30','04h00','04h30','04h36','05h00'):assert stats[name]['leftToRightRatio']>1.0, 'No continuous left-facing key'
  pairs.append((name+' '+stats[name]['moon'],frames[name,'after']))
 contact(pairs,OUT/'pre-dawn-full-times.jpg',width=836)
 contact([(n+' '+stats[n]['moon'],frames[n,'after'].crop(BOX)) for n,_ in TIMES[:9]],OUT/'pre-dawn-tower-times.jpg',width=420)
 contact([('04:36 BEFORE',frames['04h36','before']),('04:36 AFTER',frames['04h36','after'])],OUT/'04h36-full-ab.jpg',width=836)
 contact([('04:36 BEFORE',frames['04h36','before'].crop(BOX)),('04:36 AFTER',frames['04h36','after'].crop(BOX))],OUT/'04h36-tower-ab.jpg',width=585)
 contact([('04:36 OLD receiving energy',frames['receive','before'].crop(BOX)),('04:36 registered surface energy',frames['receive','after'].crop(BOX))],OUT/'receiving-energy-ab.jpg',width=585)
 a=np.asarray(frames['receive','after'],dtype=float);b=np.asarray(frames['receive','before'],dtype=float)
 stats['leftReceiveBeforeStd']=round(float(b[120:260,950:980,0].std()),3)
 stats['leftReceiveAfterStd']=round(float(a[120:260,950:980,0].std()),3)
 assert stats['leftReceiveAfterStd']<1.1,'Left receiving plane is fragmented'
 for name,box in [('hat-adjacent',(1056,48,1070,78)),('hair-gap',(1005,283,1024,309))]:
  x0,y0,x1,y1=box;valid=mask[y0:y1,x0:x1]>=254;assert valid.sum()>15
  stats[name]={'registeredSamples':int(valid.sum()),'beforeReceive':round(float(b[y0:y1,x0:x1][valid].mean()),3),'afterReceive':round(float(a[y0:y1,x0:x1][valid].mean()),3)}
  assert stats[name]['afterReceive']<stats[name]['beforeReceive']*.85,'Residual local bright receive'
 c=np.abs(np.asarray(frames['character','after'],dtype=np.int16)-np.asarray(frames['character','before'],dtype=np.int16))
 stats['characterMetadataMaxDelta']=int(c.max());assert c.max()==0
 for name in ('dawn','20h','22h','00h','02h','noon','dusk'):
  d=np.abs(np.asarray(frames[name,'after'],dtype=np.int16)-np.asarray(frames[name,'before'],dtype=np.int16))
  stats[name]['meanRgbDelta']=round(float(d.mean()),9);stats[name]['changedPixels']=int(np.any(d>0,axis=2).sum());stats[name]['maxRgbDelta']=int(d.max());assert d.max()<=1 and d.mean()<0.00001,(name,int(d.max()))
 stats['midnightMaxDelta']=int(np.abs(np.asarray(frames['00h','after'],dtype=np.int16)-np.asarray(frames['24h','after'],dtype=np.int16)).max());assert stats['midnightMaxDelta']==0
 (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
