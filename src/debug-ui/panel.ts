import type { DebugView, HeroState, LivingHero, Settings } from '../engine/renderer';
import { formatTime } from '../engine/timeline';
export function createPanel(root: HTMLElement, engine: LivingHero) {
  root.innerHTML = `<details open><summary>Living Hero <span>LIGHTING LAB · 02</span></summary>
    <div class="controls"><div class="clock"><output id="clock">12:00</output><span id="mode">MANUAL</span></div>
    <label class="check"><input id="realtime" type="checkbox">Realtime · 本地时间</label>
    <label for="time">时间 <output id="target">12:00</output></label><input id="time" type="range" min="0" max="1440" step="1" value="720">
    <div class="presets"><button data-time="360">Dawn</button><button data-time="720">Noon</button><button data-time="1050">Dusk</button><button data-time="1380">Night</button></div>
    <label class="check"><input id="refinement" type="checkbox" checked>区域光照增强 · 关闭对照一版</label>
    <div id="lighting-controls"></div>
    <label for="view">调试视图</label><select id="view"><option value="final">Final · 合成画面</option><option value="base">Base · 原图对照</option><option value="normal">Normal · 低频法线</option><option value="masks">Masks · 人物遮罩</option><option value="lighting">Lighting · 光照贡献</option><option value="scene">Scene · 窗外 / 桌面 / 灯</option><option value="overlay">Overlay · 配准叠加</option></select>
    <label class="check"><input id="animation" type="checkbox" checked>动画总开关 · 时间平滑过渡</label>
    <label class="check"><input id="reduced" type="checkbox">减少动态效果</label>
    <p class="note">手工轮廓遮罩 / 低频法线 · 仍为近似<br>含投光、Bloom、蒸汽；眨眼尚未接入。</p></div></details>`;
  const query = <T extends HTMLElement>(selector: string) => root.querySelector<T>(selector)!;
  for(const [key,label,min,max,value] of [
    ['exposure','曝光 EV',-1,1,0],['ambient','环境光',0,2,1],['sun','窗光',0,2,1],['lamp','台灯',0,2,1],['normal','法线强度',0,2,1],['face','脸部保护',0,1,.8],
    ['hair','头发受光',0,2,.85],['cloth','服装受光',0,2,.9],['night','夜间日光抑制',0,1,1],['stylized','Stylized band',0,1,.62],['softness','Band softness',0,1,.14],
  ] as const) {
    const row=document.createElement('div'); row.className='slider-row';
    row.innerHTML=`<label for="${key}">${label}<output>${value.toFixed(2)}</output></label><input id="${key}" type="range" min="${min}" max="${max}" step="0.01" value="${value}">`;
    row.querySelector('input')!.addEventListener('input',event=>{ const v=Number((event.target as HTMLInputElement).value); row.querySelector('output')!.value=v.toFixed(2); engine.setSettings({[key]:v} as Partial<Settings>); });
    query('#lighting-controls').append(row);
  }
  const time=query<HTMLInputElement>('#time'), realtime=query<HTMLInputElement>('#realtime');
  query<HTMLInputElement>('#refinement').addEventListener('change',event=>engine.setSettings({refinement:Number((event.target as HTMLInputElement).checked)}));
  time.addEventListener('input',()=>{ engine.setTime(Number(time.value)); realtime.checked=false; query('#target').textContent=Number(time.value)===1440?'24:00':formatTime(Number(time.value)); });
  realtime.addEventListener('change',()=>engine.setRealtime(realtime.checked));
  root.querySelectorAll<HTMLButtonElement>('[data-time]').forEach(button=>button.addEventListener('click',()=>{ engine.setTime(Number(button.dataset.time)); time.value=button.dataset.time!; realtime.checked=false; }));
  query<HTMLSelectElement>('#view').addEventListener('change',event=>engine.setDebugView((event.target as HTMLSelectElement).value as DebugView));
  const view = query<HTMLSelectElement>('#view');
  view.insertAdjacentHTML('beforeend', '<option value="bright">Bright Pass</option><option value="bloom">Bloom Only</option><option value="neutral">Neutral Lighting</option><option value="projected">Projected Light Only</option>');
  const projected = document.createElement('label');
  projected.className = 'check';
  projected.innerHTML = '<input id="projected" type="checkbox" checked> Projected window light';
  query('#animation').parentElement!.insertAdjacentElement('afterend', projected);
  query<HTMLInputElement>('#projected').addEventListener('change', event => engine.setSettings({ projected: Number((event.target as HTMLInputElement).checked) }));
  for (const [key, label, min, max, value] of [['projectedIntensity','Projected intensity',0,1,.42],['projectedSoftness','Projected softness',.05,.6,.22]] as const) {
    const row=document.createElement('div'); row.className='slider-row';
    row.innerHTML=`<label for="${key}">${label}<output>${value.toFixed(2)}</output></label><input id="${key}" type="range" min="${min}" max="${max}" step="0.01" value="${value}">`;
    row.querySelector('input')!.addEventListener('input',event=>{ const v=Number((event.target as HTMLInputElement).value); row.querySelector('output')!.value=v.toFixed(2); engine.setSettings({[key]:v} as Partial<Settings>); });
    query('#lighting-controls').append(row);
  }
  const steam = document.createElement('label');
  steam.className = 'check';
  steam.innerHTML = '<input id="steam" type="checkbox" checked> Coffee steam';
  query('#animation').parentElement!.insertAdjacentElement('afterend', steam);
  query<HTMLInputElement>('#steam').addEventListener('change',event=>engine.setSteam((event.target as HTMLInputElement).checked));
  const bloom = document.createElement('label');
  bloom.className = 'check';
  bloom.innerHTML = '<input id="bloom" type="checkbox" checked> Bloom';
  query('#steam').parentElement!.insertAdjacentElement('afterend', bloom);
  let bloomIntensity = .22;
  query<HTMLInputElement>('#bloom').addEventListener('change',event=>engine.setSettings({ bloom: (event.target as HTMLInputElement).checked ? bloomIntensity : 0 }));
  for (const [key, label, min, max, value] of [['bloomIntensity','Bloom intensity',0,1,.22],['bloomThreshold','Bloom threshold',.4,1,.82],['bloomRadius','Bloom radius',.5,2,1]] as const) {
    const row=document.createElement('div'); row.className='slider-row';
    row.innerHTML=`<label for="${key}">${label}<output>${value.toFixed(2)}</output></label><input id="${key}" type="range" min="${min}" max="${max}" step="0.01" value="${value}">`;
    row.querySelector('input')!.addEventListener('input',event=>{ const v=Number((event.target as HTMLInputElement).value); row.querySelector('output')!.value=v.toFixed(2); const patch: Partial<Settings> = key === 'bloomIntensity' ? { bloom:v } : key === 'bloomThreshold' ? { bloomThreshold:v } : { bloomRadius:v }; engine.setSettings(patch); if(key==='bloomIntensity') { bloomIntensity=v; query<HTMLInputElement>('#bloom').checked=v>0; } });
    query('#lighting-controls').append(row);
  }
  query<HTMLInputElement>('#animation').addEventListener('change',event=>engine.setAnimation((event.target as HTMLInputElement).checked));
  query<HTMLInputElement>('#reduced').addEventListener('change',event=>engine.setReducedMotion((event.target as HTMLInputElement).checked));
  const stats=document.createElement('p'); stats.className='note'; stats.id='gpu-stats';
  query('.controls').append(stats);
  const updateStats=()=>{ const s=engine.getStats(); stats.textContent=`GPU ${s.canvasWidth}×${s.canvasHeight} · RGB textures ${s.sourceTextureMiB} MiB · Bloom ${s.bloomWidth}×${s.bloomHeight} (${s.bloomTextureMiB} MiB)`; };
  updateStats();
  const statsTimer=window.setInterval(updateStats,1000);
  return { update(state: HeroState) {
    query('#clock').textContent=formatTime(state.minutes);
    query('#mode').textContent=state.realtime?'LOCAL TIME':'MANUAL';
    realtime.checked=state.realtime;
    if(document.activeElement!==time) time.value=String(Math.round(state.target));
    query('#target').textContent=Number(time.value)===1440?'24:00':formatTime(state.target);
    query<HTMLInputElement>('#reduced').checked=state.reducedMotion;
  }, destroy() { window.clearInterval(statsTimer); root.replaceChildren(); } };
}
