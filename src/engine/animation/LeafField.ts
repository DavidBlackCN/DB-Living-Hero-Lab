import { loadImage } from '../assets/loadImage'
import type { ArtworkLayout } from '../coordinates/artwork'

export interface LeafConfig {
  urls: readonly string[]
  desktopCount: number
  mobileCount: number
  mobileBreakpoint: number
  minVisibleSize: number
  maxVisibleSize: number
  foregroundChance: number
  foregroundVisibleSize: number
  minFallSpeed: number
  maxFallSpeed: number
  windSpeed: number
  gustSpeed: number
  gustPeriodMs: number
  swaySpeed: number
  minOpacity: number
  maxOpacity: number
  fpsCap: number
  dprCap: number
}

interface Leaf {
  image: HTMLImageElement
  x: number
  y: number
  size: number
  fallSpeed: number
  rotation: number
  rotationSpeed: number
  phase: number
  swayRate: number
  opacity: number
}

interface VisibleRect { x: number; y: number; width: number; height: number }

const randomBetween = (min: number, max: number): number => min + Math.random() * (max - min)

export class LeafField {
  private ctx: CanvasRenderingContext2D
  private images: HTMLImageElement[] = []
  private leaves: Leaf[] = []
  private layout: ArtworkLayout
  private rect: VisibleRect
  private raf = 0
  private lastTime = 0
  private destroyed = false

  constructor(private canvas: HTMLCanvasElement, private config: LeafConfig, layout: ArtworkLayout, private onCount: (count: number) => void) {
    const ctx = canvas.getContext('2d', { alpha: true })
    if (!ctx) throw new Error('2D canvas unavailable for leaves')
    this.ctx = ctx
    this.layout = layout
    this.rect = this.visibleRect(layout)
    this.resizeCanvas()
    document.addEventListener('visibilitychange', this.onVisibility)
  }

  async start(): Promise<void> {
    const results = await Promise.allSettled(this.config.urls.map(loadImage))
    if (this.destroyed) return
    this.images = results.flatMap(result => result.status === 'fulfilled' ? [result.value] : [])
    if (this.images.length === 0) {
      this.onCount(0)
      console.warn('Living Hero leaves: no textures could be loaded')
      return
    }
    this.reconcileCount()
    if (!document.hidden) this.raf = requestAnimationFrame(this.tick)
  }

  updateLayout(layout: ArtworkLayout): void {
    this.layout = layout
    this.rect = this.visibleRect(layout)
    this.resizeCanvas()
    this.reconcileCount()
    if (document.hidden) return
    this.draw()
  }

  destroy(): void {
    if (this.destroyed) return
    this.destroyed = true
    cancelAnimationFrame(this.raf)
    document.removeEventListener('visibilitychange', this.onVisibility)
    this.leaves = []
    this.onCount(0)
  }

  private visibleRect(layout: ArtworkLayout): VisibleRect {
    const x = Math.max(0, layout.x)
    const y = Math.max(0, layout.y)
    const right = Math.min(layout.viewportWidth, layout.x + layout.width)
    const bottom = Math.min(layout.viewportHeight, layout.y + layout.height)
    return { x, y, width: Math.max(0, right - x), height: Math.max(0, bottom - y) }
  }

  private resizeCanvas(): void {
    const dpr = Math.min(window.devicePixelRatio || 1, this.config.dprCap)
    this.canvas.width = Math.max(1, Math.round(this.layout.viewportWidth * dpr))
    this.canvas.height = Math.max(1, Math.round(this.layout.viewportHeight * dpr))
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  private newLeaf(initial: boolean): Leaf {
    const size = Math.random() < this.config.foregroundChance
      ? this.config.foregroundVisibleSize
      : randomBetween(this.config.minVisibleSize, this.config.maxVisibleSize)
    return {
      image: this.images[Math.floor(Math.random() * this.images.length)]!,
      x: Math.random(),
      y: initial ? Math.random() : -size / Math.max(1, this.rect.height),
      size,
      fallSpeed: randomBetween(this.config.minFallSpeed, this.config.maxFallSpeed),
      rotation: randomBetween(-Math.PI, Math.PI),
      rotationSpeed: randomBetween(-0.15, 0.15),
      phase: randomBetween(0, Math.PI * 2),
      swayRate: randomBetween(0.55, 1.05),
      opacity: randomBetween(this.config.minOpacity, this.config.maxOpacity),
    }
  }

  private reconcileCount(): void {
    if (this.images.length === 0) return
    const target = this.layout.viewportWidth <= this.config.mobileBreakpoint ? this.config.mobileCount : this.config.desktopCount
    while (this.leaves.length < target) this.leaves.push(this.newLeaf(true))
    if (this.leaves.length > target) this.leaves.length = target
    this.onCount(this.leaves.length)
  }

  private tick = (time: number): void => {
    if (this.destroyed || document.hidden) return
    this.raf = requestAnimationFrame(this.tick)
    if (this.lastTime && time - this.lastTime < 1000 / this.config.fpsCap) return
    const dt = this.lastTime ? Math.min((time - this.lastTime) / 1000, 0.05) : 0
    this.lastTime = time
    const sharedWind = this.config.windSpeed + this.config.gustSpeed * Math.sin(time * 2 * Math.PI / this.config.gustPeriodMs)
    for (const leaf of this.leaves) {
      leaf.x += (sharedWind + Math.sin(time / 1000 * leaf.swayRate + leaf.phase) * this.config.swaySpeed) * dt / Math.max(1, this.rect.width)
      leaf.y += leaf.fallSpeed * dt / Math.max(1, this.rect.height)
      leaf.rotation += leaf.rotationSpeed * dt
      if (leaf.y > 1 + leaf.size / Math.max(1, this.rect.height) || leaf.x < -0.15 || leaf.x > 1.15) {
        Object.assign(leaf, this.newLeaf(false))
      }
    }
    this.draw(time)
  }

  private draw(time = performance.now()): void {
    const { ctx, rect } = this
    ctx.clearRect(0, 0, this.layout.viewportWidth, this.layout.viewportHeight)
    if (rect.width <= 0 || rect.height <= 0) return
    ctx.save()
    ctx.beginPath()
    ctx.rect(rect.x, rect.y, rect.width, rect.height)
    ctx.clip()
    for (const leaf of this.leaves) {
      const spriteSize = leaf.size / 0.73 // masters use ~73% of their transparent square
      const tilt = 0.78 + 0.22 * Math.cos(time / 1000 * leaf.swayRate + leaf.phase)
      ctx.save()
      ctx.translate(rect.x + leaf.x * rect.width, rect.y + leaf.y * rect.height)
      ctx.rotate(leaf.rotation)
      ctx.scale(tilt, 1)
      ctx.globalAlpha = leaf.opacity
      ctx.drawImage(leaf.image, -spriteSize / 2, -spriteSize / 2, spriteSize, spriteSize)
      ctx.restore()
    }
    ctx.restore()
  }

  private onVisibility = (): void => {
    if (document.hidden) {
      cancelAnimationFrame(this.raf)
      this.lastTime = 0
    } else if (!this.destroyed && this.images.length > 0) {
      this.lastTime = 0
      this.raf = requestAnimationFrame(this.tick)
    }
  }
}
