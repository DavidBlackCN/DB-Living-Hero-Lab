<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadHeroAssets } from '../engine/assets/loadHeroAssets'
import { layoutArtwork } from '../engine/coordinates/artwork'
import { BaseRenderer } from '../engine/renderer/BaseRenderer'
import type { SkyState } from '../config/sky'
import type { MoonDirection } from '../config/moonlight'
import type { LampState } from '../config/lamps'
import type { ArtworkSpec, FitMode, LightingState, RenderView } from '../engine/types'
import { breathingConfig, type BreathingState } from '../engine/animation/breathing'
import { hairConfig, type HairState } from '../engine/animation/hair'
import type { BlinkConfig } from '../engine/animation/BlinkTimeline'
import type { PostState } from '../config/post'

const props = defineProps<{ active: boolean; maxPixels: number; artwork: ArtworkSpec; normalUrl: string; skyUrls: Record<string, string>; skyEdgeReconstructionUrl: string; skyEdgeCoverageUrl: string; hairMaskUrl: string; materialMaskUrl: string; lampSourceUrl: string; lampInfluenceUrl: string; sceneDepthUrl: string; towerReceiverUrl: string; sky: SkyState; moonDirection: MoonDirection; lamps: LampState; renderView: RenderView; lighting: LightingState; lightingDetailEnabled: boolean; directionalStrength: number; post: PostState; breathing: BreathingState; hair: HairState; blinkEyes: BlinkConfig['eyes']; blinkAmount: number; fit: FitMode; dprCap: number }>()
const emit = defineEmits<{ (e: 'ready'): void; (e: 'failed', reason: string): void; (e: 'frame', milliseconds: number): void; (e: 'progress', progress: { loaded: number; total: number }): void; (e: 'slow'): void }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let renderer: BaseRenderer | null = null
let loadController: AbortController | null = null
let maxDimension = 16384
let slowSince: number | null = null
let slowSamples = 0
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
  slowSince = null
  slowSamples = 0
}

function motionTick(time: number): void {
  if (!needsMotion() || !props.active || document.hidden || !renderer) { stopMotion(); return }
  if (lastTick !== null) {
    // Sustained frame delivery pressure, not CPU submission time or one slow frame.
    if (time - lastTick > 80) {
      slowSince ??= time
      slowSamples++
      if (time - slowSince > 8000 && slowSamples > 40) { emit('slow'); slowSince = null; slowSamples = 0 }
    } else { slowSince = null; slowSamples = 0 }
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
  if (needsMotion() && props.active && !document.hidden && renderer) motionFrame = requestAnimationFrame(motionTick)
}

function draw(): void {
  if (!renderer || !canvas.value || document.hidden) return
  const bounds = canvas.value.getBoundingClientRect()
  if (bounds.width < 1 || bounds.height < 1) return
  try {
    const start = performance.now()
    const dpr = Math.min(props.dprCap, Math.sqrt(props.maxPixels / (bounds.width * bounds.height)),
      maxDimension / bounds.width, maxDimension / bounds.height)
    renderer.render(layoutArtwork(props.artwork, bounds.width, bounds.height, props.fit), dpr, props.renderView, props.lighting, props.sky, props.moonDirection,
      props.breathing, phaseSeconds / breathingConfig.periodSeconds * Math.PI * 2, props.hair, hairSeconds, props.blinkAmount, props.lightingDetailEnabled, props.post, props.directionalStrength, props.lamps)
    emit('frame', performance.now() - start)
  } catch (error) {
    renderer.destroy()
    renderer = null
    emit('failed', String(error))
  }
}

async function initialize(): Promise<void> {
  const current = ++generation
  stopMotion()
  loadController?.abort()
  const controller = new AbortController()
  loadController = controller
  const signal = controller.signal
  renderer?.destroy()
  renderer = null
  try {
    const gl = canvas.value?.getContext('webgl2', { alpha: false, antialias: false })
    if (!gl || gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS) < 16) throw new Error('WebGL2 requirements unavailable')
    maxDimension = Math.min(gl.getParameter(gl.MAX_TEXTURE_SIZE), gl.getParameter(gl.MAX_RENDERBUFFER_SIZE))
    const [image, normalImage, dawn, noon, dusk, night, edgeReconstruction, edgeCoverage,
      hairMask, materialMask, lampSource, lampInfluence, leftBlink, rightBlink, sceneDepth, towerReceiver]
      = await loadHeroAssets(props, signal, (loaded, total) => {
        if (mounted && generation === current) emit('progress', { loaded, total })
      })
    if (!mounted || current !== generation || !canvas.value) return
    const skyImages = [dawn, noon, dusk, night]
    renderer = new BaseRenderer(canvas.value, image, normalImage, skyImages, edgeReconstruction, edgeCoverage, hairMask, materialMask, lampSource, lampInfluence, [leftBlink, rightBlink], sceneDepth, towerReceiver)
    draw()
    if (renderer) { emit('ready'); scheduleMotion() }
  } catch (error) {
    controller.abort()
    if (mounted && current === generation) emit('failed', String(error))
  }
}

function onContextLost(event: Event): void {
  event.preventDefault()
  generation++
  loadController?.abort()
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

watch(() => props.active, () => { if (props.active) draw(); scheduleMotion() })
watch(() => props.fit, draw)
watch(() => [props.dprCap, props.maxPixels], draw)
watch(() => props.renderView, draw)
watch(() => props.lightingDetailEnabled, draw)
watch(() => props.directionalStrength, draw)
watch(() => [props.post.enabled, props.post.bloomEnabled, props.post.view,
  props.post.atmosphere?.enabled, props.post.atmosphere?.hazeEnabled, props.post.atmosphere?.gradeEnabled], draw)
// Vue batches time-derived inputs into one on-demand render for Low/reduced motion.
watch(() => [props.post, props.lighting, props.sky, props.moonDirection, props.lamps],
  () => { if (!needsMotion()) draw() }, { deep: true, flush: 'post' })
watch(() => props.blinkAmount, draw)
watch(() => props.breathing, () => { draw(); scheduleMotion() }, { deep: true })
watch(() => props.hair, () => { draw(); scheduleMotion() }, { deep: true })

onBeforeUnmount(() => {
  mounted = false
  generation++
  loadController?.abort()
  stopMotion()
  resizeObserver?.disconnect()
  document.removeEventListener('visibilitychange', onVisibility)
  canvas.value?.removeEventListener('webglcontextlost', onContextLost)
  canvas.value?.removeEventListener('webglcontextrestored', onContextRestored)
  renderer?.destroy()
})
</script>

<template>
  <canvas ref="canvas" class="hero-canvas" aria-hidden="true" />
</template>
