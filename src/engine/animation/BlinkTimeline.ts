export interface BlinkConfig {
  eyes: ReadonlyArray<{ url: string; x: number; y: number; width: number; height: number }>
  intervalMinMs: number
  intervalMaxMs: number
  closedMs: number
}

export class BlinkTimeline {
  private nextTimer: number | undefined
  private openTimer: number | undefined
  private enabled = false
  private visible = true

  constructor(private config: BlinkConfig, private onClosedChange: (closed: boolean) => void) {}

  setEnabled(enabled: boolean): void {
    this.enabled = enabled
    this.clearTimers()
    this.onClosedChange(false)
    this.schedule()
  }

  setVisible(visible: boolean): void {
    this.visible = visible
    this.clearTimers()
    this.onClosedChange(false)
    this.schedule()
  }

  preview(): void {
    if (!this.visible) return
    this.clearTimers()
    this.close()
  }

  destroy(): void {
    this.enabled = false
    this.clearTimers()
    this.onClosedChange(false)
  }

  private close(): void {
    this.onClosedChange(true)
    this.openTimer = window.setTimeout(() => {
      this.openTimer = undefined
      this.onClosedChange(false)
      this.schedule()
    }, this.config.closedMs)
  }

  private schedule(): void {
    if (!this.enabled || !this.visible) return
    const { intervalMinMs, intervalMaxMs } = this.config
    const delay = intervalMinMs + Math.random() * (intervalMaxMs - intervalMinMs)
    this.nextTimer = window.setTimeout(() => {
      this.nextTimer = undefined
      this.close()
    }, delay)
  }

  private clearTimers(): void {
    window.clearTimeout(this.nextTimer)
    window.clearTimeout(this.openTimer)
    this.nextTimer = undefined
    this.openTimer = undefined
  }
}
