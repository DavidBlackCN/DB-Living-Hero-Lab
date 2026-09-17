import { test, expect } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { visualRoot } from './review-output';
import type { DebugView } from '../../src/engine/renderer';

test('v2 registered surface vectors preserve geometry and add independently oriented volumes', async ({page}) => {
  await page.goto('/?normal=v2');
  await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const im=new Image();im.src='/assets/generated/normal-registered-v2.png';await im.decode();
    const c=document.createElement('canvas');c.width=im.width;c.height=im.height;
    const ctx=c.getContext('2d')!;ctx.drawImage(im,0,0);
    const data=ctx.getImageData(0,0,c.width,c.height).data;
    let maxUnitError=0,minZ=1;
    for(let i=0;i<data.length;i+=4*13){
      const n=[data[i],data[i+1],data[i+2]].map(v=>v/255*2-1);
      maxUnitError=Math.max(maxUnitError,Math.abs(Math.hypot(...n)-1));minZ=Math.min(minZ,n[2]);
    }
    const at=(x:number,y:number)=>Array.from(ctx.getImageData(Math.round(x*3.2),Math.round(y*3.2),1,1).data).slice(0,3);
    return {size:[im.width,im.height],maxUnitError,minZ,wall:at(350,250),glass:at(1100,100),
      face:at(727,195),desk:at(1070,552),laptop:at(1100,638),chair:at(340,360),
      cupLeft:at(968,478),cupRight:at(1023,478),bookLeft:at(719,533),bookRight:at(894,515)};
  });
  expect(result.size).toEqual([3840,2160]);expect(result.maxUnitError).toBeLessThan(.008);
  expect(result.minZ).toBeGreaterThan(.5);
  expect(result.wall).toEqual([128,128,255]);expect(result.glass).toEqual([128,128,255]);
  expect(result.face[2]).toBeGreaterThan(250);
  expect(result.desk[1]).toBeLessThan(80);expect(result.laptop[1]).toBeLessThan(result.desk[1]-8);
  expect(result.chair[0]).toBeLessThan(110);
  expect(result.cupLeft[0]).toBeLessThan(100);expect(result.cupRight[0]).toBeGreaterThan(155);
  expect(result.bookRight[0]-result.bookLeft[0]).toBeGreaterThan(20);
  await mkdir(`${visualRoot}/alignment`,{recursive:true});
  await writeFile(`${visualRoot}/alignment/v2-vectors.json`,JSON.stringify(result,null,2)+'\n');
});

test('each light uses surface orientation, with a protected face and exterior', async ({page})=>{
  await page.setViewportSize({width:1200,height:675});
  await page.goto('/?normal=v2');await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);
    h.setSettings({bloom:0});
    const points={hair:[849,312],sleeve:[815,393],hand:[676,509],book:[793,521],cupLeft:[968,478],cupRight:[1023,478],desk:[1050,505],face:[727,195],glass:[1100,100],bulb:[955,224]};
    async function sample(view:DebugView,normal:number,minutes:number){
      h.setDebugView(view);h.setTime(minutes);h.setSettings({normal});
      return new Promise<Record<string,number>>(resolve=>requestAnimationFrame(()=>{
        const c=document.querySelector<HTMLCanvasElement>('#hero')!,gl=c.getContext('webgl2')!;
        const data=new Uint8Array(c.width*c.height*4);gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
        resolve(Object.fromEntries(Object.entries(points).map(([name,[x,y]])=>[name,data[((674-y)*1200+x)*4]/255])));
      }));
    }
    const projected=[await sample('projected',0,1050),await sample('projected',1,1050)];
    const lamp=[await sample('lamp',0,1380),await sample('lamp',1,1380)];
    const night=await sample('projected',1,1380);
    h.setSettings({lamp:0});const lampOff=await sample('lamp',1,1380);
    return {projected,lamp,night,lampOff};
  });
  await mkdir(`${visualRoot}/alignment`,{recursive:true});
  await writeFile(`${visualRoot}/alignment/light-response.json`,JSON.stringify(result,null,2)+'\n');
  for(const name of ['hair','sleeve','book','cupLeft','desk']) {
    expect(Math.abs(result.projected[1][name]-result.projected[0][name]),`projected ${name} must respond to normals`).toBeGreaterThan(.004);
    expect(Math.abs(result.lamp[1][name]-result.lamp[0][name]),`lamp ${name} must respond to normals`).toBeGreaterThan(.004);
  }
  expect(Math.abs(result.lamp[1].hand-result.lamp[0].hand),'restrained hand orientation').toBeGreaterThan(.002);
  expect(Math.abs(result.lamp[1].face-result.lamp[0].face)).toBeLessThan(.012);
  for(const s of [...result.projected,...result.lamp])expect(s.glass).toBe(0);
  expect(result.lamp[0].bulb).toBe(result.lamp[1].bulb);
  expect(Object.values(result.night).every(v=>v===0)).toBe(true);
  expect(Object.values(result.lampOff).every(v=>v===0)).toBe(true);
  // The source lamp is LEFT of the cup. Normalize away its distance field.
  expect(result.lamp[1].cupLeft/result.lamp[0].cupLeft)
    .toBeGreaterThan(result.lamp[1].cupRight/result.lamp[0].cupRight+.12);
});

test('v2 four-time review with isolated light and grayscale-ready outputs',async({page})=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:1920,height:1080});
  await page.goto('/?normal=v2');await page.waitForFunction(()=>!!window.livingHero);
  await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
  for(const [name,minutes] of [['dawn',360],['noon',720],['dusk',1050],['night',1380]] as const){
    for(const view of ['final','neutral','normal','projected','lamp','exterior','directional'] as DebugView[]){
      await page.evaluate(async({minutes,view})=>{
        const h=window.livingHero;h.setTime(minutes);h.setDebugView(view);
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      },{minutes,view});
      await page.screenshot({path:`${visualRoot}/alignment/v2-${name}-${view}.png`});
    }
  }
  expect(errors).toEqual([]);
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});

