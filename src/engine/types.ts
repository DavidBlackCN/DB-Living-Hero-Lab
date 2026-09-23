export interface ArtworkSpec {
  width: number
  height: number
  aspectRatio: number
  baseUrl: string
}

export type FitMode = 'auto' | 'cover' | 'contain'
export type QualityPreset = 'auto' | 'static' | 'balanced'
export type NormalView = 'base' | 'normal' | 'test-light'

export interface Point {
  x: number
  y: number
}
