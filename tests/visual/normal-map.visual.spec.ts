import { test, expect } from '@playwright/test';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { visualRoot } from './review-output';

test('registered candidate: vectors, surface orientation and protected flat regions', async ({ page }) => {
  await page.goto('/?normal=registered');
  await page.waitForFunction(() => !!window.livingHero);
  const result=await page.evaluate(async()=>{
    const image=new Image();image.src='/assets/generated/normal-registered-v1.png';await image.decode();
    const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
    const ctx=canvas.getContext('2d')!;ctx.drawImage(image,0,0);
    const data=ctx.getImageData(0,0,image.width,image.height).data;
    let maxUnitError=0,minZ=1;
    for(let i=0;i<data.length;i+=4*13){
      const n=[data[i],data[i+1],data[i+2]].map(v=>v/255*2-1);
      maxUnitError=Math.max(maxUnitError,Math.abs(Math.hypot(...n)-1));minZ=Math.min(minZ,n[2]);
    }
    const at=(x:number,y:number)=>Array.from(ctx.getImageData(Math.round(x*3.2),Math.round(y*3.2),1,1).data).slice(0,3);
    return {size:[image.width,image.height],maxUnitError,minZ,
      wall:at(350,250),glass:at(1100,100),face:at(727,195),desk:at(1070,552),
      cupLeft:at(968,478),cupRight:at(1023,478),book:at(735,520)};
  });
  expect(result.size).toEqual([3840,2160]);
  expect(result.maxUnitError).toBeLessThan(.008);
  expect(result.minZ).toBeGreaterThan(.5);
  expect(result.wall).toEqual([128,128,255]);expect(result.glass).toEqual([128,128,255]);
  expect(result.face[2]).toBeGreaterThan(250);
  expect(result.desk[1]).toBeLessThan(80);
  expect(result.cupLeft[0]).toBeLessThan(100);expect(result.cupRight[0]).toBeGreaterThan(155);
  expect(result.book[1]).toBeLessThan(110);
  await mkdir(`${visualRoot}/normals`,{recursive:true});
  await writeFile(`${visualRoot}/normals/vector-checks.json`,JSON.stringify(result,null,2)+'\n');
});

test('registered normal candidate side-by-side captures without changing light settings', async ({ page }) => {
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:1920,height:1080});
  let disabledFrame:Buffer|undefined;
  for(const variant of ['low-frequency','registered','v2']) {
    await page.goto('/?normal='+variant);
    await page.waitForFunction(()=>!!window.livingHero);
    await page.addStyleTag({content:'#debug, #status { visibility:hidden !important; }'});
    await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
    for(const [name,minutes] of [['morning',480],['noon',720],['dusk',1050],['night',1380]] as const) {
      for(const view of ['final','neutral','normal'] as const) {
        await page.evaluate(async({minutes,view})=>{
          window.livingHero.setTime(minutes);window.livingHero.setDebugView(view);
          await new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())));
        },{minutes,view});
        await page.screenshot({path:`${visualRoot}/normals/${variant}-${name}-${view}.png`});
      }
    }
    // With normals disabled both pipelines must display the same rendering.
    await page.evaluate(()=>{const h=window.livingHero;h.setSettings({normal:0});h.setDebugView('final');h.setTime(1050);});
    await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
    const frame=await page.screenshot({path:`${visualRoot}/normals/${variant}-disabled.png`});
    if(disabledFrame) expect(frame.equals(disabledFrame),'normal=0 must leave identical pixels').toBe(true);
    disabledFrame=frame;
    // Isolate the normal response from the already accepted projection/ambient.
    await page.evaluate(()=>{const h=window.livingHero;h.setSettings({normal:1,ambient:0,projected:0,lamp:0,bloom:0,stylized:0});h.setDebugView('neutral');});
    await page.evaluate(()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve()))));
    await page.screenshot({path:`${visualRoot}/normals/${variant}-directional-only.png`});
  }
  const surfaces=JSON.parse(await readFile('docs/normal-surfaces-v1.json','utf8'));
  const regions=JSON.parse(await readFile('docs/scene-regions.json','utf8'));
  const guide=await page.evaluate(async({surfaces,regions})=>{
    const image=new Image();image.src='/assets/hero-4k-digital-art.png';await image.decode();
    const canvas=document.createElement('canvas');canvas.width=1920;canvas.height=1080;
    const ctx=canvas.getContext('2d')!;ctx.drawImage(image,0,0,1920,1080);ctx.scale(1.6,1.6);ctx.lineWidth=.7;
    for(const layer of surfaces.layers){
      ctx.strokeStyle='#00ffb4';ctx.stroke(new Path2D(layer.path??regions[layer.region]));
      ctx.strokeStyle='#ffe146';
      for(const ridge of layer.ridges??[]){const [a,b,c,d]=ridge.points;ctx.beginPath();ctx.moveTo(...a as [number,number]);ctx.bezierCurveTo(...[...b,...c,...d] as [number,number,number,number,number,number]);ctx.stroke();}
    }
    return canvas.toDataURL('image/png').split(',')[1];
  },{surfaces,regions});
  await writeFile(`${visualRoot}/normals/source-guides.png`,Buffer.from(guide,'base64'));
  expect(errors).toEqual([]);
});
