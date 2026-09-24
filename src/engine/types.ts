export interface ArtworkSpec {
  width: number
  height: number
  aspectRatio: number
  baseUrl: string
}

export type FitMode = 'auto' | 'cover' | 'contain'
export type QualityPreset = 'auto' | 'static' | 'balanced'
export type RenderView = 'base' | 'normal' | 'lit'
export type LightingPresetId = 'dawn' | 'noon' | 'dusk' | 'night'

export interface RGBColor {
  r: number
  g: number
  b: number
}

export interface LightingState {
  enabled: boolean
  exposureStops: number
  relightStrength: number
  direction: { x: number; y: number; z: number }
  intensity: number
  color: RGBColor
  ambientIntensity: number
  ambientColor: RGBColor
  diffuseWrap: number
  diffuseThreshold: number
  diffuseSoftness: number
  bandStrength: number
  bandThreshold: number
  bandSoftness: number
  upperSceneAttenuation: number
  skyEnabled: boolean
}

export interface Point {
  x: number
  y: number
}
