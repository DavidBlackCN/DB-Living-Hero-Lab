import type { QualityPreset } from '../types'

export function useStaticRendering(preset: QualityPreset): boolean {
  // Reduced motion stops optional animation, but the on-demand lit image remains available.
  return preset === 'static'
}
