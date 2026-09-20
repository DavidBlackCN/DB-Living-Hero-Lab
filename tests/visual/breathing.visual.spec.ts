import {test,expect,type Page} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import ts from 'typescript';
import {visualRoot} from './review-output';
import type {DebugView} from '../../src/engine/renderer';

const out=`${visualRoot}/breathing`;
// Immutable accepted pre-experiment shader, not a second hand-maintained baseline.
const accepted=execFileSync('git',['show','e29c635:src/engine/shaders.ts'],{encoding:'utf8'});
const baseline=ts.transpileModule(accepted,{compilerOptions:{module:ts.ModuleKind.ESNext}}).outputText
  .replaceAll("'./light-layers'","'/src/engine/light-layers.ts'")
  .replaceAll("'./lamp-fields'","'/src/engine/lamp-fields.ts'");

async function setup(page:Page,old=false){
  await page.setViewportSize({width:1200,height:675});
  if(old)await page.route('**/src/engine/shaders.ts',route=>route.fulfill({contentType:'application/javascript',body:baseline}));
  await page.goto('/?correction=1');await page.waitForFunction(()=>!!window.livingHero);
  await page.evaluate(()=>{
    const h=window.livingHero;h.setAnimation(false);h.setSteam(false);h.setBlink(false);h.setSettings({correction:0});
    document.querySelector<HTMLDetailsElement>('#debug details')!.open=false;
    const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
    const draw=gl.drawArrays.bind(gl);
    gl.drawArrays=(...args)=>{
      draw(...args);if(gl.getParameter(gl.DRAW_FRAMEBUFFER_BINDING)!==null)return;
      const p=new Uint8Array(gl.drawingBufferWidth*gl.drawingBufferHeight*4);
      gl.readPixels(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight,gl.RGBA,gl.UNSIGNED_BYTE,p);
      (window as typeof window & {breathingPixels:Uint8Array}).breathingPixels=p;
      if(gl.getError())throw Error('WebGL error');
    };
  });
  await page.clock.install();await page.clock.pauseAt(new Date(Date.now()+1000));
  await mkdir(out,{recursive:true});
}
async function frame(page:Page,view:DebugView='final',path?:string){
  await page.evaluate(v=>window.livingHero.setDebugView(v),view);await page.clock.runFor(20);
  if(path)await page.locator('#hero').screenshot({path:`${out}/${path}.png`});
  return page.evaluate(async()=>{
    const p=(window as typeof window & {breathingPixels:Uint8Array}).breathingPixels;
    return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',p))).map(v=>v.toString(16).padStart(2,'0')).join('');
  });
}
async function remember(page:Page){await page.evaluate(()=>{
  const w=window as typeof window & {breathingPixels:Uint8Array;breathingOff:Uint8Array};w.breathingOff=w.breathingPixels;
});}
async function difference(page:Page){return page.evaluate(()=>{
  const w=window as typeof window & {breathingPixels:Uint8Array;breathingOff:Uint8Array};
  let inside=0,outside=0,max=0;
  for(let y=0;y<675;y++)for(let x=0;x<1200;x++){
    const i=((674-y)*1200+x)*4;
    const d=Math.max(...[0,1,2].map(c=>Math.abs(w.breathingPixels[i+c]-w.breathingOff[i+c])));
    if(d){if(x>=645&&((x-681)/73)**2+((y-380)/61)**2<=1)inside++;else outside++;max=Math.max(max,d);}
  }
  return {inside,outside,max};
});}

test('OFF is pixel-identical to accepted shader at four times and all existing views',async({page,context})=>{
  test.setTimeout(120000);
  const reference=await context.newPage();await setup(reference,true);await setup(page);
  expect(await page.evaluate(()=>window.livingHero.getState().breathing)).toBe(false);
  const views:DebugView[]=['final','base','normal','masks','lighting','scene','overlay','bright','bloom','neutral','projected','exterior','shadow','lamp','directional','correction','correctedBase','ambient','form','contact','lampFields'];
  const hashes:Record<string,string>={};
  for(const time of [360,720,1050,1380])for(const view of views){
    for(const p of [reference,page])await p.evaluate(t=>window.livingHero.setTime(t),time);
    const a=await frame(reference,view),b=await frame(page,view);
    expect(b,`${time} ${view}`).toBe(a);hashes[`${time}-${view}`]=b;
  }
  // Freeze Steam at the draw boundary, after the renderer's cached uploads.
  for(const p of [reference,page])await p.evaluate(()=>{
    const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
    const draw=gl.drawArrays.bind(gl);
    gl.drawArrays=(...args)=>{
      const program=gl.getParameter(gl.CURRENT_PROGRAM) as WebGLProgram;
      gl.uniform1f(gl.getUniformLocation(program,'uMotionTime'),2.5);draw(...args);
    };
    window.livingHero.setReducedMotion(false);window.livingHero.setAnimation(true);window.livingHero.setSteam(true);window.livingHero.setBlink(true);window.livingHero.triggerBlink();
  });
  expect(await frame(page)).toBe(await frame(reference));
  for(const p of [reference,page])await p.clock.runFor(40);
  expect(await frame(page)).toBe(await frame(reference));
  await writeFile(`${out}/off-baseline-hashes.json`,JSON.stringify(hashes,null,2));
  await reference.close();
});

