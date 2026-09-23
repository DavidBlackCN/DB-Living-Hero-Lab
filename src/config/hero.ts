import type { ArtworkSpec } from '../engine/types'

export const heroConfig: { artwork: ArtworkSpec; candidateBlinkUrl: string; dprCap: number } = {
  // The source is 1672×941, so use its true ratio for all registration math.
  artwork: {
    width: 1672,
    height: 941,
    aspectRatio: 1672 / 941,
    baseUrl: `${import.meta.env.BASE_URL}assets/hero/base/base-albedo.png`,
  },
  candidateBlinkUrl: `${import.meta.env.BASE_URL}assets/hero/blink/blink-closed-eyes-v1.png`,
  dprCap: 2,
}
