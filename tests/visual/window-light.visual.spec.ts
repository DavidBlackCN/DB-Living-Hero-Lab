import { test, expect, type Page } from '@playwright/test';
import { visualRoot } from './review-output';
import type { LivingHero, DebugView } from '../../src/engine/renderer';
import { mkdir, writeFile, readFile } from 'node:fs/promises';

const times = [['morning', 480], ['noon', 720], ['dusk', 1050], ['night', 1380]] as const;
const views: DebugView[] = ['final', 'scene', 'overlay', 'neutral', 'projected', 'exterior', 'shadow'];
declare global { interface Window { livingHero: LivingHero } }

async function settle(page: Page, minutes: number, view: DebugView) {
  await page.evaluate(async ({ minutes, view }) => {
    window.livingHero.setTime(minutes);
    window.livingHero.setDebugView(view);
    await new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
  }, { minutes, view });
}

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => !!window.livingHero);
  await page.evaluate(() => {
    window.livingHero.setReducedMotion(true);
    window.livingHero.setAnimation(false);
    window.livingHero.setSteam(false);
  });
});

test('acceptance captures: four times, seven views, registered window closeups', async ({ page }) => {
  test.setTimeout(90_000);
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.addStyleTag({ content: '#debug, #status { visibility: hidden !important; }' });
  for (const [name, minutes] of times) {
    for (const view of views) {
      await settle(page, minutes, view);
      expect(await page.evaluate(() => window.livingHero.getState().minutes)).toBe(minutes);
      await page.screenshot({ path: `${visualRoot}/acceptance/${name}-${view}.png` });
    }
  }
  // 2 screen pixels per reference pixel: inspect the actual lower sill, not a thumbnail.
  await page.setViewportSize({ width: 2400, height: 1350 });
  for (const view of ['base', 'final', 'scene', 'overlay', 'exterior'] as const) {
    await settle(page, 1380, view);
    await page.screenshot({ path: `${visualRoot}/acceptance/night-window-${view}.png`,
      clip: { x: 1640, y: 460, width: 760, height: 280 } });
    await page.screenshot({ path: `${visualRoot}/acceptance/night-right-pane-${view}.png`,
      clip: { x: 2048, y: 0, width: 352, height: 640 } });
  }
  expect(errors).toEqual([]);
  expect(await page.locator('#hero').evaluate((canvas: HTMLCanvasElement) => canvas.getContext('webgl2')!.getError())).toBe(0);
});

test('glass raster excludes lower frame, mullion, sill and indoor objects', async ({ page }) => {
  const result = await page.evaluate(async () => {
    const image = new Image(); image.src = '/assets/generated/scene-masks.svg'; await image.decode();
    const canvas = document.createElement('canvas'); canvas.width = 3840; canvas.height = 2160;
    const ctx = canvas.getContext('2d')!; ctx.drawImage(image, 0, 0);
    const sample = ([x, y]: number[]) => ctx.getImageData(Math.round(x * 3.2), Math.round(y * 3.2), 1, 1).data[0];
    // Independently picked from the original artwork, not computed from the polygons.
    const excluded = [[1008,100],[1046,100],[1087,294],[1100,298],[1120,300],[1140,304],
      [1160,312],[1190,322],[1095,320],[1100,350],[895,290],[919,299],
      [1048,305],[966,201],[960,317],[1160,355]];
    for (let x = 1085; x < 1200; x += 2) {
      for (let y = 304 + (x-1085)*.08; y < 355; y += 3) excluded.push([x, y]);
    }
    const flowers = [[1164,230],[1168,252],[1154,291],[1127,243]];
    const glass = [[1090,100],[1180,180],[1095,282],[1105,284],[885,240],[925,244]];
    return { excluded: excluded.map(p => ({ p, red: sample(p) })), glass: glass.map(p => ({ p, red: sample(p) })), flowers: flowers.map(p => ({ p, red: sample(p) })) };
  });
  for (const { p, red } of result.excluded) expect(red, `exterior leak at ${p}`).toBe(0);
  for (const { p, red } of result.glass) expect(red, `missing glass at ${p}`).toBeGreaterThan(245);
  // Fine source-colored petals retain fractional coverage at antialiased edges.
  for (const { p, red } of result.flowers) expect(red, `flower protection at ${p}`).toBeLessThan(16);
});

