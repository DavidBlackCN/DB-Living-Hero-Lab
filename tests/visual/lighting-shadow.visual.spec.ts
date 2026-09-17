import { test, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { DebugView } from '../../src/engine/renderer';
import { visualRoot } from './review-output';

test('shadow convergence captures: fixed exposure before and after', async ({page}) => {
  test.setTimeout(90_000);
  const errors:string[]=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:1920,height:1080});
  await page.goto('/'); await page.waitForFunction(()=>!!window.livingHero);
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
  const directory=`${visualRoot}/shadow`; await mkdir(directory,{recursive:true});
  for(const [name,minutes] of [['0600',360],['1200',720],['1730',1050],['2300',1380]] as const) {
    for(const view of ['final','neutral','shadow','lamp','exterior','projected','base'] as DebugView[]) {
      await page.evaluate(async({minutes,view})=>{
        window.livingHero.setTime(minutes);window.livingHero.setDebugView(view);
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      },{minutes,view});
      await page.screenshot({path:`${directory}/${name}-${view}.png`});
    }
    if(minutes>=1050) {
      await page.evaluate(async()=>{
        window.livingHero.setSettings({shadow:0});window.livingHero.setDebugView('final');
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      });
      await page.screenshot({path:`${directory}/${name}-shadow-off-final.png`});
      await page.evaluate(()=>window.livingHero.setSettings({shadow:.65}));
    }
  }
  await writeFile(`${directory}/settings.json`,JSON.stringify(await page.evaluate(()=>window.livingHero.getSettings()),null,2)+'\n');
  expect(errors).toEqual([]);
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});

test('contact bands stay registered and shadow control preserves soft faces', async ({page}) => {
  await page.setViewportSize({width:1200,height:675});
  await page.goto('/');await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setSettings({bloom:0});
    const im=new Image();im.src='/assets/generated/light-shaping.svg';await im.decode();
    const c=document.createElement('canvas');c.width=1200;c.height=675;
    const ctx=c.getContext('2d')!;ctx.drawImage(im,0,0);
    const blue=(x:number,y:number)=>ctx.getImageData(x,y,1,1).data[2];
    const contact={fringe:blue(708,160),strap:blue(609,377),chair:blue(370,380),tools:blue(985,359),
      toolsBody:blue(970,340),pageInterior:blue(740,525),floating:blue(770,575),nose:blue(728,210)};
    const points={face:[728,210],hair:[849,312],sleeve:[815,393],book:[793,521],cup:[968,478]};
    async function sample(shadow:number) {
      h.setSettings({shadow});h.setTime(1050);h.setDebugView('neutral');
      return new Promise<Record<string,number>>(resolve=>requestAnimationFrame(()=>{
        const canvas=document.querySelector<HTMLCanvasElement>('#hero')!,gl=canvas.getContext('webgl2')!;
        const a=new Uint8Array(1200*675*4);gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,a);
        resolve(Object.fromEntries(Object.entries(points).map(([n,[x,y]])=>[n,a[((674-y)*1200+x)*4]])));
      }));
    }
    return {contact,off:await sample(0),on:await sample(1)};
  });
  for(const n of ['fringe','strap','chair','tools'] as const) expect(result.contact[n],n).toBeGreaterThan(5);
  for(const n of ['toolsBody','pageInterior','floating','nose'] as const) expect(result.contact[n],n).toBeLessThan(5);
  for(const n of ['hair','sleeve','book','cup']) {
    expect(result.on[n]).toBeLessThan(result.off[n]);
    expect(result.off[n]-result.on[n]).toBeLessThan(20);
  }
  expect(Math.abs(result.off.face-result.on.face)).toBeLessThanOrEqual(1);
  await page.locator('#shadow').fill('0.35');await page.locator('#shadow').dispatchEvent('input');
  expect(await page.evaluate(()=>window.livingHero.getSettings().shadow)).toBe(.35);
  await mkdir(`${visualRoot}/shadow`,{recursive:true});
  await writeFile(`${visualRoot}/shadow/contact-control.json`,JSON.stringify(result,null,2)+'\n');
});

test('lamp reaches its sill receivers and attenuates toward the front desk', async ({page}) => {
  await page.setViewportSize({width:1200,height:675});await page.goto('/');
  await page.waitForFunction(()=>!!window.livingHero);
  const values=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setTime(1380);h.setDebugView('lamp');
    return new Promise<Record<string,number>>(resolve=>requestAnimationFrame(()=>{
      const c=document.querySelector<HTMLCanvasElement>('#hero')!,gl=c.getContext('webgl2')!;
      const a=new Uint8Array(1200*675*4);gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,a);
      const boxes={sill:[970,341,1000,349],tools:[955,297,981,327],front:[850,595,910,625],
        face:[698,183,749,223],leftPage:[680,530,730,548],rightPage:[855,515,882,533]};
      resolve(Object.fromEntries(Object.entries(boxes).map(([name,[x0,y0,x1,y1]])=>{
        let sum=0;for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++)sum+=a[((674-y)*1200+x)*4]/255;
        return [name,sum/((x1-x0)*(y1-y0))];
      })));
    }));
  });
  expect(values.sill).toBeGreaterThan(.10);expect(values.tools).toBeGreaterThan(.08);
  expect(values.sill).toBeGreaterThan(values.front*1.5);
  expect(values.rightPage).toBeGreaterThan(values.leftPage*1.5);
  expect(values.face).toBeLessThan(.025);
  await mkdir(`${visualRoot}/shadow`,{recursive:true});
  await writeFile(`${visualRoot}/shadow/lamp-location.json`,JSON.stringify(values,null,2)+'\n');
});
