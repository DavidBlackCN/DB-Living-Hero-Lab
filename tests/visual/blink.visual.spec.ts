import { test, expect, type Page } from '@playwright/test';
import { mkdir } from 'node:fs/promises';
import { visualRoot } from './review-output';

const directory = `${visualRoot}/blink`;
async function setup(page: Page) {
  await page.setViewportSize({ width: 1200, height: 675 });
  await page.goto('/');
  await page.waitForFunction(() => !!window.livingHero);
  await page.evaluate(() => {
    const h=window.livingHero; h.setReducedMotion(true); h.setSteam(false);
    const canvas=document.querySelector<HTMLCanvasElement>('#hero')!;
    const gl=canvas.getContext('webgl2')!;
    const draw=gl.drawArrays.bind(gl);
    // Read synchronously after the final draw: preserveDrawingBuffer is false.
    gl.drawArrays=(...args)=>{
      draw(...args);
      if(gl.getParameter(gl.DRAW_FRAMEBUFFER_BINDING)!==null)return;
      const pixels=new Uint8Array(canvas.width*canvas.height*4);
      gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
      (window as typeof window & {blinkPixels:Uint8Array}).blinkPixels=pixels;
      if(gl.getError()!==gl.NO_ERROR)throw new Error('WebGL error');
    };
  });
  await page.clock.install();
  await page.clock.pauseAt(new Date(Date.now()+1000));
  await mkdir(directory,{recursive:true});
}

async function capture(page: Page, name: string) {
  await page.evaluate(() => {
    window.livingHero.setDebugView(window.livingHero.getState().view);
  });
  await page.clock.runFor(20);
  await page.evaluate(()=>{
    const w=window as typeof window & {blinkPixels:Uint8Array;blinkFrames?:Uint8Array[]};
    (w.blinkFrames??=[]).push(w.blinkPixels);
  });
  await page.locator('#hero').screenshot({path:`${directory}/${name}.png`});
}

for(const [name,minutes] of [['dawn',360],['noon',720],['dusk',1050],['night',1380]] as const) {
  test(`registered blink and unchanged surroundings: ${name}`,async({page})=>{
    await setup(page);
    await page.evaluate(m=>window.livingHero.setTime(m),minutes);
    await capture(page,`${name}-open`);
    await page.evaluate(()=>{window.livingHero.setReducedMotion(false);window.livingHero.triggerBlink();});
    await capture(page,`${name}-half`);
    expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('half');
    await page.clock.runFor(40);
    await capture(page,`${name}-closed`);
    expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
    await page.clock.runFor(120);
    await capture(page,`${name}-returned`);
    const diff=await page.evaluate(()=>{
      const [open,half,closed,returned]=(window as typeof window & {blinkFrames:Uint8Array[]}).blinkFrames;
      const counts=[half,closed,returned].map(frame=>{
        let inside=0,outside=0;
        for(let y=0;y<675;y++)for(let x=0;x<1200;x++) {
          const i=((674-y)*1200+x)*4;
          if(frame[i]!==open[i]||frame[i+1]!==open[i+1]||frame[i+2]!==open[i+2]) {
            if(x>=605&&x<=826&&y>=121&&y<=269)inside++;else outside++;
          }
        }
        return {inside,outside};
      });
      return counts;
    });
    expect(diff[0].inside).toBeGreaterThan(500);
    expect(diff[1].inside).toBeGreaterThan(500);
    expect(diff.map(d=>d.outside)).toEqual([0,0,0]);
    expect(diff[2].inside).toBe(0);
  });
}

