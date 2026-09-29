export const hairConfig = {
  primaryPeriodSeconds: 6.4,
  secondaryPeriodSeconds: 9.1,
  loopSeconds: 582.4,
  maxDisplacementPx: 5.8,
  headMassDisplacementPx: 2.5,
  headHairDisplacementPx: 3.6,
} as const

export interface HairState {
  enabled: boolean
  strength: number
  showRegion: boolean
}
