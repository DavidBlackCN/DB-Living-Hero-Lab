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
// All phases have background depth; R6 Scene and Bloom settings stay intact.
export function atmosphereFor(minutes: number): Omit<AtmosphereState, 'enabled' | 'hazeEnabled' | 'gradeEnabled'> {
  const { dawn, day, dusk, night } = postTimeWeights(minutes)
  return {
    hazeAmount: dawn * 0.090 + day * 0.120 + dusk * 0.160 + night * 0.200,
    depthSaturation: 1 - dawn * 0.050 - day * 0.040 - dusk * 0.065 - night * 0.080,
    airColor: [
      dawn * 0.60 + day * 0.67 + dusk * 0.60 + night * 0.21,
      dawn * 0.65 + day * 0.68 + dusk * 0.45 + night * 0.235,
      dawn * 0.72 + day * 0.70 + dusk * 0.38 + night * 0.27,
    ],
    saturation: 1 - dawn * 0.004 + dusk * 0.003 - night * 0.010,
    tint: [1 - dawn * 0.002 - night * 0.003 + dusk * 0.003,
      1, 1 + dawn * 0.002 + night * 0.003 - dusk * 0.001],
    bloomScale: 1 - dawn * 0.25 - dusk * 0.25,
    bloomProtection: 1 - day,
  }
}