test('final grayscale has different spatial structure after removing mean brightness',async({page})=>{
  await page.setViewportSize({width:1200,height:675});await page.goto('/?normal=v2');
  await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);
    const frames:number[][]=[];
    for(const minutes of [360,720,1050]) {
      h.setTime(minutes);h.setDebugView('final');
      frames.push(await new Promise<number[]>(resolve=>requestAnimationFrame(()=>{
        const c=document.querySelector<HTMLCanvasElement>('#hero')!,gl=c.getContext('webgl2')!;
        const data=new Uint8Array(c.width*c.height*4);gl.readPixels(0,0,c.width,c.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
        const a:number[]=[];
        for(let y=63;y<625;y+=4)for(let x=450;x<1063;x+=4){
          const i=((674-y)*1200+x)*4;a.push(data[i]*.2126+data[i+1]*.7152+data[i+2]*.0722);
        }
        resolve(a);
      })));
    }
    return [[0,1],[1,2],[0,2]].map(([a,b])=>{
      const x=frames[a],y=frames[b],mx=x.reduce((s,v)=>s+v,0)/x.length,my=y.reduce((s,v)=>s+v,0)/y.length;
      const delta=x.map((v,i)=>Math.abs(v/mx-y[i]/my));
      return {pair:[a,b],normalizedMAE:delta.reduce((s,v)=>s+v,0)/delta.length,fractionOver5Percent:delta.filter(v=>v>.05).length/delta.length};
    });
  });
  for(const pair of result){expect(pair.normalizedMAE).toBeGreaterThan(.03);expect(pair.fractionOver5Percent).toBeGreaterThan(.18);}
  await mkdir(`${visualRoot}/alignment`,{recursive:true});
  await writeFile(`${visualRoot}/alignment/grayscale-gpu.json`,JSON.stringify(result,null,2)+'\n');
});

test('optional intrinsic correction preserves original, identity regions and exact off behavior',async({page})=>{
  test.setTimeout(90_000);
  await page.setViewportSize({width:1920,height:1080});
  async function ready(url:string){
    await page.goto(url);await page.waitForFunction(()=>!!window.livingHero);
    await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
    await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setTime(1050);h.setSettings({bloom:0});});
  }
  async function frame(view:DebugView,correction:number,minutes=1050){
    await page.evaluate(async({view,correction,minutes})=>{
      const h=window.livingHero;h.setTime(minutes);h.setSettings({correction});h.setDebugView(view);
      await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
    },{view,correction,minutes});
    return page.screenshot();
  }
  await ready('/?normal=v2');const absent=await frame('final',0);
  await ready('/?normal=v2&correction=1');
  expect(await page.evaluate(()=>window.livingHero.correctionAvailable)).toBe(true);
  expect((await frame('final',0)).equals(absent),'optional map at zero must be pixel identical').toBe(true);
  const original=await frame('base',0);
  expect((await frame('base',1)).equals(original),'Base always shows unchanged source').toBe(true);
  expect((await frame('correctedBase',0)).equals(original),'zero gain preserves base exactly').toBe(true);
  const data=await page.evaluate(async()=>{
    const im=new Image();im.src='/assets/generated/intrinsic-correction-v1.png';await im.decode();
    const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const ctx=c.getContext('2d')!;ctx.drawImage(im,0,0);
    const a=ctx.getImageData(0,0,c.width,c.height).data;let min=255,max=0;
    for(let i=0;i<a.length;i+=4){min=Math.min(min,a[i]);max=Math.max(max,a[i]);}
    const at=(x:number,y:number)=>ctx.getImageData(Math.round(x*3.2),Math.round(y*3.2),1,1).data[0];
    return {size:[im.width,im.height],min,max,protected:[[727,195],[675,510],[908,492],[1100,100],[350,250]].map(([x,y])=>at(x,y)),stats:window.livingHero.getStats()};
  });
  expect(data.size).toEqual([3840,2160]);expect(data.min).toBeGreaterThanOrEqual(64);expect(data.max).toBeLessThanOrEqual(167);
  expect(data.min).toBeLessThan(115);expect(data.max).toBeGreaterThan(140);
  expect(data.protected).toEqual([128,128,128,128,128]);expect(data.stats.sourceTextureMiB).toBe(105.15);
  await mkdir(`${visualRoot}/alignment`,{recursive:true});
  for(const [name,minutes] of [['dawn',360],['noon',720],['dusk',1050],['night',1380]] as const){
    const off=await frame('final',0,minutes),on=await frame('final',1,minutes);
    expect(on.equals(off)).toBe(false);
    await writeFile(`${visualRoot}/alignment/correction-${name}-off.png`,off);
    await writeFile(`${visualRoot}/alignment/correction-${name}-on.png`,on);
  }
  await writeFile(`${visualRoot}/alignment/correction-map.png`,await frame('correction',1));
  await writeFile(`${visualRoot}/alignment/corrected-base.png`,await frame('correctedBase',1));
  await writeFile(`${visualRoot}/alignment/original-base.png`,original);
  await writeFile(`${visualRoot}/alignment/correction-checks.json`,JSON.stringify(data,null,2)+'\n');
  expect(await page.locator('#hero').evaluate((c:HTMLCanvasElement)=>c.getContext('webgl2')!.getError())).toBe(0);
});
