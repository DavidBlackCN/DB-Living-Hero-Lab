<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import DebugPanel from './DebugPanel.vue'
import BlinkLayer from './BlinkLayer.vue'
import HeroCanvas from './HeroCanvas.vue'
import LeavesLayer from './LeavesLayer.vue'
import { heroConfig } from '../config/hero'
import { createLightingStateForTime } from '../config/lighting'
import { skyFor } from '../config/sky'
import { moonDirectionFor } from '../config/moonlight'
import { leafToneFor } from '../config/leafTone'
import { postFor, type PostState } from '../config/post'
import { layoutArtwork } from '../engine/coordinates/artwork'
import type { BreathingState } from '../engine/animation/breathing'
import type { HairState } from '../engine/animation/hair'
import { useStaticRendering } from '../engine/quality/policy'
import { TimeController, clockMinutes } from '../engine/time/TimeController'
import type { TimeSnapshot } from '../engine/time/TimeController'
import type { FitMode, LightingPresetId, LightingState, QualityPreset, RenderView } from '../engine/types'

const root = ref<HTMLElement | null>(null)
const rendererEnabled = ref(true)
const rendererReady = ref(false)
const rendererError = ref('')
const fit = ref<FitMode>('auto')
const quality = ref<QualityPreset>('auto')
const renderView = ref<RenderView>('lit')
const lightingMinutes = ref(clockMinutes(new Date()))
const timeMode = ref<TimeSnapshot['mode']>('realtime')
const lighting = ref<LightingState>(createLightingStateForTime(lightingMinutes.value))
const sky = computed(() => skyFor(lightingMinutes.value))
const moonDirection = computed(() => moonDirectionFor(lightingMinutes.value))
const leafStyle = computed(() => {
  const tone = leafToneFor(lightingMinutes.value)
  return { filter: `brightness(${tone.brightness.toFixed(3)}) saturate(${tone.saturation.toFixed(3)})` }
})
const showBounds = ref(false)
const showGrid = ref(false)
const blinkEnabled = ref(true)
const blinkPreviewToken = ref(0)
const blinkClosed = ref(false)
const showBlinkRegions = ref(false)
const leavesEnabled = ref(true)
const leavesCount = ref(0)
const breathing = ref<BreathingState>({ enabled: true, strength: 1, showRegion: false })
const hair = ref<HairState>({ enabled: true, strength: 1, showRegion: false })
const lightingDetailEnabled = ref(true)
const directionalEnabled = ref(true)
const directionalGain = ref(1)
const postEnabled = ref(true)
const bloomEnabled = ref(true)
const postView = ref<PostState['view']>('final')
const post = computed<PostState>(() => ({ ...postFor(lightingMinutes.value), enabled: postEnabled.value,
  bloomEnabled: bloomEnabled.value, view: postView.value }))
const frameTime = ref<number | null>(null)
const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedMotion = ref(motionQuery.matches)
const size = ref({ width: window.innerWidth, height: window.innerHeight })
const layout = computed(() => layoutArtwork(heroConfig.artwork, size.value.width, size.value.height, fit.value))
const staticPolicy = computed(() => useStaticRendering(quality.value))
const wantsRenderer = computed(() => rendererEnabled.value && !staticPolicy.value)
const sceneView = computed(() => renderView.value === 'base' || renderView.value === 'lit')
const leavesActive = computed(() => leavesEnabled.value && !reducedMotion.value && quality.value !== 'static' && sceneView.value)
const blinkActive = computed(() => blinkEnabled.value && !reducedMotion.value && quality.value !== 'static' && sceneView.value)
const breathingState = computed<BreathingState>(() => ({ ...breathing.value, enabled: breathing.value.enabled && !reducedMotion.value && wantsRenderer.value }))
const hairState = computed<HairState>(() => ({ ...hair.value, enabled: hair.value.enabled && !reducedMotion.value && wantsRenderer.value }))
const rendererStatus = computed(() => !wantsRenderer.value ? 'static' : rendererError.value ? 'fallback' : rendererReady.value ? 'WebGL2' : 'loading')
const imageStyle = computed(() => ({ left: `${layout.value.x}px`, top: `${layout.value.y}px`, width: `${layout.value.width}px`, height: `${layout.value.height}px` }))
let observer: ResizeObserver | null = null
const timeController = new TimeController(state => {
  timeMode.value = state.mode
  lightingMinutes.value = state.minutes
  lighting.value = { ...createLightingStateForTime(state.minutes), skyEnabled: lighting.value.skyEnabled }
})

watch(wantsRenderer, () => {
  rendererReady.value = false
  frameTime.value = null
})

