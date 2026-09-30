"""Isolate Face coverage from shading/Post; no runtime diagnostic patch."""

from io import BytesIO
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from validate_atmosphere import EDGE, PHASES, capture, contact, setup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/validation/r7-3b-final-fix'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    old = subprocess.check_output(['git', 'show', 'f56cd9f:public/assets/hero/material/material-mask.png'])
    old_mask = np.asarray(Image.open(BytesIO(old)))
    mask = np.asarray(Image.open(ROOT / 'public/assets/hero/material/material-mask.png'))
    assert np.array_equal(old_mask[:,:,1:], mask[:,:,1:]), 'Hair/Iris/unused channels changed'
    difference = np.any(mask != old_mask, axis=2)
    ys,xs = np.where(difference)
    # Face coverage now also includes the contiguous exposed neck at the jaw.
    assert xs.min() >= 1070 and xs.max() < 1235 and ys.min() >= 170 and ys.max() < 326
    assert mask[245,1155,0] >= 250, 'Pale nose still falls through Face receive'
    assert mask[290,1150,0] > 180, 'Pale jaw still falls through Face receive'
    contact([('Legacy Face channel', Image.fromarray(old_mask[:,:,0]).convert('RGB').crop((1060,165,1240,310))),
             ('Corrected Face channel', Image.fromarray(mask[:,:,0]).convert('RGB').crop((1060,165,1240,310)))],
            OUT/'face-mask-ab.jpg',width=720)
    result = {'maskChangedPixels':int(difference.sum()), 'changedBounds':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
        'noseCoverageBeforeAfter':[int(old_mask[245,1155,0]),int(mask[245,1155,0])],
        'jawCoverageBeforeAfter':[int(old_mask[290,1150,0]),int(mask[290,1150,0])]}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE, headless=True,
            args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
        frames = {}
        for mode in ('legacy','fixed'):
            page = browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
            if mode == 'legacy':
                page.route('**/assets/hero/material/material-mask.png', lambda route: route.fulfill(body=old,content_type='image/png'))
            setup(page)
            page.get_by_label('Atmosphere on/off').uncheck()
            for phase in PHASES:
                page.get_by_role('button',name=phase,exact=True).click()
                frames[phase,mode] = capture(page)
            page.close()
        head_pairs = []
        for phase in PHASES:
            old_frame, new_frame = frames[phase,'legacy'],frames[phase,'fixed']
            contact([('Legacy Face coverage',old_frame.crop((1070,175,1250,308))),
                     ('Corrected Face coverage',new_frame.crop((1070,175,1250,308)))],
                    OUT/(phase.lower()+'-face-coverage-ab.jpg'),width=720)
            head = Image.open(OUT/(phase.lower()+'.png')).crop((990,10,1370,335))
            head.resize((760,650)).save(OUT/(phase.lower()+'-head.png'))
            head_pairs.append((phase,head))
            delta = np.abs(np.asarray(new_frame,dtype=np.int16)-np.asarray(old_frame,dtype=np.int16))
            result[phase] = {'faceMeanRgbDelta':round(float(delta[190:295,1080:1230].mean()),4),
                'lampRegionMaxRgbDelta':int(delta[:425,:260].max())}
            assert delta[:425,:260].max() == 0, 'Face coverage affected lamp illumination'
        contact(head_pairs,OUT/'four-heads.jpg',width=760)
        contact([('Night old coverage / same Post',frames['Night','legacy']),
                 ('Night fixed coverage / same Post',frames['Night','fixed'])],OUT/'night-coverage-full-ab.jpg')
        browser.close()
    (OUT/'face-audit-stats.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
