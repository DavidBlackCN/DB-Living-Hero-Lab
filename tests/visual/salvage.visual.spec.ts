import {test,expect} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
import {visualRoot} from './review-output';

test('lamp fields separate near source from compact desk and protected front',async({page})=>{
  await page.setViewportSize({width:1200,height:675});await page.goto('/');
  await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);
    h.setSettings({bloom:0});h.setTime(1380);
    const boxes={tools:[955,297,981,327],frame:[1040,307,1060,343],
      nearSill:[966,359,995,368],farSill:[1076,385,1090,392],
      face:[704,182,751,224],chest:[650,320,715,405],hair:[854,310,889,383],
      sleeve:[808,373,838,450],rightPage:[855,515,882,533],cup:[970,460,1025,498],
      leftPage:[680,530,730,548],front:[850,595,910,625],glass:[1080,80,1140,180]};
    async function sample(view:'lamp'|'lampFields'|'contact'|'projected',time=1380,shadow=.65){
      h.setTime(time);h.setSettings({shadow});h.setDebugView(view);
      return new Promise<Record<string,number[]>>(resolve=>requestAnimationFrame(()=>{
        const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
        const a=new Uint8Array(1200*675*4);gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,a);
        resolve(Object.fromEntries(Object.entries(boxes).map(([n,[x0,y0,x1,y1]])=>{
          const sum=[0,0,0];for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++)
            for(let c=0;c<3;c++)sum[c]+=a[((674-y)*1200+x)*4+c]/255;
          return [n,sum.map(v=>v/((x1-x0)*(y1-y0)))];
        })));
      }));
    }
    return {lamp:await sample('lamp'),fields:await sample('lampFields'),
      dawnContact:await sample('contact',360),nightContact:await sample('contact'),
      blocked:await sample('projected',1050,1),open:await sample('projected',1050,0)};
  });
  await mkdir(`${visualRoot}/salvage`,{recursive:true});
  await writeFile(`${visualRoot}/salvage/probes.json`,JSON.stringify(result,null,2));
  const {lamp,fields}=result;
  expect(lamp.tools[0]).toBeGreaterThan(lamp.cup[0]*.8);
  expect(lamp.nearSill[0]).toBeGreaterThan(lamp.front[0]*3);
  expect(lamp.rightPage[0]).toBeGreaterThan(.25);
  expect(lamp.leftPage[0]).toBeLessThan(lamp.rightPage[0]*.45);
  expect(lamp.front[0]).toBeLessThan(.04);
  expect(lamp.face[0]).toBeLessThan(.015);expect(lamp.chest[0]).toBeLessThan(.025);
  expect(fields.tools[0]).toBeGreaterThan(.3);expect(fields.tools[1]).toBe(0);
  expect(fields.cup[1]).toBeGreaterThan(.4);expect(fields.cup[0]).toBe(0);
  expect(fields.hair[2]).toBeGreaterThan(.1);expect(fields.glass).toEqual([0,0,0]);
  expect(result.dawnContact).toEqual(result.nightContact);
  expect(result.blocked.chest[0]).toBeLessThan(result.open.chest[0]*.9);
  expect(result.blocked.rightPage[0]).toBeGreaterThan(result.open.rightPage[0]*.90);
});

test('lamp-field and optional compensation review',async({page})=>{
  await page.setViewportSize({width:1920,height:1080});await page.goto('/?correction=1');
  await page.waitForFunction(()=>!!window.livingHero);
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setTime(1380);});
  await mkdir(`${visualRoot}/salvage`,{recursive:true});
  for(const value of [0,.25]){
    await page.evaluate(async(value)=>{const h=window.livingHero;h.setSettings({correction:value});h.setDebugView('final');await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));},value);
    await page.screenshot({path:`${visualRoot}/salvage/2300-correction-${value}.png`});
  }
  await page.evaluate(async()=>{window.livingHero.setSettings({correction:0});window.livingHero.setDebugView('lampFields');await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
  await page.screenshot({path:`${visualRoot}/salvage/2300-fields.png`});
});
