"""Standalone scene page: no navigation; real controls; deployable relative assets."""
import json,io
from pathlib import Path
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE,contact

OUT=Path('docs/validation/homepage-followup')

def scene_pixels(page):
 style=page.add_style_tag(content='.interface,.frame-line,.immersive-button{visibility:hidden!important}')
 result=np.asarray(Image.open(io.BytesIO(page.locator('.hero-canvas').screenshot())).convert('RGB'),dtype=np.int16)
 style.evaluate('n=>n.remove()')
 return result

def run():
 OUT.mkdir(exist_ok=True)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=EDGE,headless=True,args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
  page=b.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:4174/dist/');page.locator('[data-status="WebGL2"]').wait_for(timeout=40000);page.wait_for_timeout(900)
  assert page.locator('a[href]').count()==0
  assert page.evaluate('document.documentElement.scrollHeight <= innerHeight')
  assert page.locator('.hero-image').get_attribute('src').startswith('./assets/hero')
  page.locator('.dock-toggle').click();page.wait_for_timeout(300)
  # Actual controls work from a built page hosted under /dist/, without a router.
  page.locator('.playback button').nth(1).click();assert page.locator('.leaves-canvas').count()==0
  assert page.locator('.control-dock').evaluate('e=>e.scrollHeight<=e.clientHeight+1'), 'Primary menu overflows'
  pairs=[]
  for i,name in enumerate(['dawn','noon','dusk','night']):
   page.locator('.presets button').nth(i).click();page.wait_for_timeout(150)
   page.screenshot(path=str(OUT/f'{name}.png'));pairs.append((name,Image.open(OUT/f'{name}.png')))
  contact(pairs,OUT/'four-phases.jpg',width=836)
  page.locator('.presets button').nth(3).click();page.wait_for_timeout(100)
  before=scene_pixels(page)
  identity=page.locator('.hero-canvas').element_handle()
  page.locator('.settings-launch').click();page.wait_for_timeout(200)
  page.get_by_role('slider',name='曝光补偿',exact=True).fill('0.5')
  assert page.locator('.control-dock').evaluate('e=>e.scrollHeight<=e.clientHeight+1'), 'Expanded desktop menu overflows'
  page.screenshot(path=str(OUT/'lighting-drawer.png'))
  page.keyboard.press('Escape');page.wait_for_timeout(100)
  assert page.locator('.settings-launch').get_attribute('aria-expanded')=='false'
  after=scene_pixels(page)
  assert np.abs(after-before).mean()>3
  page.locator('.settings-launch').click();page.wait_for_timeout(200)
  # Every slider reaches the actual renderer: restore before testing the next.
  slider_effects={}
  for label,value in [('泛光强度','0.45'),('高亮阈值','0.1'),('方向明暗','0'),('边缘柔和','0.65'),('色彩饱和','0.6')]:
   if page.locator('.settings-mode button').inner_text()=='恢复昼夜自动':page.locator('.settings-mode button').click()
   slider=page.get_by_role('slider',name=label,exact=True);slider.fill(value)
   page.keyboard.press('Escape');page.wait_for_timeout(100)
   image=scene_pixels(page)
   slider_effects[label]=float(np.abs(image-before).mean());assert slider_effects[label]>0,label
   page.locator('.settings-launch').click();page.wait_for_timeout(200)
  page.locator('.settings-mode button').click();page.keyboard.press('Escape');page.wait_for_timeout(100)
  restored=scene_pixels(page)
  assert np.array_equal(before,restored)
  assert page.locator('.hero-canvas').evaluate('(n,old)=>n===old',identity)
  page.locator('.themed-select > button').click();page.get_by_role('menuitemradio').nth(2).click();page.locator('.dock-toggle').click();page.locator('.settings-launch').click()
  assert page.get_by_role('slider',name='曝光补偿',exact=True).is_disabled()
  page.keyboard.press('Escape');page.locator('.themed-select > button').click();page.get_by_role('menuitemradio').nth(0).click();page.locator('.dock-toggle').click()
  page.get_by_role('button',name='播放昼夜轮播',exact=True).click();t=page.locator('.dock-heading > output').inner_text();page.wait_for_timeout(200)
  assert t!=page.locator('.dock-heading > output').inner_text()
  page.get_by_role('button',name='暂停昼夜轮播',exact=True).click()
  page.locator('.sync-button').click();assert page.locator('.sync-button').is_disabled()
  page.locator('.immersive-button').click();assert page.locator('.control-dock').is_hidden()
  assert page.locator('.clock-block').is_visible()
  page.screenshot(path=str(OUT/'immersive.png'));page.keyboard.press('h');assert page.locator('.dock-toggle').is_visible()
  page.get_by_role('button',name='进入全屏',exact=True).click();page.wait_for_timeout(150)
  assert page.evaluate('!!document.fullscreenElement');page.get_by_role('button',name='退出全屏',exact=True).click()
  page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(250)
  assert page.evaluate('document.documentElement.scrollHeight <= innerHeight && document.documentElement.scrollWidth <= innerWidth')
  page.screenshot(path=str(OUT/'mobile.png'))
  page.locator('.dock-toggle').click()
  page.locator('.settings-launch').click();page.wait_for_timeout(200);page.screenshot(path=str(OUT/'mobile-drawer.png'))
  page.keyboard.press('Escape');page.close()
  page=b.new_page(reduced_motion='reduce');page.goto('http://127.0.0.1:4174/dist/');page.locator('[data-status="WebGL2"]').wait_for()
  page.locator('.dock-toggle').click()
  assert page.locator('.playback button').nth(0).is_disabled() and page.locator('.playback button').nth(1).is_disabled()
  assert page.locator('.leaves-canvas').count()==0
  b.close()
 assert not errors,errors
 stats={'builtSubpathDeployment':True,'noNavigationOrScroll':True,'slidersMeanPixelChange':slider_effects,'autoRestoreExact':True,'canvasNotReinitialized':True,'timePlayRealtime':True,'fullscreenImmersive':True,'mobileReducedMotion':True,'errors':errors}
 (OUT/'checks.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8');print(stats)

if __name__=='__main__':run()