for(const [name,time] of [['dawn',360],['noon',720],['dusk',1050],['night',1380]] as const){
  test(`bounded registered garment motion: ${name}`,async({page})=>{
    await setup(page);await page.evaluate(t=>{window.livingHero.setTime(t);window.livingHero.setSettings({bloom:0});},time);
    const off=await frame(page,'final',`${name}-off`);await remember(page);
    await page.screenshot({path:`${out}/${name}-torso-off.png`,clip:{x:580,y:280,width:220,height:180}});
    const stats=await page.evaluate(()=>window.livingHero.getStats());
    await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(false);h.setAnimation(true);h.setBreathing(true);});
    await page.clock.runFor(2700);await frame(page,'final',`${name}-on-peak`);
    const diff=await difference(page);expect(diff.inside).toBeGreaterThan(500);expect(diff.outside).toBe(0);
    expect(await page.evaluate(()=>window.livingHero.getStats())).toEqual(stats);
    await page.screenshot({path:`${out}/${name}-torso-peak.png`,clip:{x:580,y:280,width:220,height:180}});
    await frame(page,'breathingWeight',`${name}-weight`);
    await page.evaluate(()=>window.livingHero.setBreathing(false));
    expect(await frame(page)).toBe(off);
    await writeFile(`${out}/${name}-difference.json`,JSON.stringify(diff));
  });
}

test('motion gates, hidden clock, controls and destroy',async({page})=>{
  await setup(page);const off=await frame(page);
  await page.evaluate(()=>{const h=window.livingHero;h.setBreathing(true);h.setAnimation(true);h.setReducedMotion(false);});
  await page.clock.runFor(1000);
  const phase=await page.evaluate(()=>window.livingHero.getState().breathingPhase);
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'));});
  await page.clock.runFor(30000);expect(await page.evaluate(()=>window.livingHero.getState().breathingPhase)).toBe(phase);
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'));});
  await page.clock.runFor(17);expect(await page.evaluate(()=>window.livingHero.getState().breathingPhase)).toBeCloseTo(phase,2);
  for(const gate of ['setReducedMotion','setAnimation'] as const){
    await page.evaluate(g=>window.livingHero[g](g==='setReducedMotion'),gate);
    expect(await frame(page)).toBe(off);
    await page.clock.runFor(6000);expect(await page.evaluate(()=>window.livingHero.getState().breathingPhase)).toBe(0);
    await page.evaluate(g=>window.livingHero[g](g!=='setReducedMotion'),gate);await page.clock.runFor(1000);
  }
  await page.evaluate(()=>{window.livingHero.setSettings({breathingStrength:99,breathingCycle:-2});});
  expect(await page.evaluate(()=>{const s=window.livingHero.getSettings();return [s.breathingStrength,s.breathingCycle];})).toEqual([3,5]);
  await page.evaluate(()=>window.livingHero.setSettings({breathingStrength:0}));expect(await frame(page)).toBe(off);
  await page.evaluate(()=>window.livingHero.destroy());await page.clock.runFor(6000);
  expect(await page.evaluate(()=>window.livingHero.getState().breathingPhase)).toBe(0);
});

test('Blink crop remains identical while breathing runs',async({page})=>{
  await setup(page);
  await page.evaluate(()=>{const h=window.livingHero;h.setAnimation(true);h.setReducedMotion(false);h.setBlink(true);});
  const crops:number[][]=[];
  for(const enabled of [false,true]){
    await page.evaluate(e=>{const h=window.livingHero;h.setBreathing(e);h.setBlink(true);h.triggerBlink();},enabled);
    await page.clock.runFor(50);await frame(page);
    expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('closed');
    crops.push(await page.evaluate(()=>{
      const p=(window as typeof window & {breathingPixels:Uint8Array}).breathingPixels;const a:number[]=[];
      for(let y=121;y<270;y++)for(let x=605;x<827;x++){const i=((674-y)*1200+x)*4;a.push(p[i],p[i+1],p[i+2]);}return a;
    }));
    await page.clock.runFor(160);expect(await page.evaluate(()=>window.livingHero.getState().blinkPhase)).toBe('open');
  }
  expect(crops[1]).toEqual(crops[0]);
});

