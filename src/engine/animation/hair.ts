export const hairConfig = {
  primaryPeriodSeconds: 6.4,
  secondaryPeriodSeconds: 9.1,
  loopSeconds: 582.4,
  maxDisplacementPx: 5.2,
  headMassDisplacementPx: 0.9,
  headHairDisplacementPx: 2.1,
} as const

export interface HairState {
  enabled: boolean
  strength: number
  showRegion: boolean
}
