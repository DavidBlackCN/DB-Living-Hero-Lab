import {test,expect} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
import {visualRoot} from './review-output';

test('exposed forehead shares face safety without protecting brown bangs or adding light',async({page})=>{
  await page.setViewportSize({width:1200,height:675});await page.goto('/');
  await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setSettings({bloom:0});
    const points={forehead:[710,140],rightForehead:[770,168],bangs:[738,140],cheek:[727,211],hat:[740,20],desk:[1070,570]};
    async function read(view:'masks'|'normal'|'final'){
      h.setDebugView(view);
      return new Promise<Record<string,number[]>>(resolve=>requestAnimationFrame(()=>{
        const g=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
        const a=new Uint8Array(1200*675*4);g.readPixels(0,0,1200,675,g.RGBA,g.UNSIGNED_BYTE,a);
        resolve(Object.fromEntries(Object.entries(points).map(([name,[x,y]])=>[name,Array.from(a.slice(((674-y)*1200+x)*4,((674-y)*1200+x)*4+3))])));
      }));
    }
    const masks=await read('masks'),normal=await read('normal');
    const night=[];
    for(const time of [360,720,1050,1380]){
      h.setTime(time);h.setSettings({ambient:0,sun:0,lamp:0});night.push(await read('final'));
    }
    return {masks,normal,unlit:night};
  });
  await mkdir(`${visualRoot}/face`,{recursive:true});
  await writeFile(`${visualRoot}/face/probes.json`,JSON.stringify(result,null,2));
  expect(result.masks.forehead[0]).toBeGreaterThan(180);
  expect(result.masks.rightForehead[0]).toBeGreaterThan(180);
  expect(result.masks.bangs[0]).toBeLessThan(25);
  expect(result.masks.bangs[1]).toBeGreaterThan(230);
  expect(result.masks.cheek[0]).toBe(255);
  expect(result.masks.hat[0]).toBe(0);expect(result.masks.desk[0]).toBe(0);
  expect(result.normal.forehead[2]).toBeGreaterThan(245);
  for(const frame of result.unlit)for(const v of Object.values(frame))expect(v).toEqual([0,0,0]);
});
