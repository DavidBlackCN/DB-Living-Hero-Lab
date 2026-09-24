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

export const skyKeyframes: ReadonlyArray<{ id: SkyPhaseId; minutes: number }> = [
  { id: 'dawn', minutes: 390 },
  { id: 'noon', minutes: 720 },
  { id: 'dusk', minutes: 1050 },
  { id: 'night', minutes: 1320 },
]

const clamp01 = (value: number): number => Math.max(0, Math.min(1, value))

function smooth(amount: number): number {
  const t = clamp01(amount)
  return t * t * (3 - 2 * t)
}

export function skyFor(minutes: number): SkyState {
  const input = Number.isFinite(minutes) ? Math.max(0, Math.min(1440, minutes)) : 720
  const value = input === 1440 ? 0 : input
  const count = skyKeyframes.length

  for (let index = 0; index < count; index++) {
    const start = skyKeyframes[index]
    const nextIndex = (index + 1) % count
    const end = skyKeyframes[nextIndex]
    const endMinute = nextIndex === 0 ? end.minutes + 1440 : end.minutes
    const sampleMinute = value < start.minutes ? value + 1440 : value
    if (sampleMinute >= start.minutes && sampleMinute <= endMinute) {
      return {
        first: start.id,
        second: end.id,
        mix: smooth((sampleMinute - start.minutes) / (endMinute - start.minutes)),
      }
    }
  }

  return { first: 'night', second: 'dawn', mix: 0 }
}
