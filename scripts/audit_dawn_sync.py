"""Morning Sky/scene synchronization: actual frames, progress and continuity."""
from pathlib import Path
import subprocess,json
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE,setup,capture,contact
from audit_pre_dawn_tower import time
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/validation/dawn-sync'
TIMES=sorted(set(range(270,421,5))|{0,210,720,1050,1320,1440})
SELECT=[300,315,330,345,360,375,390]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 old=subprocess.check_output(['git','show','ecc955e:src/config/lighting.ts']).decode('utf-8')
 js=subprocess.run(['node','--input-type=module','-e',"import ts from 'typescript';let s='';for await(const c of process.stdin)s+=c;process.stdout.write(ts.transpileModule(s,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText)"],input=old,text=True,encoding='utf-8',capture_output=True,check=True).stdout
 sky=np.asarray(Image.open(ROOT/'public/assets/hero/sky/sky-dawn.png'))[:,:,3]>=254
 region=np.zeros(sky.shape,bool);region[50:300,1250:1600]=True;sky=sky&region
 solid=np.asarray(Image.open(ROOT/'public/assets/hero/sky/sky-dawn.png'))[:,:,3]==0
 solid[:,:250]=False
 frames={};stats={};metrics={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  for mode in ('before','after'):
   page=browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   if mode=='before':page.route('**/src/config/lighting.ts*',lambda r:r.fulfill(body=js,content_type='application/javascript'))
   setup(page);metrics[mode]={}
   for minute in TIMES:
    time(page,minute);f=capture(page);frames[mode,minute]=f;a=np.asarray(f,dtype=float)
    metrics[mode][minute]={'sky':float(a[sky].mean()),'scene':float(a[solid].mean()),'face':float(a[240:270,1120:1180].mean())}
    if mode=='after' and minute in SELECT:f.save(OUT/f'time-{minute:04d}.jpg',quality=95)
   assert not errors,errors
   assert page.locator('canvas.hero-canvas').evaluate('n=>n.getContext("webgl2").getError()')==0
   page.close()
  browser.close()
 for minute in TIMES:
  d=np.abs(np.asarray(frames['after',minute],dtype=np.int16)-np.asarray(frames['before',minute],dtype=np.int16))
  if not 300<minute<390:assert d.max()==0,(minute,int(d.max()),'Outside dawn ramp changed')
 stats['outsideTransitionUnchanged']=True
 stats['midnightMaxDelta']=int(np.abs(np.asarray(frames['after',0],dtype=np.int16)-np.asarray(frames['after',1440],dtype=np.int16)).max());assert stats['midnightMaxDelta']==0
 for mode in ('before','after'):
  for minute in SELECT:
   for key in ('sky','scene','face'):
    m=metrics[mode];m[minute][key+'Progress']=(m[minute][key]-m[300][key])/(m[390][key]-m[300][key])
  m=metrics[mode];stats[mode+'MeanProgressGap']=float(np.mean([abs(m[t]['skyProgress']-m[t]['sceneProgress']) for t in SELECT]))
 assert stats['afterMeanProgressGap']<stats['beforeMeanProgressGap']*.7,'Sky and scene still visibly out of step'
 for key in ('sky','scene','face'):
  assert all(metrics['after'][t][key]>=metrics['after'][t-5][key] for t in range(305,391,5)),(key,'Morning brightness dipped')
 stats['metrics']=metrics
 contact([(f'{t//60:02}:{t%60:02} '+mode,frames[mode,t]) for t in SELECT for mode in ('before','after')],OUT/'dawn-ab.jpg',width=700)
 contact([(f'{t//60:02}:{t%60:02}',frames['after',t]) for t in SELECT],OUT/'dawn-times.jpg',width=836)
 contact([(name,frames['after',t]) for name,t in [('Dawn',390),('Noon',720),('Dusk',1050),('Night',1320)]],OUT/'four-phases.jpg',width=836)
 (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in stats.items() if k!='metrics'},indent=2))
 print(json.dumps({mode:{t:metrics[mode][t] for t in SELECT} for mode in ('before','after')},indent=2))
if __name__=='__main__':main()
