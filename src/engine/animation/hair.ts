export const hairConfig = {
  primaryPeriodSeconds: 6.4,
  secondaryPeriodSeconds: 9.1,
  loopSeconds: 582.4,
  maxDisplacementPx: 5.2,
  headMassDisplacementPx: 1.8,
  headHairDisplacementPx: 3.0,
} as const

export interface HairState {
  enabled: boolean
  strength: number
  showRegion: boolean
}
