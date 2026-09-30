"""Actual-render jaw/neck material-boundary audit against 62929ab."""

from io import BytesIO
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

from validate_atmosphere import EDGE, PHASES, capture, contact, setup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/validation/r7-3b-chin-followup'
REFERENCE = '62929ab'
HEAD = (1040, 45, 1300, 335)
JAW = (1100, 270, 1170, 325)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    old_bytes = subprocess.check_output(['git', 'show', f'{REFERENCE}:public/assets/hero/material/material-mask.png'])
    old_mask = np.asarray(Image.open(BytesIO(old_bytes)))
    mask = np.asarray(Image.open(ROOT / 'public/assets/hero/material/material-mask.png'))
    assert np.array_equal(old_mask[:,:,1:], mask[:,:,1:]), 'Hair/Iris channels changed'
    changed = mask[:,:,0] != old_mask[:,:,0]
    yy,xx = np.where(changed)
    assert xx.min() >= 1090 and xx.max() <= 1190 and yy.min() >= 265 and yy.max() <= 326
    assert mask[294,1150,0] >= 250 and mask[300,1135,0] >= 250, 'Jaw/neck still fall out of skin receive'
    assert mask[326,1144,0] == 0, 'Skin region leaks into tie/collar'
    contact([('62929ab skin coverage', Image.fromarray(old_mask[:,:,0]).convert('RGB').crop((1080,255,1200,330))),
             ('Continuous face/neck coverage', Image.fromarray(mask[:,:,0]).convert('RGB').crop((1080,255,1200,330)))],
            OUT/'skin-coverage-ab.jpg',width=720)
    stats = {'reference': REFERENCE, 'changedMaskPixels':int(changed.sum()),
        'changedMaskBounds':[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],
        'jawCoverageBeforeAfter':[int(old_mask[294,1150,0]),int(mask[294,1150,0])],
        'neckCoverageBeforeAfter':[int(old_mask[300,1135,0]),int(mask[300,1135,0])]}
    frames = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=EDGE,headless=True,
            args=['--enable-webgl','--use-gl=angle','--use-angle=d3d11'])
        for mode in ('before','after'):
            page = browser.new_page(viewport={'width':1672,'height':941},device_scale_factor=1)
            if mode == 'before':
                page.route('**/assets/hero/material/material-mask.png',lambda route: route.fulfill(body=old_bytes,content_type='image/png'))
            setup(page)
            for phase in PHASES:
                page.get_by_role('button',name=phase,exact=True).click()
                frames[phase,mode] = capture(page,OUT/f'{phase.lower()}-{mode}.png')
            if mode == 'after':
                slider = page.get_by_role('slider',name='24H Preview')
                midnight = []
                for minute in (0,1440):
                    slider.evaluate("(node,value)=>{node.value=String(value);node.dispatchEvent(new Event('input',{bubbles:true}));}",minute)
                    midnight.append(np.asarray(capture(page),dtype=np.int16))
                stats['midnightMaxRgbDelta'] = int(np.abs(midnight[0]-midnight[1]).max())
                assert stats['midnightMaxRgbDelta'] == 0, 'Midnight wrap mismatch'
            page.close()
        browser.close()
    head_pairs = []
    for phase in PHASES:
        before,after = frames[phase,'before'],frames[phase,'after']
        contact([(f'{phase} / 62929ab',before.crop(HEAD)),(f'{phase} / continuous skin receive',after.crop(HEAD))],
            OUT/f'{phase.lower()}-head-ab.jpg',width=780)
        contact([(f'{phase} / 62929ab',before.crop(JAW)),(f'{phase} / continuous skin receive',after.crop(JAW))],
            OUT/f'{phase.lower()}-jaw-ab.jpg',width=560)
        head_pairs.append((phase,after.crop(HEAD)))
        delta = np.abs(np.asarray(after,dtype=np.int16)-np.asarray(before,dtype=np.int16))
        outside = delta.copy();outside[255:335,1080:1200] = 0
        stats[phase] = {'jawMeanRgbDelta':round(float(delta[285:307,1115:1160].mean()),4),
            'outsideJawNeckMaxRgbDelta':int(outside.max())}
        assert outside.max() <= 1, 'Change escaped jaw/neck area'
    contact(head_pairs,OUT/'four-heads.jpg',width=780)
    contact([(phase,frames[phase,'after']) for phase in PHASES],OUT/'four-phases.jpg')
    (OUT/'audit-stats.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
    print(json.dumps(stats,indent=2))


if __name__ == '__main__':
    main()
