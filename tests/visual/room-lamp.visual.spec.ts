import { test, expect, type Page } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { DebugView, Settings } from '../../src/engine/renderer';
import { visualRoot } from './review-output';

// Artwork-located patches, not generated mask contours or shader coordinates.
// Book now samples the right page: left-page illumination is intentionally
// reduced by the salvage pass and separately bounded in salvage.visual.spec.ts.
const boxes = {
  wall: [180,180,330,380], shelf: [50,200,112,370], foreground: [50,500,175,620],
  face: [704,182,751,224], chest: [650,320,715,405],
  hair: [854,310,889,383], sleeve: [808,373,838,450],
  book: [855,515,882,533], cup: [970,460,1025,498], glass: [1080,80,1140,180],
};

async function sample(page: Page, minutes: number, view: DebugView, patch: Partial<Settings> = {}) {
  return page.evaluate(async ({ minutes, view, patch, boxes }) => {
    const h=window.livingHero;
    h.setSettings({ambient:1,projected:1,sun:1,lamp:1,refinement:1,...patch});
    h.setTime(minutes); h.setDebugView(view);
    return new Promise<Record<string, number>>(resolve => requestAnimationFrame(() => {
      const c=document.querySelector<HTMLCanvasElement>('#hero')!, gl=c.getContext('webgl2')!;
      const data=new Uint8Array(1200*675*4);
      gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,data);
      resolve(Object.fromEntries(Object.entries(boxes).map(([name,[x0,y0,x1,y1]]) => {
        let sum=0;
        for(let y=y0;y<y1;y++) for(let x=x0;x<x1;x++) sum+=data[((674-y)*1200+x)*4]/255;
        return [name,sum/((x1-x0)*(y1-y0))];
      })));
    }));
  }, { minutes, view, patch, boxes });
}

test.beforeEach(async ({page}) => {
  await page.setViewportSize({width:1200,height:675});
  await page.goto('/'); await page.waitForFunction(()=>!!window.livingHero);
  await page.evaluate(()=>{const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setSettings({bloom:0});});
});

test('room receives spatial daylight, independently of ambient, and goes dark with projection', async ({page}) => {
  const results=[];
  for(const minutes of [360,720,1050]) {
    const p=await sample(page,minutes,'projected');
    for(const name of ['wall','shelf','foreground']) expect(p[name],`${minutes} ${name}`).toBeGreaterThan(.004);
    expect(p.wall).toBeGreaterThan(p.shelf*1.3); // Not a uniform left-half lift.
    expect(p.wall).toBeLessThan(p.book); // Reading area remains the main receiver.
    expect(p.glass).toBe(0); expect(p.face).toBe(0);
    expect(await sample(page,minutes,'projected',{ambient:0})).toEqual(p);
    for(const patch of [{projected:0},{sun:0},{refinement:0}]) {
      const off=await sample(page,minutes,'projected',patch);
      expect(Object.values(off).every(v=>v===0)).toBe(true);
    }
    results.push({minutes,...p});
  }
  expect(Object.values(await sample(page,1380,'projected')).every(v=>v===0)).toBe(true);
  await mkdir(`${visualRoot}/room-lamp`,{recursive:true});
  await writeFile(`${visualRoot}/room-lamp/room-probes.json`,JSON.stringify(results,null,2)+'\n');
});

test('rear-side lamp favors the reading area over the front face and chest', async ({page}) => {
  const lamp=await sample(page,1380,'lamp');
  expect(lamp.face).toBeLessThan(.025); expect(lamp.chest).toBeLessThan(.05);
  expect(lamp.hair).toBeGreaterThan(.12); expect(lamp.sleeve).toBeGreaterThan(.15);
  expect(lamp.book).toBeGreaterThan(.25); expect(lamp.cup).toBeGreaterThan(.20);
  expect(lamp.sleeve).toBeGreaterThan(lamp.chest*4);
  expect(lamp.glass).toBe(0); expect(lamp.wall).toBe(0);
  const final=await sample(page,1380,'final');
  expect(final.face).toBeGreaterThan(.25); // Expression remains visible.
  expect(Object.values(await sample(page,1380,'lamp',{lamp:0})).every(v=>v===0)).toBe(true);
  await mkdir(`${visualRoot}/room-lamp`,{recursive:true});
  await writeFile(`${visualRoot}/room-lamp/lamp-probes.json`,JSON.stringify({lamp,final},null,2)+'\n');
});