test('glass meets source edges without an eroded seam or lower-frame spill', async ({ page }) => {
  const probes=JSON.parse(await readFile('docs/window-edge-probes.json','utf8'));
  const samples=await page.evaluate(async (probes) => {
    const image=new Image();image.src='/assets/generated/scene-masks.svg';await image.decode();
    const canvas=document.createElement('canvas');canvas.width=3840;canvas.height=2160;
    const ctx=canvas.getContext('2d')!;ctx.drawImage(image,0,0);
    const at=(x:number,y:number)=>ctx.getImageData(Math.round(x),Math.round(y),1,1).data[0];
    const d=probes.sampleDistancePixels;
    return [
      ...probes.verticalRightPane.map(([x,y]:number[])=>({edge:[x,y],glass:at(x+d,y),frame:at(x-d,y)})),
      ...probes.lowerRightPane.map(([x,y]:number[])=>({edge:[x,y],glass:at(x,y-d),frame:at(x,y+d)})),
    ];
  }, probes);
  for(const sample of samples) {
    expect(sample.glass,`uncovered glass beside ${sample.edge}`).toBeGreaterThan(245);
    expect(sample.frame,`frame spill beside ${sample.edge}`).toBeLessThan(5);
  }
  await mkdir(`${visualRoot}/acceptance`,{recursive:true});
  await writeFile(`${visualRoot}/acceptance/window-edge-results.json`,JSON.stringify(samples,null,2)+'\n');
});

test('projected light moves spatially, reaches objects, and shuts off at night', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 675 });
  async function capture(minutes: number, patch: Record<string, number> = {}) {
    return page.evaluate(async ({ minutes, patch }) => {
      const hero=window.livingHero;
      hero.setSettings({ projected: 1, sun: 1, refinement: 1, ...patch });
      hero.setTime(minutes); hero.setDebugView('projected');
      return new Promise<{ grid: number[]; mean: number; centroid: number[]; objects: Record<string,number>; max: number }>(resolve => requestAnimationFrame(() => {
        const canvas=document.querySelector<HTMLCanvasElement>('#hero')!;
        const gl=canvas.getContext('webgl2')!;
        const data=new Uint8Array(canvas.width*canvas.height*4);
        gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
        const at=(x:number,y:number)=>data[((canvas.height-1-y)*canvas.width+x)*4]/255;
        const grid: number[]=[]; let sum=0,sx=0,sy=0,max=0;
        for(let y=0;y<675;y+=10) for(let x=0;x<1200;x+=10) {
          const v=at(x,y); grid.push(v);sum+=v;sx+=v*x;sy+=v*y;max=Math.max(max,v);
        }
        const boxes: Record<string,number[]>={book:[760,520,810,540],cup:[965,465,1015,490],shoulder:[790,310,815,355],hair:[852,305,875,333],glass:[1080,80,1140,180],face:[710,180,740,215]};
        const objects: Record<string,number>={};
        for(const [name,[x0,y0,x1,y1]] of Object.entries(boxes)) {
          let s=0,n=0;for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){s+=at(x,y);n++;}objects[name]=s/n;
        }
        resolve({grid,mean:sum/grid.length,centroid:sum?[sx/sum,sy/sum]:[0,0],objects,max});
      }));
    }, { minutes, patch });
  }
  const samples=[];
  for(const [name,minutes] of times) samples.push({name,...await capture(minutes)});
  const [morning,noon,dusk,night]=samples;
  expect(night.max).toBe(0);
  // Morning crosses the book diagonally; noon falls further right from above.
  for(const [a,b] of [[morning,noon],[noon,dusk],[morning,dusk]])
    expect(Math.hypot(a.centroid[0]-b.centroid[0],a.centroid[1]-b.centroid[1])).toBeGreaterThan(35);
  for(const name of ['book','shoulder']) expect(morning.objects[name],`morning ${name}`).toBeGreaterThan(.025);
  for(const s of [morning,noon,dusk]) expect(s.objects.glass).toBe(0);
  expect(dusk.objects.face).toBe(0);
  for(const name of ['book','cup','shoulder','hair']) expect(dusk.objects[name],name).toBeGreaterThan(.025);
  // Normalize away energy: equal-shaped brightness/tint changes fail this check.
  const differences=[];
  for(const [a,b] of [[morning,noon],[noon,dusk]]) {
    const difference=a.grid.reduce((s,v,i)=>s+Math.abs(v/a.mean-b.grid[i]/b.mean),0)/a.grid.length;
    expect(difference).toBeGreaterThan(.3); differences.push({pair:[a.name,b.name],difference});
  }
  for(const patch of [{projected:0},{sun:0},{refinement:0}]) expect((await capture(1050,patch)).max).toBe(0);
  await mkdir(`${visualRoot}/acceptance`,{recursive:true});
  await writeFile(`${visualRoot}/acceptance/projected-metrics.json`,JSON.stringify({samples:samples.map(({grid,...summary})=>summary),normalizedShapeDifferences:differences},null,2)+'\n');
});

