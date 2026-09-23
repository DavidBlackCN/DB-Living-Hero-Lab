import type { ArtworkSpec, FitMode, Point } from '../types'

export interface ArtworkLayout {
  x: number
  y: number
  width: number
  height: number
  viewportWidth: number
  viewportHeight: number
}

// CSS pixels, origin at the top left. Negative x/y indicate cropped artwork in cover mode.
export function layoutArtwork(spec: ArtworkSpec, viewportWidth: number, viewportHeight: number, fit: FitMode): ArtworkLayout {
  const resolvedFit = fit === 'auto' ? (viewportWidth / viewportHeight < 0.9 ? 'contain' : 'cover') : fit
  const scale = (resolvedFit === 'cover' ? Math.max : Math.min)(viewportWidth / spec.width, viewportHeight / spec.height)
  const width = spec.width * scale
  const height = spec.height * scale
  return { x: (viewportWidth - width) / 2, y: (viewportHeight - height) / 2, width, height, viewportWidth, viewportHeight }
}

export function uvToSource(uv: Point, spec: ArtworkSpec): Point {
  return { x: uv.x * spec.width, y: uv.y * spec.height }
}

export function sourceToUv(pixel: Point, spec: ArtworkSpec): Point {
  return { x: pixel.x / spec.width, y: pixel.y / spec.height }
}

export function uvToDisplay(uv: Point, layout: ArtworkLayout): Point {
  return { x: layout.x + uv.x * layout.width, y: layout.y + uv.y * layout.height }
}

export function displayToUv(point: Point, layout: ArtworkLayout): Point {
  return { x: (point.x - layout.x) / layout.width, y: (point.y - layout.y) / layout.height }
}

export function displayToCanvas(point: Point, canvas: HTMLCanvasElement, layout: ArtworkLayout): Point {
  return { x: point.x * canvas.width / layout.viewportWidth, y: point.y * canvas.height / layout.viewportHeight }
}
