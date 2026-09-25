<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadImage } from '../engine/assets/loadImage'
import { layoutArtwork } from '../engine/coordinates/artwork'
import { BaseRenderer } from '../engine/renderer/BaseRenderer'
import type { SkyState } from '../config/sky'
import type { ArtworkSpec, FitMode, LightingState, RenderView } from '../engine/types'
import { breathingConfig, type BreathingState } from '../engine/animation/breathing'
import { hairConfig, type HairState } from '../engine/animation/hair'
import type { BlinkConfig } from '../engine/animation/BlinkTimeline'

const props = defineProps<{ artwork: ArtworkSpec; normalUrl: string; skyUrls: Record<string, string>; skyEdgeToneUrl: string; hairMaskUrl: string; sky: SkyState; renderView: RenderView; lighting: LightingState; breathing: BreathingState; hair: HairState; blinkEyes: BlinkConfig['eyes']; blinkClosed: boolean; fit: FitMode; dprCap: number }>()
const emit = defineEmits<{ (e: 'ready'): void; (e: 'failed', reason: string): void; (e: 'frame', milliseconds: number): void }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let renderer: BaseRenderer | null = null
let resizeObserver: ResizeObserver | null = null
let mounted = false
let generation = 0
let motionFrame: number | null = null
let lastTick: number | null = null
let lastDraw = 0
let phaseSeconds = 0
let hairSeconds = 0

function needsMotion(): boolean { return props.breathing.enabled || props.hair.enabled }

function stopMotion(): void {
  if (motionFrame !== null) cancelAnimationFrame(motionFrame)
  motionFrame = null
  lastTick = null
}

function motionTick(time: number): void {
  if (!needsMotion() || document.hidden || !renderer) { stopMotion(); return }
  if (lastTick !== null) {
    const delta = Math.min((time - lastTick) / 1000, 0.05)
    if (props.breathing.enabled) phaseSeconds = (phaseSeconds + delta) % breathingConfig.periodSeconds
    if (props.hair.enabled) hairSeconds = (hairSeconds + delta) % hairConfig.loopSeconds
  }
  lastTick = time
  if (time - lastDraw >= 1000 / 30) {
    lastDraw = time
    draw()
  }
  motionFrame = requestAnimationFrame(motionTick)
}

function scheduleMotion(): void {
  stopMotion()
  if (needsMotion() && !document.hidden && renderer) motionFrame = requestAnimationFrame(motionTick)
}

function draw(): void {
  if (!renderer || !canvas.value || document.hidden) return
  const bounds = canvas.value.getBoundingClientRect()
  if (bounds.width < 1 || bounds.height < 1) return
  try {
    const start = performance.now()
    renderer.render(layoutArtwork(props.artwork, bounds.width, bounds.height, props.fit), props.dprCap, props.renderView, props.lighting, props.sky,
      props.breathing, phaseSeconds / breathingConfig.periodSeconds * Math.PI * 2, props.hair, hairSeconds, props.blinkClosed)
    emit('frame', performance.now() - start)
  } catch (error) {
    renderer.destroy()
    renderer = null
    emit('failed', String(error))
  }
}

async function initialize(): Promise<void> {
  const current = ++generation
  renderer?.destroy()
  renderer = null
  try {
    const [image, normalImage, dawn, noon, dusk, night, edgeTone, hairMask, leftBlink, rightBlink] = await Promise.all([
      loadImage(props.artwork.baseUrl), loadImage(props.normalUrl), loadImage(props.skyUrls.dawn),
      loadImage(props.skyUrls.noon), loadImage(props.skyUrls.dusk), loadImage(props.skyUrls.night),
      loadImage(props.skyEdgeToneUrl),
      loadImage(props.hairMaskUrl),
      loadImage(props.blinkEyes[0].url), loadImage(props.blinkEyes[1].url),
    ])
    if (!mounted || current !== generation || !canvas.value) return
    if (image.naturalWidth !== props.artwork.width || image.naturalHeight !== props.artwork.height) {
      throw new Error('Base image dimensions do not match Artwork Space')
    }
    if (normalImage.naturalWidth !== props.artwork.width || normalImage.naturalHeight !== props.artwork.height) {
      throw new Error('Normal image dimensions do not match Artwork Space')
    }
    const skyImages = [dawn, noon, dusk, night]
    if (skyImages.some(skyImage => skyImage.naturalWidth !== props.artwork.width || skyImage.naturalHeight !== props.artwork.height)) {
      throw new Error('Sky image dimensions do not match Artwork Space')
    }
    if (edgeTone.naturalWidth !== props.artwork.width || edgeTone.naturalHeight !== props.artwork.height) {
      throw new Error('Sky edge tone image dimensions do not match Artwork Space')
    }
    if (hairMask.naturalWidth !== props.artwork.width || hairMask.naturalHeight !== props.artwork.height) {
      throw new Error('Hair mask dimensions do not match Artwork Space')
    }
    if (leftBlink.naturalWidth !== props.blinkEyes[0].width || leftBlink.naturalHeight !== props.blinkEyes[0].height
      || rightBlink.naturalWidth !== props.blinkEyes[1].width || rightBlink.naturalHeight !== props.blinkEyes[1].height) {
      throw new Error('Local Blink images do not match registered eye rectangles')
    }
    renderer = new BaseRenderer(canvas.value, image, normalImage, skyImages, edgeTone, hairMask, [leftBlink, rightBlink])
    draw()
    if (renderer) { emit('ready'); scheduleMotion() }
  } catch (error) {
    if (mounted && current === generation) emit('failed', String(error))
  }
}

function onContextLost(event: Event): void {
  event.preventDefault()
  stopMotion()
  renderer?.destroy()
  renderer = null
  emit('failed', 'WebGL context lost')
}

function onContextRestored(): void {
  void initialize()
}

function onVisibility(): void {
  if (document.hidden) stopMotion()
  else { draw(); scheduleMotion() }
}

onMounted(() => {
  mounted = true
  canvas.value?.addEventListener('webglcontextlost', onContextLost)
  canvas.value?.addEventListener('webglcontextrestored', onContextRestored)
  document.addEventListener('visibilitychange', onVisibility)
  resizeObserver = new ResizeObserver(draw)
  if (canvas.value) resizeObserver.observe(canvas.value)
  void initialize()
})

watch(() => props.fit, draw)
watch(() => props.dprCap, draw)
watch(() => props.renderView, draw)
watch(() => props.lighting, () => { if (!needsMotion()) draw() }, { deep: true })
watch(() => props.sky, () => { if (!needsMotion()) draw() }, { deep: true })
watch(() => props.blinkClosed, draw)
watch(() => props.breathing, () => { draw(); scheduleMotion() }, { deep: true })
watch(() => props.hair, () => { draw(); scheduleMotion() }, { deep: true })

onBeforeUnmount(() => {
  mounted = false
  generation++
  stopMotion()
  resizeObserver?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  canvas.value?.removeEventListener('webglcontextlost', onContextLost)
  canvas.value?.removeEventListener('webglcontextrestored', onContextRestored)
  renderer?.destroy()
})
</script>

<template>
  <canvas ref="canvas" class="hero-canvas" aria-label="Base Albedo WebGL preview" />
</template>
