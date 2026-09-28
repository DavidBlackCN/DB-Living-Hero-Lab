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
  backgroundChance: number
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

export type LeafDepth = 'background' | 'midground' | 'foreground'
export type LeafDebugView = 'none' | 'depth' | 'lamp-off'

interface Leaf {
  depth: LeafDepth
  sprite: LeafSprite
  x: number
  y: number
  size: number
  fallSpeed: number
  driftSpeed: number
  swayAmplitude: number
  rotation: number
  rotationSpeed: number
  phase: number
  swayRate: number
  turbulencePhase: number
  turbulenceRate: number
  liftPhase: number
  liftRate: number
  avoidanceSide: number
  opacity: number
}

interface LeafSprite {
  base: HTMLCanvasElement
  warm: HTMLCanvasElement
}

interface VisibleRect { x: number; y: number; width: number; height: number }

const ARTWORK_WIDTH = 1672
const ARTWORK_HEIGHT = 941
const FACE = { x: 1150, y: 242, rx: 112, ry: 98 }

function smooth(start: number, end: number, value: number): number {
  const t = Math.max(0, Math.min(1, (value - start) / (end - start)))
  return t * t * (3 - 2 * t)
}

function faceDistance(x: number, y: number, radius: number): number {
  return Math.hypot((x - FACE.x) / (FACE.rx + radius), (y - FACE.y) / (FACE.ry + radius))
}

// A small, artwork-space approximation of the existing corridor influence.
// It never changes the WebGL lamp mask or its surface-light response.
export function leafLampInfluence(x: number, y: number): number {
  if (x >= 390 || y >= 548) return 0
  const near = Math.exp(-2 * (((x - 52) / 151) ** 2 + ((y - 146) / 177) ** 2))
  const far = 0.94 * Math.exp(-2 * (((x - 159) / 165) ** 2 + ((y - 262) / 180) ** 2))
  return Math.max(near, far) * smooth(390, 342, x) * smooth(548, 488, y)
}

