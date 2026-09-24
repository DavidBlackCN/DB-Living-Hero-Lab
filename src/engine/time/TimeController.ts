export type TimeMode = 'realtime' | 'manual' | 'playing'

export interface TimeSnapshot {
  mode: TimeMode
  minutes: number
}

export const DAY_MINUTES = 1440
export const PLAYBACK_MINUTES_PER_MS = DAY_MINUTES / 60_000

export function clockMinutes(date: Date): number {
  return date.getHours() * 60 + date.getMinutes() + date.getSeconds() / 60 + date.getMilliseconds() / 60_000
}

export function wrapMinutes(minutes: number): number {
  return ((minutes % DAY_MINUTES) + DAY_MINUTES) % DAY_MINUTES
}

export function playbackMinutes(start: number, elapsedMs: number): number {
  return wrapMinutes(start + Math.max(0, elapsedMs) * PLAYBACK_MINUTES_PER_MS)
}

export class TimeController {
  private state: TimeSnapshot
  private interval: ReturnType<typeof setInterval> | null = null
  private frame: number | null = null
  private lastFrame: number | null = null
  private visible = true

  constructor(private readonly onChange: (state: TimeSnapshot) => void, now = new Date()) {
    this.state = { mode: 'realtime', minutes: clockMinutes(now) }
  }

  get snapshot(): TimeSnapshot { return { ...this.state } }

  start(): void { this.schedule() }

  select(minutes: number): void {
    if (!Number.isFinite(minutes)) return
    this.stopDrivers()
    this.setState('manual', Math.max(0, Math.min(DAY_MINUTES, Math.round(minutes))))
  }

  backToNow(): void {
    this.stopDrivers()
    this.setState('realtime', clockMinutes(new Date()))
    this.schedule()
  }

  play(): void {
    if (this.state.mode === 'playing') return
    this.stopDrivers()
    this.setState('playing', wrapMinutes(this.state.minutes))
    this.schedule()
  }

  pause(): void {
    if (this.state.mode !== 'playing') return
    this.stopDrivers()
    this.setState('manual', this.state.minutes)
  }

  setVisible(visible: boolean): void {
    if (this.visible === visible) return
    this.visible = visible
    this.stopDrivers()
    if (visible) {
      if (this.state.mode === 'realtime') this.setState('realtime', clockMinutes(new Date()))
      this.schedule()
    }
  }

  destroy(): void { this.stopDrivers() }

  private setState(mode: TimeMode, minutes: number): void {
    this.state = { mode, minutes }
    this.onChange(this.snapshot)
  }

  private schedule(): void {
    if (!this.visible) return
    if (this.state.mode === 'realtime') {
      this.interval = setInterval(() => this.setState('realtime', clockMinutes(new Date())), 1000)
    } else if (this.state.mode === 'playing') {
      this.lastFrame = null
      this.frame = requestAnimationFrame(this.tick)
    }
  }

  private tick = (timestamp: number): void => {
    if (this.state.mode !== 'playing' || !this.visible) return
    if (this.lastFrame !== null) {
      this.setState('playing', playbackMinutes(this.state.minutes, timestamp - this.lastFrame))
    }
    this.lastFrame = timestamp
    this.frame = requestAnimationFrame(this.tick)
  }

  private stopDrivers(): void {
    if (this.interval !== null) clearInterval(this.interval)
    if (this.frame !== null) cancelAnimationFrame(this.frame)
    this.interval = null
    this.frame = null
    this.lastFrame = null
  }
}
