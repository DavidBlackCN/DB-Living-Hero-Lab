export type BlinkPhase = 'open' | 'half' | 'closed';

/** Clocked by the renderer; owns no timers and never catches up hidden time. */
export class BlinkController {
  private remaining: number;
  private elapsed: number | null = null;
  private previous: number | null = null;
  constructor(private random: () => number = Math.random) { this.remaining = this.interval(); }
  private interval() { return 2800 + this.random() * 2700; }
  get phase(): BlinkPhase {
    return this.elapsed === null ? 'open' : this.elapsed < 40 || this.elapsed >= 110 ? 'half' : 'closed';
  }
  get active() { return this.elapsed !== null; }
  get delay() { return this.active ? 0 : this.remaining; }
  trigger(now: number) {
    if (this.active) return false;
    this.elapsed = 0; this.previous = now;
    return true;
  }
  update(now: number) {
    const dt = this.previous === null ? 0 : Math.max(0, now - this.previous);
    this.previous = now;
    if (this.elapsed !== null) {
      this.elapsed += dt;
      if (this.elapsed >= 160) { this.elapsed = null; this.remaining = this.interval(); }
    } else {
      this.remaining -= dt;
      if (this.remaining <= 0) this.trigger(now);
    }
  }
  pause() { this.previous = null; }
  reset() { this.elapsed = null; this.remaining = this.interval(); this.pause(); }
}

export interface BlinkMetadata {
  version: 1;
  canvas: { width: number; height: number };
  crop: { x: number; y: number; width: number; height: number };
  alpha: 'straight';
  colorSpace: 'srgb';
  states: { half: string; closed: string };
}

export function validateBlinkMetadata(value: unknown, width: number, height: number): asserts value is BlinkMetadata {
  const m = value as BlinkMetadata | null;
  const c = m?.crop;
  if (m?.version !== 1 || m.alpha !== 'straight' || m.colorSpace !== 'srgb' ||
    m.canvas?.width !== width || m.canvas?.height !== height || !c ||
    ![c.x, c.y, c.width, c.height].every(Number.isInteger) ||
    c.x < 0 || c.y < 0 || c.width <= 0 || c.height <= 0 ||
    c.x + c.width > width || c.y + c.height > height ||
    typeof m.states?.half !== 'string' || !m.states.half ||
    typeof m.states?.closed !== 'string' || !m.states.closed) {
    throw new Error('Invalid Blink metadata or canvas registration');
  }
}