function onMotionChange(): void {
  reducedMotion.value = motionQuery.matches
  if (reducedMotion.value) timeController.pause()
}

function onVisibility(): void { timeController.setVisible(!document.hidden) }

function onRendererFailed(reason: string): void {
  rendererReady.value = false
  rendererError.value = reason
  console.warn('Living Hero static fallback:', reason)
}

function onRendererReady(): void {
  rendererError.value = ''
  rendererReady.value = true
}

function selectLightingPreset(preset: LightingPresetId): void {
  const minutes = { dawn: 390, noon: 720, dusk: 1050, night: 1320 }[preset]
  selectLightingTime(minutes)
}

function selectLightingTime(minutes: number): void {
  timeController.select(minutes)
}

onMounted(() => {
  timeController.setVisible(!document.hidden)
  timeController.backToNow()
  document.addEventListener('visibilitychange', onVisibility)
  onMotionChange()
  motionQuery.addEventListener('change', onMotionChange)
  observer = new ResizeObserver(([entry]) => {
    if (entry) size.value = { width: entry.contentRect.width, height: entry.contentRect.height }
  })
  if (root.value) observer.observe(root.value)
})

onBeforeUnmount(() => {
  timeController.destroy()
  document.removeEventListener('visibilitychange', onVisibility)
  observer?.disconnect()
  motionQuery.removeEventListener('change', onMotionChange)
})
</script>

<template>
  <main ref="root" class="hero-stage">
    <img class="hero-image" :style="imageStyle" :src="heroConfig.artwork.baseUrl" alt="DB Living Hero artwork preview" />
    <HeroCanvas v-if="wantsRenderer" :artwork="heroConfig.artwork" :normal-url="heroConfig.normal.url" :sky-urls="heroConfig.sky.urls" :sky-edge-tone-url="heroConfig.sky.edgeToneUrl" :hair-mask-url="heroConfig.hair.maskUrl" :material-mask-url="heroConfig.material.maskUrl"
      :sky="sky" :moon-direction="moonDirection" :render-view="renderView" :lighting="lighting" :post="post" :breathing="breathingState" :hair="hairState" :blink-eyes="heroConfig.blink.eyes"
      :blink-closed="blinkClosed && blinkActive && (renderView === 'lit' || (renderView === 'base' && hairState.enabled))" :lighting-detail-enabled="lightingDetailEnabled" :directional-strength="directionalEnabled ? directionalGain : 0" :fit="fit" :dpr-cap="heroConfig.dprCap"
      :class="{ 'canvas-ready': rendererReady }" @ready="onRendererReady" @failed="onRendererFailed" @frame="frameTime = $event" />
    <BlinkLayer v-if="sceneView" :artwork="heroConfig.artwork" :layout="layout" :config="heroConfig.blink" :enabled="blinkActive"
      :preview-token="blinkPreviewToken" :show-regions="showBlinkRegions" :show-patch="renderView === 'base' && !hairState.enabled" @closed="blinkClosed = $event" />
    <LeavesLayer v-if="leavesActive" :layout="layout" :config="heroConfig.leaves" :style="leafStyle" @count="leavesCount = $event" />
    <div v-if="showBounds || showGrid" class="artwork-overlay" :class="{ 'show-bounds': showBounds, 'show-grid': showGrid }" :style="imageStyle" aria-hidden="true" />
    <DebugPanel v-model:renderer-enabled="rendererEnabled" v-model:fit="fit" v-model:quality="quality" v-model:render-view="renderView"
      v-model:lighting="lighting" v-model:lighting-detail-enabled="lightingDetailEnabled" v-model:directional-enabled="directionalEnabled" v-model:directional-gain="directionalGain" v-model:post-enabled="postEnabled" v-model:bloom-enabled="bloomEnabled" v-model:post-view="postView" :lighting-minutes="lightingMinutes" :moon-direction="moonDirection" :time-mode="timeMode" @select-lighting-preset="selectLightingPreset"
      @select-lighting-time="selectLightingTime"
      @back-to-now="timeController.backToNow()" @toggle-playback="timeMode === 'playing' ? timeController.pause() : timeController.play()"
      v-model:blink-enabled="blinkEnabled" v-model:show-blink-regions="showBlinkRegions"
      v-model:leaves-enabled="leavesEnabled" @preview-blink="blinkPreviewToken++"
      v-model:breathing="breathing"
      v-model:hair="hair"
      v-model:show-bounds="showBounds" v-model:show-grid="showGrid" :renderer-status="rendererStatus"
      :frame-time="wantsRenderer ? frameTime : null" :reduced-motion="reducedMotion" :leaves-count="leavesCount" :leaves-fps-cap="heroConfig.leaves.fpsCap" />
  </main>
</template>
