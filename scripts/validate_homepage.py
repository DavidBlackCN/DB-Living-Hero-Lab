"""Example homepage: poster/Lit entrance, state-preserving drawer and layouts."""
import io,json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE,contact

OUT=Path('docs/validation/homepage')

def run():
 OUT.mkdir(exist_ok=True)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=b.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  held=[];page.route('**/base-normal-v3.png',lambda route:held.append(route))
  page.goto('http://127.0.0.1:5173',wait_until='domcontentloaded')
  page.wait_for_function("document.querySelector('.hero-image')?.naturalWidth > 0")
  page.wait_for_timeout(200)
  assert page.locator('.hero-canvas').evaluate("n=>getComputedStyle(n).opacity")=='0'
  page.screenshot(path=str(OUT/'entrance-base.png'))
  frames=[Image.open(io.BytesIO(page.screenshot())).convert('RGB')]
  page.wait_for_function("document.querySelector('.hero-canvas') !== null")
  assert held
  for route in held:route.continue_()
  page.locator('[data-status="WebGL2"]').wait_for(timeout=40000)
  for _ in range(6):
   page.wait_for_timeout(130);frames.append(Image.open(io.BytesIO(page.screenshot())).convert('RGB'))
  page.wait_for_timeout(400)
  assert page.locator('.hero-canvas').evaluate("n=>getComputedStyle(n).opacity")=='1'
  page.screenshot(path=str(OUT/'entrance-lit.png'))
  frames=[im.resize((836,470)) for im in frames]
  frames[0].save(OUT/'entrance.gif',save_all=True,append_images=frames[1:],duration=[500]+[170]*6,loop=0)
  pairs=[]
  for i,name in enumerate(['dawn','noon','dusk','night']):
   page.locator('.scene-presets button').nth(i).click();page.wait_for_timeout(250)
   page.screenshot(path=str(OUT/f'{name}.png'))
   pairs.append((name,Image.open(OUT/f'{name}.png')))
  contact(pairs,OUT/'four-phases.jpg',width=836)
  node=page.locator('.hero-canvas').element_handle()
  page.locator('.debug-reopen').click();page.wait_for_timeout(220)
  assert page.locator('.debug-panel').evaluate('n=>n.open')
  page.get_by_role('slider',name='24H Preview').evaluate("n=>{n.value=1320;n.dispatchEvent(new Event('input',{bubbles:true}))}")
  page.screenshot(path=str(OUT/'drawer.png'))
  for _ in range(45):
   page.keyboard.press('Tab');assert page.evaluate("document.querySelector('.debug-panel').contains(document.activeElement)")
  page.keyboard.press('Escape')
  assert page.locator('.debug-reopen').evaluate('n=>n===document.activeElement')
  assert page.locator('.hero-canvas').evaluate('(n,old)=>n===old',node)
  assert page.locator('.scene-note time').inner_text()=='22:00'
  page.locator('.debug-reopen').click();page.wait_for_timeout(200)
  page.get_by_role('button',name='Play',exact=True).click()
  page.keyboard.press('Escape');before=page.locator('.scene-note time').inner_text();page.wait_for_timeout(250)
  assert before!=page.locator('.scene-note time').inner_text()
  page.locator('.scene-presets button').nth(1).click()
  page.screenshot(path=str(OUT/'desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(500)
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
  page.screenshot(path=str(OUT/'mobile.png'),full_page=True)
  page.locator('.debug-reopen').click();page.wait_for_timeout(220)
  assert page.locator('.debug-panel').bounding_box()['width']<=390
  page.screenshot(path=str(OUT/'mobile-drawer.png'));page.keyboard.press('Escape')
  page.get_by_role('link',name='随便逛逛').click();page.wait_for_timeout(100)
  assert page.locator('#explore').bounding_box()['y'] < 50
  page.close()
  page=b.new_page(viewport={'width':1200,'height':800},reduced_motion='reduce')
  page.goto('http://127.0.0.1:5173');page.locator('[data-status="WebGL2"]').wait_for()
  assert page.locator('.hero-canvas').evaluate("n=>getComputedStyle(n).transitionDuration")=='0s'
  assert page.locator('.leaves-canvas').count()==0
  b.close()
 assert not errors,errors
 result={'posterBeforeLit':True,'drawerFocusAndEscape':True,'drawerPreservesRendererTimeAndPlay':True,'responsiveAndAnchors':True,'reducedMotion':True,'pageErrors':errors}
 (OUT/'checks.json').write_text(json.dumps(result,indent=2));print(result)

def frozen_visual():
 import numpy as np
 from validate_final_integration import mount,ready,option,exposed
 stats={}
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=mount(b);page.set_viewport_size({'width':1672,'height':941});page.goto('http://127.0.0.1:5173');ready(page)
  option(page,debug=True,paused=True,style={'height':'941px'});page.locator('#host-title').evaluate('n=>n.remove()')
  page.locator('.debug-reopen').click()
  for label in ['Leaves','Blink on/off','Breathing on/off','Hair Motion on/off']:page.get_by_label(label).uncheck()
  page.keyboard.press('Escape');page.locator('.debug-reopen').evaluate('n=>n.style.visibility="hidden"')
  for name,m in [('dawn',390),('noon',720),('dusk',1050),('night',1320)]:
   exposed(page,'setTime',m);page.wait_for_timeout(150)
   current=np.asarray(Image.open(io.BytesIO(page.screenshot())).convert('RGB'),dtype=np.int16)
   baseline=np.asarray(Image.open(f'docs/validation/r7-4/{name}-baseline.png').convert('RGB'),dtype=np.int16)
   delta=np.abs(current-baseline)
   # Golden capture includes the old top-left Debug button, now relocated.
   delta[16:40,16:66]=0
   stats[name]={'maxOutsideOldDebugButton':int(delta.max()),'mean':float(delta.mean())}
   assert delta.max()==0,stats
  b.close()
 (OUT/'visual-regression.json').write_text(json.dumps(stats,indent=2));print(stats)

if __name__=='__main__':
 import sys
 if '--visual' in sys.argv:frozen_visual()
 else:run()
