import {test,expect} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
import type {DebugView} from '../../src/engine/renderer';
import {visualRoot} from './review-output';

test('screen-right hand uses a feathered skin mask and broad normal response',async({page})=>{
  test.setTimeout(60_000);
  await page.setViewportSize({width:1920,height:1080});
  await page.goto('/?normal=v2');await page.waitForFunction(()=>!!window.livingHero);
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
  const directory=`${visualRoot}/hand-safe`;await mkdir(directory,{recursive:true});
  const result=await page.evaluate(async()=>{
    async function load(src:string){
      const im=new Image();im.src=src;await im.decode();
      const c=document.createElement('canvas');c.width=1200;c.height=675;
      const x=c.getContext('2d')!;x.drawImage(im,0,0,1200,675);return x;
    }
    const mask=await load('/assets/generated/character-masks.svg');
    const contact=await load('/assets/generated/light-shaping.svg');
    const points=[[890,480],[905,490],[921,500]];
    return {
      mask:points.map(([x,y])=>Array.from(mask.getImageData(x,y,1,1).data).slice(0,3)),
      contact:points.map(([x,y])=>contact.getImageData(x,y,1,1).data[2]),
    };
  });
  for(const rgb of result.mask)for(const channel of rgb)expect(channel).toBeGreaterThan(240);
  for(const contact of result.contact)expect(contact).toBeLessThan(5);

  for(const [name,minutes] of [['1200',720],['1730',1050],['2300',1380]] as const){
    const views:DebugView[]=minutes===1380
      ? ['final','normal','form','shadow','contact','lamp','masks'] : ['final'];
    for(const view of views){
      await page.evaluate(async({minutes,view})=>{
        window.livingHero.setTime(minutes);window.livingHero.setDebugView(view);
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      },{minutes,view});
      await page.screenshot({path:`${directory}/${name}-${view}.png`});
      if(view==='final')await page.screenshot({
        path:`${directory}/${name}-hand.png`,clip:{x:1280,y:680,width:270,height:180}});
    }
  }
  await writeFile(`${directory}/semantic-probes.json`,JSON.stringify(result,null,2)+'\n');
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});
