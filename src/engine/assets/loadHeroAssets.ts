import type { ArtworkSpec } from '../types'
import type { BlinkConfig } from '../animation/BlinkTimeline'
import { loadImage } from './loadImage'

export interface HeroAssetSpec {
  artwork: ArtworkSpec
  normalUrl: string
  skyUrls: Record<string, string>
  skyEdgeReconstructionUrl: string
  skyEdgeCoverageUrl: string
  hairMaskUrl: string
  materialMaskUrl: string
  lampSourceUrl: string
  lampInfluenceUrl: string
  blinkEyes: BlinkConfig['eyes']
  sceneDepthUrl: string
  towerReceiverUrl: string
}

/** Order is the renderer texture contract; every fixed asset is registered here. */
export async function loadHeroAssets(spec: HeroAssetSpec, signal: AbortSignal,
  progress: (loaded: number, total: number) => void): Promise<HTMLImageElement[]> {
  const { width, height } = spec.artwork
  const full = (name: string, url: string): [string, string, number, number] => [name, url, width, height]
  const entries = [
    full('Base', spec.artwork.baseUrl), full('Normal', spec.normalUrl),
    ...['dawn', 'noon', 'dusk', 'night'].map(phase => full(`Sky ${phase}`, spec.skyUrls[phase])),
    full('Sky reconstruction', spec.skyEdgeReconstructionUrl), full('Sky coverage', spec.skyEdgeCoverageUrl),
    full('Hair', spec.hairMaskUrl), full('Material', spec.materialMaskUrl),
    full('Lamp source', spec.lampSourceUrl), full('Lamp influence', spec.lampInfluenceUrl),
    ...spec.blinkEyes.map((eye, i): [string, string, number, number] => [`Blink ${i}`, eye.url, eye.width, eye.height]),
    full('Scene depth', spec.sceneDepthUrl), full('Tower receiver', spec.towerReceiverUrl),
  ]
  let loaded = 0
  progress(loaded, entries.length)
  return Promise.all(entries.map(async ([name, url, w, h]) => {
    const image = await loadImage(url, { signal, priority: name === 'Base' ? 'high' : 'low' })
    if (image.naturalWidth !== w || image.naturalHeight !== h) throw new Error(`${name} does not match its registered dimensions`)
    progress(++loaded, entries.length)
    return image
  }))
}
