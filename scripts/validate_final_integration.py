"""R7.4 host API, quality, fallback and lifecycle acceptance."""
import json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/validation/r7-4'
HOST='''import {h,ref} from '/node_modules/.vite/deps/vue.js';
import Hero from '/src/components/LivingHero.vue';
export default {setup(){const options=ref({quality:'high',minutes:1320,style:{height:'600px'}}),alive=ref(true),spacer=ref(0);window.host={options,alive,spacer,status:[],errors:[]};return()=>h('div',{},[h('div',{style:{height:spacer.value+'px'}}),alive.value?h(Hero,{...options.value,onStatus:s=>window.host.status.push(s),onError:e=>window.host.errors.push(e)}, {default:()=>h('h1',{id:'host-title'},'Hero slot')}):null]);}};'''
COUNTERS='''window.counts={gl:0,leaf:0};const d=WebGL2RenderingContext.prototype.drawArrays;WebGL2RenderingContext.prototype.drawArrays=function(...a){window.counts.gl++;return d.apply(this,a)};const f=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(...a){window.counts.leaf++;return f.apply(this,a)};'''
def mount(browser,init='',dpr=1):
 page=browser.new_page(viewport={'width':1200,'height':800},device_scale_factor=dpr)
 page.add_init_script(COUNTERS+init)
 compiled=page.request.get('http://127.0.0.1:5173/src/components/LivingHero.vue').text()
 vue=re.search(r'from [\"\']([^\"\']*deps/vue.js[^\"\']*)',compiled).group(1)
 host=HOST.replace('/node_modules/.vite/deps/vue.js',vue)
 page.route('**/src/app/App.vue*',lambda r:r.fulfill(body=host,content_type='application/javascript'))
 page.errors=[];page.on('pageerror',lambda e:page.errors.append(str(e)))
 return page

def ready(page):page.locator('.hero-stage[data-status="WebGL2"]').wait_for(timeout=30000)
def option(page,**kwargs):page.evaluate('(v)=>Object.assign(window.host.options.value,v)',kwargs)
def exposed(page,method,*args):page.locator('.hero-stage').evaluate('(n,a)=>n.__vueParentComponent.exposed[a[0]](...a.slice(1))',[method,*args])
def idle(page):
 page.wait_for_timeout(300);a=page.evaluate('window.counts');page.wait_for_timeout(400);b=page.evaluate('window.counts');assert a==b,(a,b)