test('sunlight includes shadows and night separates lamp, room and exterior', async ({ page }) => {
  await page.setViewportSize({ width: 1200, height: 675 });
  async function sample(minutes:number, projected:number, lamp:number, view:DebugView) {
    return page.evaluate(async ({minutes,projected,lamp,view}) => {
      const hero=window.livingHero;
      hero.setSettings({projected,lamp,bloom:0});hero.setTime(minutes);hero.setDebugView(view);
      return new Promise<{grid:number[];areas:Record<string,number[]>}>(resolve=>requestAnimationFrame(()=>{
        const canvas=document.querySelector<HTMLCanvasElement>('#hero')!;
        const gl=canvas.getContext('webgl2')!;
        const data=new Uint8Array(canvas.width*canvas.height*4);
        gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,data);
        const at=(x:number,y:number,c:number)=>data[((canvas.height-1-y)*canvas.width+x)*4+c]/255;
        const grid:number[]=[];
        for(let y=280;y<600;y+=4)for(let x=400;x<1100;x+=4)grid.push(at(x,y,0));
        const boxes:Record<string,number[]>={glass:[1090,80,1140,180],lampPool:[940,515,1000,532],room:[350,310,400,380]};
        const areas:Record<string,number[]>={};
        for(const [name,[x0,y0,x1,y1]] of Object.entries(boxes)){
          const sums=[0,0,0];let n=0;
          for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){for(let c=0;c<3;c++)sums[c]+=at(x,y,c);n++;}
          areas[name]=sums.map(s=>s/n);
        }
        resolve({grid,areas});
      }));
    },{minutes,projected,lamp,view});
  }
  const daylight=[];
  for(const [name,minutes] of times.slice(0,3)) {
    const off=await sample(minutes,0,1,'neutral'),on=await sample(minutes,1,1,'neutral');
    const delta=on.grid.map((v,i)=>v-off.grid[i]);
    daylight.push({name,litFraction:delta.filter(v=>v>.015).length/delta.length,
      shadowFraction:delta.filter(v=>v<-.02).length/delta.length});
  }
  const night=await sample(1380,1,1,'lighting');
  const noLamp=await sample(1380,1,0,'lighting');
  await mkdir(`${visualRoot}/acceptance`,{recursive:true});
  await writeFile(`${visualRoot}/acceptance/spatial-contrast.json`,JSON.stringify({daylight,night:night.areas,noLamp:noLamp.areas},null,2)+'\n');
  for(const result of daylight) {
    expect(result.litFraction,`${result.name} receiving light`).toBeGreaterThan(.025);
    expect(result.shadowFraction,`${result.name} receiving shadow`).toBeGreaterThan(.15);
  }
  const {glass,lampPool,room}=night.areas;
  expect(glass[2]-glass[0],'cool exterior').toBeGreaterThan(.08);
  expect(lampPool[0]-lampPool[2],'warm lamp pool').toBeGreaterThan(.08);
  expect(lampPool[0]-room[0],'lamp vs dark room').toBeGreaterThan(.2);
  expect(lampPool[0]-noLamp.areas.lampPool[0],'local lamp response').toBeGreaterThan(.15);
  expect(noLamp.areas.glass,'lamp must not relight glass').toEqual(glass);
});
