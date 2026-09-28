import type { ArtworkSpec } from '../engine/types'
import type { LeafConfig } from '../engine/animation/LeafField'
import type { BlinkConfig } from '../engine/animation/BlinkTimeline'
import { defaultLighting } from './lighting'
import { skyAssets } from './sky'

export const heroConfig: { artwork: ArtworkSpec; blink: BlinkConfig; normal: { url: string }; sky: { urls: typeof skyAssets; edgeReconstructionUrl: string; edgeCoverageUrl: string }; hair: { maskUrl: string }; material: { maskUrl: string }; lamps: { sourceUrl: string; influenceUrl: string }; lighting: typeof defaultLighting; dprCap: number; leaves: LeafConfig } = {
  // The source is 1672×941, so use its true ratio for all registration math.
  artwork: {
    width: 1672,
    height: 941,
    aspectRatio: 1672 / 941,
    baseUrl: `${import.meta.env.BASE_URL}assets/hero/base/base-albedo.png`,
  },
  blink: {
    eyes: [
      { url: `${import.meta.env.BASE_URL}assets/hero/blink/left-closed-v1.png`, x: 1080, y: 177, width: 92, height: 73 },
      { url: `${import.meta.env.BASE_URL}assets/hero/blink/right-closed-v1.png`, x: 1152, y: 195, width: 92, height: 78 },
    ],
    intervalMinMs: 4200,
    intervalMaxMs: 7600,
    closedMs: 115,
  },
  normal: {
    url: `${import.meta.env.BASE_URL}assets/hero/normal/base-normal-v3.png`,
  },
  sky: { urls: skyAssets, edgeReconstructionUrl: `${import.meta.env.BASE_URL}assets/hero/sky/sky-edge-reconstruction.png`, edgeCoverageUrl: `${import.meta.env.BASE_URL}assets/hero/sky/sky-edge-skyfill.png` },
  hair: { maskUrl: `${import.meta.env.BASE_URL}assets/hero/motion/hair-motion-mask.png` },
  material: { maskUrl: `${import.meta.env.BASE_URL}assets/hero/material/material-mask.png` },
  lamps: { sourceUrl: `${import.meta.env.BASE_URL}assets/hero/lighting/lamp-source-mask.png`, influenceUrl: `${import.meta.env.BASE_URL}assets/hero/lighting/lamp-influence-mask.png` },
  lighting: defaultLighting,
  dprCap: 2,
  leaves: {
    urls: [1, 2, 3, 4].map(n => `${import.meta.env.BASE_URL}assets/hero/leaves/leaf-${String(n).padStart(2, '0')}.png`),
    desktopCount: 18,
    mobileCount: 10,
    mobileBreakpoint: 640,
    minVisibleSize: 15,
    maxVisibleSize: 30,
    backgroundChance: 0.17,
    foregroundChance: 0.10,
    foregroundVisibleSize: 37,
    minFallSpeed: 11,
    maxFallSpeed: 22,
    windSpeed: 2.5,
    gustSpeed: 3.6,
    gustPeriodMs: 9300,
    swaySpeed: 2.7,
    minOpacity: 0.56,
    maxOpacity: 0.80,
    fpsCap: 30,
    dprCap: 1.5,
  },
}
