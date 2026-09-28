export type LampMaskView = 'none' | 'source' | 'influence'

export interface LampState {
  enabled: boolean
  strength: number
  weight: number
  maskView: LampMaskView
}

function smooth(start: number, end: number, value: number): number {
  const t = Math.max(0, Math.min(1, (value - start) / (end - start)))
  return t * t * (3 - 2 * t)
}

// Fixed artwork lamps share one eased switch, including across midnight.
export function lampWeightFor(minutes: number): number {
  const time = ((Number.isFinite(minutes) ? minutes : 720) % 1440 + 1440) % 1440
  const evening = smooth(1035, 1110, time)
  const morning = 1 - smooth(315, 390, time)
  return Math.max(evening, morning)
}
