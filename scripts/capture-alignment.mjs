import { chromium } from '@playwright/test';
import { mkdir, readFile, writeFile } from 'node:fs/promises';

// Capture a running local app; no scene or runtime mutation is persisted.
const root = process.argv[2] ?? 'docs/screenshots/technical-art-alignment/review';
const variant = process.argv[3] ?? 'registered';
const port = process.argv[4] ?? '4173';
await mkdir(root, { recursive: true });
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, reducedMotion: 'reduce' });
  await page.goto(`http://127.0.0.1:${port}/?normal=${variant}`);
  await page.waitForFunction(() => !!window.livingHero);
  await page.addStyleTag({ content: '#debug,#status{visibility:hidden!important}' });
  await page.evaluate(() => { const h=window.livingHero;h.setAnimation(false);h.setSteam(false); });
  for (const [name, minutes] of [['dawn',360],['noon',720],['dusk',1050],['night',1380]]) {
    for (const view of ['final','neutral','normal','projected','exterior','overlay']) {
      await page.evaluate(async ({minutes,view}) => {
        const h=window.livingHero;h.setTime(minutes);h.setDebugView(view);
        await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      },{minutes,view});
      await page.screenshot({path:`${root}/${variant}-${name}-${view}.png`});
    }
  }
  await page.evaluate(async () => {
    const h=window.livingHero;h.setTime(1050);h.setSettings({ambient:0,lamp:0,projected:0,bloom:0,stylized:0});h.setDebugView('neutral');
    await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  });
  await page.screenshot({path:`${root}/${variant}-directional-only.png`});
  const surfaces=JSON.parse(await readFile(variant==='registered'?'docs/normal-surfaces-v1.json':'docs/normal-surfaces.json','utf8'));
  const regions=JSON.parse(await readFile('docs/scene-regions.json','utf8'));
  const guide=await page.evaluate(async ({surfaces,regions})=>{
    const im=new Image();im.src='/assets/hero-4k-digital-art.png';await im.decode();
    const c=document.createElement('canvas');c.width=1920;c.height=1080;
    const ctx=c.getContext('2d');ctx.drawImage(im,0,0,1920,1080);ctx.scale(1.6,1.6);ctx.lineWidth=.65;
    for(const layer of surfaces.layers){
      ctx.strokeStyle='#00ffb4';ctx.stroke(new Path2D(layer.path??regions[layer.region]));
      ctx.strokeStyle='#ffe146';
      for(const r of [...(layer.ridges??[]),...(layer.ribbons??[])]){
        const [a,b,c,d]=r.points;ctx.beginPath();ctx.moveTo(...a);ctx.bezierCurveTo(...b,...c,...d);ctx.stroke();
      }
    }
    return c.toDataURL('image/png').split(',')[1];
  },{surfaces,regions});
  await writeFile(`${root}/${variant}-source-guides.png`,Buffer.from(guide,'base64'));
} finally { await browser.close(); }
