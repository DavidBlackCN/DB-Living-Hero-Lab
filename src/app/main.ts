import './style.css';
import { createLivingHero } from '../engine/renderer';
import { createPanel } from '../debug-ui/panel';
const status=document.querySelector<HTMLElement>('#status')!;
let panel: ReturnType<typeof createPanel> | undefined;
try {
  const engine=await createLivingHero(document.querySelector<HTMLCanvasElement>('#hero')!,{
    // Keep both previous assets addressable for controlled same-light comparisons.
    normalUrl: new URLSearchParams(location.search).get('normal') === 'low-frequency'
      ? '/assets/generated/normal-low-frequency.svg'
      : ['registered','v1'].includes(new URLSearchParams(location.search).get('normal') ?? '')
        ? '/assets/generated/normal-registered-v1.png' : '/assets/generated/normal-registered-v2.png',
    maskUrl: '/assets/generated/character-masks.svg',
    sceneMaskUrl: '/assets/generated/scene-masks.svg',
    lightShapingUrl: '/assets/generated/light-shaping.svg',
    blinkMetadataUrl: '/assets/generated/blink/blink-metadata.json',
    correctionUrl: new URLSearchParams(location.search).get('correction') === '1'
      ? '/assets/generated/intrinsic-correction-v1.png' : undefined,
    onUpdate: state=>panel?.update(state), onError: message=>status.textContent=message,
  });
  engine.setSettings({correction:Number(engine.correctionAvailable)});
  panel=createPanel(document.querySelector('#debug')!,engine);
  (window as Window & { livingHero?: typeof engine }).livingHero = engine;
  panel.update(engine.getState());
  status.textContent='WEBGL2 · 3840 × 2160 · 完整构图 · DPR ≤ 1.5';
  window.addEventListener('pagehide',event=>{ if(!event.persisted) { panel?.destroy(); engine.destroy(); } });
} catch(error) {
  console.error(error); status.textContent=error instanceof Error?error.message:String(error);
  document.querySelector<HTMLCanvasElement>('#hero')!.style.background='url(/assets/hero-4k-digital-art.png) center / contain no-repeat';
}
