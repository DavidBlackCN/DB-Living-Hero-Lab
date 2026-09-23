<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { loadImage } from '../engine/assets/loadImage'
import { layoutArtwork } from '../engine/coordinates/artwork'
import { BaseRenderer } from '../engine/renderer/BaseRenderer'
import type { ArtworkSpec, FitMode, NormalView } from '../engine/types'

const props = defineProps<{ artwork: ArtworkSpec; normalUrl: string; normalView: NormalView; lightAngle: number; testStrength: number; fit: FitMode; dprCap: number }>()
const emit = defineEmits<{ (e: 'ready'): void; (e: 'failed', reason: string): void; (e: 'frame', milliseconds: number): void }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let renderer: BaseRenderer | null = null
let resizeObserver: ResizeObserver | null = null
let mounted = false
let generation = 0

function draw(): void {
  if (!renderer || !canvas.value || document.hidden) return
  const bounds = canvas.value.getBoundingClientRect()
  if (bounds.width < 1 || bounds.height < 1) return
  try {
    const start = performance.now()
    renderer.render(layoutArtwork(props.artwork, bounds.width, bounds.height, props.fit), props.dprCap, props.normalView, props.lightAngle, props.testStrength)
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
    const [image, normalImage] = await Promise.all([loadImage(props.artwork.baseUrl), loadImage(props.normalUrl)])
    if (!mounted || current !== generation || !canvas.value) return
    if (image.naturalWidth !== props.artwork.width || image.naturalHeight !== props.artwork.height) {
      throw new Error('Base image dimensions do not match Artwork Space')
    }
    if (normalImage.naturalWidth !== props.artwork.width || normalImage.naturalHeight !== props.artwork.height) {
      throw new Error('Normal image dimensions do not match Artwork Space')
    }
    renderer = new BaseRenderer(canvas.value, image, normalImage)
    draw()
    if (renderer) emit('ready')
  } catch (error) {
    if (mounted && current === generation) emit('failed', String(error))
  }
}

function onContextLost(event: Event): void {
  event.preventDefault()
  renderer?.destroy()
  renderer = null
  emit('failed', 'WebGL context lost')
}

function onContextRestored(): void {
  void initialize()
}

function onVisibility(): void {
  if (!document.hidden) draw()
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
watch(() => props.normalView, draw)
watch(() => props.lightAngle, draw)

onBeforeUnmount(() => {
  mounted = false
  generation++
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
