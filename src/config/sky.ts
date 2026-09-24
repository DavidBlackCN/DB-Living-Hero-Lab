export type SkyPhaseId = 'dawn' | 'noon' | 'dusk' | 'night'

export interface SkyState {
  first: SkyPhaseId
  second: SkyPhaseId
  mix: number
}

export const skyAssets: Record<SkyPhaseId, string> = {
  dawn: `${import.meta.env.BASE_URL}assets/hero/sky/sky-dawn.png`,
  noon: `${import.meta.env.BASE_URL}assets/hero/sky/sky-noon.png`,
  dusk: `${import.meta.env.BASE_URL}assets/hero/sky/sky-dusk.png`,
  night: `${import.meta.env.BASE_URL}assets/hero/sky/sky-night.png`,
}

// Preview shortcuts are not sky phase boundaries. Keep the authored Dawn and
// Dusk assets at their shortcut times while holding Night through the night.
const skyTransitions: ReadonlyArray<{ start: number; end: number; first: SkyPhaseId; second: SkyPhaseId }> = [
  { start: 300, end: 390, first: 'night', second: 'dawn' },
  { start: 390, end: 480, first: 'dawn', second: 'noon' },
  { start: 960, end: 1050, first: 'noon', second: 'dusk' },
  { start: 1050, end: 1200, first: 'dusk', second: 'night' },
]

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value))

function smooth(amount: number): number {
  const t = clamp01(amount)
  return t * t * (3 - 2 * t)
}

export function skyFor(minutes: number): SkyState {
  const input = Number.isFinite(minutes) ? Math.max(0, Math.min(1440, minutes)) : 720
  const value = input === 1440 ? 0 : input

  for (const transition of skyTransitions) {
    if (value >= transition.start && value < transition.end) {
      return { first: transition.first, second: transition.second, mix: smooth((value - transition.start) / (transition.end - transition.start)) }
    }
  }

  const phase: SkyPhaseId = value >= 480 && value < 960 ? 'noon' : 'night'
  return { first: phase, second: phase, mix: 0 }
}
