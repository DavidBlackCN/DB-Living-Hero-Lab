import type { ArtworkSpec } from '../engine/types'
import type { LeafConfig } from '../engine/animation/LeafField'

export const heroConfig: { artwork: ArtworkSpec; candidateBlinkUrl: string; dprCap: number; leaves: LeafConfig } = {
  // The source is 1672×941, so use its true ratio for all registration math.
  artwork: {
    width: 1672,
    height: 941,
    aspectRatio: 1672 / 941,
    baseUrl: `${import.meta.env.BASE_URL}assets/hero/base/base-albedo.png`,
  },
  candidateBlinkUrl: `${import.meta.env.BASE_URL}assets/hero/blink/blink-closed-eyes-v1.png`,
  dprCap: 2,
  leaves: {
    urls: [1, 2, 3, 4].map(n => `${import.meta.env.BASE_URL}assets/hero/leaves/leaf-${String(n).padStart(2, '0')}.png`),
    desktopCount: 18,
    mobileCount: 10,
    mobileBreakpoint: 640,
    minVisibleSize: 14,
    maxVisibleSize: 32,
    foregroundChance: 0.08,
    foregroundVisibleSize: 38,
    minFallSpeed: 10,
    maxFallSpeed: 22,
    windSpeed: 2.5,
    gustSpeed: 5,
    gustPeriodMs: 9000,
    swaySpeed: 2.5,
    minOpacity: 0.58,
    maxOpacity: 0.84,
    fpsCap: 30,
    dprCap: 1.5,
  },
}
