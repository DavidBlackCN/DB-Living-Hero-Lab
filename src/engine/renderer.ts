import { loadAssets, type AssetOptions } from './assets';
import { lightingAt, projectedLightAt } from './lighting';
import { Timeline } from './timeline';
import { vertex, fragment } from './shaders';
import { createBloom } from './postprocessing';
export type DebugView = 'final' | 'base' | 'normal' | 'masks' | 'lighting' | 'scene' | 'overlay' | 'bright' | 'bloom' | 'neutral' | 'projected' | 'exterior' | 'shadow' | 'lamp' | 'directional' | 'correction' | 'correctedBase';
export interface Settings { shadow: number; correction: number; exposure: number; ambient: number; sun: number; lamp: number; normal: number; face: number; hair: number; cloth: number; night: number; refinement: number; stylized: number; softness: number; projected: number; projectedIntensity: number; projectedSoftness: number; bloom: number; bloomThreshold: number; bloomRadius: number }
export interface HeroState { minutes: number; target: number; realtime: boolean; reducedMotion: boolean; animation: boolean; steam: boolean; view: DebugView }
export interface HeroStats { dpr: number; canvasWidth: number; canvasHeight: number; artworkWidth: number; artworkHeight: number; sourceTextureMiB: number; bloomWidth: number; bloomHeight: number; bloomTextureMiB: number; contextLost: boolean }
export interface HeroOptions extends AssetOptions { time?: number; onUpdate?: (state: HeroState) => void; onError?: (message: string) => void }
export async function createLivingHero(canvas: HTMLCanvasElement, options: HeroOptions = {}) {
  const assets = await loadAssets(options);
  const context = canvas.getContext('webgl2', { alpha: false, antialias: false, depth: false, powerPreference: 'low-power' });
  if (!context) throw new Error('此浏览器无法启用 WebGL2；请使用支持硬件加速的桌面浏览器。');
  const gl: WebGL2RenderingContext = context;
  const textures: WebGLTexture[] = [], shaders: WebGLShader[] = [];
  const program = gl.createProgram()!;
  function cleanup() { textures.forEach(t => gl!.deleteTexture(t)); shaders.forEach(s => gl!.deleteShader(s)); gl!.deleteProgram(program); }
  try {
    for (const [type, source] of [[gl.VERTEX_SHADER, vertex], [gl.FRAGMENT_SHADER, fragment]] as const) {
      const shader = gl.createShader(type)!; shaders.push(shader);
      gl.shaderSource(shader, source); gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader) ?? 'Shader compile failed');
      gl.attachShader(program, shader);
    }
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program) ?? 'Shader link failed');
    gl.useProgram(program);
    [assets.base, assets.normal, assets.mask, assets.sceneMask, assets.lightShaping, assets.correction].forEach((image, i) => {
      const texture = gl.createTexture()!; textures.push(texture);
      gl.activeTexture(gl.TEXTURE0+(i>=4?i+1:i)); gl.bindTexture(gl.TEXTURE_2D,texture);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      // None of the scene maps use alpha. RGB8 avoids allocating an unused
      // fourth channel for the four 4K maps and smaller light-shaping map.
      if(i===5) {
        if(image) gl.texImage2D(gl.TEXTURE_2D,0,gl.R8,gl.RED,gl.UNSIGNED_BYTE,image);
        else gl.texImage2D(gl.TEXTURE_2D,0,gl.R8,1,1,0,gl.RED,gl.UNSIGNED_BYTE,new Uint8Array([128]));
      }
      else if(image) gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB8,gl.RGB,gl.UNSIGNED_BYTE,image);
      else gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB8,1,1,0,gl.RGB,gl.UNSIGNED_BYTE,new Uint8Array([128,128,255]));
    });
  } catch(error) { cleanup(); throw error; }
  const uniforms = new Map<string, WebGLUniformLocation | null>();
  const loc = (name: string) => {
    if(!uniforms.has(name)) uniforms.set(name,gl.getUniformLocation(program,name));
    return uniforms.get(name)!;
  };
  ['uBase','uNormal','uMask','uSceneMask'].forEach((name,i)=>gl.uniform1i(loc(name),i));
  gl.uniform1i(loc('uHasNormal'),Number(!!assets.normal)); gl.uniform1i(loc('uHasMask'),Number(!!assets.mask));
  gl.uniform1i(loc('uHasSceneMask'),Number(!!assets.sceneMask));
  gl.uniform1i(loc('uLightShaping'),5);
  gl.uniform1i(loc('uHasLightShaping'),Number(!!assets.lightShaping));
  gl.uniform1i(loc('uBloomMap'),4);
  gl.uniform1i(loc('uCorrectionMap'),6);
  gl.uniform1i(loc('uHasCorrection'),Number(!!assets.correction));
  let post: ReturnType<typeof createBloom>;
  try { post=createBloom(gl); } catch(error) { cleanup(); throw error; }
  const timeline = new Timeline(options.time ?? 720);
  const settings: Settings = { shadow: .65, correction: 0, exposure: 0, ambient: 1, sun: 1, lamp: 1, normal: 1, face: 0.85, hair: 0.95, cloth: 0.94, night: 1, refinement: 1, stylized: 0.50, softness: 0.18, projected: 1, projectedIntensity: 0.42, projectedSoftness: 0.22, bloom: 0.22, bloomThreshold: 0.82, bloomRadius: 1 };
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  let reducedMotion = media.matches, animation = true, steam = true, view: DebugView = 'final';
  let frame = 0, timer = 0, destroyed = false, lost = false, previous = performance.now(), lastNotify = -Infinity;
  const state = (): HeroState => ({ minutes: timeline.minutes, target: timeline.target, realtime: timeline.realtime, reducedMotion, animation, steam, view });
  function render(now = performance.now()) {
    gl.useProgram(program);
    const dpr = Math.min(devicePixelRatio || 1,1.5);
    const w=Math.max(1,Math.round(canvas.clientWidth*dpr)),h=Math.max(1,Math.round(canvas.clientHeight*dpr));
    if(canvas.width!==w||canvas.height!==h) { canvas.width=w; canvas.height=h; }
    gl.clearColor(.055,.063,.076,1); gl.clear(gl.COLOR_BUFFER_BIT);
    const scale=Math.min(w/assets.base.width,h/assets.base.height);
    const vw=Math.round(assets.base.width*scale),vh=Math.round(assets.base.height*scale);
    gl.viewport(Math.round((w-vw)/2),Math.round((h-vh)/2),vw,vh);
    const light=lightingAt(timeline.minutes);
    const projection=projectedLightAt(timeline.minutes);
    gl.uniform4f(loc('uProjectionGeometry'),projection.origin[0],projection.origin[1],projection.axis[0],projection.axis[1]);
    gl.uniform4f(loc('uProjectionShape'),projection.width,projection.spread,projection.separation,projection.reach);
    gl.uniform1f(loc('uProjectionEnergy'),projection.energy);
    gl.uniform1f(loc('uMinutes'),timeline.minutes);
    gl.uniform3fv(loc('uAmbient'),light.ambient); gl.uniform3fv(loc('uSun'),light.sun); gl.uniform3fv(loc('uDirection'),light.direction);
    gl.uniform1f(loc('uLamp'),light.lamp);
    gl.uniform1f(loc('uMotionTime'), now / 1000);
    gl.uniform1f(loc('uSteam'), Number(steam && animation && !reducedMotion));
    gl.uniform1f(loc('uNight'),light.night);
    gl.uniform1f(loc('uBloomMood'),.12+.88*Math.max(light.night,light.lamp));
    gl.uniform1f(loc('uProjected'),settings.projected);
    gl.uniform1f(loc('uCorrection'),settings.correction);
    for(const [key,name] of Object.entries({shadow:'uShadow',exposure:'uExposure',ambient:'uAmbientStrength',sun:'uSunStrength',lamp:'uLampStrength',normal:'uNormalStrength',face:'uFace',hair:'uHair',cloth:'uCloth',night:'uNightStrength',refinement:'uRefinement',stylized:'uStylized',softness:'uSoftness',projectedIntensity:'uProjectedIntensity',projectedSoftness:'uProjectedSoftness',bloom:'uBloom',bloomThreshold:'uBloomThreshold',bloomRadius:'uBloomRadius'})) gl.uniform1f(loc(name),settings[key as keyof Settings]);
    gl.uniform1i(loc('uView'),['final','base','normal','masks','lighting','scene','overlay','bright','bloom','neutral','projected','exterior','shadow','lamp','directional','correction','correctedBase'].indexOf(view));
    const bloomActive=(view==='final'&&settings.bloom>0)||view==='bright'||view==='bloom';
    if(bloomActive) {
      post.begin(vw,vh);
      gl.uniform1i(loc('uView'),7); gl.drawArrays(gl.TRIANGLES,0,3);
      post.finish(settings.bloomRadius*dpr);
      gl.useProgram(program);
      gl.viewport(Math.round((w-vw)/2),Math.round((h-vh)/2),vw,vh);
      gl.uniform1i(loc('uView'),view==='bright'?7:view==='bloom'?8:0);
    }
    gl.drawArrays(gl.TRIANGLES,0,3);
  }
  function tick(now: number) {
    frame=0; if(destroyed||lost||document.hidden) return;
    timeline.update(Math.max(0,Math.min((now-previous)/1000,.1)),reducedMotion||!animation); previous=now;
    render(now);
    if(now-lastNotify>80 || timeline.minutes===timeline.target) { options.onUpdate?.(state()); lastNotify=now; }
    if(timeline.minutes!==timeline.target) frame=requestAnimationFrame(tick);
    else if(timeline.realtime || (steam && animation && !reducedMotion)) timer=window.setTimeout(wake, steam ? 33 : 1000);
  }
  function wake() { clearTimeout(timer); if(!destroyed&&!lost&&!document.hidden&&!frame) { previous=performance.now(); frame=requestAnimationFrame(tick); } }
  function visibility() { cancelAnimationFrame(frame); clearTimeout(timer); frame=0; wake(); }
  function motion() { reducedMotion=media.matches; wake(); }
  function contextLost(event: Event) { event.preventDefault(); lost=true; cancelAnimationFrame(frame); clearTimeout(timer); frame=0; options.onError?.('WebGL 上下文已丢失，请重新加载页面恢复。'); }
  function contextRestored() {
    // GPU objects are invalid after loss. A full page restart is the safe
    // recovery until resource construction is split into a reusable factory.
    if(destroyed) return;
    options.onError?.('WebGL 上下文已恢复，正在重新加载场景。');
    window.location.reload();
  }
  const observer = new ResizeObserver(wake); observer.observe(canvas);
  document.addEventListener('visibilitychange',visibility); media.addEventListener('change',motion); canvas.addEventListener('webglcontextlost',contextLost); canvas.addEventListener('webglcontextrestored',contextRestored);
  wake();
  return {
    correctionAvailable: !!assets.correction,
    setTime(minutes: number) { timeline.setTime(minutes); wake(); },
    setRealtime(enabled: boolean) { timeline.realtime=enabled; wake(); },
    setReducedMotion(enabled: boolean) { reducedMotion=enabled; wake(); },
    setAnimation(enabled: boolean) { animation=enabled; wake(); },
    setSteam(enabled: boolean) { steam=enabled; wake(); },
    setDebugView(mode: DebugView) { view=mode; wake(); },
    setSettings(patch: Partial<Settings>) {
      for(const [key,value] of Object.entries(patch)) {
        if(!Number.isFinite(value)) continue;
        const k=key as keyof Settings;
        if (!(k in settings)) continue;
        settings[k]=Math.max(k==='exposure'?-1:k==='bloomThreshold'?.4:0,Math.min(['face','night','refinement','correction','shadow'].includes(k)?1:k==='bloomThreshold'?1:2,value));
      }
      wake();
    },
    getState: state,
    getSettings: (): Settings => ({ ...settings }),
    getStats: (): HeroStats => {
      const dpr=Math.min(devicePixelRatio||1,1.5);
      const canvasWidth=Math.max(1,Math.round(canvas.clientWidth*dpr)), canvasHeight=Math.max(1,Math.round(canvas.clientHeight*dpr));
      const bloomSize=post.getSize();
      const sourceBytes=[assets.base,assets.normal,assets.mask,assets.sceneMask,assets.lightShaping].reduce((sum,map)=>sum+(map?map.width*map.height*3:3),0)+(assets.correction?assets.correction.width*assets.correction.height:1);
      return { dpr, canvasWidth, canvasHeight, artworkWidth: assets.base.width, artworkHeight: assets.base.height, sourceTextureMiB: Number((sourceBytes/1048576).toFixed(2)), bloomWidth: bloomSize.width, bloomHeight: bloomSize.height, bloomTextureMiB: Number((bloomSize.width*bloomSize.height*4*3/1048576).toFixed(2)), contextLost: lost };
    },
    destroy() { if(destroyed)return; destroyed=true; cancelAnimationFrame(frame); clearTimeout(timer); observer.disconnect(); document.removeEventListener('visibilitychange',visibility); media.removeEventListener('change',motion); canvas.removeEventListener('webglcontextlost',contextLost); canvas.removeEventListener('webglcontextrestored',contextRestored); post.destroy(); cleanup(); },
  };
}
export type LivingHero = Awaited<ReturnType<typeof createLivingHero>>;
