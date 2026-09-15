export const wrapTime = (minutes: number) => ((minutes % 1440) + 1440) % 1440;
export function localMinutes(date = new Date()) {
  return date.getHours() * 60 + date.getMinutes() + date.getSeconds() / 60;
}
export function formatTime(minutes: number) {
  const value = Math.floor(wrapTime(minutes));
  return `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(value % 60).padStart(2, '0')}`;
}
export class Timeline {
  minutes: number;
  target: number;
  realtime = false;
  constructor(minutes = 720) { this.minutes = this.target = wrapTime(minutes); }
  setTime(minutes: number) {
    if (!Number.isFinite(minutes)) throw new Error('Time must be finite');
    this.realtime = false; this.target = wrapTime(minutes);
  }
  update(dt: number, reducedMotion: boolean) {
    if (this.realtime) this.target = localMinutes();
    const delta = ((this.target - this.minutes + 2160) % 1440) - 720;
    this.minutes = wrapTime(this.minutes + delta * (reducedMotion ? 1 : 1 - Math.exp(-dt * 8)));
    if (Math.abs(delta) < 0.01) this.minutes = this.target;
  }
}
