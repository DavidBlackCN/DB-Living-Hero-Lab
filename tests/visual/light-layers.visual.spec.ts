import { test, expect, type Page } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { DebugView, Settings } from '../../src/engine/renderer';
import { visualRoot } from './review-output';

const points={wall:[250,300],chair:[350,360],plant:[150,560],
  hair:[849,312],sleeve:[815,393],cupLeft:[968,478],cupRight:[1023,478],
  strap:[609,377],openCloth:[635,377],bulb:[955,224],face:[728,210],glass:[1100,100]};
async function sample(page:Page,view:DebugView,minutes:number,settings:Partial<Settings>={}) {
  return page.evaluate(async({view,minutes,settings,points})=>{
    const h=window.livingHero;h.setTime(minutes);h.setDebugView(view);h.setSettings(settings);
    return new Promise<Record<string,number[]>>(resolve=>requestAnimationFrame(()=>{
      const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
      const a=new Uint8Array(1200*675*4);gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,a);
      resolve(Object.fromEntries(Object.entries(points).map(([name,[x,y]])=>{
        const i=((674-y)*1200+x)*4;return [name,Array.from(a.slice(i,i+4))];
      })));
    }));
  },{view,minutes,settings,points});
}
test.beforeEach(async({page})=>{
  await page.setViewportSize({width:1200,height:675});await page.goto('/');
  await page.waitForFunction(()=>!!window.livingHero);
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setSettings({bloom:0});});
});

test('environment fill follows orientation and contact while lamp emission stays independent',async({page})=>{
  const flat=await sample(page,'ambient',1050,{normal:0});
  const curved=await sample(page,'ambient',1050,{normal:1});
  for(const name of ['hair','sleeve','cupLeft','cupRight'])
    expect(Math.abs(curved[name][0]-flat[name][0]),`${name} sky response`).toBeGreaterThan(1);
  const open=await sample(page,'ambient',1050,{shadow:0});
  const occluded=await sample(page,'ambient',1050,{shadow:1});
  expect(open.strap[0]-occluded.strap[0]).toBeGreaterThan(open.openCloth[0]-occluded.openCloth[0]+3);
  const lampOpen=await sample(page,'lamp',1380,{shadow:0});
  const lampOccluded=await sample(page,'lamp',1380,{shadow:1});
  expect(lampOpen.bulb).toEqual(lampOccluded.bulb);
  expect(lampOpen.strap[0]).toBeGreaterThanOrEqual(lampOccluded.strap[0]);
  const noLight=await sample(page,'shadow',1380,{ambient:0,sun:0,lamp:0});
  for(const value of Object.values(noLight))expect(value).toEqual([0,0,0,255]);
  await mkdir(`${visualRoot}/layers`,{recursive:true});
  await writeFile(`${visualRoot}/layers/source-independence.json`,JSON.stringify({flat,curved,open,occluded,lampOpen,lampOccluded},null,2));
});

test('whole-room fill changes color and form layers stay independent of exposure',async({page})=>{
  const dawn=await sample(page,'ambient',360),dusk=await sample(page,'ambient',1050);
  for(const name of ['wall','chair','plant']) {
    expect(dawn[name][2]/dawn[name][0]).toBeGreaterThan(dusk[name][2]/dusk[name][0]+.05);
    expect(dawn[name]).not.toEqual(dusk[name]);
  }
  const form=await sample(page,'form',1050);
  expect(await sample(page,'form',1050,{exposure:1})).toEqual(form);
  expect(Math.abs(form.cupLeft[0]-form.cupRight[0])).toBeGreaterThan(30);
});

test('capture incident light layers at four review times',async({page})=>{
  test.setTimeout(60_000);
  await page.setViewportSize({width:1920,height:1080});
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>window.livingHero.setSettings({bloom:.22}));
  for(const [name,minutes] of [['0600',360],['1200',720],['1730',1050],['2300',1380]] as const){
    for(const view of ['ambient','form','contact','directional','shadow','lamp','neutral','final'] as DebugView[]){
      await page.evaluate(async({minutes,view})=>{
        window.livingHero.setTime(minutes);window.livingHero.setDebugView(view);
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      },{minutes,view});
      await page.screenshot({path:`${visualRoot}/layers/${name}-${view}.png`});
    }
  }
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});
