export interface MoonDirection {
  x: number
  y: number
  z: number
}

// Art-directed moon arc: it rises opposite the Dusk sun at 20:00, climbs
// toward the center overnight, then moves across the frame before Dawn.
// The existing Night sky weight controls its twilight fade separately.
export function moonDirectionFor(minutes: number): MoonDirection {
  const value = Number.isFinite(minutes) ? Math.max(0, Math.min(1440, minutes)) % 1440 : 0
  const nightMinutes = value < 300 ? value + 1440 : value
  const progress = Math.max(0, Math.min(1, (nightMinutes - 1200) / 540))
  const eased = progress * progress * (3 - 2 * progress)
  const azimuth = (35 + 110 * eased) * Math.PI / 180
  const elevation = (12 + 43 * Math.sin(Math.PI * progress)) * Math.PI / 180
  const planar = Math.cos(elevation)
  return { x: Math.cos(azimuth) * planar, y: Math.sin(azimuth) * planar, z: Math.sin(elevation) }
}
