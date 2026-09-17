import { test, expect } from '@playwright/test';

test('glass excludes the complete indoor strip at preview and native resolution', async ({page}) => {
  await page.goto('/');
  const checks=await page.evaluate(async()=>{
    const image=new Image();image.src='/assets/generated/scene-masks.svg';await image.decode();
    return [1,1.6,3.2].map(scale=>{
      const c=document.createElement('canvas');c.width=1200*scale;c.height=675*scale;
      const ctx=c.getContext('2d')!;ctx.drawImage(image,0,0,c.width,c.height);
      const pixels=ctx.getImageData(0,0,c.width,c.height).data;
      let max=0,count=0;
      // Independently selected room strip below the sill glass edge, including
      // lamp base, tools, frame, vase and the upper desktop. No polygon-derived oracle.
      for(let y=Math.ceil(300*scale);y<550*scale;y++)for(let x=Math.ceil(870*scale);x<c.width;x++){
        max=Math.max(max,pixels[(y*c.width+x)*4]);count++;
      }
      return {scale,max,count};
    });
  });
  for(const c of checks){expect(c.count).toBeGreaterThan(80000);expect(c.max,`indoor leak at scale ${c.scale}`).toBe(0);}
});

test('room dark sides participate in shadow control without changing exterior',async({page})=>{
  await page.setViewportSize({width:1200,height:675});
  await page.goto('/');await page.waitForFunction(()=>!!window.livingHero);
  const result=await page.evaluate(async()=>{
    const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setSettings({bloom:0});
    async function capture(minutes:number,shadow:number){
      h.setTime(minutes);h.setSettings({shadow});h.setDebugView('neutral');
      // Read in the draw frame: preserveDrawingBuffer is intentionally false.
      return new Promise<number[]>(resolve=>requestAnimationFrame(()=>{
        const gl=document.querySelector<HTMLCanvasElement>('#hero')!.getContext('webgl2')!;
        const pixels=new Uint8Array(1200*675*4);gl.readPixels(0,0,1200,675,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
        resolve([[250,300],[350,360],[150,560],[1100,100]].map(([x,y])=>pixels[((674-y)*1200+x)*4]));
      }));
    }
    const out=[];for(const t of [360,720,1050,1380])out.push({t,off:await capture(t,0),on:await capture(t,1)});
    return out;
  });
  for(const r of result){
    expect(r.off[3],'valid rendered glass sample').toBeGreaterThan(0);
    for(let i=0;i<3;i++){expect(r.on[i],`${r.t} room region ${i}`).toBeLessThan(r.off[i]);expect(r.off[i]-r.on[i]).toBeLessThan(25);}
    expect(r.on[3]).toBe(r.off[3]);
  }
});
