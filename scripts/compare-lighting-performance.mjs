// Isolated forced-render comparison. Run after visual tests, not alongside them.
// Baseline source shares current public assets (same dimensions), isolating GPU
// shader cost. Timings include RAF scheduling + gl.finish, not GPU timer queries.
import { mkdir, writeFile, symlink, lstat, rmdir } from 'node:fs/promises';
import { execFileSync, spawn } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { chromium } from '@playwright/test';
const revision=process.argv[2] ?? 'f941549';
const animated=process.argv.includes('--animated');
if(!/^[a-f0-9]{7,40}$/.test(revision))throw new Error('Use a commit hash');
const out=resolve('docs/screenshots/code-only-salvage'),baseline=resolve(out,'performance-baseline');
const paths=execFileSync('git',['ls-tree','-r','--name-only',revision,'src','index.html','package.json'],{encoding:'utf8'}).trim().split('\n');
for(const path of paths){const target=resolve(baseline,path);await mkdir(dirname(target),{recursive:true});await writeFile(target,execFileSync('git',['show',`${revision}:${path}`]));}
const publicLink=resolve(baseline,'public');
await symlink(resolve('public'),publicLink,'junction');
const servers=[spawn(process.execPath,['node_modules/vite/bin/vite.js',baseline,'--host','127.0.0.1','--port','4274','--strictPort'],{windowsHide:true,stdio:'ignore'}),spawn(process.execPath,['node_modules/vite/bin/vite.js','--host','127.0.0.1','--port','4275','--strictPort'],{windowsHide:true,stdio:'ignore'})];
const results=[];
try {
  for(const port of [4274,4275]){let ready=false;for(let i=0;i<100;i++){try{if((await fetch(`http://127.0.0.1:${port}`)).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}if(!ready)throw new Error(`Port ${port} not ready`);}
  const modes=[{name:'software',options:{args:['--use-angle=swiftshader']}},
    {name:'edge-d3d11',options:{channel:'msedge',args:['--use-angle=d3d11','--ignore-gpu-blocklist']}}];
  for(const mode of modes){
    let browser;
    try{
      browser=await chromium.launch(mode.options);
      for(const dpr of [1,1.5])for(const minutes of [1050,1380])for(const name of ['before','after','after','before']){
        const context=await browser.newContext({viewport:{width:1440,height:900},deviceScaleFactor:dpr,reducedMotion:'reduce'});
        try{
          const page=await context.newPage();await page.goto(`http://127.0.0.1:${name==='before'?4274:4275}`);
          await page.waitForFunction(()=>!!window.livingHero,{},{timeout:15000});
          const sample=await page.evaluate(async({minutes,animated})=>{
            const h=window.livingHero;h.setReducedMotion(true);h.setAnimation(false);h.setSteam(false);h.setTime(minutes);
            const g=document.querySelector('#hero').getContext('webgl2'),ext=g.getExtension('WEBGL_debug_renderer_info');
            const renderer=ext?g.getParameter(ext.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER);
            const values=[];let draws=0;
            const draw=g.drawArrays.bind(g);g.drawArrays=(...args)=>{draws++;draw(...args);};
            if(animated){
              h.setReducedMotion(false);h.setAnimation(true);h.setSteam(true);
              let last=0;
              await new Promise(resolve=>{let i=0;const tick=t=>{
                if(i>20)values.push(t-last);last=t;
                if(++i<90)requestAnimationFrame(tick);else resolve();
              };requestAnimationFrame(tick);});
            }else for(let i=0;i<50;i++){
                const start=performance.now();h.setTime(minutes);
                await new Promise(r=>requestAnimationFrame(()=>{g.finish();r();}));
                if(i>=10)values.push(performance.now()-start);
            }
            values.sort((a,b)=>a-b);
            g.drawArrays=draw;
            return {renderer,draws,median:values[Math.floor(values.length*.5)],p95:values[Math.floor(values.length*.95)],error:g.getError(),stats:h.getStats()};
          },{minutes,animated});
          results.push({mode:mode.name,name,dpr,minutes,...sample});
          console.log(JSON.stringify(results.at(-1)));
          if(name==='after'&&minutes===1380&&dpr===1){
            await page.addStyleTag({content:'#debug,#status{visibility:hidden!important}'});
            await page.screenshot({path:resolve(out,`${mode.name}-browser-night.png`)});
          }
        }finally{await context.close();}
      }
    }catch(error){results.push({mode:mode.name,unavailable:String(error)});console.log(JSON.stringify(results.at(-1)));}
    finally{await browser?.close();}
    await writeFile(resolve(out,animated?'performance-animated.json':'performance.json'),JSON.stringify({revision,method:animated?'Default steam/bloom, 90 RAF samples, 20 warmup, same current assets':'50 forced renders; 10 warmup; RAF + gl.finish; same current assets',results},null,2));
  }
} finally {
  for(const server of servers)server.kill();
  // Remove only our junction, never its target or an arbitrary directory.
  if((await lstat(publicLink)).isSymbolicLink())await rmdir(publicLink);
}