export class LeafField {
  private ctx: CanvasRenderingContext2D
  private sprites: LeafSprite[] = []
  private leaves: Leaf[] = []
  private layout: ArtworkLayout
  private rect: VisibleRect
  private raf = 0
  private lastTime = 0
  private elapsedSeconds = 0
  private destroyed = false
  private randomState = 0x6d2b79fa
  private lampWeight = 0
  private debugView: LeafDebugView = 'none'

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
    this.sprites = results.flatMap(result => result.status === 'fulfilled' ? [this.prepareSprite(result.value)] : [])
    if (this.sprites.length === 0) {
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

  updateLighting(lampWeight: number): void {
    this.lampWeight = Math.max(0, Math.min(1, lampWeight))
  }

  updateDebugView(view: LeafDebugView): void {
    this.debugView = view
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

  private random(): number {
    // Stable independent sequence; respawns consume new values rather than
    // replaying a common batch or relying on Math.random during validation.
    this.randomState = (this.randomState + 0x6d2b79f5) >>> 0
    let value = this.randomState
    value = Math.imul(value ^ (value >>> 15), value | 1)
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61)
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296
  }

  private between(min: number, max: number): number {
    return min + this.random() * (max - min)
  }

  private prepareSprite(image: HTMLImageElement): LeafSprite {
    // The source PNGs are 1024px squares displayed at only a few dozen pixels.
    // Downsample once, including the very slight lamp tint, instead of applying
    // a Canvas filter to every leaf on every animation frame.
    const make = (warm: boolean): HTMLCanvasElement => {
      const canvas = document.createElement('canvas')
      canvas.width = canvas.height = 256
      const context = canvas.getContext('2d', { alpha: true })!
      context.imageSmoothingQuality = 'high'
      if (warm) context.filter = 'sepia(0.30) saturate(1.06) brightness(1.14)'
      context.drawImage(image, 0, 0, 256, 256)
      return canvas
    }
    return { base: make(false), warm: make(true) }
  }

  private newLeaf(initial: boolean, depth: LeafDepth): Leaf {
    const size = depth === 'background' ? this.between(this.config.minVisibleSize * 0.7, this.config.minVisibleSize * 1.05)
      : depth === 'foreground' ? this.between(this.config.foregroundVisibleSize * 0.86, this.config.foregroundVisibleSize)
        : this.between(this.config.minVisibleSize, this.config.maxVisibleSize)
    const speedScale = depth === 'background' ? 0.7 : depth === 'foreground' ? 1.35 : 1
    let x = this.random()
    const y = initial ? this.random() : -size / Math.max(1, this.rect.height) - this.between(0.02, 0.20)
    if (depth === 'foreground') {
      // Reject likely center-face passages at birth; moving leaves get a soft
      // steering/opacity guard below, so this never becomes a rectangular cut.
      for (let attempt = 0; attempt < 5; attempt++) {
        const sourceX = (this.rect.x + x * this.rect.width - this.layout.x) / this.layout.width * ARTWORK_WIDTH
        const sourceY = (this.rect.y + y * this.rect.height - this.layout.y) / this.layout.height * ARTWORK_HEIGHT
        if (sourceY > FACE.y + FACE.ry || Math.abs(sourceX - FACE.x) > FACE.rx * 1.25) break
        x = this.random()
      }
    }
    return {
      depth,
      sprite: this.sprites[Math.floor(this.random() * this.sprites.length)]!,
      x,
      y,
      size,
      fallSpeed: this.between(this.config.minFallSpeed, this.config.maxFallSpeed) * speedScale,
      driftSpeed: this.between(-3.0, 3.0),
      swayAmplitude: this.between(1.2, this.config.swaySpeed * (depth === 'foreground' ? 1.6 : 1.1)),
      rotation: this.between(-Math.PI, Math.PI),
      rotationSpeed: this.between(-0.16, 0.16) * speedScale,
      phase: this.between(0, Math.PI * 2),
      swayRate: this.between(0.42, 1.30),
      turbulencePhase: this.between(0, Math.PI * 2),
      turbulenceRate: this.between(1.25, 2.35),
      liftPhase: this.between(0, Math.PI * 2),
      liftRate: this.between(0.35, 0.82),
      avoidanceSide: 0,
      opacity: this.between(this.config.minOpacity, this.config.maxOpacity) *
        (depth === 'background' ? 0.66 : depth === 'foreground' ? 0.83 : 1),
    }
  }

  private reconcileCount(): void {
    if (this.sprites.length === 0) return
    const target = this.layout.viewportWidth <= this.config.mobileBreakpoint ? this.config.mobileCount : this.config.desktopCount
    const background = Math.round(target * this.config.backgroundChance)
    const foreground = Math.max(1, Math.round(target * this.config.foregroundChance))
    const counts: Record<LeafDepth, number> = { background, midground: target - background - foreground, foreground }
    const next: Leaf[] = []
    for (const depth of ['background', 'midground', 'foreground'] as const) {
      const kept = this.leaves.filter(leaf => leaf.depth === depth).slice(0, counts[depth])
      next.push(...kept)
      for (let index = kept.length; index < counts[depth]; index++) next.push(this.newLeaf(true, depth))
    }
    this.leaves = next
    this.onCount(this.leaves.length)
  }

  private tick = (time: number): void => {
    if (this.destroyed || document.hidden) return
    this.raf = requestAnimationFrame(this.tick)
    if (this.lastTime && time - this.lastTime < 1000 / this.config.fpsCap) return
    const dt = this.lastTime ? Math.min((time - this.lastTime) / 1000, 0.05) : 0
    this.lastTime = time
    this.elapsedSeconds += dt
    const seconds = this.elapsedSeconds
    const sharedWind = this.config.windSpeed + this.config.gustSpeed * Math.sin(seconds * 2000 * Math.PI / this.config.gustPeriodMs + 0.18 * Math.sin(seconds * 0.19))
    for (const leaf of this.leaves) {
      const sway = Math.sin(seconds * leaf.swayRate + leaf.phase) * leaf.swayAmplitude
      const turbulence = Math.sin(seconds * leaf.turbulenceRate + leaf.turbulencePhase) * 0.85
      const source = this.sourcePosition(leaf)
      const distance = faceDistance(source.x, source.y, leaf.size * 0.5)
      if (distance < 1.42 && leaf.avoidanceSide === 0) leaf.avoidanceSide = source.x < FACE.x ? -1 : 1
      if (distance > 1.65) leaf.avoidanceSide = 0
      const faceSteer = leaf.avoidanceSide * (leaf.depth === 'foreground' ? 15 : 7) * (1 - smooth(0.55, 1.45, distance))
      leaf.x += (sharedWind + leaf.driftSpeed + sway + turbulence + faceSteer) * dt / Math.max(1, this.rect.width)
      const lift = Math.max(0, Math.sin(seconds * leaf.liftRate + leaf.liftPhase)) ** 12 * 5.5
      leaf.y += (leaf.fallSpeed * (0.82 + 0.22 * Math.sin(seconds * leaf.swayRate * 0.71 + leaf.phase)) - lift) * dt / Math.max(1, this.rect.height)
      leaf.rotation += (leaf.rotationSpeed + 0.035 * Math.cos(seconds * leaf.swayRate + leaf.turbulencePhase)) * dt
      if (leaf.y > 1 + leaf.size / Math.max(1, this.rect.height) || leaf.x < -0.15 || leaf.x > 1.15) {
        Object.assign(leaf, this.newLeaf(false, leaf.depth))
      }
    }
    this.draw()
  }

  private draw(): void {
    const { ctx, rect } = this
    ctx.clearRect(0, 0, this.layout.viewportWidth, this.layout.viewportHeight)
    if (rect.width <= 0 || rect.height <= 0) return
    ctx.save()
    ctx.beginPath()
    ctx.rect(rect.x, rect.y, rect.width, rect.height)
    ctx.clip()
    for (const leaf of this.leaves) {
      const spriteSize = leaf.size / 0.73 // masters use ~73% of their transparent square
      const tilt = 0.78 + 0.22 * Math.cos(this.elapsedSeconds * leaf.swayRate + leaf.phase)
      const source = this.sourcePosition(leaf)
      const faceDistanceValue = faceDistance(source.x, source.y, leaf.size * 0.5)
      const minimum = leaf.depth === 'foreground' ? 0.05 : leaf.depth === 'midground' ? 0.22 : 0.48
      const faceVisibility = minimum + (1 - minimum) * smooth(0.32, 1.35, faceDistanceValue)
      const lamp = this.debugView === 'lamp-off' ? 0 : this.lampWeight * leafLampInfluence(source.x, source.y)
      ctx.save()
      ctx.translate(rect.x + leaf.x * rect.width, rect.y + leaf.y * rect.height)
      ctx.rotate(leaf.rotation)
      ctx.scale(tilt, 1)
      const alpha = leaf.opacity * faceVisibility
      ctx.globalAlpha = alpha * (1 - lamp * 0.35)
      ctx.drawImage(leaf.sprite.base, -spriteSize / 2, -spriteSize / 2, spriteSize, spriteSize)
      if (lamp > 0.015) {
        ctx.globalAlpha = alpha * lamp * 0.55
        ctx.drawImage(leaf.sprite.warm, -spriteSize / 2, -spriteSize / 2, spriteSize, spriteSize)
      }
      if (this.debugView === 'depth') {
        ctx.globalAlpha = 0.9
        ctx.strokeStyle = leaf.depth === 'background' ? '#6db6ff' : leaf.depth === 'foreground' ? '#ffa45a' : '#70df9b'
        ctx.strokeRect(-spriteSize / 2, -spriteSize / 2, spriteSize, spriteSize)
      }
      ctx.restore()
    }
    if (this.debugView === 'depth') {
      ctx.strokeStyle = '#69f2d8'
      ctx.lineWidth = 1.5
      ctx.beginPath()
      ctx.ellipse(this.layout.x + FACE.x / ARTWORK_WIDTH * this.layout.width,
        this.layout.y + FACE.y / ARTWORK_HEIGHT * this.layout.height,
        FACE.rx / ARTWORK_WIDTH * this.layout.width, FACE.ry / ARTWORK_HEIGHT * this.layout.height, 0, 0, Math.PI * 2)
      ctx.stroke()
    }
    ctx.restore()
  }

  private sourcePosition(leaf: Leaf): { x: number; y: number } {
    return {
      x: (this.rect.x + leaf.x * this.rect.width - this.layout.x) / this.layout.width * ARTWORK_WIDTH,
      y: (this.rect.y + leaf.y * this.rect.height - this.layout.y) / this.layout.height * ARTWORK_HEIGHT,
    }
  }

  private onVisibility = (): void => {
    if (document.hidden) {
      cancelAnimationFrame(this.raf)
      this.lastTime = 0
    } else if (!this.destroyed && this.sprites.length > 0) {
      this.lastTime = 0
      this.raf = requestAnimationFrame(this.tick)
    }
  }
}
