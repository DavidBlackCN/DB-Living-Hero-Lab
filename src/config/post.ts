export type PostView = 'final' | 'bright' | 'bloom' | 'grade'

export interface PostState {
  enabled: boolean
  bloomEnabled: boolean
  view: PostView
  exposureStops: number
  threshold: number
  knee: number
  bloomStrength: number
  saturation: number
  contrast: number
  tint: [number, number, number]
}

const clamp01 = (v: number): number => Math.max(0, Math.min(1, v))
const smooth = (a: number, b: number, v: number): number => {
  const t = clamp01((v - a) / (b - a))
  return t * t * (3 - 2 * t)
}

// Continuous hold/transition windows. Both 00:00 and 24:00 are the same Night hold.
export function postFor(minutes: number): Omit<PostState, 'enabled' | 'bloomEnabled' | 'view'> {
  const t = ((Number.isFinite(minutes) ? minutes : 720) % 1440 + 1440) % 1440
  const dawn = smooth(300, 390, t) * (1 - smooth(390, 510, t))
  const day = smooth(390, 510, t) * (1 - smooth(960, 1050, t))
  const dusk = smooth(960, 1050, t) * (1 - smooth(1050, 1200, t))
  const night = Math.max(0, 1 - dawn - day - dusk)
  return {
    exposureStops: dawn * 0.015 - day * 0.018 + dusk * 0.008,
    threshold: night * 0.60 + dawn * 0.37 + day * 0.43 + dusk * 0.38,
    knee: 0.22,
    bloomStrength: night * 0.014 + dawn * 0.17 + day * 0.075 + dusk * 0.22,
    saturation: 1 - dawn * 0.008 + day * 0.008 + dusk * 0.025 - night * 0.012,
    contrast: 1 - dawn * 0.020 + day * 0.018 + dusk * 0.010 + night * 0.010,
    tint: [1 + dusk * 0.024 - dawn * 0.008 - night * 0.016,
      1 + dawn * 0.002 - dusk * 0.003 - night * 0.005,
      1 + dawn * 0.015 + night * 0.025 - dusk * 0.016],
  }
}
