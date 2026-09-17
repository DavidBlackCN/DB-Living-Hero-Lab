import { test, expect } from '@playwright/test';
import { visualRoot } from './review-output';
import { mkdir, writeFile } from 'node:fs/promises';

test('hand receiving light is continuous and book shadows stay at contact', async ({page})=>{
  await page.setViewportSize({width:1200,height:675});
  await page.goto('/');
  await page.waitForFunction(()=>!!window.livingHero);
  const regions=await page.evaluate(async()=>{
    async function load(src:string) {
      const image=new Image();image.src=src;await image.decode();
      const canvas=document.createElement('canvas');canvas.width=1200;canvas.height=675;
      const ctx=canvas.getContext('2d')!;ctx.drawImage(image,0,0,1200,675);
      return (x:number,y:number)=>Array.from(ctx.getImageData(x,y,1,1).data).slice(0,3);
    }
    const scene=await load('/assets/generated/scene-masks.svg');
    const shape=await load('/assets/generated/light-shaping.svg');
    const character=await load('/assets/generated/character-masks.svg');
    // Independently located on the artwork: wrist/palm/knuckle, sleeve,
    // page interior, obsolete floating stripe, and the real lower book edge.
    return {
      skin:[[595,508],[615,510],[650,485]].map(([x,y])=>({p:[x,y],scene:scene(x,y),character:character(x,y)})),
      sleeve:scene(830,470),
      page:shape(740,525),floating:shape(770,575),contact:shape(720,581),
    };
  });
  for(const point of regions.skin) {
    expect(point.scene[1],`hand receives light at ${point.p}`).toBeGreaterThan(245);
    expect(point.character[2],`skin is not cloth at ${point.p}`).toBeLessThan(5);
  }
  expect(regions.sleeve[1],'desk does not continue through sleeve').toBeLessThan(5);
  expect(regions.page[2],'contact must not cover page').toBe(0);
  expect(regions.floating[2],'old floating book shadow is gone').toBeLessThan(5);
  expect(regions.contact[2],'contact stays at real book edge').toBeGreaterThan(15);

  const measurements=[];
  for(const normal of ['low-frequency','registered','v2']) {
    await page.goto('/?normal='+normal);
    await page.waitForFunction(()=>!!window.livingHero);
    for(const minutes of [0,720]) {
      const result=await page.evaluate(async(minutes)=>{
        const hero=window.livingHero;hero.setReducedMotion(true);hero.setAnimation(false);hero.setSteam(false);
        hero.setTime(minutes);hero.setDebugView('neutral');
        async function pixels() {
          // Read in the render frame, before the non-preserved buffer is cleared.
          return new Promise<Uint8Array>(resolve=>requestAnimationFrame(()=>{
            const canvas=document.querySelector<HTMLCanvasElement>('#hero')!;
            const gl=canvas.getContext('webgl2')!;
            const data=new Uint8Array(canvas.width*canvas.height*4);
            gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,data);resolve(data);
          }));
        }
        const at=(data:Uint8Array,x:number,y:number)=>data[((674-y)*1200+x)*4];
        const neutral=await pixels();
        const wrist=Array.from({length:48},(_,i)=>at(neutral,595+i,508));
        hero.setDebugView('shadow');const shadow=await pixels();
        const page=Array.from({length:32},(_,i)=>at(shadow,740,510+i));
        return {wristMinimum:Math.min(...wrist),pageShadowMinimum:Math.min(...page),
          maxWristStep:Math.max(...wrist.slice(1).map((v,i)=>Math.abs(v-wrist[i]))),
          pageShadowRange:Math.max(...page)-Math.min(...page)};
      },minutes);
      expect(result.maxWristStep,`${normal} ${minutes}: no polygon step across skin`).toBeLessThanOrEqual(3);
      expect(result.wristMinimum,'sampled a rendered lighting buffer').toBeGreaterThan(10);
      expect(result.pageShadowMinimum,'sampled a rendered shadow buffer').toBeGreaterThan(10);
      if(minutes===0) expect(result.pageShadowRange,'no translated silhouette on night page').toBeLessThanOrEqual(1);
      measurements.push({normal,minutes,...result});
    }
  }
  await mkdir(`${visualRoot}/desk`,{recursive:true});
  await writeFile(`${visualRoot}/desk/continuity.json`,JSON.stringify({regions,measurements},null,2)+'\n');
});

test('desk review: noon and midnight closeups on both normal maps', async ({page})=>{
  test.setTimeout(90_000);
  const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
  await page.setViewportSize({width:1920,height:1080});
  for(const normal of ['low-frequency','registered','v2']) {
    await page.goto('/?normal='+normal);
    await page.waitForFunction(()=>!!window.livingHero);
    await page.addStyleTag({content:'#debug, #status {visibility:hidden!important}'});
    await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);});
    for(const [name,minutes] of [['midnight',0],['noon',720]] as const)for(const view of ['base','final','neutral','shadow','scene'] as const){
      await page.evaluate(async({minutes,view})=>{
        window.livingHero.setTime(minutes);window.livingHero.setDebugView(view);
        await new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())));
      },{minutes,view});
      await page.screenshot({path:`${visualRoot}/desk/${normal}-${name}-${view}.png`,clip:{x:896,y:640,width:1024,height:440}});
    }
  }
  expect(errors).toEqual([]);
});
