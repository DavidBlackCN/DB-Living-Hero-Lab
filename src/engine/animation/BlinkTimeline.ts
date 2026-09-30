export interface BlinkConfig {
  eyes: ReadonlyArray<{ url: string; x: number; y: number; width: number; height: number }>
  intervalMinMs: number
  intervalMaxMs: number
  durationMs: number
}

export function blinkAmountAt(ageMs: number, durationMs: number): number {
  if (ageMs <= 0 || ageMs >= durationMs) return 0
  return Math.pow(Math.sin(Math.PI * ageMs / durationMs), 0.6)
}

export class BlinkTimeline {
  private nextTimer: number | undefined
  private frame: number | undefined
  private enabled = false
  private visible = true

  constructor(private config: BlinkConfig, private onAmountChange: (amount: number) => void) {}

  setEnabled(enabled: boolean): void {
    this.enabled = enabled
    this.clearTimers()
    this.onAmountChange(0)
    this.schedule()
  }

  setVisible(visible: boolean): void {
    this.visible = visible
    this.clearTimers()
    this.onAmountChange(0)
    this.schedule()
  }

  preview(): void {
    if (!this.visible) return
    this.clearTimers()
    this.startBlink()
  }

  destroy(): void {
    this.enabled = false
    this.clearTimers()
    this.onAmountChange(0)
  }

  private startBlink(): void {
    const startedAt = performance.now()
    const tick = (now: number): void => {
      const age = now - startedAt
      this.onAmountChange(blinkAmountAt(age, this.config.durationMs))
      if (age < this.config.durationMs && this.visible) {
        this.frame = requestAnimationFrame(tick)
      } else {
        this.frame = undefined
        this.onAmountChange(0)
        this.schedule()
      }
    }
    this.frame = requestAnimationFrame(tick)
  }

  private schedule(): void {
    if (!this.enabled || !this.visible) return
    const { intervalMinMs, intervalMaxMs } = this.config
    const delay = intervalMinMs + Math.random() * (intervalMaxMs - intervalMinMs)
    this.nextTimer = window.setTimeout(() => {
      this.nextTimer = undefined
      this.startBlink()
    }, delay)
  }

  private clearTimers(): void {
    window.clearTimeout(this.nextTimer)
    if (this.frame !== undefined) cancelAnimationFrame(this.frame)
    this.nextTimer = undefined
    this.frame = undefined
  }
}
