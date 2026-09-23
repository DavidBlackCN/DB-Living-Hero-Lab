import type { LightingPresetId, LightingState } from '../engine/types'

export interface LightingPreset {
  id: LightingPresetId
  label: string
  lighting: Omit<LightingState, 'enabled'>
}

export const lightingPresets: Record<LightingPresetId, LightingPreset> = {
  dawn: {
    id: 'dawn',
    label: 'Dawn',
    lighting: {
      exposure: 0.98,
      direction: { x: -0.62, y: 0.06, z: 0.78 },
      intensity: 0.32,
      color: { r: 1, g: 0.78, b: 0.61 },
      ambientIntensity: 0.055,
      ambientColor: { r: 0.86, g: 0.78, b: 0.83 },
      diffuseWrap: 0.22,
      diffuseThreshold: 0.85,
      diffuseSoftness: 0.1,
    },
  },
  noon: {
    id: 'noon',
    label: 'Noon',
    lighting: {
      exposure: 1,
      direction: { x: 0.12, y: -0.2, z: 0.97 },
      intensity: 0.28,
      color: { r: 1, g: 0.96, b: 0.9 },
      ambientIntensity: 0.04,
      ambientColor: { r: 0.86, g: 0.91, b: 1 },
      diffuseWrap: 0.24,
      diffuseThreshold: 0.86,
      diffuseSoftness: 0.12,
    },
  },
  dusk: {
    id: 'dusk',
    label: 'Dusk',
    lighting: {
      exposure: 0.94,
      direction: { x: 0.68, y: 0.12, z: 0.72 },
      intensity: 0.34,
      color: { r: 1, g: 0.64, b: 0.43 },
      ambientIntensity: 0.05,
      ambientColor: { r: 0.66, g: 0.72, b: 0.94 },
      diffuseWrap: 0.2,
      diffuseThreshold: 0.84,
      diffuseSoftness: 0.1,
    },
  },
  night: {
    id: 'night',
    label: 'Night',
    lighting: {
      exposure: 0.78,
      direction: { x: -0.38, y: 0.04, z: 0.92 },
      intensity: 0.2,
      color: { r: 0.72, g: 0.8, b: 1 },
      ambientIntensity: 0.07,
      ambientColor: { r: 0.64, g: 0.73, b: 1 },
      diffuseWrap: 0.28,
      diffuseThreshold: 0.8,
      diffuseSoftness: 0.16,
    },
  },
}

export function createLightingState(preset: LightingPresetId): LightingState {
  return { enabled: true, ...structuredClone(lightingPresets[preset].lighting) }
}

export const defaultLighting: LightingState = createLightingState('noon')