def main():
 OUT.mkdir(exist_ok=True);stats={}
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=mount(b,dpr=2);page.goto('http://127.0.0.1:5173');ready(page)
  assert page.locator('.debug-panel').count()==0 and page.locator('#host-title').count()==1
  stats['loadingProgress']=page.evaluate('host.status.map(s=>s.loaded)');assert 16 in stats['loadingProgress']
  stats['qualityBuffers']={}
  for q,scale in [('high',2),('medium',1.5),('low',1)]:
   option(page,quality=q);page.wait_for_timeout(350)
   dims=page.locator('.hero-canvas').evaluate('n=>[n.width,n.height]');stats['qualityBuffers'][q]=dims
   assert dims==[int(1200*scale),int(600*scale)],(q,dims,page.locator('.hero-stage').get_attribute('data-quality'))
   if q=='low':assert page.locator('.leaves-canvas').count()==0;idle(page)
  option(page,quality='high');page.set_viewport_size({'width':3840,'height':2160});page.wait_for_timeout(300)
  pixels=page.locator('.hero-canvas').evaluate('n=>n.width*n.height');assert pixels<=8294400*1.002;stats['highPixelCeiling']=pixels
  page.set_viewport_size({'width':1200,'height':800})
  option(page,quality='static');page.wait_for_timeout(300);assert page.locator('.hero-canvas').count()==0;idle(page)
  option(page,quality='high');ready(page);option(page,paused=True);idle(page);option(page,paused=False)
  # Controlled time and exposed imperative API remain independent.
  exposed(page,'setTime',390);page.wait_for_timeout(100)
  exposed(page,'play');page.wait_for_timeout(200);exposed(page,'pause')
  page.evaluate('host.spacer.value=1800');page.wait_for_timeout(350);idle(page)
  page.evaluate('host.spacer.value=0');page.wait_for_timeout(350)
  # Nested asset root; do not require a server-root deployment.
  page.route('**/blog/assets/hero/**',lambda r:r.continue_(url=r.request.url.replace('/blog/assets/','/assets/')))
  option(page,assetRoot='/blog/assets/hero');ready(page)
  assert '/blog/assets/hero/' in page.locator('.hero-image').get_attribute('src')
  page.screenshot(path=str(OUT/'production-host.png'))
  page.evaluate('host.alive.value=false');page.wait_for_timeout(400);idle(page)
  page.evaluate('host.alive.value=true');ready(page)
  assert not page.errors,page.errors
  stats['hostApiAndOffscreenPause']=True;stats['unmountRemount']=True;page.close()
  page=mount(b,"const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(k,...a){return k==='webgl2'?null:original.call(this,k,...a)};")
  page.goto('http://127.0.0.1:5173');page.locator('[data-status="fallback"]').wait_for();assert page.locator('.hero-image').is_visible();assert page.locator('.leaves-canvas').count()==0;idle(page);page.screenshot(path=str(OUT/'webgl-fallback.png'));stats['webglFallback']=True;page.close()
  page=mount(b);page.route('**/base-normal-v3.png',lambda r:r.abort());page.goto('http://127.0.0.1:5173');page.locator('[data-status="fallback"]').wait_for();assert page.evaluate('host.errors.length')>0
  page.unroute('**/base-normal-v3.png');exposed(page,'retry');ready(page);stats['assetFailureRetry']=True;page.close()
  page=mount(b,"Object.defineProperty(navigator,'deviceMemory',{get:()=>2});")
  page.goto('http://127.0.0.1:5173');ready(page);option(page,quality='auto');page.locator('[data-quality="static"]').wait_for();assert page.locator('.hero-canvas').count()==0;stats['lowMemoryFallback']=True;page.close()
  page=mount(b);page.emulate_media(reduced_motion='reduce');page.goto('http://127.0.0.1:5173');ready(page);assert page.locator('.leaves-canvas').count()==0;idle(page);stats['reducedMotion']=True;page.close()
  page=mount(b)
  # Unmount while critical assets are in flight; stale ready must not revive it.
  page.route('**/base-normal-v3.png',lambda r:r.abort())
  page.goto('http://127.0.0.1:5173',wait_until='domcontentloaded')
  page.wait_for_function('!!window.host')
  page.evaluate('host.alive.value=false');page.wait_for_timeout(300);idle(page)
  assert page.locator('.hero-stage').count()==0 and not page.errors
  stats['pendingUnmount']=True;page.close()
  # Feed the existing cadence-pressure event: auto alone may step down.
  page=mount(b);page.goto('http://127.0.0.1:5173');ready(page);option(page,quality='auto');page.wait_for_timeout(100)
  initial=page.locator('.hero-stage').get_attribute('data-quality')
  page.locator('.hero-canvas').evaluate("n=>n.__vueParentComponent.emit('slow')");page.wait_for_timeout(100)
  assert page.locator('.hero-stage').get_attribute('data-quality')!=initial
  stats['adaptiveBudgetEvent']=True;page.close();b.close()
 (OUT/'integration-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2))
def visual():
 import numpy as np
 from PIL import Image
 from validate_atmosphere import setup,capture,contact
 from audit_pre_dawn_tower import time
 stats={};pairs=[]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=b.new_page(viewport={'width':1672,'height':941},device_scale_factor=1);setup(page)
  for label,t in [('dawn',390),('noon',720),('dusk',1050),('night',1320),('predawn',283),('transition',345),('midnight',0)]:
   time(page,t);f=capture(page);old=Image.open(OUT/f'{label}-baseline.png').convert('RGB')
   delta=np.abs(np.asarray(f,dtype=np.int16)-np.asarray(old,dtype=np.int16))
   stats[label]={'max':int(delta.max()),'mean':float(delta.mean())};assert delta.max()==0,(label,stats[label])
   pairs.append((label,f))
  time(page,1440);end=capture(page);assert np.array_equal(np.asarray(end),np.asarray(pairs[-1][1]))
  contact(pairs[:4],OUT/'four-phases.jpg',width=836);b.close()
 (OUT/'baseline-stats.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2))

if __name__=='__main__':
 import sys
 if '--visual' in sys.argv:visual()
 else:main()