test('native registration, protected closeups, Bloom and debug controls',async({page})=>{
  test.setTimeout(60000);
  await setup(page);
  await page.setViewportSize({width:1920,height:1080});
  await page.evaluate(()=>{const h=window.livingHero;h.setTime(1050);h.setSettings({bloom:.22});});
  await frame(page,'final','large-bloom-off');await remember(page);
  const regions={face:{x:1010,y:165,width:300,height:245},neck:{x:1020,y:375,width:220,height:120},
    torso:{x:945,y:490,width:310,height:220},handsBook:{x:900,y:720,width:650,height:220},
    hairLeft:{x:690,y:340,width:270,height:430},hairRight:{x:1250,y:270,width:280,height:480}};
  for(const [name,clip] of Object.entries(regions))await page.screenshot({path:`${out}/large-${name}-off.png`,clip});
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(false);h.setAnimation(true);h.setBreathing(true);});
  await page.clock.runFor(2700);await frame(page,'final','large-bloom-on');
  for(const [name,clip] of Object.entries(regions))await page.screenshot({path:`${out}/large-${name}-on.png`,clip});
  const protectedChanged=await page.evaluate(rects=>{
    const w=window as typeof window & {breathingPixels:Uint8Array;breathingOff:Uint8Array};
    return rects.map(r=>{let changed=0;for(let y=r.y;y<r.y+r.height;y++)for(let x=r.x;x<r.x+r.width;x++){
      const i=((1079-y)*1920+x)*4;
      if([0,1,2].some(c=>w.breathingPixels[i+c]!==w.breathingOff[i+c]))changed++;
    }return changed;});
  },Object.entries(regions).filter(([name])=>name!=='torso').map(([,r])=>r));
  expect(protectedChanged).toEqual([0,0,0,0,0]);
  // Exact normalization/registration at a fixed peak, using original shader lookups.
  const normalResult=await page.evaluate(async()=>{
    const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
    const program=gl.getParameter(gl.CURRENT_PROGRAM) as WebGLProgram;
    const source=Array.from(gl.getAttachedShaders(program)!).map(s=>gl.getShaderSource(s)!).find(s=>s.includes('breathingWeight'))!;
    return {normal:source.includes('texture(uNormal,materialUV)'),mask:source.includes('texture(uMask,materialUV)'),
      correction:source.includes('texture(uCorrectionMap,materialUV)'),contact:source.includes('texture(uLightShaping,materialUV).b'),
      world:source.includes('texture(uSceneMask,uv)')&&source.includes('lampFieldsAt(uv,')};
  });
  expect(Object.values(normalResult).every(Boolean)).toBe(true);
  await page.locator('#debug summary').click();
  await page.locator('#breathing').uncheck();await page.clock.runFor(20);
  expect(await page.evaluate(()=>window.livingHero.getState().breathing)).toBe(false);
  await page.locator('#breathingStrength').fill('1.5');await page.locator('#breathingCycle').fill('6');
  expect(await page.evaluate(()=>{const s=window.livingHero.getSettings();return [s.breathingStrength,s.breathingCycle];})).toEqual([1.5,6]);
});

test('checkbox starts real-time motion and reports disabled conditions',async({page})=>{
  await page.setViewportSize({width:1440,height:900});
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.goto('/');await page.waitForFunction(()=>!!window.livingHero);
  await page.locator('#blink').uncheck();await page.locator('#steam').uncheck();
  await page.locator('#breathing').check();
  await expect(page.locator('#breathing-status')).toHaveText('Running');
  await expect.poll(()=>page.evaluate(()=>window.livingHero.getState().breathingDisplacement),{timeout:5000}).toBeGreaterThan(1.5);
  await expect(page.locator('#breathing-displacement')).not.toHaveText('0.00 px');
  const sample=await page.evaluate(()=>{
    const h=window.livingHero,gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
    const program=gl.getParameter(gl.CURRENT_PROGRAM) as WebGLProgram;
    return {phase:h.getState().breathingPhase,amount:gl.getUniform(program,gl.getUniformLocation(program,'uBreathingAmount')),
      screenPeak:h.getSettings().breathingStrength*Math.min(innerWidth/3840,innerHeight/2160)};
  });
  expect(sample.amount).toBeGreaterThan(1.5);expect(sample.screenPeak).toBe(.75);
  await page.locator('#refinement').uncheck();
  await expect(page.locator('#breathing-status')).toHaveText('Refinement off');
  await expect(page.locator('#breathing-displacement')).toHaveText('0.00 px');
  await page.locator('#refinement').check();await page.locator('#reduced').check();
  await expect(page.locator('#breathing-status')).toHaveText('Reduced motion');
  await page.locator('#reduced').uncheck();await page.locator('#animation').uncheck();
  await expect(page.locator('#breathing-status')).toHaveText('Animation off');
  await page.locator('#animation').check();await page.locator('#breathingStrength').fill('0');
  await expect(page.locator('#breathing-status')).toHaveText('Strength zero');
  await page.locator('#breathing').uncheck();await expect(page.locator('#breathing-status')).toHaveText('Off');
});
