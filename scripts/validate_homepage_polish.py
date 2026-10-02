"""Visual layout checks at the user's desktop size and mobile; browser preview."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
from validate_atmosphere import EDGE
OUT=Path('docs/validation/homepage-followup')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=EDGE,headless=False)
 page=b.new_page(viewport={'width':3828,'height':1931},device_scale_factor=1)
 page.goto('http://127.0.0.1:4174/dist/');page.locator('[data-status="WebGL2"]').wait_for(timeout=40000);page.wait_for_timeout(1000)
 page.locator('.dock-toggle').click();page.locator('.presets button').nth(3).click();page.locator('.playback button').nth(1).click();page.wait_for_timeout(250)
 assert page.locator('.control-dock').evaluate('e=>e.scrollHeight<=e.clientHeight+1')
 page.screenshot(path=str(OUT/'desktop-primary.png'))
 page.locator('.settings-launch').click();page.wait_for_timeout(250)
 assert page.locator('.control-dock').evaluate('e=>e.scrollHeight<=e.clientHeight+1')
 page.screenshot(path=str(OUT/'desktop-expanded.png'))
 page.keyboard.press('Escape');page.keyboard.press('Escape');page.wait_for_timeout(200)
 assert page.locator('a[href]').count()==0
 for button in page.locator('.social-links button').all():
  before=page.url;button.click();assert page.url==before
 page.screenshot(path=str(OUT/'desktop-home.png'))
 page.locator('.themed-select > button').click();page.wait_for_timeout(200);page.screenshot(path=str(OUT/'view-menu.png'));page.keyboard.press('ArrowDown');page.keyboard.press('Enter')
 page.locator('.themed-select > button').click();page.keyboard.press('Home');page.keyboard.press('Enter')
 page.locator('.immersive-button').click();assert page.locator('.clock-block').is_visible();assert page.locator('.dream-header').is_hidden();page.screenshot(path=str(OUT/'desktop-immersive.png'));page.locator('.immersive-button').click()
 stats={'clockPx':page.locator('.clock').evaluate('e=>getComputedStyle(e).fontSize'),'desktopPrimaryNoScroll':True,'desktopExpandedNoScroll':True,'socialButtonsNoNavigation':True}
 for width,height in [(1280,720),(390,844),(360,640),(844,390)]:
  page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200)
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
  page.locator('.dock-toggle').click();page.wait_for_timeout(250)
  assert page.locator('.control-dock').evaluate('e=>e.scrollHeight<=e.clientHeight+1'),(width,height)
  page.locator('.settings-launch').click();page.wait_for_timeout(250)
  assert page.locator('.control-dock').evaluate('e=>{let r=e.getBoundingClientRect();return r.top>=0 && r.bottom<=innerHeight}')
  page.screenshot(path=str(OUT/f'layout-{width}x{height}.png'))
  page.keyboard.press('Escape');page.keyboard.press('Escape')
 (OUT/'layout-checks.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
 b.close()
