<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DebugPanel from './DebugPanel.vue'
import HeroCanvas from './HeroCanvas.vue'
import LeavesLayer from './LeavesLayer.vue'
import { heroConfig } from '../config/hero'
import { layoutArtwork } from '../engine/coordinates/artwork'
import { useStaticRendering } from '../engine/quality/policy'
import type { FitMode, QualityPreset } from '../engine/types'

const root = ref<HTMLElement | null>(null)
const rendererEnabled = ref(true)
const rendererReady = ref(false)
const rendererError = ref('')
const fit = ref<FitMode>('auto')
const quality = ref<QualityPreset>('auto')
const showBounds = ref(false)
const showGrid = ref(false)
const previewBlink = ref(false)
const leavesEnabled = ref(true)
const leavesCount = ref(0)
const frameTime = ref<number | null>(null)
const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedMotion = ref(motionQuery.matches)
const size = ref({ width: window.innerWidth, height: window.innerHeight })
const layout = computed(() => layoutArtwork(heroConfig.artwork, size.value.width, size.value.height, fit.value))
const activeArtwork = computed(() => ({ ...heroConfig.artwork, baseUrl: previewBlink.value ? heroConfig.candidateBlinkUrl : heroConfig.artwork.baseUrl }))
const staticPolicy = computed(() => useStaticRendering(quality.value, reducedMotion.value))
const wantsRenderer = computed(() => rendererEnabled.value && !staticPolicy.value)
const leavesActive = computed(() => leavesEnabled.value && !reducedMotion.value && quality.value !== 'static')
const rendererStatus = computed(() => !wantsRenderer.value ? 'static' : rendererError.value ? 'fallback' : rendererReady.value ? 'WebGL2' : 'loading')
const imageStyle = computed(() => ({ left: `${layout.value.x}px`, top: `${layout.value.y}px`, width: `${layout.value.width}px`, height: `${layout.value.height}px` }))
let observer: ResizeObserver | null = null

watch(wantsRenderer, () => {
  rendererReady.value = false
  frameTime.value = null
})

watch(previewBlink, () => {
  rendererReady.value = false
  frameTime.value = null
})

function onMotionChange(): void {
  reducedMotion.value = motionQuery.matches
}

function onRendererFailed(reason: string): void {
  rendererReady.value = false
  rendererError.value = reason
  console.warn('Living Hero static fallback:', reason)
}

function onRendererReady(): void {
  rendererError.value = ''
  rendererReady.value = true
}

onMounted(() => {
  onMotionChange()
  motionQuery.addEventListener('change', onMotionChange)
  observer = new ResizeObserver(([entry]) => {
    if (entry) size.value = { width: entry.contentRect.width, height: entry.contentRect.height }
  })
  if (root.value) observer.observe(root.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
  motionQuery.removeEventListener('change', onMotionChange)
})
</script>

<template>
  <main ref="root" class="hero-stage">
    <img class="hero-image" :style="imageStyle" :src="activeArtwork.baseUrl" alt="DB Living Hero artwork preview" />
    <HeroCanvas v-if="wantsRenderer" :key="activeArtwork.baseUrl" :artwork="activeArtwork" :fit="fit" :dpr-cap="heroConfig.dprCap"
      :class="{ 'canvas-ready': rendererReady }" @ready="onRendererReady" @failed="onRendererFailed" @frame="frameTime = $event" />
    <LeavesLayer v-if="leavesActive" :layout="layout" :config="heroConfig.leaves" @count="leavesCount = $event" />
    <div v-if="showBounds || showGrid" class="artwork-overlay" :class="{ 'show-bounds': showBounds, 'show-grid': showGrid }" :style="imageStyle" aria-hidden="true" />
    <DebugPanel v-model:renderer-enabled="rendererEnabled" v-model:fit="fit" v-model:quality="quality" v-model:preview-blink="previewBlink" v-model:leaves-enabled="leavesEnabled"
      v-model:show-bounds="showBounds" v-model:show-grid="showGrid" :renderer-status="rendererStatus"
      :frame-time="wantsRenderer ? frameTime : null" :reduced-motion="reducedMotion" :leaves-count="leavesCount" :leaves-fps-cap="heroConfig.leaves.fpsCap" />
  </main>
</template>
