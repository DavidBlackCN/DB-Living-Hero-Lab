import { test, expect } from '@playwright/test';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import type { DebugView } from '../../src/engine/renderer';
import { visualRoot } from './review-output';

const times=[['0600',360],['0700',420],['0800',480],['1200',720],['1730',1050],['2300',1380]] as const;
const views:DebugView[]=['final','neutral','directional','projected','lamp','exterior'];

test('convergence: same-exposure morning sequence and protected noon dusk night',async({page})=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:1920,height:1080});
  await page.goto('/');await page.waitForFunction(()=>!!window.livingHero);
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
  const settings=await page.evaluate(()=>window.livingHero.getSettings());
  expect(settings.exposure).toBe(0);expect(settings.correction).toBe(0);
  const directory=`${visualRoot}/convergence`;await mkdir(directory,{recursive:true});
  const protectedFrames:string[]=[];
  for(const [name,minutes] of times)for(const view of views){
    await page.evaluate(async({minutes,view})=>{
      const h=window.livingHero;h.setTime(minutes);h.setDebugView(view);
      await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
    },{minutes,view});
    const filename=`${name}-${view}.png`;
    const buffer=await page.screenshot({path:`${directory}/${filename}`});
    if(process.env.CONVERGENCE_BASELINE && minutes>=720){
      const before=await readFile(`${process.env.CONVERGENCE_BASELINE}/${filename}`);
      expect(buffer.equals(before),`${name} ${view}: preserve accepted baseline exactly`).toBe(true);
      protectedFrames.push(filename);
    }
  }
  await writeFile(`${directory}/capture.json`,JSON.stringify({settings,viewport:[1920,1080],dpr:1,
    times,protectedFrames,pageErrors:errors,webglError:await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())},null,2)+'\n');
  expect(errors).toEqual([]);
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});

test('convergence: native 4K normal and night material inspection at DPR 1.5',async({browser})=>{
  test.setTimeout(90_000);
  const context=await browser.newContext({viewport:{width:2560,height:1440},deviceScaleFactor:1.5,reducedMotion:'reduce'});
  try{
    const page=await context.newPage();await page.goto('/');await page.waitForFunction(()=>!!window.livingHero);
    await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
    await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setTime(1380);});
    expect(await page.evaluate(()=>window.livingHero.getStats().canvasWidth)).toBe(3840);
    for(const view of ['base','normal','final','lamp','exterior'] as DebugView[]){
      await page.evaluate(async(view)=>{window.livingHero.setDebugView(view);await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));},view);
      await page.screenshot({path:`${visualRoot}/convergence/native-${view}.png`});
    }
    expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
  }finally{await context.close();}
});
