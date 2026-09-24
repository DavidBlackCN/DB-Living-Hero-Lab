const smooth = (start: number, end: number, value: number): number => {
  const t = Math.max(0, Math.min(1, (value - start) / (end - start)))
  return t * t * (3 - 2 * t)
}

// CSS compositing bridge for the accepted Canvas2D leaves; LeafField is unchanged.
export function leafToneFor(minutes: number): { brightness: number; saturation: number } {
  const time = Number.isFinite(minutes) ? ((minutes % 1440) + 1440) % 1440 : 720
  const daylight = time < 300 || time >= 1200 ? 0
    : time < 480 ? smooth(300, 480, time)
      : time < 960 ? 1
        : 1 - smooth(960, 1200, time)
  return { brightness: 0.48 + 0.52 * daylight, saturation: 0.60 + 0.40 * daylight }
}
