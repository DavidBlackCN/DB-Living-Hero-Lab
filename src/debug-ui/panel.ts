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
    <p class="note">手工轮廓遮罩 / 低频法线 · 仍为近似<br>当前阶段不含眨眼、呼吸与蒸汽。</p></div></details>`;
  const query = <T extends HTMLElement>(selector: string) => root.querySelector<T>(selector)!;
  for(const [key,label,min,max,value] of [
    ['exposure','曝光 EV',-1,1,0],['ambient','环境光',0,2,1],['sun','窗光',0,2,1],['lamp','台灯',0,2,1],['normal','法线强度',0,2,1],['face','脸部保护',0,1,.8],
    ['hair','头发受光',0,2,.85],['cloth','服装受光',0,2,.9],['night','夜间日光抑制',0,1,1],
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
  const steam = document.createElement('label');
  steam.className = 'check';
  steam.innerHTML = '<input id="steam" type="checkbox" checked> Coffee steam';
  query('#animation').parentElement!.insertAdjacentElement('afterend', steam);
  query<HTMLInputElement>('#steam').addEventListener('change',event=>engine.setSteam((event.target as HTMLInputElement).checked));
  query<HTMLInputElement>('#animation').addEventListener('change',event=>engine.setAnimation((event.target as HTMLInputElement).checked));
  query<HTMLInputElement>('#reduced').addEventListener('change',event=>engine.setReducedMotion((event.target as HTMLInputElement).checked));
  return { update(state: HeroState) {
    query('#clock').textContent=formatTime(state.minutes);
    query('#mode').textContent=state.realtime?'LOCAL TIME':'MANUAL';
    realtime.checked=state.realtime;
    if(document.activeElement!==time) time.value=String(Math.round(state.target));
    query('#target').textContent=Number(time.value)===1440?'24:00':formatTime(state.target);
    query<HTMLInputElement>('#reduced').checked=state.reducedMotion;
  }, destroy() { root.replaceChildren(); } };
}
