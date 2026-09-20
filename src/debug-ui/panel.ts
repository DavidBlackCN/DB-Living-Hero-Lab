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
    <label class="check"><input id="blink" type="checkbox" checked>Blink</label>
    <button id="trigger-blink" type="button">触发眨眼</button> <output id="blink-phase">open</output>
    <label class="check"><input id="breathing" type="checkbox">Breathing · Experimental</label>
    <div id="breathing-controls"></div>
    <label>Breathing <output id="breathing-status">Off</output></label>
    <label>Displacement <output id="breathing-displacement">0.00 px</output></label>
    <label class="check"><input id="reduced" type="checkbox">减少动态效果</label>
    </div></details>`;
  const query = <T extends HTMLElement>(selector: string) => root.querySelector<T>(selector)!;
  for(const [key,label,min,max,value] of [
    ['exposure','曝光 EV',-1,1,0],['ambient','环境光',0,2,1],['sun','窗光',0,2,1],['lamp','台灯',0,2,1],['normal','法线强度',0,2,1],['face','脸部保护',0,1,.85],
    ['hair','头发受光',0,2,.95],['cloth','服装受光',0,2,.94],['night','夜间日光抑制',0,1,1],['stylized','Stylized band',0,1,.50],['softness','Band softness',0,1,.18],
    ['shadow','柔和阴影 / 接触遮挡',0,1,.65],
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
  view.insertAdjacentHTML('beforeend','<option value="breathingWeight">Breathing Weight</option>');
  query<HTMLInputElement>('#breathing').addEventListener('change',event=>engine.setBreathing((event.target as HTMLInputElement).checked));
  for(const [key,label,min,max,step] of [['breathingStrength','Strength (source px)',0,3,.1],['breathingCycle','Cycle (s)',5,6,.1]] as const) {
    const row=document.createElement('div'); row.className='slider-row';
    const value=engine.getSettings()[key];
    row.innerHTML=`<label for="${key}">${label}<output>${value.toFixed(1)}</output></label><input id="${key}" type="range" min="${min}" max="${max}" step="${step}" value="${value}">`;
    row.querySelector('input')!.addEventListener('input',event=>{const v=Number((event.target as HTMLInputElement).value);row.querySelector('output')!.value=v.toFixed(1);engine.setSettings({[key]:v});});
    query('#breathing-controls').append(row);
  }
  view.insertAdjacentHTML('beforeend', '<option value="ambient">Ambient Fill Only</option><option value="form">Form Light Bands</option><option value="contact">Contact Visibility</option>');
  view.insertAdjacentHTML('beforeend', '<option value="lampFields">Lamp Fields (R near / G desk / B character)</option>');
  view.querySelector<HTMLOptionElement>('option[value="normal"]')!.textContent='Normal · 表面法线';
  view.insertAdjacentHTML('beforeend', '<option value="lamp">Lamp Contribution Only</option><option value="directional">Directional Only</option>');
  if(engine.correctionAvailable) {
    view.insertAdjacentHTML('beforeend','<option value="correction">Correction · 增益贴图</option><option value="correctedBase">Corrected Base · 校正底图</option>');
    const row=document.createElement('label');row.className='check';
    row.innerHTML='<input id="correction" type="checkbox" checked> Intrinsic correction · 实验';
    row.querySelector('input')!.checked=engine.getSettings().correction>0;
    row.querySelector('input')!.addEventListener('change',e=>engine.setSettings({correction:Number((e.target as HTMLInputElement).checked)}));
    query('#lighting-controls').append(row);
  }
  view.insertAdjacentHTML('beforeend', '<option value="bright">Bright Pass</option><option value="bloom">Bloom Only</option><option value="neutral">Neutral Lighting</option><option value="projected">Projected Light Only</option><option value="exterior">Exterior Mask</option><option value="shadow">Shadow / Occlusion</option>');
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
  query<HTMLInputElement>('#blink').disabled=!engine.blinkAvailable;
  query<HTMLInputElement>('#blink').addEventListener('change',event=>engine.setBlink((event.target as HTMLInputElement).checked));
  query<HTMLButtonElement>('#trigger-blink').addEventListener('click',()=>engine.triggerBlink());
  query<HTMLInputElement>('#reduced').addEventListener('change',event=>engine.setReducedMotion((event.target as HTMLInputElement).checked));
  const stats=document.createElement('p'); stats.className='note'; stats.id='gpu-stats';
  query('.controls').append(stats);
  const updateStats=()=>{ const s=engine.getStats(); stats.textContent=`GPU ${s.canvasWidth}×${s.canvasHeight} · Textures ${s.sourceTextureMiB} MiB · Bloom ${s.bloomWidth}×${s.bloomHeight} (${s.bloomTextureMiB} MiB)`; };
  updateStats();
  const statsTimer=window.setInterval(updateStats,1000);
  return { update(state: HeroState) {
    query('#clock').textContent=formatTime(state.minutes);
    query('#mode').textContent=state.realtime?'LOCAL TIME':'MANUAL';
    realtime.checked=state.realtime;
    if(document.activeElement!==time) time.value=String(Math.round(state.target));
    query('#target').textContent=Number(time.value)===1440?'24:00':formatTime(state.target);
    query<HTMLInputElement>('#reduced').checked=state.reducedMotion;
    query<HTMLInputElement>('#animation').checked=state.animation;
    query<HTMLInputElement>('#blink').checked=state.blink;
    query<HTMLInputElement>('#breathing').checked=state.breathing;
    query('#breathing-status').textContent=state.breathingStatus;
    query('#breathing-displacement').textContent=`${state.breathingDisplacement.toFixed(2)} px`;
    query('#breathing-displacement').title='Peak local displacement in original artwork pixels';
    query<HTMLButtonElement>('#trigger-blink').disabled=!state.blink || !state.animation || state.reducedMotion;
    query('#blink-phase').textContent=state.blinkPhase;
  }, destroy() { window.clearInterval(statsTimer); root.replaceChildren(); } };
}
