// All positions and displacement values use the frozen 1672×941 Artwork Space.
export const breathingConfig = {
  periodSeconds: 5.2,
  maxDisplacementPx: 4.8,
} as const

export interface BreathingState {
  enabled: boolean
  strength: number
  showRegion: boolean
}
