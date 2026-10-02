import type { QualityPreset } from '../types'

export type ResolvedQuality = 'high' | 'medium' | 'low' | 'static'
export interface DeviceHints { cores?: number; memory?: number; saveData?: boolean }
export const qualityBudgets = {
  high: { pixels: 8294400, dpr: 2, leaves: 18, mobileLeaves: 10, leafDpr: 1.5, motion: true },
  medium: { pixels: 3686400, dpr: 1.5, leaves: 12, mobileLeaves: 8, leafDpr: 1, motion: true },
  low: { pixels: 2073600, dpr: 1, leaves: 0, mobileLeaves: 0, leafDpr: 1, motion: false },
  static: { pixels: 0, dpr: 1, leaves: 0, mobileLeaves: 0, leafDpr: 1, motion: false },
} as const

export function resolveQuality(preset: QualityPreset, hints: DeviceHints = {}): ResolvedQuality {
  if (preset === 'balanced') return 'medium' // legacy host compatibility
  if (preset !== 'auto') return preset
  if (hints.saveData || (hints.memory !== undefined && hints.memory <= 2)) return 'static'
  if (hints.cores !== undefined && hints.cores <= 2) return 'low'
  if ((hints.memory !== undefined && hints.memory <= 4) || (hints.cores !== undefined && hints.cores <= 4)) return 'medium'
  return 'high'
}

export function lowerQuality(value: ResolvedQuality): ResolvedQuality {
  return value === 'high' ? 'medium' : value === 'medium' ? 'low' : value
}
