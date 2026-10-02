import type { FitMode, QualityPreset, RenderView } from './engine/types'
import type { ResolvedQuality } from './engine/quality/policy'

export interface LivingHeroProps {
  assetRoot?: string
  quality?: QualityPreset
  fit?: FitMode
  minutes?: number
  debug?: boolean
  entrance?: boolean
  motion?: boolean
  view?: RenderView
  adjustments?: HeroAdjustments
  paused?: boolean
  adaptive?: boolean
  alt?: string
}
/** Optional viewer controls; undefined values use the frozen time-driven defaults. */
export interface HeroAdjustments {
  exposureOffset?: number
  bloomStrength?: number
  threshold?: number
  saturation?: number
  directionalStrength?: number
  bandSoftness?: number
}
export interface HeroStatus {
  mode: 'static' | 'fallback' | 'WebGL2' | 'loading'
  loaded: number
  total: number
  quality: ResolvedQuality
}
export interface LivingHeroHandle {
  setTime(minutes: number): void
  backToNow(): void
  play(): void
  pause(): void
  retry(): void
}
