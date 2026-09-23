import type { QualityPreset } from '../types'

export function useStaticRendering(preset: QualityPreset, reducedMotion: boolean): boolean {
  return preset === 'static' || (preset === 'auto' && reducedMotion)
}
