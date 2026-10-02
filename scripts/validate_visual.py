import io,json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from browser_support import EDGE
OUT=Path("artifacts/visual");OUT.mkdir(parents=True,exist_ok=True)
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
   baseline=np.asarray(Image.open(f'docs/validation/baseline/{name}.png').convert('RGB'),dtype=np.int16)
   delta=np.abs(current-baseline)
   # Golden capture includes the old top-left Debug button, now relocated.
   delta[16:40,16:66]=0
   # R7.4 predates the accepted R7.1 source-mask refinement. Exclude only
   # the two glass footprints (+ filter fringe); validate_repository hashes
   # all current assets and validate_lamp_masks checks the actual six panes.
   delta[127:173,33:69]=0
   delta[244:278,145:171]=0
   # Accepted pane changes also leave <=1 display-code Bloom differences nearby.
   fringe=delta[70:301,0:211]
   assert fringe.max()<=1, 'Unexpected lamp neighborhood difference'
   stats[name]={'maxOutsideHistoricalUiAndLampPanes':int(delta.max()),'mean':float(delta.mean())}
   stats[name]['lampBloomFringeMax']=int(fringe.max())
   fringe[:]=0
   assert delta.max()==0,stats
  b.close()
 (OUT/'visual-regression.json').write_text(json.dumps(stats,indent=2));print(stats)


if __name__ == "__main__": frozen_visual()
