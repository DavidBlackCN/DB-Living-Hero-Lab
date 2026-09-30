import { postTimeWeights } from './post'

export interface AtmosphereState {
  enabled: boolean
  hazeEnabled: boolean
  gradeEnabled: boolean
  hazeAmount: number
  depthSaturation: number
  airColor: [number, number, number]
  saturation: number
  tint: [number, number, number]
  bloomScale: number
  bloomProtection: number
}

// Final display polish, independent of the frozen scene/character light field.
// Noon is identity. Other phases use the same continuous windows as R6 Post.
export function atmosphereFor(minutes: number): Omit<AtmosphereState, 'enabled' | 'hazeEnabled' | 'gradeEnabled'> {
  const { dawn, day, dusk, night } = postTimeWeights(minutes)
  return {
    hazeAmount: dawn * 0.045 + dusk * 0.035 + night * 0.050,
    depthSaturation: 1 - dawn * 0.025 - dusk * 0.015 - night * 0.045,
    airColor: [
      dawn * 0.60 + day * 0.62 + dusk * 0.57 + night * 0.15,
      dawn * 0.65 + day * 0.65 + dusk * 0.43 + night * 0.18,
      dawn * 0.72 + day * 0.69 + dusk * 0.36 + night * 0.23,
    ],
    saturation: 1 - dawn * 0.004 + dusk * 0.003 - night * 0.010,
    tint: [1 - dawn * 0.002 - night * 0.003 + dusk * 0.003,
      1, 1 + dawn * 0.002 + night * 0.003 - dusk * 0.001],
    bloomScale: 1 - dawn * 0.25 - dusk * 0.25,
    bloomProtection: 1 - day,
  }
}
