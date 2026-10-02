import type { FitMode, QualityPreset } from './engine/types'
import type { ResolvedQuality } from './engine/quality/policy'

export interface LivingHeroProps {
  assetRoot?: string
  quality?: QualityPreset
  fit?: FitMode
  minutes?: number
  debug?: boolean
  entrance?: boolean
  paused?: boolean
  adaptive?: boolean
  alt?: string
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