test('automatic blink, UI trigger, motion gates, visibility pause and destruction',async({page})=>{
  await setup(page);
  await expect(page.locator('#trigger-blink')).toBeDisabled();
  expect(await page.evaluate(()=>window.livingHero.triggerBlink())).toBe(false);
  await page.evaluate(()=>window.livingHero.setReducedMotion(false));
  await page.clock.runFor(20);
  await page.locator('#trigger-blink').click();
  await page.clock.runFor(60);
  expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
  await page.evaluate(()=>{
    Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await page.clock.runFor(10000);
  expect(await page.evaluate(()=>window.livingHero.triggerBlink())).toBe(false);
  expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
  await page.evaluate(()=>{
    Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});
    document.dispatchEvent(new Event('visibilitychange'));
  });
  await page.clock.runFor(20);
  expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
  await page.clock.runFor(160);
  for(const gate of ['setBlink','setAnimation','setReducedMotion'] as const) {
    const result=await page.evaluate(g=>{
      const h=window.livingHero;h.triggerBlink();h[g](g==='setReducedMotion');
      return {phase:h.getState().blinkPhase,trigger:h.triggerBlink()};
    },gate);
    expect(result).toEqual({phase:'open',trigger:false});
    await page.clock.runFor(6000);
    expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('open');
    await page.evaluate(g=>window.livingHero[g](g!=='setReducedMotion'),gate);
  }
  await page.evaluate(()=>{
    const phases:string[]=[];
    (window as typeof window & {blinkObserved:string[]}).blinkObserved=phases;
    function sample(){phases.push(window.livingHero.getState().blinkPhase);requestAnimationFrame(sample);}
    requestAnimationFrame(sample);
  });
  await page.clock.runFor(5800);
  expect(await page.evaluate(()=>(window as typeof window & {blinkObserved:string[]}).blinkObserved)).toContain('closed');
  await page.evaluate(()=>window.livingHero.destroy());
  await page.clock.runFor(6000);
  expect(await page.evaluate(()=>window.livingHero.triggerBlink())).toBe(false);
  expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('open');
});

test('blink shares lighting and preserves source/technical diagnostics',async({page})=>{
  await setup(page);
  for(const view of ['base','normal','scene','masks','lighting','bloom'] as const) {
    await page.evaluate(v=>{const h=window.livingHero;h.setReducedMotion(true);h.setTime(1380);h.setDebugView(v);},view);
    await capture(page,`diagnostic-${view}-open`);
    await page.evaluate(()=>{window.livingHero.setReducedMotion(false);window.livingHero.triggerBlink();});
    await page.clock.runFor(45);
    await capture(page,`diagnostic-${view}-closed`);
    expect(await page.evaluate(()=>{
      const frames=(window as typeof window & {blinkFrames:Uint8Array[]}).blinkFrames;
      return frames.at(-1)!.every((v,i)=>v===frames.at(-2)![i]);
    }),view).toBe(true);
  }
  await page.evaluate(()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setDebugView('final');
    h.setSettings({ambient:0,sun:0,lamp:0,bloom:0});
  });
  await page.clock.runFor(20);
  await page.evaluate(()=>{window.livingHero.setReducedMotion(false);window.livingHero.triggerBlink();});
  await page.clock.runFor(45);
  await capture(page,'night-unlit-closed');
  expect(await page.evaluate(()=>(window as typeof window & {blinkFrames:Uint8Array[]}).blinkFrames.at(-1)!.every((v,i)=>i%4===3||v===0))).toBe(true);
});

test('system reduced-motion changes reset Blink and narrow view retains composition',async({page})=>{
  await setup(page);
  await page.setViewportSize({width:390,height:844});
  await page.emulateMedia({reducedMotion:'no-preference'});
  await expect.poll(async()=>{
    await page.clock.runFor(20);
    return page.evaluate(()=>window.livingHero.getState().reducedMotion);
  }).toBe(false);
  await page.evaluate(()=>window.livingHero.triggerBlink());
  await page.clock.runFor(45);
  await capture(page,'narrow-closed');
  expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
  expect(await page.evaluate(()=>{
    const w=window as typeof window & {blinkPixels:Uint8Array};
    const stats=window.livingHero.getStats();
    return {width:stats.canvasWidth,height:stats.canvasHeight,nonblank:w.blinkPixels.some((v,i)=>i%4!==3&&v>100)};
  })).toEqual({width:390,height:844,nonblank:true});
  await page.emulateMedia({reducedMotion:'reduce'});
  await expect.poll(async()=>{
    await page.clock.runFor(20);
    return page.evaluate(()=>window.livingHero.getState().reducedMotion);
  }).toBe(true);
  expect(await page.evaluate(()=>({phase:window.livingHero.getState().blinkPhase,trigger:window.livingHero.triggerBlink()}))).toEqual({phase:'open',trigger:false});
  await page.clock.runFor(20);
  await expect(page.locator('#trigger-blink')).toBeDisabled();
});
